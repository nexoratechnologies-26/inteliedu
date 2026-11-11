"""Supervisor Agent interface, curriculum context validation, and duplicate cache checks."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.api.schemas import GenerationRequest
from app.config import Settings, get_settings
from app.storage.metadata import MetadataRepository, compute_request_hash


class SupervisorBridge:
    """Normalizes incoming Supervisor Agent payloads and enforces platform guardrails."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        metadata_repo: Optional[MetadataRepository] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_repo = metadata_repo or MetadataRepository(self.settings)

    def check_duplicate_cache(self, req: GenerationRequest) -> Optional[Dict[str, Any]]:
        if req.force_regenerate or not self.settings.enable_video_cache:
            return None
        req_hash = compute_request_hash(req)
        return self.metadata_repo.find_cached_video(req_hash)

    def validate_curriculum_context(self, req: GenerationRequest) -> Tuple[bool, str]:
        if req.duration > self.settings.max_video_duration_seconds:
            return (
                False,
                f"Requested duration ({req.duration}s) exceeds maximum limit ({self.settings.max_video_duration_seconds}s).",
            )
        if req.class_level < 1 or req.class_level > 12:
            return False, f"Invalid class level: {req.class_level} (must be 1..12)."
        if not req.topic.strip():
            return False, "Topic cannot be empty."
        return True, "Curriculum context validated."

