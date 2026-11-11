"""Asynchronous background job queue with concurrency guardrails and deduplication."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, Optional

from app.agent.graph import ThreeDGenerationGraph
from app.api.schemas import GenerationRequest
from app.config import Settings, get_settings
from app.storage.metadata import MetadataRepository, compute_request_hash
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JobService:
    """Manages non-blocking background video generation jobs."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        metadata_repo: Optional[MetadataRepository] = None,
        graph: Optional[ThreeDGenerationGraph] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_repo = metadata_repo or MetadataRepository(self.settings)
        self.graph = graph or ThreeDGenerationGraph(
            settings=self.settings, metadata_repo=self.metadata_repo
        )
        self._semaphore = asyncio.Semaphore(max(1, self.settings.max_concurrent_jobs))
        self._tasks: Dict[str, asyncio.Task[Any]] = {}
        self._inflight_hashes: Dict[str, str] = {}

    def submit_job(self, request: GenerationRequest, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Enqueue a new background generation job or return an in-flight duplicate."""
        req_hash = compute_request_hash(request)
        if not request.force_regenerate and req_hash in self._inflight_hashes:
            existing_job_id = self._inflight_hashes[req_hash]
            existing = self.metadata_repo.get_job(existing_job_id)
            if existing and existing.get("status") in ("queued", "processing"):
                return {
                    "job_id": existing_job_id,
                    "status": existing["status"],
                    "deduplicated": True,
                }

        jid = job_id or f"generation-job-{uuid.uuid4().hex[:10]}"
        self.metadata_repo.upsert_job(
            job_id=jid,
            status="queued",
            progress_pct=0,
            current_stage="queued",
            message="Educational video generation queued.",
            request_data=request.model_dump(by_alias=True),
            content_hash=req_hash,
        )
        self._inflight_hashes[req_hash] = jid
        task = asyncio.create_task(self._run_job(jid, request, req_hash))
        self._tasks[jid] = task
        return {
            "job_id": jid,
            "status": "processing",
            "deduplicated": False,
        }

    async def run_job_sync(self, request: GenerationRequest, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a workflow directly (useful for deterministic testing or synchronous callers)."""
        jid = job_id or f"generation-job-{uuid.uuid4().hex[:10]}"
        req_hash = compute_request_hash(request)
        self.metadata_repo.upsert_job(
            job_id=jid,
            status="queued",
            progress_pct=0,
            current_stage="queued",
            message="Educational video generation started.",
            request_data=request.model_dump(by_alias=True),
            content_hash=req_hash,
        )
        return dict(await self.graph.run(jid, request))

    async def _run_job(self, job_id: str, request: GenerationRequest, req_hash: str) -> None:
        try:
            async with self._semaphore:
                await self.graph.run(job_id, request)
        except Exception as exc:
            logger.exception("Unhandled error in background generation job %s", job_id)
            self.metadata_repo.upsert_job(
                job_id=job_id,
                status="failed",
                progress_pct=100,
                current_stage="failed",
                message=str(exc),
                request_data=request.model_dump(by_alias=True),
                result_data={"errors": [str(exc)]},
                content_hash=req_hash,
            )
        finally:
            self._tasks.pop(job_id, None)
            if self._inflight_hashes.get(req_hash) == job_id:
                self._inflight_hashes.pop(req_hash, None)

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.metadata_repo.get_job(job_id)

    async def wait_all(self) -> None:
        if self._tasks:
            await asyncio.gather(*list(self._tasks.values()), return_exceptions=True)

