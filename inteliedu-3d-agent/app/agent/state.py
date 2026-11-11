"""Shared LangGraph workflow state schema for the 3D Generation Agent."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    job_id: str
    request: Dict[str, Any]
    status: str  # queued | processing | completed | skipped | blocked | failed
    progress_pct: int
    current_stage: str
    message: str

    # Module 1 & 2
    topic_understanding: Optional[Dict[str, Any]]
    curriculum_valid: bool
    video_required: bool
    storyboard: Optional[Dict[str, Any]]
    storyboard_valid: bool

    # Routing & MCP Discovery
    routing_decision: Optional[Dict[str, Any]]
    generation_engine: str
    discovered_mcp_tools: Dict[str, List[Dict[str, Any]]]

    # Generation Outputs
    generated_scripts: List[str]
    blender_clips: List[str]
    runway_clips: List[str]
    scene_clips: List[str]
    actual_engine_used: str

    # Post-Processing, Validation & Storage
    final_video_path: Optional[str]
    thumbnail_path: Optional[str]
    subtitle_path: Optional[str]
    validation_report: Optional[Dict[str, Any]]
    stored_video: Optional[Dict[str, Any]]

    # Resilience & Observability
    retry_count: int
    max_retries: int
    missing_dependencies: List[str]
    errors: List[str]
    logs: List[Dict[str, Any]]
    is_simulated: bool

