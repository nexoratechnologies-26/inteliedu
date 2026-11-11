"""Module 1: Topic Understanding for State Board Classes 6-12 educational requests."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.api.schemas import GenerationRequest, TopicUnderstanding
from app.blender.scene_generator import ASSET_CATALOG
from app.config import Settings, get_settings
from app.services.llm_client import LLMClient


_NON_VISUAL_PATTERNS = [
    r"\bwho (wrote|invented|discovered|was|were)\b",
    r"\bwhat year\b",
    r"\bwhen (did|was)\b",
    r"\bcapital of\b",
    r"\bspell(ing)?\b",
    r"\bsynonym\b",
    r"\bantonym\b",
    r"\btranslate\b",
    r"^\s*define\b",
    r"^\s*solve\s+[\d\sx+\-*/=()]+\s*$",
]

_TOPIC_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "keywords": ("solar system", "planet", "sun and planets", "planetary revolution", "orbit"),
        "normalized": "Solar System",
        "chapter": "Universe & Space Science",
        "objective": "Understand the Sun, the eight planets in order, planetary rotation, and orbital revolution.",
        "concepts": [
            "Sun at the center",
            "Eight planets in order (Mercury to Neptune)",
            "Axial rotation vs orbital revolution",
            "Non-scale educational visualization disclosure",
        ],
        "viz": "3D planetary orbital animation",
        "template": "solar_system",
        "engine": "blender",
        "complexity": "high",
        "notes": [
            "Maintain exact heliocentric order: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune.",
            "Explicitly disclose that orbital distances and planetary radii are adjusted for visual clarity.",
        ],
    },
    {
        "keywords": ("heart", "cardiac", "blood circulation", "cardiovascular", "aorta"),
        "normalized": "Human Heart",
        "chapter": "Life Processes & Circulation",
        "objective": "Understand the four chambers of the human heart, blood flow, and cardiac pumping.",
        "concepts": ["Right & left atria", "Right & left ventricles", "Aorta & pulmonary circulation", "Cardiac cycle"],
        "viz": "3D anatomical asset animation",
        "template": "anatomy_asset",
        "engine": "existing_asset_blender",
        "asset": ASSET_CATALOG["human_heart"]["filename"],
        "complexity": "medium",
        "notes": ["Reuse approved anatomical GLB asset before procedural generation."],
    },
    {
        "keywords": ("water cycle", "evaporation", "condensation", "precipitation", "hydrologic"),
        "normalized": "Water Cycle",
        "chapter": "Natural Resources & Weather",
        "objective": "Visualize continuous circulation of water via evaporation, condensation, precipitation, and collection.",
        "concepts": ["Solar heating", "Evaporation", "Condensation into clouds", "Precipitation & runoff"],
        "viz": "3D environmental process simulation",
        "template": "water_cycle",
        "engine": "blender",
        "complexity": "medium",
        "notes": ["Highlight energy input from Sun driving state transitions."],
    },
    {
        "keywords": ("photosynthesis", "chloroplast", "chlorophyll"),
        "normalized": "Photosynthesis",
        "chapter": "Nutrition in Plants",
        "objective": "Demonstrate how plants use sunlight, carbon dioxide, and water to produce glucose and oxygen.",
        "concepts": ["Sunlight absorption", "CO2 intake via stomata", "Water transport", "Oxygen release"],
        "viz": "3D biological process animation",
        "template": "photosynthesis",
        "engine": "blender",
        "complexity": "medium",
        "notes": ["Clearly distinguish inputs (CO2, H2O, light) and outputs (glucose, O2)."],
    },
    {
        "keywords": ("atom", "atomic structure", "electron", "proton", "neutron", "nucleus"),
        "normalized": "Atomic Structure",
        "chapter": "Structure of the Atom",
        "objective": "Visualize protons and neutrons inside the nucleus surrounded by electrons in orbital shells.",
        "concepts": ["Protons (+)", "Neutrons (0)", "Electrons (-)", "Electron shells"],
        "viz": "3D atomic model animation",
        "template": "atomic_structure",
        "engine": "blender",
        "complexity": "medium",
        "notes": ["Clarify Bohr shell diagram is a conceptual visualization."],
    },
    {
        "keywords": ("electric circuit", "circuit", "current flow", "ohms law", "battery"),
        "normalized": "Electric Circuits",
        "chapter": "Electricity & Circuits",
        "objective": "Demonstrate how a closed circuit enables current flow from a voltage source to power a load.",
        "concepts": ["Voltage source", "Closed conducting loop", "Load/bulb illumination", "Charge flow"],
        "viz": "3D circuit simulation",
        "template": "electric_circuits",
        "engine": "blender",
        "complexity": "medium",
        "notes": ["Emphasize requirement of a closed path."],
    },
    {
        "keywords": ("volcano", "magma", "lava", "eruption", "tectonic"),
        "normalized": "Volcano Formation",
        "chapter": "Earth Movements & Landforms",
        "objective": "Show magma chamber formation, conduit rise, and volcanic eruption.",
        "concepts": ["Magma chamber", "Vent/conduit", "Crater", "Lava ejection"],
        "viz": "3D geological cutaway animation",
        "template": "volcano_formation",
        "engine": "blender",
        "complexity": "medium",
        "notes": ["Differentiate underground magma from surface lava."],
    },
    {
        "keywords": ("rotating cube", "cube rotation", "cube test"),
        "normalized": "Rotating Cube",
        "chapter": "3D Geometry Fundamentals",
        "objective": "Demonstrate 3D rotational axes and spatial orientation of a cube.",
        "concepts": ["Vertices, edges, faces", "X/Y/Z axis rotation"],
        "viz": "3D geometric animation",
        "template": "rotating_cube",
        "engine": "blender",
        "complexity": "low",
        "notes": [],
    },
    {
        "keywords": ("geometry", "geometrical shapes", "3d shapes", "polyhedra", "cone", "cylinder", "sphere"),
        "normalized": "Geometrical Shapes",
        "chapter": "Visualizing Solid Shapes",
        "objective": "Compare 3D solid shapes: cube, sphere, cone, and cylinder.",
        "concepts": ["Faces, edges, vertices", "Curved vs flat surfaces"],
        "viz": "3D geometric solids showcase",
        "template": "geometrical_shapes",
        "engine": "blender",
        "complexity": "low",
        "notes": [],
    },
    {
        "keywords": ("historical", "indus valley", "mohenjo", "harappa", "ancient civilization", "taj mahal", "ecosystem"),
        "normalized": "Environmental / Historical Visualization",
        "chapter": "History & Environment",
        "objective": "Provide immersive visual context for historical or natural environments.",
        "concepts": ["Architectural/environmental context", "Historical timeline"],
        "viz": "Supplementary cinematic AI clip",
        "template": "generic_stem",
        "engine": "runway",
        "requires_runway": True,
        "complexity": "medium",
        "notes": ["Use Runway supplementary visual clip where realistic environmental footage aids understanding."],
    },
]


class TopicUnderstandingModule:
    """Module 1: Analyzes educational requests and outputs structured TopicUnderstanding JSON."""

    def __init__(self, settings: Optional[Settings] = None, llm_client: Optional[LLMClient] = None) -> None:
        self.settings = settings or get_settings()
        self.llm_client = llm_client or LLMClient(self.settings)

    async def analyze(self, req: GenerationRequest) -> TopicUnderstanding:
        topic_lower = req.topic.lower()

        # 1. Heuristic check for non-visual queries that do NOT need a 3D video
        for pattern in _NON_VISUAL_PATTERNS:
            if re.search(pattern, topic_lower):
                return TopicUnderstanding(
                    topic=req.topic,
                    normalized_topic=req.topic,
                    **{"class": req.class_level},
                    board=req.board,
                    subject=req.subject,
                    chapter=req.chapter or "General",
                    learning_objective=f"Provide a clear text/voice explanation for: {req.topic}",
                    key_concepts=[],
                    visualization_type="text_explanation",
                    video_required=False,
                    video_requirement_reason=(
                        "This query is factual/definitional and does not benefit from a multi-scene 3D video render."
                    ),
                    estimated_duration=0,
                    complexity="low",
                    template_key="generic_stem",
                    recommended_engine="none",
                    requires_runway_clip=False,
                )

        # 2. Match known educational domain templates & existing assets
        matched = None
        for entry in _TOPIC_KNOWLEDGE_BASE:
            if any(kw in topic_lower for kw in entry["keywords"]):
                matched = entry
                break

        # 3. Enrich with LLM when available (without breaking deterministic routing)
        llm_data: Optional[Dict[str, Any]] = None
        if self.llm_client.is_configured:
            system_prompt = (
                "You are Module 1 (Topic Understanding) of Inteliedu's 3D Generation Agent for Classes 6-12. "
                "Return ONLY valid JSON with keys: topic, learning_objective, key_concepts (list of strings), "
                "visualization_type, video_required (boolean), video_requirement_reason, complexity (low|medium|high), "
                "chapter, educational_notes (list of strings). "
                "Only set video_required=false if a video adds zero spatial/process value."
            )
            user_prompt = (
                f"Question/Topic: {req.topic}\nClass: {req.class_level}\nBoard: {req.board}\n"
                f"Subject: {req.subject}\nChapter: {req.chapter or 'Auto'}\n"
                f"Context: {req.educational_context or 'None'}\nRequested duration: {req.duration}s"
            )
            llm_data = await self.llm_client.complete_json(system_prompt, user_prompt, temperature=0.15)

        if matched:
            existing_asset = matched.get("asset")
            if existing_asset and not (self.settings.existing_models_dir / existing_asset).is_file():
                existing_asset = None
            engine = matched["engine"]
            if engine == "existing_asset_blender" and not existing_asset:
                engine = "blender"

            if req.prefer_runway and engine in ("blender", "existing_asset_blender"):
                engine = "hybrid"

            return TopicUnderstanding(
                topic=req.topic,
                normalized_topic=matched["normalized"],
                **{"class": req.class_level},
                board=req.board,
                subject=req.subject,
                chapter=req.chapter or (llm_data or {}).get("chapter") or matched["chapter"],
                learning_objective=(llm_data or {}).get("learning_objective") or matched["objective"],
                key_concepts=(llm_data or {}).get("key_concepts") or matched["concepts"],
                visualization_type=matched["viz"],
                video_required=True,
                video_requirement_reason="Spatial 3D visualization enhances conceptual retention.",
                estimated_duration=req.duration,
                complexity=matched["complexity"],
                template_key=matched["template"],
                recommended_engine=engine,
                requires_runway_clip=bool(matched.get("requires_runway") or req.prefer_runway),
                existing_asset_filename=existing_asset,
                educational_notes=matched["notes"],
            )

        # Unknown visual topic -> use LLM understanding if available, else generic STEM 3D visualization
        video_required = bool((llm_data or {}).get("video_required", True))
        engine = "runway" if req.prefer_runway and not video_required else ("hybrid" if req.prefer_runway else "blender")
        if not video_required:
            engine = "none"

        return TopicUnderstanding(
            topic=req.topic,
            normalized_topic=(llm_data or {}).get("topic") or req.topic,
            **{"class": req.class_level},
            board=req.board,
            subject=req.subject,
            chapter=req.chapter or (llm_data or {}).get("chapter") or f"Class {req.class_level} {req.subject}",
            learning_objective=(llm_data or {}).get("learning_objective")
            or f"Understand the core principles and 3D structure of {req.topic}.",
            key_concepts=(llm_data or {}).get("key_concepts")
            or [req.topic, "Core Structure", "Process Mechanism", "Real-World Application"],
            visualization_type=(llm_data or {}).get("visualization_type") or "3D conceptual animation",
            video_required=video_required,
            video_requirement_reason=(llm_data or {}).get("video_requirement_reason")
            or "Visual 3D representation helps explain mechanisms clearly.",
            estimated_duration=req.duration if video_required else 0,
            complexity=(llm_data or {}).get("complexity") if (llm_data or {}).get("complexity") in {"low", "medium", "high"} else "medium",
            template_key="generic_stem",
            recommended_engine=engine,
            requires_runway_clip=req.prefer_runway,
            existing_asset_filename=None,
            educational_notes=(llm_data or {}).get("educational_notes") or [],
        )

