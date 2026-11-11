"""Thumbnail extraction utility using FFmpeg."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from app.config import Settings, get_settings
from app.utils.error_handler import VideoProcessingError


async def generate_thumbnail(
    video_path: Path,
    output_path: Path,
    timestamp_seconds: float = 1.0,
    settings: Optional[Settings] = None,
) -> Path:
    """Extract a JPEG thumbnail frame from a rendered MP4 video."""
    cfg = settings or get_settings()
    if not video_path.is_file():
        raise VideoProcessingError(f"Cannot extract thumbnail; video not found: {video_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        cfg.resolved_ffmpeg_path,
        "-y",
        "-ss",
        f"{max(0.0, timestamp_seconds):.2f}",
        "-i",
        str(video_path),
        "-vframes",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    proc = await asyncio.to_thread(
        subprocess.run,
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0 or not output_path.is_file() or output_path.stat().st_size == 0:
        # Retry at t=0.0 if requested seek exceeded video length
        retry_cmd = list(cmd)
        retry_cmd[3] = "0.00"
        proc = await asyncio.to_thread(
            subprocess.run,
            retry_cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if proc.returncode != 0 or not output_path.is_file() or output_path.stat().st_size == 0:
            raise VideoProcessingError(
                f"FFmpeg thumbnail extraction failed: {proc.stderr[-800:]}"
            )
    return output_path

