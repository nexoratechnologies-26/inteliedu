"""High-level orchestration service connecting FastAPI endpoints to the agent workflow."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.agent.routing import select_generation_route
from app.agent.supervisor import SupervisorBridge
from app.agent.topic_understanding import TopicUnderstandingModule
from app.agent.video_planner import VideoPlannerModule
from app.api.schemas import GenerationRequest, PlanRequest, PlanResponse
from app.blender.scene_generator import BlenderSceneGenerator
from app.config import Settings, get_settings
from app.services.job_service import JobService
from app.storage.metadata import MetadataRepository
from app.storage.storage_service import build_storage_backend
from app.utils.error_handler import AgentError, ValidationError


class GenerationService:
    """Facade exposing planning, background job control, caching, and video asset CRUD."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        metadata_repo: Optional[MetadataRepository] = None,
        job_service: Optional[JobService] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_repo = metadata_repo or MetadataRepository(self.settings)
        self.job_service = job_service or JobService(
            settings=self.settings, metadata_repo=self.metadata_repo
        )
        self.supervisor = SupervisorBridge(self.settings, self.metadata_repo)
        self.topic_module = TopicUnderstandingModule(self.settings)
        self.planner_module = VideoPlannerModule(self.settings)
        self.scene_generator = BlenderSceneGenerator(self.settings)
        self.storage_backend = build_storage_backend(self.settings)

    async def plan_only(self, plan_req: PlanRequest) -> PlanResponse:
        """Analyze topic and generate a validated educational storyboard without rendering."""
        req = GenerationRequest(**plan_req.model_dump(by_alias=True))
        valid_ctx, ctx_msg = self.supervisor.validate_curriculum_context(req)
        if not valid_ctx:
            raise ValidationError(ctx_msg)

        topic_info = await self.topic_module.analyze(req)
        if not topic_info.video_required:
            route = select_generation_route(topic_info, None, self.scene_generator)
            return PlanResponse(
                topic_understanding=topic_info,
                storyboard=None,
                routing_decision=route.to_dict(),
                message=topic_info.video_requirement_reason,
            )

        storyboard = await self.planner_module.create_storyboard(
            topic_info=topic_info,
            language=req.language,
            requested_duration=req.duration,
        )
        valid_sb, sb_errors = VideoPlannerModule.validate_storyboard(storyboard)
        if not valid_sb:
            raise ValidationError(
                "Generated storyboard failed educational validation.",
                details={"errors": sb_errors},
            )
        route = select_generation_route(topic_info, storyboard, self.scene_generator)
        return PlanResponse(
            topic_understanding=topic_info,
            storyboard=storyboard,
            routing_decision=route.to_dict(),
            message="Educational storyboard generated and validated.",
        )

    def start_generation(self, req: GenerationRequest) -> Dict[str, Any]:
        """Return cached video if available, otherwise start an asynchronous generation job."""
        valid_ctx, ctx_msg = self.supervisor.validate_curriculum_context(req)
        if not valid_ctx:
            raise ValidationError(ctx_msg)

        cached = self.supervisor.check_duplicate_cache(req)
        if cached:
            return {
                "success": True,
                "job_id": cached.get("job_id", "cached"),
                "status": "completed",
                "cached": True,
                "message": "Returning cached educational video.",
                "video": cached,
            }

        submission = self.job_service.submit_job(req)
        return {
            "success": True,
            "job_id": submission["job_id"],
            "status": submission["status"],
            "cached": False,
            "message": (
                "Duplicate in-flight job reused."
                if submission.get("deduplicated")
                else "Educational video generation started."
            ),
            "video": None,
        }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        job = self.job_service.get_status(job_id)
        if not job:
            raise AgentError(f"Job '{job_id}' not found.", code="JOB_NOT_FOUND", status_code=404)
        res = job.get("result") or {}
        return {
            "success": True,
            "job_id": job["job_id"],
            "status": job["status"],
            "progress_pct": job["progress_pct"],
            "current_stage": job["current_stage"],
            "message": job["message"],
            "video": res.get("video"),
            "topic_understanding": res.get("topic_understanding"),
            "storyboard": res.get("storyboard"),
            "missing_dependencies": res.get("missing_dependencies", []),
            "errors": res.get("errors", []),
            "logs": res.get("logs", []),
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at"),
        }

    def retry_job(self, job_id: str) -> Dict[str, Any]:
        job = self.job_service.get_status(job_id)
        if not job:
            raise AgentError(f"Job '{job_id}' not found.", code="JOB_NOT_FOUND", status_code=404)
        if job["status"] not in ("failed", "blocked"):
            raise ValidationError(
                f"Job '{job_id}' has status '{job['status']}' and is not eligible for retry."
            )
        req = GenerationRequest(**job["request"])
        req.force_regenerate = True
        submission = self.job_service.submit_job(req)
        return {
            "success": True,
            "job_id": submission["job_id"],
            "retried_from_job_id": job_id,
            "status": submission["status"],
            "message": f"Retry started from job '{job_id}'.",
        }

    def get_video(self, video_id: str) -> Dict[str, Any]:
        video = self.metadata_repo.get_video(video_id)
        if not video:
            raise AgentError(f"Video '{video_id}' not found.", code="VIDEO_NOT_FOUND", status_code=404)
        return video

    def list_videos(
        self,
        topic: Optional[str] = None,
        class_level: Optional[int] = None,
        subject: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        return self.metadata_repo.list_videos(
            topic=topic, class_level=class_level, subject=subject, limit=limit
        )

    async def delete_video(self, video_id: str) -> Dict[str, Any]:
        deleted = self.metadata_repo.delete_video(video_id)
        if not deleted:
            raise AgentError(f"Video '{video_id}' not found.", code="VIDEO_NOT_FOUND", status_code=404)
        for fname in ("video.mp4", "thumbnail.jpg", "subtitles.srt"):
            try:
                await self.storage_backend.delete_object(f"{video_id}/{fname}")
            except Exception:
                pass
        return {
            "success": True,
            "video_id": video_id,
            "message": "Video deleted according to retention policy.",
        }

