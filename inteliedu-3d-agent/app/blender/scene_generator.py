"""Blender scene script assembler, existing GLB asset catalog, and render dispatcher."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from app.api.schemas import SceneSpec
from app.blender.animation import BLENDER_ANIMATION_SNIPPET
from app.blender.camera import BLENDER_CAMERA_SNIPPET
from app.blender.materials import BLENDER_MATERIALS_SNIPPET
from app.blender.renderer import BLENDER_RENDERER_SNIPPET
from app.blender.templates.common import BLENDER_COMMON_SNIPPET
from app.blender.templates.educational_templates import build_template_body
from app.config import Settings, get_settings
from app.mcp.blender_client import BlenderExecutionResult, BlenderMCPClient


ASSET_CATALOG: Dict[str, Dict[str, str]] = {
    "human_heart": {
        "filename": "real_human_anatomy.glb",
        "description": "Existing Inteliedu anatomical human model with thoracic organs",
    },
    "human_anatomy": {
        "filename": "real_human_anatomy.glb",
        "description": "Existing Inteliedu anatomical human model",
    },
    "human_teacher": {
        "filename": "human_teacher.glb",
        "description": "Existing Inteliedu 3D human teacher model",
    },
    "human_head": {
        "filename": "human_head_scan.glb",
        "description": "Existing Inteliedu 3D cranial/head scan asset",
    },
}


class BlenderSceneGenerator:
    """Assembles parameterized bpy scripts and executes them via BlenderMCPClient."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        blender_client: Optional[BlenderMCPClient] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.blender_client = blender_client or BlenderMCPClient(settings=self.settings)

    def resolve_existing_asset(self, asset_filename: Optional[str]) -> Optional[Path]:
        if not asset_filename:
            return None
        candidate = self.settings.existing_models_dir / asset_filename
        if candidate.is_file():
            return candidate
        return None

    def generate_script(
        self,
        job_id: str,
        scene: SceneSpec,
        output_mp4_path: Path,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        asset_path: Optional[Path] = None,
        export_glb_path: Optional[Path] = None,
    ) -> Path:
        """Build a standalone, deterministic Blender Python script for a SceneSpec."""
        total_frames = max(int(scene.duration * fps), fps * 2)
        template_body = build_template_body(
            scene=scene,
            total_frames=total_frames,
            asset_path=str(asset_path) if asset_path else None,
        )

        out_mp4_str = str(output_mp4_path).replace("\\", "/")
        out_glb_str = str(export_glb_path).replace("\\", "/") if export_glb_path else None

        script_text = "\n".join(
            [
                '"""Auto-generated Inteliedu Blender 3D Educational Scene Script."""',
                BLENDER_COMMON_SNIPPET,
                BLENDER_MATERIALS_SNIPPET,
                BLENDER_CAMERA_SNIPPET,
                BLENDER_ANIMATION_SNIPPET,
                BLENDER_RENDERER_SNIPPET,
                template_body,
                "",
                'if __name__ == "__main__":',
                "    build_educational_scene()",
                f"    configure_and_render(",
                f"        output_mp4_path={out_mp4_str!r},",
                f"        width={int(width)},",
                f"        height={int(height)},",
                f"        fps={int(fps)},",
                f"        total_frames={int(total_frames)},",
                f"        samples={int(self.settings.blender_samples)},",
                f"        preferred_engine={self.settings.blender_render_engine!r},",
                f"        export_glb_path={out_glb_str!r},",
                "    )",
                "",
            ]
        )

        script_dir = self.settings.resolved_generated_dir / "scripts"
        script_dir.mkdir(parents=True, exist_ok=True)
        script_path = script_dir / f"{job_id}_scene_{scene.scene_id:02d}.py"
        script_path.write_text(script_text, encoding="utf-8")
        return script_path

    async def render_scene(
        self,
        job_id: str,
        scene: SceneSpec,
        asset_filename: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
    ) -> BlenderExecutionResult:
        """Generate the scene script and execute it through Blender MCP (or local Blender CLI)."""
        render_width = width or self.settings.video_default_width
        render_height = height or self.settings.video_default_height
        render_fps = fps or self.settings.video_default_fps

        output_dir = self.settings.resolved_generated_dir / "renders" / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_mp4 = output_dir / f"scene_{scene.scene_id:02d}.mp4"
        asset_path = self.resolve_existing_asset(asset_filename)

        script_path = self.generate_script(
            job_id=job_id,
            scene=scene,
            output_mp4_path=output_mp4,
            width=render_width,
            height=render_height,
            fps=render_fps,
            asset_path=asset_path,
        )

        return await self.blender_client.execute_scene_script(
            script_path=script_path,
            expected_output_path=output_mp4,
        )

