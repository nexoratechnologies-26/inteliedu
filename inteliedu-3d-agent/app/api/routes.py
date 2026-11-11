"""FastAPI routes for the Inteliedu 3D Generation Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import FileResponse

from app.api.schemas import (
    GenerationRequest,
    GenerationStartResponse,
    JobStatusResponse,
    PlanRequest,
    PlanResponse,
    VideoListResponse,
)
from app.config import Settings, get_settings
from app.services.generation_service import GenerationService
from app.utils.error_handler import AgentError

router = APIRouter(tags=["3D Generation Agent"])

_service_singleton: Optional[GenerationService] = None


def get_generation_service() -> GenerationService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = GenerationService()
    return _service_singleton


def verify_service_auth(
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Enforce optional internal service token when AGENT_API_KEY is configured."""
    expected = settings.agent_api_key
    if not expected:
        return
    bearer = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()
    if x_api_key == expected or bearer == expected:
        return
    raise AgentError(
        "Unauthorized: invalid or missing service credentials.",
        code="UNAUTHORIZED",
        status_code=401,
    )


@router.get("/capabilities")
async def get_capabilities(
    _: None = Depends(verify_service_auth),
    settings: Settings = Depends(get_settings),
):
    """Report live integration availability (Blender MCP, Blender CLI, Runway, FFmpeg, Storage)."""
    return {"success": True, "capabilities": settings.capabilities_report()}


@router.post("/generate", response_model=GenerationStartResponse)
async def generate_video(
    request: GenerationRequest,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Start an asynchronous educational video generation job (or return cached hit)."""
    return service.start_generation(request)


@router.post("/plan", response_model=PlanResponse)
async def create_plan(
    request: PlanRequest,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Analyze topic and generate a validated educational storyboard without rendering."""
    return await service.plan_only(request)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Check progress, storyboard, validation results, and logs for a generation job."""
    return service.get_job_status(job_id)


@router.get("/video/{video_id}")
async def get_video(
    video_id: str,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Retrieve generated video metadata and playback URL."""
    video = service.get_video(video_id)
    return {"success": True, "video": video}


@router.get("/videos", response_model=VideoListResponse)
async def list_videos(
    topic: Optional[str] = Query(default=None),
    class_level: Optional[int] = Query(default=None, alias="class"),
    subject: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Retrieve previously generated educational videos."""
    videos = service.list_videos(topic=topic, class_level=class_level, subject=subject, limit=limit)
    return {"success": True, "count": len(videos), "videos": videos}


@router.post("/retry/{job_id}")
async def retry_job(
    job_id: str,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Retry an eligible failed or dependency-blocked generation job."""
    return service.retry_job(job_id)


@router.delete("/video/{video_id}")
async def delete_video(
    video_id: str,
    _: None = Depends(verify_service_auth),
    service: GenerationService = Depends(get_generation_service),
):
    """Delete a stored video and its metadata."""
    return await service.delete_video(video_id)


@router.get("/assets/{object_key:path}")
async def serve_local_asset(
    object_key: str,
    settings: Settings = Depends(get_settings),
):
    """Serve locally stored MP4, thumbnail, and SRT subtitle files safely."""
    storage_root = (settings.resolved_generated_dir / "storage").resolve()
    target = (storage_root / object_key).resolve()
    if not str(target).startswith(str(storage_root)) or not target.is_file():
        raise AgentError("Asset not found.", code="ASSET_NOT_FOUND", status_code=404)
    media_type = "application/octet-stream"
    if target.suffix == ".mp4":
        media_type = "video/mp4"
    elif target.suffix in (".jpg", ".jpeg"):
        media_type = "image/jpeg"
    elif target.suffix == ".srt":
        media_type = "text/plain; charset=utf-8"
    return FileResponse(path=Path(target), media_type=media_type)

