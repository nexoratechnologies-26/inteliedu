"""Technical and educational validation pipeline for generated videos."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional

from app.api.schemas import (
    EducationalValidationResult,
    Storyboard,
    TechnicalValidationResult,
    ValidationReport,
)
from app.config import Settings, get_settings
from app.video.processor import probe_media


SOLAR_SYSTEM_PLANETS_ORDER = [
    "mercury",
    "venus",
    "earth",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
]


class VideoValidator:
    """Validates both technical media integrity (via FFprobe/FFmpeg) and educational accuracy."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    async def validate_technical(
        self,
        video_path: Path,
        require_audio: bool = False,
    ) -> TechnicalValidationResult:
        if not video_path.is_file():
            return TechnicalValidationResult(
                passed=False,
                file_exists=False,
                decode_errors=[f"Video file does not exist: {video_path}"],
            )

        file_size = video_path.stat().st_size
        max_bytes = self.settings.video_max_size_mb * 1024 * 1024
        if file_size <= 0:
            return TechnicalValidationResult(
                passed=False,
                file_exists=True,
                file_size_bytes=0,
                decode_errors=["Video file is empty (0 bytes)."],
            )

        decode_errors: List[str] = []
        if file_size > max_bytes:
            decode_errors.append(
                f"File size {file_size} bytes exceeds limit of {self.settings.video_max_size_mb} MB."
            )

        try:
            probe_data = await probe_media(video_path, self.settings)
        except Exception as exc:
            return TechnicalValidationResult(
                passed=False,
                file_exists=True,
                can_open=False,
                file_size_bytes=file_size,
                decode_errors=[str(exc)],
            )

        fmt = probe_data.get("format", {})
        duration = float(fmt.get("duration") or 0.0)
        video_stream = next(
            (s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None
        )
        audio_stream = next(
            (s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None
        )

        if not video_stream:
            decode_errors.append("No video stream detected in container.")
            return TechnicalValidationResult(
                passed=False,
                file_exists=True,
                can_open=False,
                file_size_bytes=file_size,
                decode_errors=decode_errors,
            )

        width = int(video_stream.get("width") or 0)
        height = int(video_stream.get("height") or 0)
        vcodec = video_stream.get("codec_name")
        pix_fmt = video_stream.get("pix_fmt")
        acodec = audio_stream.get("codec_name") if audio_stream else None
        has_audio = audio_stream is not None

        fps_str = str(video_stream.get("r_frame_rate") or "0/1")
        try:
            num, den = fps_str.split("/")
            fps = round(float(num) / float(den), 2) if float(den) else 0.0
        except Exception:
            fps = 0.0

        if duration <= 0.1:
            decode_errors.append(f"Invalid video duration: {duration}s.")
        if width <= 0 or height <= 0:
            decode_errors.append(f"Invalid resolution: {width}x{height}.")
        if require_audio and not has_audio:
            decode_errors.append("Audio stream was required but none is present.")

        browser_compatible = vcodec in {"h264", "vp8", "vp9", "av1"} and (
            pix_fmt in {"yuv420p", "yuvj420p", None}
        )
        if not browser_compatible:
            decode_errors.append(
                f"Encoding ({vcodec}/{pix_fmt}) is not universally browser-compatible (expected h264/yuv420p)."
            )

        # Full-stream frame decode verification for corrupted frames
        decode_cmd = [
            self.settings.resolved_ffmpeg_path,
            "-v",
            "error",
            "-i",
            str(video_path),
            "-f",
            "null",
            "-",
        ]
        proc = await asyncio.to_thread(
            subprocess.run,
            decode_cmd,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if proc.returncode != 0 or proc.stderr.strip():
            err_lines = [line.strip() for line in proc.stderr.splitlines() if line.strip()]
            decode_errors.extend(err_lines[:5] or [f"ffmpeg decode exit={proc.returncode}"])

        return TechnicalValidationResult(
            passed=len(decode_errors) == 0,
            file_exists=True,
            can_open=True,
            duration_seconds=round(duration, 2),
            width=width,
            height=height,
            fps=fps,
            video_codec=vcodec,
            pixel_format=pix_fmt,
            audio_codec=acodec,
            has_audio=has_audio,
            file_size_bytes=file_size,
            decode_errors=decode_errors,
            browser_compatible=browser_compatible,
        )

    def validate_educational(
        self,
        storyboard: Storyboard,
        rendered_scene_count: int,
        is_simulated: bool = False,
    ) -> EducationalValidationResult:
        """Verify storyboard completeness, object coverage, and curriculum accuracy."""
        errors: List[str] = []
        warnings: List[str] = []
        checks: List[str] = []

        expected_count = len(storyboard.scenes)
        if rendered_scene_count < expected_count:
            errors.append(
                f"Rendered scene count ({rendered_scene_count}) is fewer than storyboard scenes ({expected_count})."
            )
        else:
            checks.append(f"All {expected_count} storyboard scenes rendered in sequence.")

        if is_simulated:
            errors.append("Output is a simulated artifact, not a real 3D/AI rendered video.")

        combined_text = " ".join(
            [
                storyboard.video_title,
                storyboard.topic,
                storyboard.scale_disclosure or "",
                " ".join(storyboard.scientific_accuracy_notes),
                " ".join(
                    f"{s.title} {s.description} {' '.join(s.objects)} {' '.join(s.labels)} {s.narration}"
                    for s in storyboard.scenes
                ),
            ]
        ).lower()

        missing_objects: List[str] = []
        topic_lower = storyboard.topic.lower()

        if "solar system" in topic_lower:
            missing_planets = [p.title() for p in SOLAR_SYSTEM_PLANETS_ORDER if p not in combined_text]
            if missing_planets:
                missing_objects.extend(missing_planets)
                errors.append(f"Solar System storyboard missing planets: {', '.join(missing_planets)}")
            else:
                checks.append("All 8 planets (Mercury through Neptune) present in Solar System plan.")
            if "sun" not in combined_text:
                missing_objects.append("Sun")
                errors.append("Solar System storyboard missing the Sun.")
            if not storyboard.scale_disclosure and "not to scale" not in combined_text:
                errors.append(
                    "Solar System visualization must explicitly disclose that sizes and distances are not to scale."
                )
            else:
                checks.append("Scale disclosure present for Solar System visualization.")

        elif "water cycle" in topic_lower:
            for concept in ("evaporation", "condensation", "precipitation"):
                if concept not in combined_text:
                    missing_objects.append(concept.title())
            if missing_objects:
                errors.append(f"Water Cycle missing key stages: {', '.join(missing_objects)}")
            else:
                checks.append("Water Cycle covers evaporation, condensation, and precipitation.")

        elif "heart" in topic_lower:
            if not any(w in combined_text for w in ("chamber", "atria", "ventricle", "blood", "aorta", "heart")):
                missing_objects.append("Heart anatomical structures")
                errors.append("Human Heart storyboard lacks core anatomical terms.")
            else:
                checks.append("Human Heart anatomical terminology validated.")

        elif "photosynthesis" in topic_lower:
            for term in ("sunlight", "carbon dioxide", "water", "oxygen"):
                if term not in combined_text and term.replace(" ", "") not in combined_text:
                    warnings.append(f"Photosynthesis plan should explicitly mention '{term}'.")
            checks.append("Photosynthesis reactants and products checked.")

        elif "atom" in topic_lower:
            if "nucleus" not in combined_text or "electron" not in combined_text:
                missing_objects.append("Nucleus / Electrons")
                errors.append("Atomic structure plan must include both nucleus and electrons.")
            else:
                checks.append("Atomic structure includes nucleus and orbiting electrons.")

        return EducationalValidationResult(
            passed=len(errors) == 0,
            scene_count_expected=expected_count,
            scene_count_rendered=rendered_scene_count,
            required_objects_present=len(missing_objects) == 0,
            missing_objects=missing_objects,
            scientific_checks=checks,
            warnings=warnings,
            errors=errors,
        )

    async def validate(
        self,
        video_path: Path,
        storyboard: Storyboard,
        rendered_scene_count: int,
        require_audio: bool = False,
        is_simulated: bool = False,
    ) -> ValidationReport:
        technical = await self.validate_technical(video_path, require_audio=require_audio)
        educational = self.validate_educational(
            storyboard=storyboard,
            rendered_scene_count=rendered_scene_count,
            is_simulated=is_simulated,
        )
        return ValidationReport(
            passed=technical.passed and educational.passed,
            technical=technical,
            educational=educational,
        )

