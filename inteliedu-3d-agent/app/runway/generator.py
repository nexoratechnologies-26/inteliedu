"""Runway supplementary clip orchestrator preferring Runway MCP, then official REST API."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from app.api.schemas import SceneSpec
from app.config import Settings, get_settings
from app.mcp.runway_client import RunwayMCPClient
from app.runway.client import RunwayAPIClient, RunwayTaskResult
from app.utils.error_handler import DependencyUnavailableError, MCPConnectionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _clamp_runway_duration(seconds: int) -> int:
    """Map arbitrary scene durations to supported Runway clip durations (5 or 10)."""
    return 10 if seconds >= 8 else 5


class RunwayGenerator:
    """Generates supplementary AI educational video clips via Runway MCP or official API."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        mcp_client: Optional[RunwayMCPClient] = None,
        api_client: Optional[RunwayAPIClient] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.mcp_client = mcp_client or RunwayMCPClient(settings=self.settings)
        self.api_client = api_client or RunwayAPIClient(settings=self.settings)

    async def generate_scene_clip(
        self,
        job_id: str,
        scene: SceneSpec,
        prompt_image: Optional[str] = None,
    ) -> RunwayTaskResult:
        """Generate a supplementary Runway clip and save it under `generated/clips/<job_id>/`."""
        prompt_text = scene.runway_prompt or (
            f"Educational visual scene: {scene.title}. {scene.description}. "
            f"Clear classroom-friendly lighting, smooth camera: {scene.camera_movement}."
        )
        duration = _clamp_runway_duration(scene.duration)
        dest_path = (
            self.settings.resolved_generated_dir
            / "clips"
            / job_id
            / f"runway_scene_{scene.scene_id:02d}.mp4"
        )

        mcp_error: Optional[str] = None
        if self.mcp_client.build_server_config() is not None:
            try:
                mcp_res = await self.mcp_client.generate_video(
                    prompt_text=prompt_text,
                    duration=duration,
                    prompt_image=prompt_image,
                )
                if not mcp_res.is_error:
                    output_url = self._extract_url(mcp_res.structured_content, mcp_res.text_content)
                    if output_url:
                        await self.api_client.download_output(output_url, dest_path)
                        return RunwayTaskResult(
                            task_id=f"mcp-{job_id}-{scene.scene_id}",
                            status="SUCCEEDED",
                            outputs=[output_url],
                            local_path=str(dest_path),
                        )
            except MCPConnectionError as exc:
                mcp_error = str(exc)
                logger.warning("Runway MCP unavailable (%s); falling back to Runway REST API.", exc)

        if not self.api_client.is_configured:
            missing = ["RUNWAY_API_KEY (not configured)"]
            if mcp_error:
                missing.append(f"Runway MCP ({mcp_error})")
            else:
                missing.append("RUNWAY_MCP_URL / RUNWAY_MCP_COMMAND (not configured)")
            raise DependencyUnavailableError(
                "Runway supplementary video generation cannot run without RUNWAY_API_KEY or a connected Runway MCP server.",
                missing_dependencies=missing,
            )

        if prompt_image:
            task_id = await self.api_client.create_image_to_video(
                prompt_image=prompt_image,
                prompt_text=prompt_text,
                duration=duration,
            )
        else:
            task_id = await self.api_client.create_text_to_video(
                prompt_text=prompt_text,
                duration=duration,
            )

        result = await self.api_client.wait_for_task(task_id)
        if not result.outputs:
            raise RuntimeError(f"Runway task {task_id} succeeded without output URLs.")

        await self.api_client.download_output(result.outputs[0], dest_path)
        result.local_path = str(dest_path)
        return result

    @staticmethod
    def _extract_url(structured: object, text: str) -> Optional[str]:
        if isinstance(structured, dict):
            for key in ("url", "video_url", "output_url"):
                val = structured.get(key)
                if isinstance(val, str) and val.startswith("http"):
                    return val
            outputs = structured.get("output") or structured.get("outputs")
            if isinstance(outputs, list) and outputs and isinstance(outputs[0], str):
                return outputs[0]
        match = re.search(r"https?://[^\s\"']+\.mp4[^\s\"']*", text or "")
        return match.group(0) if match else None

