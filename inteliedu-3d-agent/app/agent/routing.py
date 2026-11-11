"""Intelligent Generation Routing following cost and accuracy priority rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from app.api.schemas import Storyboard, TopicUnderstanding
from app.blender.scene_generator import BlenderSceneGenerator


@dataclass
class RoutingDecision:
    primary_engine: str  # "existing_asset_blender" | "blender_template" | "blender_procedural" | "runway" | "hybrid" | "none"
    uses_blender: bool
    uses_runway: bool
    existing_asset_path: str | None
    priority_tier: int
    rationale: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "primary_engine": self.primary_engine,
            "uses_blender": self.uses_blender,
            "uses_runway": self.uses_runway,
            "existing_asset_path": self.existing_asset_path,
            "priority_tier": self.priority_tier,
            "rationale": self.rationale,
        }


def select_generation_route(
    topic_info: TopicUnderstanding,
    storyboard: Storyboard | None,
    scene_generator: BlenderSceneGenerator | None = None,
) -> RoutingDecision:
    """
    Priority order (Section 6):
    1. Existing approved 3D assets (GLB in frontend/public/assets/models/)
    2. Reusable Blender templates
    3. Procedural Blender generation
    4. External AI generation APIs (Runway) only when supplementary/environmental/cinematic
    """
    if not topic_info.video_required:
        return RoutingDecision(
            primary_engine="none",
            uses_blender=False,
            uses_runway=False,
            existing_asset_path=None,
            priority_tier=0,
            rationale="Topic does not require video generation.",
        )

    gen = scene_generator or BlenderSceneGenerator()
    asset_path = gen.resolve_existing_asset(topic_info.existing_asset_filename)

    scene_engines: List[str] = [s.render_engine for s in (storyboard.scenes if storyboard else [])]
    needs_runway = topic_info.requires_runway_clip or ("runway" in scene_engines)
    needs_blender = any(e in ("blender", "existing_asset_blender") for e in scene_engines) or (
        topic_info.recommended_engine != "runway"
    )

    if asset_path is not None and not needs_runway:
        return RoutingDecision(
            primary_engine="existing_asset_blender",
            uses_blender=True,
            uses_runway=False,
            existing_asset_path=str(asset_path),
            priority_tier=1,
            rationale=f"Tier 1: Reusing approved Inteliedu GLB asset '{asset_path.name}' with Blender camera animation.",
        )

    if needs_blender and needs_runway:
        return RoutingDecision(
            primary_engine="hybrid",
            uses_blender=True,
            uses_runway=True,
            existing_asset_path=str(asset_path) if asset_path else None,
            priority_tier=4,
            rationale="Hybrid routing: Blender for scientifically accurate 3D core + Runway for supplementary cinematic clips.",
        )

    if needs_runway and not needs_blender:
        return RoutingDecision(
            primary_engine="runway",
            uses_blender=False,
            uses_runway=True,
            existing_asset_path=None,
            priority_tier=4,
            rationale="Tier 4: Environmental/historical visual sequence routed to Runway AI.",
        )

    if topic_info.template_key != "generic_stem":
        return RoutingDecision(
            primary_engine="blender_template",
            uses_blender=True,
            uses_runway=False,
            existing_asset_path=None,
            priority_tier=2,
            rationale=f"Tier 2: Using reusable educational Blender template '{topic_info.template_key}'.",
        )

    return RoutingDecision(
        primary_engine="blender_procedural",
        uses_blender=True,
        uses_runway=False,
        existing_asset_path=None,
        priority_tier=3,
        rationale="Tier 3: Procedural Blender STEM scene generation.",
    )

