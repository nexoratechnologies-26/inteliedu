"""LangGraph 14-node workflow orchestrating topic understanding, MCP, rendering, validation, and storage."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.graph import END, START, StateGraph

from app.agent.routing import select_generation_route
from app.agent.scene_planner import ScenePlanner
from app.agent.state import AgentState
from app.agent.supervisor import SupervisorBridge
from app.agent.topic_understanding import TopicUnderstandingModule
from app.agent.video_planner import VideoPlannerModule
from app.api.schemas import GenerationRequest, SceneSpec, Storyboard, TopicUnderstanding, VideoMetadata
from app.blender.scene_generator import BlenderSceneGenerator
from app.config import Settings, get_settings
from app.mcp.blender_client import BlenderMCPClient
from app.mcp.runway_client import RunwayMCPClient
from app.runway.generator import RunwayGenerator
from app.storage.metadata import MetadataRepository, compute_request_hash
from app.storage.storage_service import build_storage_backend
from app.utils.error_handler import DependencyUnavailableError
from app.utils.logger import append_job_log, get_logger
from app.video.processor import VideoProcessor
from app.video.subtitles import generate_srt_for_storyboard
from app.video.thumbnail import generate_thumbnail
from app.video.validator import VideoValidator

logger = get_logger(__name__)


class ThreeDGenerationGraph:
    """Compiles and runs the 14-node LangGraph workflow for 3D educational video generation."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        metadata_repo: Optional[MetadataRepository] = None,
        blender_client: Optional[BlenderMCPClient] = None,
        runway_generator: Optional[RunwayGenerator] = None,
        video_processor: Optional[VideoProcessor] = None,
        video_validator: Optional[VideoValidator] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.metadata_repo = metadata_repo or MetadataRepository(self.settings)
        self.supervisor = SupervisorBridge(self.settings, self.metadata_repo)
        self.topic_module = TopicUnderstandingModule(self.settings)
        self.planner_module = VideoPlannerModule(self.settings)
        self.blender_client = blender_client or BlenderMCPClient(self.settings)
        self.scene_generator = BlenderSceneGenerator(self.settings, self.blender_client)
        self.scene_planner = ScenePlanner(self.scene_generator)
        self.runway_mcp_client = RunwayMCPClient(self.settings)
        self.runway_generator = runway_generator or RunwayGenerator(self.settings, self.runway_mcp_client)
        self.video_processor = video_processor or VideoProcessor(self.settings)
        self.video_validator = video_validator or VideoValidator(self.settings)
        self.storage_backend = build_storage_backend(self.settings)
        self.compiled = self._build_graph().compile()

    def _persist_progress(self, state: AgentState) -> None:
        job_id = state.get("job_id")
        if not job_id:
            return
        req_data = state.get("request") or {}
        req = GenerationRequest(**req_data)
        self.metadata_repo.upsert_job(
            job_id=job_id,
            status=state.get("status", "processing"),
            progress_pct=int(state.get("progress_pct", 0)),
            current_stage=state.get("current_stage", "processing"),
            message=state.get("message", ""),
            request_data=req_data,
            result_data={
                "topic_understanding": state.get("topic_understanding"),
                "storyboard": state.get("storyboard"),
                "routing_decision": state.get("routing_decision"),
                "discovered_mcp_tools": state.get("discovered_mcp_tools"),
                "generated_scripts": state.get("generated_scripts"),
                "video": state.get("stored_video"),
                "validation_report": state.get("validation_report"),
                "missing_dependencies": state.get("missing_dependencies", []),
                "errors": state.get("errors", []),
                "logs": state.get("logs", []),
                "is_simulated": state.get("is_simulated", False),
            },
            content_hash=compute_request_hash(req),
        )

    # --- 14 Logical LangGraph Nodes ---

    async def receive_request(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        logs = append_job_log(
            state.get("logs"),
            "receive_request",
            f"Received request for topic='{req.topic}', class={req.class_level}, board='{req.board}'.",
        )
        next_state: AgentState = {
            **state,
            "status": "processing",
            "progress_pct": 5,
            "current_stage": "receive_request",
            "message": "Request received from Supervisor Agent.",
            "generated_scripts": state.get("generated_scripts", []),
            "blender_clips": state.get("blender_clips", []),
            "runway_clips": state.get("runway_clips", []),
            "scene_clips": state.get("scene_clips", []),
            "discovered_mcp_tools": state.get("discovered_mcp_tools", {}),
            "missing_dependencies": state.get("missing_dependencies", []),
            "errors": state.get("errors", []),
            "retry_count": state.get("retry_count", 0),
            "max_retries": state.get("max_retries", self.settings.max_retries),
            "is_simulated": False,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def understand_topic(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        understanding = await self.topic_module.analyze(req)
        logs = append_job_log(
            state.get("logs"),
            "understand_topic",
            f"Classified topic='{understanding.normalized_topic}', viz='{understanding.visualization_type}', video_required={understanding.video_required}.",
        )
        next_state: AgentState = {
            **state,
            "progress_pct": 15,
            "current_stage": "understand_topic",
            "topic_understanding": understanding.model_dump(by_alias=True),
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def validate_curriculum_context(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        valid, msg = self.supervisor.validate_curriculum_context(req)
        logs = append_job_log(state.get("logs"), "validate_curriculum_context", msg)
        errors = list(state.get("errors", []))
        if not valid:
            errors.append(msg)
        next_state: AgentState = {
            **state,
            "curriculum_valid": valid,
            "progress_pct": 22,
            "current_stage": "validate_curriculum_context",
            "message": msg,
            "errors": errors,
            "logs": logs,
        }
        if not valid:
            next_state["status"] = "failed"
        self._persist_progress(next_state)
        return next_state

    async def determine_video_requirement(self, state: AgentState) -> AgentState:
        info = TopicUnderstanding(**state["topic_understanding"])
        required = bool(state.get("curriculum_valid", True) and info.video_required)
        msg = (
            "Video generation required."
            if required
            else info.video_requirement_reason or "Video generation not required for this query."
        )
        logs = append_job_log(state.get("logs"), "determine_video_requirement", msg)
        next_state: AgentState = {
            **state,
            "video_required": required,
            "progress_pct": 28,
            "current_stage": "determine_video_requirement",
            "message": msg,
            "status": state["status"] if required else ("skipped" if state.get("curriculum_valid", True) else "failed"),
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def create_video_plan(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        info = TopicUnderstanding(**state["topic_understanding"])
        storyboard = await self.planner_module.create_storyboard(
            topic_info=info,
            language=req.language,
            requested_duration=req.duration,
        )
        self.scene_planner.build_scene_manifests(storyboard, info)
        logs = append_job_log(
            state.get("logs"),
            "create_video_plan",
            f"Generated storyboard '{storyboard.video_title}' with {len(storyboard.scenes)} scenes ({storyboard.total_duration}s).",
        )
        next_state: AgentState = {
            **state,
            "progress_pct": 38,
            "current_stage": "create_video_plan",
            "storyboard": storyboard.model_dump(by_alias=True),
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def validate_storyboard(self, state: AgentState) -> AgentState:
        storyboard = Storyboard(**state["storyboard"])
        valid, sb_errors = VideoPlannerModule.validate_storyboard(storyboard)
        errors = list(state.get("errors", []))
        errors.extend(sb_errors)
        msg = "Storyboard validated." if valid else f"Storyboard validation failed: {'; '.join(sb_errors)}"
        logs = append_job_log(
            state.get("logs"),
            "validate_storyboard",
            msg,
            level="INFO" if valid else "ERROR",
        )
        next_state: AgentState = {
            **state,
            "storyboard_valid": valid,
            "progress_pct": 45,
            "current_stage": "validate_storyboard",
            "message": msg,
            "errors": errors,
            "status": state["status"] if valid else "failed",
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def select_generation_engine(self, state: AgentState) -> AgentState:
        info = TopicUnderstanding(**state["topic_understanding"])
        storyboard = Storyboard(**state["storyboard"])
        decision = select_generation_route(info, storyboard, self.scene_generator)
        logs = append_job_log(
            state.get("logs"),
            "select_generation_engine",
            f"Routing selected: {decision.primary_engine} ({decision.rationale})",
        )
        next_state: AgentState = {
            **state,
            "progress_pct": 52,
            "current_stage": "select_generation_engine",
            "routing_decision": decision.to_dict(),
            "generation_engine": decision.primary_engine,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def discover_mcp_tools(self, state: AgentState) -> AgentState:
        decision = state.get("routing_decision") or {}
        discovered: Dict[str, List[Dict[str, Any]]] = {}
        logs = list(state.get("logs", []))

        if decision.get("uses_blender"):
            try:
                tools = await self.blender_client.discover_tools()
                discovered["blender_mcp"] = [t.to_dict() for t in tools]
                logs = append_job_log(
                    logs,
                    "discover_mcp_tools",
                    f"Discovered {len(tools)} Blender MCP tools: {[t.name for t in tools]}",
                )
            except Exception as exc:
                discovered["blender_mcp"] = []
                logs = append_job_log(
                    logs,
                    "discover_mcp_tools",
                    f"Blender MCP unavailable during discovery ({exc}); will evaluate Blender CLI fallback.",
                    level="WARNING",
                )

        if decision.get("uses_runway"):
            try:
                tools = await self.runway_mcp_client.discover_tools()
                discovered["runway_mcp"] = [t.to_dict() for t in tools]
                logs = append_job_log(
                    logs,
                    "discover_mcp_tools",
                    f"Discovered {len(tools)} Runway MCP tools: {[t.name for t in tools]}",
                )
            except Exception as exc:
                discovered["runway_mcp"] = []
                logs = append_job_log(
                    logs,
                    "discover_mcp_tools",
                    f"Runway MCP unavailable during discovery ({exc}); will evaluate Runway REST API adapter.",
                    level="WARNING",
                )

        next_state: AgentState = {
            **state,
            "progress_pct": 58,
            "current_stage": "discover_mcp_tools",
            "discovered_mcp_tools": discovered,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def generate_blender_scenes(self, state: AgentState) -> AgentState:
        storyboard = Storyboard(**state["storyboard"])
        info = TopicUnderstanding(**state["topic_understanding"])
        job_id = state["job_id"]
        blender_clips: List[str] = []
        generated_scripts: List[str] = list(state.get("generated_scripts", []))
        logs = list(state.get("logs", []))
        errors = list(state.get("errors", []))
        missing = list(state.get("missing_dependencies", []))
        actual_engine = state.get("actual_engine_used", "blender")

        blender_scenes = [s for s in storyboard.scenes if s.render_engine in ("blender", "existing_asset_blender")]
        for scene in blender_scenes:
            # Always write reproducible bpy script artifact before execution attempt
            asset_path = self.scene_generator.resolve_existing_asset(info.existing_asset_filename)
            out_mp4 = self.settings.resolved_generated_dir / "renders" / job_id / f"scene_{scene.scene_id:02d}.mp4"
            script_path = self.scene_generator.generate_script(
                job_id=job_id,
                scene=scene,
                output_mp4_path=out_mp4,
                width=self.settings.video_default_width,
                height=self.settings.video_default_height,
                fps=self.settings.video_default_fps,
                asset_path=asset_path,
            )
            if str(script_path) not in generated_scripts:
                generated_scripts.append(str(script_path))

            try:
                res = await self.blender_client.execute_scene_script(
                    script_path=script_path,
                    expected_output_path=out_mp4,
                )
                if res.output_path:
                    blender_clips.append(res.output_path)
                    actual_engine = res.engine_used
                    logs = append_job_log(
                        logs,
                        "generate_blender_scenes",
                        f"Scene {scene.scene_id} rendered via {res.engine_used}: {res.output_path}",
                    )
            except DependencyUnavailableError as exc:
                for dep in exc.missing_dependencies:
                    if dep not in missing:
                        missing.append(dep)
                errors.append(exc.message)
                logs = append_job_log(
                    logs,
                    "generate_blender_scenes",
                    f"Blender rendering unavailable for Scene {scene.scene_id}: {exc.message}",
                    level="ERROR",
                    details={"script_path": str(script_path), "missing": exc.missing_dependencies},
                )
                next_state: AgentState = {
                    **state,
                    "status": "blocked",
                    "progress_pct": 65,
                    "current_stage": "generate_blender_scenes",
                    "message": exc.message,
                    "generated_scripts": generated_scripts,
                    "blender_clips": blender_clips,
                    "missing_dependencies": missing,
                    "errors": errors,
                    "logs": logs,
                }
                self._persist_progress(next_state)
                return next_state
            except Exception as exc:
                errors.append(f"Scene {scene.scene_id} Blender error: {exc}")
                logs = append_job_log(
                    logs,
                    "generate_blender_scenes",
                    f"Scene {scene.scene_id} failed: {exc}",
                    level="ERROR",
                )
                next_state = {
                    **state,
                    "status": "failed",
                    "progress_pct": 65,
                    "current_stage": "generate_blender_scenes",
                    "message": str(exc),
                    "generated_scripts": generated_scripts,
                    "blender_clips": blender_clips,
                    "retry_count": state.get("retry_count", 0) + 1,
                    "errors": errors,
                    "logs": logs,
                }
                self._persist_progress(next_state)
                return next_state

        next_state = {
            **state,
            "status": "processing",
            "progress_pct": 74,
            "current_stage": "generate_blender_scenes",
            "generated_scripts": generated_scripts,
            "blender_clips": blender_clips,
            "scene_clips": list(blender_clips),
            "actual_engine_used": actual_engine,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def generate_runway_clips(self, state: AgentState) -> AgentState:
        storyboard = Storyboard(**state["storyboard"])
        job_id = state["job_id"]
        runway_scenes = [s for s in storyboard.scenes if s.render_engine == "runway"]
        runway_clips: List[str] = list(state.get("runway_clips", []))
        scene_clips: List[str] = list(state.get("scene_clips", []))
        logs = list(state.get("logs", []))
        errors = list(state.get("errors", []))
        missing = list(state.get("missing_dependencies", []))

        for scene in runway_scenes:
            try:
                res = await self.runway_generator.generate_scene_clip(job_id=job_id, scene=scene)
                if res.local_path:
                    runway_clips.append(res.local_path)
                    scene_clips.append(res.local_path)
                    logs = append_job_log(
                        logs,
                        "generate_runway_clips",
                        f"Scene {scene.scene_id} generated via Runway ({res.task_id}): {res.local_path}",
                    )
            except DependencyUnavailableError as exc:
                for dep in exc.missing_dependencies:
                    if dep not in missing:
                        missing.append(dep)
                errors.append(exc.message)
                logs = append_job_log(
                    logs,
                    "generate_runway_clips",
                    f"Runway unavailable for Scene {scene.scene_id}: {exc.message}",
                    level="ERROR",
                )
                next_state: AgentState = {
                    **state,
                    "status": "blocked",
                    "progress_pct": 78,
                    "current_stage": "generate_runway_clips",
                    "message": exc.message,
                    "runway_clips": runway_clips,
                    "scene_clips": scene_clips,
                    "missing_dependencies": missing,
                    "errors": errors,
                    "logs": logs,
                }
                self._persist_progress(next_state)
                return next_state
            except Exception as exc:
                errors.append(f"Runway Scene {scene.scene_id} failed: {exc}")
                logs = append_job_log(
                    logs,
                    "generate_runway_clips",
                    f"Runway failed on Scene {scene.scene_id}: {exc}",
                    level="ERROR",
                )
                next_state = {
                    **state,
                    "status": "failed",
                    "progress_pct": 78,
                    "current_stage": "generate_runway_clips",
                    "message": str(exc),
                    "errors": errors,
                    "logs": logs,
                }
                self._persist_progress(next_state)
                return next_state

        engine_used = state.get("actual_engine_used") or "runway"
        if state.get("blender_clips") and runway_clips:
            engine_used = f"{engine_used}+runway"
        elif runway_clips and not state.get("blender_clips"):
            engine_used = "runway"

        next_state = {
            **state,
            "progress_pct": 80,
            "current_stage": "generate_runway_clips",
            "runway_clips": runway_clips,
            "scene_clips": scene_clips,
            "actual_engine_used": engine_used,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def process_video(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        storyboard = Storyboard(**state["storyboard"])
        job_id = state["job_id"]
        clips = [Path(p) for p in state.get("scene_clips", [])]

        subtitle_path: Optional[Path] = None
        if req.include_subtitles:
            sub_target = self.settings.resolved_generated_dir / "subtitles" / f"{job_id}.srt"
            subtitle_path = generate_srt_for_storyboard(storyboard, sub_target)

        narration_path = Path(req.narration_audio_path) if req.narration_audio_path else None
        final_video = self.settings.resolved_generated_dir / "renders" / f"{job_id}_final.mp4"
        thumb_path = self.settings.resolved_generated_dir / "thumbnails" / f"{job_id}.jpg"

        processed_video = await self.video_processor.process_video(
            job_id=job_id,
            clip_paths=clips,
            output_path=final_video,
            narration_audio_path=narration_path,
            subtitle_path=subtitle_path,
        )
        generated_thumb = await generate_thumbnail(processed_video, thumb_path, settings=self.settings)

        logs = append_job_log(
            state.get("logs"),
            "process_video",
            f"FFmpeg combined {len(clips)} clip(s) into {processed_video.name} + thumbnail {generated_thumb.name}.",
        )
        next_state: AgentState = {
            **state,
            "progress_pct": 88,
            "current_stage": "process_video",
            "final_video_path": str(processed_video),
            "thumbnail_path": str(generated_thumb),
            "subtitle_path": str(subtitle_path) if subtitle_path else None,
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def validate_video(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        storyboard = Storyboard(**state["storyboard"])
        video_path = Path(state["final_video_path"])
        require_audio = bool(req.narration_audio_path and Path(req.narration_audio_path).is_file())

        report = await self.video_validator.validate(
            video_path=video_path,
            storyboard=storyboard,
            rendered_scene_count=len(state.get("scene_clips", [])),
            require_audio=require_audio,
            is_simulated=bool(state.get("is_simulated", False)),
        )
        errors = list(state.get("errors", []))
        if not report.passed:
            errors.extend(report.technical.decode_errors)
            errors.extend(report.educational.errors)

        logs = append_job_log(
            state.get("logs"),
            "validate_video",
            f"Video validation passed={report.passed} (duration={report.technical.duration_seconds}s, {report.technical.width}x{report.technical.height}).",
            level="INFO" if report.passed else "ERROR",
        )
        next_state: AgentState = {
            **state,
            "progress_pct": 94,
            "current_stage": "validate_video",
            "validation_report": report.model_dump(),
            "errors": errors,
            "status": state["status"] if report.passed else "failed",
            "message": "Video validation passed." if report.passed else "Video validation failed.",
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def store_video(self, state: AgentState) -> AgentState:
        req = GenerationRequest(**state["request"])
        storyboard = Storyboard(**state["storyboard"])
        report = state.get("validation_report") or {}
        tech = report.get("technical", {})

        video_id = f"video-{uuid.uuid4().hex[:12]}"
        final_video_path = Path(state["final_video_path"])
        thumb_path = Path(state["thumbnail_path"]) if state.get("thumbnail_path") else None
        sub_path = Path(state["subtitle_path"]) if state.get("subtitle_path") else None

        stored_video = await self.storage_backend.upload_file(
            final_video_path, f"{video_id}/video.mp4", "video/mp4"
        )
        stored_thumb = (
            await self.storage_backend.upload_file(thumb_path, f"{video_id}/thumbnail.jpg", "image/jpeg")
            if thumb_path and thumb_path.is_file()
            else None
        )
        stored_sub = (
            await self.storage_backend.upload_file(sub_path, f"{video_id}/subtitles.srt", "text/plain")
            if sub_path and sub_path.is_file()
            else None
        )

        metadata = VideoMetadata(
            video_id=video_id,
            job_id=state["job_id"],
            topic=storyboard.topic,
            title=storyboard.video_title,
            **{"class": storyboard.class_level},
            subject=storyboard.subject,
            board=storyboard.board,
            chapter=storyboard.chapter,
            language=storyboard.language,
            status="completed",
            video_url=stored_video.url,
            thumbnail_url=stored_thumb.url if stored_thumb else None,
            subtitle_url=stored_sub.url if stored_sub else None,
            duration=float(tech.get("duration_seconds") or storyboard.total_duration),
            format="mp4",
            resolution=f"{tech.get('width', 1280)}x{tech.get('height', 720)}",
            fps=float(tech.get("fps") or self.settings.video_default_fps),
            size_bytes=int(tech.get("file_size_bytes") or final_video_path.stat().st_size),
            generation_engine=state.get("actual_engine_used") or state.get("generation_engine", "blender"),
            is_simulated=bool(state.get("is_simulated", False)),
            content_hash=compute_request_hash(req),
            storage_provider=stored_video.provider,
            local_video_path=stored_video.local_path,
            local_thumbnail_path=stored_thumb.local_path if stored_thumb else None,
            local_subtitle_path=stored_sub.local_path if stored_sub else None,
            storyboard=state.get("storyboard"),
            validation=report,
        )
        self.metadata_repo.save_video(metadata)
        logs = append_job_log(
            state.get("logs"),
            "store_video",
            f"Stored video '{video_id}' via provider='{stored_video.provider}' at '{stored_video.url}'.",
        )
        next_state: AgentState = {
            **state,
            "status": "completed",
            "progress_pct": 100,
            "current_stage": "store_video",
            "message": "Educational video generated, validated, and stored successfully.",
            "stored_video": metadata.model_dump(by_alias=True),
            "logs": logs,
        }
        self._persist_progress(next_state)
        return next_state

    async def return_result(self, state: AgentState) -> AgentState:
        logs = append_job_log(
            state.get("logs"),
            "return_result",
            f"Workflow finalized with status='{state.get('status')}', stage='{state.get('current_stage')}'.",
        )
        final_state: AgentState = {**state, "logs": logs}
        self._persist_progress(final_state)
        return final_state

    # --- Conditional Routers ---

    @staticmethod
    def _route_after_requirement(state: AgentState) -> str:
        return "create_video_plan" if state.get("video_required") else "return_result"

    @staticmethod
    def _route_after_storyboard_validation(state: AgentState) -> str:
        return "select_generation_engine" if state.get("storyboard_valid") else "return_result"

    @staticmethod
    def _route_after_discovery(state: AgentState) -> str:
        decision = state.get("routing_decision") or {}
        if decision.get("uses_blender"):
            return "generate_blender_scenes"
        if decision.get("uses_runway"):
            return "generate_runway_clips"
        return "return_result"

    @staticmethod
    def _route_after_blender(state: AgentState) -> str:
        if state.get("status") == "blocked":
            return "return_result"
        if state.get("status") == "failed":
            if state.get("retry_count", 0) <= state.get("max_retries", 0):
                return "generate_blender_scenes"
            return "return_result"
        decision = state.get("routing_decision") or {}
        if decision.get("uses_runway"):
            return "generate_runway_clips"
        return "process_video" if state.get("scene_clips") else "return_result"

    @staticmethod
    def _route_after_runway(state: AgentState) -> str:
        if state.get("status") in ("blocked", "failed"):
            return "return_result"
        return "process_video" if state.get("scene_clips") else "return_result"

    @staticmethod
    def _route_after_validation(state: AgentState) -> str:
        report = state.get("validation_report") or {}
        return "store_video" if report.get("passed") else "return_result"

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        nodes = [
            ("receive_request", self.receive_request),
            ("understand_topic", self.understand_topic),
            ("validate_curriculum_context", self.validate_curriculum_context),
            ("determine_video_requirement", self.determine_video_requirement),
            ("create_video_plan", self.create_video_plan),
            ("validate_storyboard", self.validate_storyboard),
            ("select_generation_engine", self.select_generation_engine),
            ("discover_mcp_tools", self.discover_mcp_tools),
            ("generate_blender_scenes", self.generate_blender_scenes),
            ("generate_runway_clips", self.generate_runway_clips),
            ("process_video", self.process_video),
            ("validate_video", self.validate_video),
            ("store_video", self.store_video),
            ("return_result", self.return_result),
        ]
        for name, fn in nodes:
            graph.add_node(name, fn)

        graph.add_edge(START, "receive_request")
        graph.add_edge("receive_request", "understand_topic")
        graph.add_edge("understand_topic", "validate_curriculum_context")
        graph.add_edge("validate_curriculum_context", "determine_video_requirement")

        graph.add_conditional_edges(
            "determine_video_requirement",
            self._route_after_requirement,
            {"create_video_plan": "create_video_plan", "return_result": "return_result"},
        )
        graph.add_edge("create_video_plan", "validate_storyboard")
        graph.add_conditional_edges(
            "validate_storyboard",
            self._route_after_storyboard_validation,
            {"select_generation_engine": "select_generation_engine", "return_result": "return_result"},
        )
        graph.add_edge("select_generation_engine", "discover_mcp_tools")
        graph.add_conditional_edges(
            "discover_mcp_tools",
            self._route_after_discovery,
            {
                "generate_blender_scenes": "generate_blender_scenes",
                "generate_runway_clips": "generate_runway_clips",
                "return_result": "return_result",
            },
        )
        graph.add_conditional_edges(
            "generate_blender_scenes",
            self._route_after_blender,
            {
                "generate_blender_scenes": "generate_blender_scenes",
                "generate_runway_clips": "generate_runway_clips",
                "process_video": "process_video",
                "return_result": "return_result",
            },
        )
        graph.add_conditional_edges(
            "generate_runway_clips",
            self._route_after_runway,
            {"process_video": "process_video", "return_result": "return_result"},
        )
        graph.add_edge("process_video", "validate_video")
        graph.add_conditional_edges(
            "validate_video",
            self._route_after_validation,
            {"store_video": "store_video", "return_result": "return_result"},
        )
        graph.add_edge("store_video", "return_result")
        graph.add_edge("return_result", END)
        return graph

    async def run(self, job_id: str, request: GenerationRequest) -> AgentState:
        initial_state: AgentState = {
            "job_id": job_id,
            "request": request.model_dump(by_alias=True),
        }
        return await self.compiled.ainvoke(initial_state)
