"""FFmpeg video post-processing pipeline: merge scenes, audio, subtitles, and encode MP4."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import Settings, get_settings
from app.utils.error_handler import VideoProcessingError
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def probe_media(file_path: Path, settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Run ffprobe on a media file and return parsed JSON streams & format metadata."""
    cfg = settings or get_settings()
    cmd = [
        cfg.resolved_ffprobe_path,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]
    proc = await asyncio.to_thread(
        subprocess.run,
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise VideoProcessingError(f"ffprobe failed for {file_path}: {proc.stderr[-500:]}")
    return json.loads(proc.stdout)


def _extract_video_dims(probe_data: Dict[str, Any]) -> Tuple[int, int, bool]:
    """Return (width, height, has_audio) from ffprobe JSON."""
    width = 0
    height = 0
    has_audio = False
    for stream in probe_data.get("streams", []):
        if stream.get("codec_type") == "video" and width == 0:
            width = int(stream.get("width") or 0)
            height = int(stream.get("height") or 0)
        elif stream.get("codec_type") == "audio":
            has_audio = True
    return width, height, has_audio


class VideoProcessor:
    """Combines scene clips, narration audio, and subtitles into browser-compatible MP4."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    async def process_video(
        self,
        job_id: str,
        clip_paths: List[Path],
        output_path: Path,
        *,
        narration_audio_path: Optional[Path] = None,
        subtitle_path: Optional[Path] = None,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        target_fps: Optional[int] = None,
        allow_upscale: Optional[bool] = None,
    ) -> Path:
        """
        Combine scene clips into one MP4 (H.264 + AAC), optionally mixing normalized narration
        and embedding soft subtitles (`mov_text`). Never upscales unless `allow_upscale=True`.
        """
        valid_clips = [Path(p) for p in clip_paths if Path(p).is_file() and Path(p).stat().st_size > 0]
        if not valid_clips:
            raise VideoProcessingError("No valid video clips provided for FFmpeg processing.")

        req_w = target_width or self.settings.video_default_width
        req_h = target_height or self.settings.video_default_height
        fps = target_fps or self.settings.video_default_fps
        upscale = self.settings.video_allow_upscale if allow_upscale is None else allow_upscale

        tmp_dir = self.settings.resolved_generated_dir / "tmp" / job_id
        tmp_dir.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Determine safe resolution (never upscale beyond lowest source unless allowed)
            probed = [await probe_media(p, self.settings) for p in valid_clips]
            dims = [_extract_video_dims(d) for d in probed]
            src_widths = [w for w, _, _ in dims if w > 0]
            src_heights = [h for _, h, _ in dims if h > 0]

            out_w = req_w
            out_h = req_h
            if not upscale and src_widths and src_heights:
                max_w = max(src_widths)
                max_h = max(src_heights)
                if max_w < req_w or max_h < req_h:
                    out_w = max_w - (max_w % 2)
                    out_h = max_h - (max_h % 2)
                    logger.info(
                        "Preserving source resolution %sx%s instead of upscaling to %sx%s",
                        out_w,
                        out_h,
                        req_w,
                        req_h,
                    )

            # Normalize each clip to uniform H.264 / yuv420p / fps so concat is rock-solid
            normalized_clips: List[Path] = []
            for idx, clip in enumerate(valid_clips):
                norm_path = tmp_dir / f"norm_{idx:02d}.mp4"
                vf = (
                    f"scale={out_w}:{out_h}:force_original_aspect_ratio=decrease,"
                    f"pad={out_w}:{out_h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
                )
                cmd = [
                    self.settings.resolved_ffmpeg_path,
                    "-y",
                    "-i",
                    str(clip),
                    "-vf",
                    vf,
                    "-r",
                    str(fps),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "medium",
                    "-crf",
                    "22",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(norm_path),
                ]
                await self._run_ffmpeg(cmd, f"normalize clip {clip.name}")
                normalized_clips.append(norm_path)

            concat_video = tmp_dir / "concat_video.mp4"
            if len(normalized_clips) == 1:
                shutil.copy2(normalized_clips[0], concat_video)
            else:
                list_file = tmp_dir / "concat_list.txt"
                lines = [f"file '{p.as_posix()}'" for p in normalized_clips]
                list_file.write_text("\n".join(lines), encoding="utf-8")
                concat_cmd = [
                    self.settings.resolved_ffmpeg_path,
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(list_file),
                    "-c",
                    "copy",
                    str(concat_video),
                ]
                await self._run_ffmpeg(concat_cmd, "concatenate scenes")

            # Mux optional narration audio (normalized) and optional soft SRT subtitle track
            has_narration = bool(narration_audio_path and Path(narration_audio_path).is_file())
            has_subs = bool(subtitle_path and Path(subtitle_path).is_file())

            if not has_narration and not has_subs:
                final_cmd = [
                    self.settings.resolved_ffmpeg_path,
                    "-y",
                    "-i",
                    str(concat_video),
                    "-c:v",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(output_path),
                ]
                await self._run_ffmpeg(final_cmd, "finalize browser MP4")
                return output_path

            final_cmd = [self.settings.resolved_ffmpeg_path, "-y", "-i", str(concat_video)]
            map_args = ["-map", "0:v:0"]
            codec_args = ["-c:v", "copy"]

            next_input_idx = 1
            if has_narration:
                final_cmd.extend(["-i", str(narration_audio_path)])
                map_args.extend(["-map", f"{next_input_idx}:a:0"])
                codec_args.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest"])
                next_input_idx += 1

            if has_subs:
                final_cmd.extend(["-i", str(subtitle_path)])
                map_args.extend(["-map", f"{next_input_idx}:s:0"])
                codec_args.extend(["-c:s", "mov_text", "-metadata:s:s:0", "language=eng"])

            final_cmd.extend(map_args)
            final_cmd.extend(codec_args)
            final_cmd.extend(["-movflags", "+faststart", str(output_path)])
            await self._run_ffmpeg(final_cmd, "mux audio and subtitles")
            return output_path
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    async def _run_ffmpeg(self, cmd: List[str], step_label: str) -> None:
        proc = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if proc.returncode != 0:
            raise VideoProcessingError(
                f"FFmpeg failed during '{step_label}' (exit={proc.returncode}): {proc.stderr[-1200:]}"
            )

