"""SRT subtitle generator synchronized with educational storyboard scenes."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.api.schemas import Storyboard


def _format_srt_timestamp(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def generate_srt_for_storyboard(storyboard: Storyboard, output_path: Path) -> Optional[Path]:
    """Create an .srt subtitle file from storyboard scene timings and narrations."""
    entries = []
    cursor = 0.0
    index = 1

    for scene in storyboard.scenes:
        text = (scene.narration or scene.description or scene.title).strip()
        duration = float(scene.duration)
        if text and duration > 0:
            start_ts = _format_srt_timestamp(cursor)
            end_ts = _format_srt_timestamp(cursor + duration)
            entries.append(f"{index}\n{start_ts} --> {end_ts}\n{text}\n")
            index += 1
        cursor += duration

    if not entries:
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(entries), encoding="utf-8")
    return output_path

