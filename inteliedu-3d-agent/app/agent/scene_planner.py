"""Scene Planning helper preparing concrete templates, assets, and prompts."""

from __future__ import annotations

from typing import Any, Dict, List

from app.api.schemas import Storyboard, TopicUnderstanding
from app.blender.scene_generator import BlenderSceneGenerator


class ScenePlanner:
    """Translates storyboard scenes into concrete asset bindings and execution manifests."""

    def __init__(self, scene_generator: BlenderSceneGenerator | None = None) -> None:
        self.scene_generator = scene_generator or BlenderSceneGenerator()

    def build_scene_manifests(
        self, storyboard: Storyboard, topic_info: TopicUnderstanding
    ) -> List[Dict[str, Any]]:
        asset_path = self.scene_generator.resolve_existing_asset(topic_info.existing_asset_filename)
        manifests: List[Dict[str, Any]] = []
        for scene in storyboard.scenes:
            manifests.append(
                {
                    "scene_id": scene.scene_id,
                    "title": scene.title,
                    "render_engine": scene.render_engine,
                    "template_name": scene.template_name,
                    "existing_asset_path": str(asset_path) if asset_path else None,
                    "duration": scene.duration,
                    "camera_position": scene.camera_position,
                    "camera_movement": scene.camera_movement,
                    "objects": scene.objects,
                }
            )
        return manifests

