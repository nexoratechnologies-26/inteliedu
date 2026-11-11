"""Official Runway Developer API v1 asynchronous client."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings, get_settings
from app.utils.error_handler import DependencyUnavailableError, RunwayAPIError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RunwayTaskResult:
    """Result from polling a Runway asynchronous generation task."""

    task_id: str
    status: str
    outputs: List[str]
    failure: Optional[str] = None
    failure_code: Optional[str] = None
    local_path: Optional[str] = None


class RunwayAPIClient:
    """Async REST client for Runway Developer API (`https://api.dev.runwayml.com/v1`)."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.runway_api_key)

    def _headers(self) -> Dict[str, str]:
        if not self.settings.runway_api_key:
            raise DependencyUnavailableError(
                "Runway generation requested, but RUNWAY_API_KEY is not configured.",
                missing_dependencies=["RUNWAY_API_KEY"],
            )
        return {
            "Authorization": f"Bearer {self.settings.runway_api_key}",
            "X-Runway-Version": self.settings.runway_api_version,
            "Content-Type": "application/json",
        }

    async def _request_with_rate_limit(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        url = f"{self.settings.runway_api_base_url.rstrip('/')}/{path.lstrip('/')}"
        headers = self._headers()

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.request(method, url, headers=headers, json=json_body)
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
                    if attempt < max_retries:
                        logger.warning("Runway API rate limited (429); retrying in %.1fs", retry_after)
                        await asyncio.sleep(min(retry_after, 30.0))
                        continue
                    raise RunwayAPIError(
                        "Runway API rate limit exceeded.", status_code=429, details={"body": resp.text}
                    )
                if resp.status_code >= 400:
                    raise RunwayAPIError(
                        f"Runway API HTTP {resp.status_code}: {resp.text}",
                        status_code=resp.status_code,
                    )
                return resp.json()
            except httpx.HTTPError as exc:
                if attempt < max_retries:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                raise RunwayAPIError(f"Runway HTTP transport error: {exc}") from exc

        raise RunwayAPIError("Runway request exhausted retries.")

    async def create_text_to_video(
        self,
        prompt_text: str,
        duration: int = 5,
        ratio: str = "1280:720",
        model: Optional[str] = None,
    ) -> str:
        payload = {
            "model": model or self.settings.runway_model,
            "promptText": prompt_text[:1000],
            "ratio": ratio,
            "duration": int(duration),
        }
        data = await self._request_with_rate_limit("POST", "/text_to_video", json_body=payload)
        task_id = data.get("id")
        if not task_id:
            raise RunwayAPIError("Runway text_to_video response missing task id.", details=data)
        return str(task_id)

    async def create_image_to_video(
        self,
        prompt_image: str,
        prompt_text: Optional[str] = None,
        duration: int = 5,
        ratio: str = "1280:720",
        model: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": model or self.settings.runway_model,
            "promptImage": prompt_image,
            "ratio": ratio,
            "duration": int(duration),
        }
        if prompt_text:
            payload["promptText"] = prompt_text[:1000]
        data = await self._request_with_rate_limit("POST", "/image_to_video", json_body=payload)
        task_id = data.get("id")
        if not task_id:
            raise RunwayAPIError("Runway image_to_video response missing task id.", details=data)
        return str(task_id)

    async def get_task(self, task_id: str) -> RunwayTaskResult:
        data = await self._request_with_rate_limit("GET", f"/tasks/{task_id}")
        return RunwayTaskResult(
            task_id=str(data.get("id", task_id)),
            status=str(data.get("status", "UNKNOWN")),
            outputs=list(data.get("output") or []),
            failure=data.get("failure"),
            failure_code=data.get("failureCode"),
        )

    async def wait_for_task(
        self,
        task_id: str,
        timeout_seconds: Optional[int] = None,
        poll_interval_seconds: float = 4.0,
    ) -> RunwayTaskResult:
        timeout = float(timeout_seconds or self.settings.runway_timeout_seconds)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            res = await self.get_task(task_id)
            if res.status == "SUCCEEDED":
                return res
            if res.status in {"FAILED", "CANCELED", "CANCELLED"}:
                raise RunwayAPIError(
                    f"Runway task {task_id} failed: {res.failure or res.failure_code or res.status}",
                    details={"task_id": task_id, "failure_code": res.failure_code},
                )
            await asyncio.sleep(poll_interval_seconds)

        raise RunwayAPIError(
            f"Runway task {task_id} timed out after {timeout:.0f}s.",
            status_code=504,
            details={"task_id": task_id},
        )

    async def download_output(self, url: str, dest_path: Path) -> Path:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            dest_path.write_bytes(resp.content)
        return dest_path

