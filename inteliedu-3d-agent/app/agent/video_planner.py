"""Module 2: Educational Video Storyboard Planning and Validation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.api.schemas import SceneSpec, Storyboard, TopicUnderstanding
from app.config import Settings, get_settings
from app.services.llm_client import LLMClient
from app.video.validator import SOLAR_SYSTEM_PLANETS_ORDER


def _allocate_durations(total_duration: int, weights: List[int]) -> List[int]:
    """Distribute total_duration across scenes while ensuring every scene >= 2 seconds."""
    count = len(weights)
    if count == 0:
        return []
    total = max(total_duration, count * 2)
    weight_sum = sum(weights)
    allocated = [max(2, round(total * w / weight_sum)) for w in weights]
    diff = total - sum(allocated)
    idx = 0
    while diff != 0:
        if diff > 0:
            allocated[idx % count] += 1
            diff -= 1
        elif allocated[idx % count] > 2:
            allocated[idx % count] -= 1
            diff += 1
        idx += 1
        if idx > count * 20:
            break
    return allocated


class VideoPlannerModule:
    """Module 2: Divides educational topics into logical, validated scenes."""

    def __init__(self, settings: Optional[Settings] = None, llm_client: Optional[LLMClient] = None) -> None:
        self.settings = settings or get_settings()
        self.llm_client = llm_client or LLMClient(self.settings)

    async def create_storyboard(
        self,
        topic_info: TopicUnderstanding,
        language: str = "English",
        requested_duration: int = 60,
    ) -> Storyboard:
        template = topic_info.template_key
        total_duration = max(10, min(requested_duration, self.settings.max_video_duration_seconds))

        if template == "solar_system":
            return self._build_solar_system_storyboard(topic_info, language, total_duration)
        if template == "water_cycle":
            return self._build_water_cycle_storyboard(topic_info, language, total_duration)
        if template == "anatomy_asset":
            return self._build_heart_anatomy_storyboard(topic_info, language, total_duration)
        if template == "rotating_cube":
            return self._build_rotating_cube_storyboard(topic_info, language, total_duration)

        # Try LLM storyboard synthesis for general/custom topics
        if self.llm_client.is_configured:
            llm_sb = await self._try_llm_storyboard(topic_info, language, total_duration)
            if llm_sb is not None:
                return llm_sb

        return self._build_generic_storyboard(topic_info, language, total_duration)

    def _build_solar_system_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Storyboard:
        durs = _allocate_durations(total_duration, [15, 20, 25, 20, 25, 15])
        all_planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
        scenes = [
            SceneSpec(
                scene_id=1,
                title="Introduction to the Solar System",
                educational_objective="Introduce the Sun and the eight planets bound by gravity.",
                description="Wide orbital view of the Sun surrounded by eight concentric planetary orbits.",
                objects=["Sun"] + all_planets,
                camera_position="elevated-wide",
                camera_movement="smooth_zoom",
                object_movement="slow_orbital_revolution",
                animation_instructions="Wide perspective slowly zooming toward the central Sun while planets orbit.",
                duration=durs[0],
                narration="Our Solar System consists of the Sun at the center and eight planets orbiting around it under gravity.",
                transition="crossfade",
                render_engine="blender",
                template_name="solar_system",
                labels=["Sun"] + all_planets,
            ),
            SceneSpec(
                scene_id=2,
                title="The Sun: Our Central Star",
                educational_objective="Explain the Sun as the energy and gravitational center of the Solar System.",
                description="Close-up view of the glowing Sun radiating heat and light outward.",
                objects=["Sun"],
                camera_position="front-close",
                camera_movement="smooth_orbit",
                object_movement="axial_spin",
                animation_instructions="Focus on the Sun rotating steadily with emissive solar glow.",
                duration=durs[1],
                narration="The Sun is a star containing nearly all the mass of the Solar System and providing light and heat.",
                transition="crossfade",
                render_engine="blender",
                template_name="solar_system",
                labels=["Sun"],
            ),
            SceneSpec(
                scene_id=3,
                title="The Eight Planets in Order",
                educational_objective="Identify all eight planets in correct heliocentric order from the Sun.",
                description="Sequential reveal of Mercury, Venus, Earth, Mars, Jupiter, Saturn with rings, Uranus, and Neptune.",
                objects=["Sun"] + all_planets,
                camera_position="oblique-pan",
                camera_movement="pan",
                object_movement="ordered_orbit_showcase",
                animation_instructions="Pan across inner rocky planets and outer gas and ice giants in exact order.",
                duration=durs[2],
                narration="Moving outward from the Sun, the eight planets are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.",
                transition="crossfade",
                render_engine="blender",
                template_name="solar_system",
                labels=all_planets,
            ),
            SceneSpec(
                scene_id=4,
                title="Planetary Rotation (Day and Night)",
                educational_objective="Distinguish axial rotation on a planet's axis causing day and night.",
                description="Observe planets spinning around their tilted axes.",
                objects=["Sun", "Earth", "Jupiter"],
                camera_position="mid-orbital",
                camera_movement="smooth_orbit",
                object_movement="axial_rotation",
                animation_instructions="Highlight axial rotation of Earth and other planets on their axes.",
                duration=durs[3],
                narration="Each planet rotates on its own axis; Earth takes about 24 hours for one rotation, creating day and night.",
                transition="crossfade",
                render_engine="blender",
                template_name="solar_system",
                labels=["Earth", "Axial Rotation"],
            ),
            SceneSpec(
                scene_id=5,
                title="Planetary Revolution (Orbits and Years)",
                educational_objective="Explain revolution along orbital paths around the Sun.",
                description="Top-down and oblique view showing inner planets completing faster orbits than outer planets.",
                objects=["Sun"] + all_planets,
                camera_position="top-oblique",
                camera_movement="smooth_orbit",
                object_movement="keplerian_relative_orbit",
                animation_instructions="Show inner planets revolving faster around the Sun than distant outer planets.",
                duration=durs[4],
                narration="As planets spin, they also revolve around the Sun along elliptical orbits; closer planets orbit faster.",
                transition="crossfade",
                render_engine="blender",
                template_name="solar_system",
                labels=["Orbital Revolution", "Sun"],
            ),
            SceneSpec(
                scene_id=6,
                title="Summary of the Solar System",
                educational_objective="Reinforce planetary order, rotation vs revolution, and scale awareness.",
                description="Full system overview with clear labels and non-scale educational disclaimer.",
                objects=["Sun"] + all_planets,
                camera_position="elevated-wide",
                camera_movement="smooth_orbit",
                object_movement="continuous_orbit",
                animation_instructions="Pull back to reveal all eight labeled planetary orbits and scale notice.",
                duration=durs[5],
                narration="To summarize, eight planets rotate on their axes while revolving around the Sun. Note that sizes and distances shown are not to scale.",
                transition="fade_out",
                render_engine="blender",
                template_name="solar_system",
                labels=["Sun"] + all_planets,
            ),
        ]
        return Storyboard(
            video_title="Understanding the Solar System",
            topic=info.normalized_topic,
            **{"class": info.class_level},
            subject=info.subject,
            board=info.board,
            chapter=info.chapter,
            language=language,
            total_duration=sum(s.duration for s in scenes),
            scale_disclosure="Note: Planetary sizes and orbital distances are adjusted for educational clarity and are not shown to true scale.",
            scientific_accuracy_notes=info.educational_notes,
            scenes=scenes,
        )

    def _build_water_cycle_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Storyboard:
        durs = _allocate_durations(total_duration, [25, 25, 25, 25])
        scenes = [
            SceneSpec(
                scene_id=1,
                title="Solar Heating & Evaporation",
                educational_objective="Explain how solar energy turns liquid ocean water into rising water vapor.",
                description="Sunlight warms the ocean surface as water vapor droplets rise into the atmosphere.",
                objects=["Sun", "Ocean", "Water Vapor"],
                camera_position="front-elevated",
                camera_movement="smooth_zoom",
                object_movement="rising_vapor",
                animation_instructions="Animate water vapor spheres rising upward from the ocean surface toward the sky.",
                duration=durs[0],
                narration="Heat from the Sun warms oceans, rivers, and lakes, causing liquid water to evaporate into invisible water vapor.",
                transition="crossfade",
                render_engine="blender",
                template_name="water_cycle",
                labels=["Evaporation", "Sun", "Ocean"],
            ),
            SceneSpec(
                scene_id=2,
                title="Condensation & Cloud Formation",
                educational_objective="Explain cooling of water vapor at high altitude to form clouds.",
                description="Rising vapor cools and condenses into billowing white cloud clusters above land.",
                objects=["Water Vapor", "Clouds"],
                camera_position="sky-elevated",
                camera_movement="pan",
                object_movement="cloud_drift",
                animation_instructions="Move condensed cloud clusters smoothly from ocean air toward mountain peaks.",
                duration=durs[1],
                narration="As warm water vapor rises and cools high in the atmosphere, it condenses into tiny droplets that form clouds.",
                transition="crossfade",
                render_engine="blender",
                template_name="water_cycle",
                labels=["Condensation", "Clouds"],
            ),
            SceneSpec(
                scene_id=3,
                title="Precipitation",
                educational_objective="Explain rain falling when cloud droplets become too heavy.",
                description="Raindrops descend from dense clouds onto highland terrain.",
                objects=["Clouds", "Raindrops", "Mountain Terrain"],
                camera_position="side-elevated",
                camera_movement="smooth_orbit",
                object_movement="falling_rain",
                animation_instructions="Animate vertical rainfall from cloud clusters onto mountain slopes.",
                duration=durs[2],
                narration="When water droplets inside clouds grow heavy enough, gravity pulls them down as precipitation such as rain or snow.",
                transition="crossfade",
                render_engine="blender",
                template_name="water_cycle",
                labels=["Precipitation", "Mountain"],
            ),
            SceneSpec(
                scene_id=4,
                title="Collection & Continuous Cycle",
                educational_objective="Explain runoff returning water to oceans and repeating the cycle.",
                description="Full landscape view linking runoff back into the ocean reservoir.",
                objects=["Mountain Terrain", "Runoff Stream", "Ocean"],
                camera_position="wide-elevated",
                camera_movement="smooth_orbit",
                object_movement="complete_water_cycle",
                animation_instructions="Orbit the complete terrain showing evaporation, condensation, precipitation, and collection together.",
                duration=durs[3],
                narration="Rainwater flows over land back into rivers and oceans during collection, powering the continuous water cycle.",
                transition="fade_out",
                render_engine="blender",
                template_name="water_cycle",
                labels=["Collection", "Runoff"],
            ),
        ]
        return Storyboard(
            video_title="Understanding the Water Cycle",
            topic=info.normalized_topic,
            **{"class": info.class_level},
            subject=info.subject,
            board=info.board,
            chapter=info.chapter,
            language=language,
            total_duration=sum(s.duration for s in scenes),
            scientific_accuracy_notes=info.educational_notes,
            scenes=scenes,
        )

    def _build_heart_anatomy_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Storyboard:
        durs = _allocate_durations(total_duration, [35, 35, 30])
        engine = "existing_asset_blender" if info.existing_asset_filename else "blender"
        scenes = [
            SceneSpec(
                scene_id=1,
                title="Location & Role of the Human Heart",
                educational_objective="Locate the heart inside the thoracic cavity and introduce its pumping role.",
                description="Orbit around the approved Inteliedu human anatomy model highlighting the thoracic heart region.",
                objects=["Human Anatomy Model", "Human Heart", "Thoracic Cavity"],
                camera_position="front-thoracic",
                camera_movement="smooth_zoom",
                object_movement="gentle_cardiac_pulse",
                animation_instructions="Load approved anatomical GLB asset and focus camera on chest cardiac marker.",
                duration=durs[0],
                narration="The human heart is a muscular organ inside the chest that continuously pumps blood throughout the body.",
                transition="crossfade",
                render_engine=engine,
                template_name="anatomy_asset",
                labels=["Human Heart", "Thoracic Region"],
            ),
            SceneSpec(
                scene_id=2,
                title="Four Chambers & Major Blood Vessels",
                educational_objective="Explain the two atria, two ventricles, and the aorta.",
                description="Close orbital sweep around the cardiac marker showing rhythmic contraction.",
                objects=["Left Atrium", "Right Atrium", "Left Ventricle", "Right Ventricle", "Aorta"],
                camera_position="close-cardiac",
                camera_movement="smooth_orbit",
                object_movement="rhythmic_heartbeat",
                animation_instructions="Pulse cardiac indicator at ~72 BPM rate while orbiting slowly for 3D depth.",
                duration=durs[1],
                narration="The heart has four chambers: upper left and right atria receive blood, while lower ventricles pump blood through vessels like the aorta.",
                transition="crossfade",
                render_engine=engine,
                template_name="anatomy_asset",
                labels=["Four Chambers", "Aorta"],
            ),
            SceneSpec(
                scene_id=3,
                title="Double Circulation Summary",
                educational_objective="Summarize oxygenation in lungs and delivery to body tissues.",
                description="Wide overview linking heart pumping to systemic and pulmonary circulation.",
                objects=["Human Heart", "Lungs", "Circulatory System"],
                camera_position="front-elevated",
                camera_movement="smooth_orbit",
                object_movement="cardiac_pulse",
                animation_instructions="Pull camera back smoothly while maintaining heart highlight and labels.",
                duration=durs[2],
                narration="Deoxygenated blood travels from the right side to the lungs, and oxygen-rich blood returns to the left side to nourish the entire body.",
                transition="fade_out",
                render_engine=engine,
                template_name="anatomy_asset",
                labels=["Double Circulation", "Oxygenation"],
            ),
        ]
        return Storyboard(
            video_title="Understanding the Human Heart",
            topic=info.normalized_topic,
            **{"class": info.class_level},
            subject=info.subject,
            board=info.board,
            chapter=info.chapter,
            language=language,
            total_duration=sum(s.duration for s in scenes),
            scientific_accuracy_notes=info.educational_notes,
            scenes=scenes,
        )

    def _build_rotating_cube_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Storyboard:
        dur = max(4, min(total_duration, 15))
        scenes = [
            SceneSpec(
                scene_id=1,
                title="3D Rotating Cube Geometry",
                educational_objective="Demonstrate faces, edges, vertices, and multi-axis 3D rotation.",
                description="A studio-lit 3D cube rotating smoothly about vertical and horizontal axes.",
                objects=["Cube"],
                camera_position="front-elevated",
                camera_movement="static_focus",
                object_movement="continuous_rotation",
                animation_instructions="Rotate cube 360 degrees around Z and 180 degrees around X with linear keyframes.",
                duration=dur,
                narration="A cube has 6 square faces, 12 edges, and 8 vertices. Rotating it in 3D space reveals all sides clearly.",
                transition="fade_out",
                render_engine="blender",
                template_name="rotating_cube",
                labels=["Cube", "3D Rotation"],
            )
        ]
        return Storyboard(
            video_title="Rotating 3D Cube Demonstration",
            topic=info.normalized_topic,
            **{"class": info.class_level},
            subject=info.subject,
            board=info.board,
            chapter=info.chapter,
            language=language,
            total_duration=dur,
            scenes=scenes,
        )

    async def _try_llm_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Optional[Storyboard]:
        system_prompt = (
            "You are Module 2 (Video Planning) of Inteliedu's 3D Generation Agent. "
            "Create a scientifically accurate storyboard JSON for State Board students. "
            "Return ONLY valid JSON: {\"video_title\": str, \"scale_disclosure\": str|null, "
            "\"scenes\": [{\"scene_id\": int, \"title\": str, \"educational_objective\": str, "
            "\"description\": str, \"objects\": [str], \"camera_position\": str, \"camera_movement\": str, "
            "\"object_movement\": str, \"animation_instructions\": str, \"duration\": int, "
            "\"narration\": str, \"transition\": str}]}. "
            f"Produce 2 to 5 scenes whose durations sum to approximately {total_duration}s."
        )
        user_prompt = (
            f"Topic: {info.normalized_topic}\nClass: {info.class_level}\nBoard: {info.board}\n"
            f"Subject: {info.subject}\nObjective: {info.learning_objective}\n"
            f"Key concepts: {', '.join(info.key_concepts)}\nLanguage: {language}"
        )
        data = await self.llm_client.complete_json(system_prompt, user_prompt, temperature=0.2, max_tokens=2048)
        if not data or not isinstance(data.get("scenes"), list) or not data["scenes"]:
            return None

        try:
            scenes: List[SceneSpec] = []
            for idx, raw in enumerate(data["scenes"], start=1):
                engine = "runway" if info.recommended_engine == "runway" else "blender"
                scenes.append(
                    SceneSpec(
                        scene_id=idx,
                        title=str(raw.get("title") or f"Scene {idx}"),
                        educational_objective=str(raw.get("educational_objective") or info.learning_objective),
                        description=str(raw.get("description") or info.learning_objective),
                        objects=[str(o) for o in (raw.get("objects") or info.key_concepts[:4])],
                        camera_position=str(raw.get("camera_position") or "front-elevated"),
                        camera_movement=str(raw.get("camera_movement") or "smooth_orbit"),
                        object_movement=str(raw.get("object_movement") or "educational_motion"),
                        animation_instructions=str(raw.get("animation_instructions") or "Animate key components cleanly."),
                        duration=max(3, min(int(raw.get("duration") or 10), 60)),
                        narration=str(raw.get("narration") or ""),
                        transition=str(raw.get("transition") or "crossfade"),
                        render_engine=engine,
                        template_name=info.template_key,
                        labels=[str(o) for o in (raw.get("objects") or [])[:5]],
                    )
                )
            return Storyboard(
                video_title=str(data.get("video_title") or f"Understanding {info.normalized_topic}"),
                topic=info.normalized_topic,
                **{"class": info.class_level},
                subject=info.subject,
                board=info.board,
                chapter=info.chapter,
                language=language,
                total_duration=sum(s.duration for s in scenes),
                scale_disclosure=data.get("scale_disclosure"),
                scientific_accuracy_notes=info.educational_notes,
                scenes=scenes,
            )
        except Exception:
            return None

    def _build_generic_storyboard(
        self, info: TopicUnderstanding, language: str, total_duration: int
    ) -> Storyboard:
        durs = _allocate_durations(total_duration, [30, 40, 30])
        concepts = info.key_concepts or [info.normalized_topic, "Structure", "Mechanism"]
        engine = "runway" if info.recommended_engine == "runway" else "blender"
        scenes = [
            SceneSpec(
                scene_id=1,
                title=f"Introduction to {info.normalized_topic}",
                educational_objective=info.learning_objective,
                description=f"Introduce core components of {info.normalized_topic}.",
                objects=concepts[:3],
                camera_position="front-elevated",
                camera_movement="smooth_zoom",
                object_movement="gentle_rotation",
                animation_instructions="Present labeled 3D components with slow zoom.",
                duration=durs[0],
                narration=f"Let us explore {info.normalized_topic} and understand its essential components.",
                transition="crossfade",
                render_engine=engine,
                template_name=info.template_key,
                labels=concepts[:3],
            ),
            SceneSpec(
                scene_id=2,
                title=f"How {info.normalized_topic} Works",
                educational_objective=f"Demonstrate core process of {info.normalized_topic}.",
                description=f"Dynamic 3D animation illustrating {info.normalized_topic} in action.",
                objects=concepts[:4],
                camera_position="mid-oblique",
                camera_movement="smooth_orbit",
                object_movement="process_animation",
                animation_instructions="Animate interaction and motion paths between key elements.",
                duration=durs[1],
                narration=f"Observe how each component interacts during {info.normalized_topic}.",
                transition="crossfade",
                render_engine=engine,
                template_name=info.template_key,
                labels=concepts[:4],
            ),
            SceneSpec(
                scene_id=3,
                title=f"Key Takeaways: {info.normalized_topic}",
                educational_objective="Summarize core learning outcomes.",
                description=f"Full overview of {info.normalized_topic} with summary labels.",
                objects=concepts[:4],
                camera_position="elevated-wide",
                camera_movement="smooth_orbit",
                object_movement="steady_overview",
                animation_instructions="Orbit around complete assembly with summary labels.",
                duration=durs[2],
                narration=f"To review, {info.learning_objective}",
                transition="fade_out",
                render_engine="blender" if info.recommended_engine != "runway" else "runway",
                template_name=info.template_key,
                labels=concepts[:4],
            ),
        ]
        if info.recommended_engine == "hybrid":
            scenes[-1].render_engine = "runway"
            scenes[-1].runway_prompt = (
                f"Cinematic real-world educational footage illustrating {info.normalized_topic} "
                f"for Class {info.class_level} {info.subject}."
            )
        return Storyboard(
            video_title=f"Understanding {info.normalized_topic}",
            topic=info.normalized_topic,
            **{"class": info.class_level},
            subject=info.subject,
            board=info.board,
            chapter=info.chapter,
            language=language,
            total_duration=sum(s.duration for s in scenes),
            scientific_accuracy_notes=info.educational_notes,
            scenes=scenes,
        )

    @staticmethod
    def validate_storyboard(storyboard: Storyboard) -> Tuple[bool, List[str]]:
        """Verify storyboard structural completeness and curriculum accuracy prior to rendering."""
        errors: List[str] = []
        if not storyboard.scenes:
            errors.append("Storyboard contains zero scenes.")
            return False, errors

        expected_id = 1
        for scene in storyboard.scenes:
            if scene.scene_id != expected_id:
                errors.append(f"Scene numbering out of order: expected {expected_id}, got {scene.scene_id}.")
            expected_id += 1
            if scene.duration <= 0:
                errors.append(f"Scene {scene.scene_id} has non-positive duration: {scene.duration}.")
            if not scene.educational_objective.strip():
                errors.append(f"Scene {scene.scene_id} is missing an educational_objective.")
            if not scene.objects:
                errors.append(f"Scene {scene.scene_id} lists no required 3D objects.")

        if "solar system" in storyboard.topic.lower():
            all_text = " ".join(
                f"{s.title} {' '.join(s.objects)} {' '.join(s.labels)} {s.narration}"
                for s in storyboard.scenes
            ).lower()
            for planet in SOLAR_SYSTEM_PLANETS_ORDER:
                if planet not in all_text:
                    errors.append(f"Solar System storyboard omits planet '{planet.title()}'.")
            if not storyboard.scale_disclosure:
                errors.append("Solar System storyboard requires an explicit scale_disclosure.")

        return len(errors) == 0, errors

