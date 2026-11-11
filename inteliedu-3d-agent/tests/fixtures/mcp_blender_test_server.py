"""
Test-only stdio MCP server speaking the real Model Context Protocol (`mcp.server.mcpserver.MCPServer`).
Used strictly by automated tests in `tests/` to exercise live MCP discovery, JSON schema validation,
and tool invocation over stdio without mocking the MCP SDK transport.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

server = MCPServer("inteliedu-blender-test-harness")


def _find_ffmpeg() -> str:
    env_ff = os.environ.get("FFMPEG_PATH", "ffmpeg")
    if Path(env_ff).is_file():
        return env_ff
    found = shutil.which(env_ff) or shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError("ffmpeg binary not found for MCP test harness")


@server.tool()
def get_scene_info() -> str:
    """Return mock active Blender scene summary for MCP discovery testing."""
    return json.dumps(
        {
            "scene": "Scene",
            "objects": ["Camera", "Light"],
            "engine": "BLENDER_EEVEE_NEXT",
        }
    )


@server.tool()
def execute_blender_code(code: str) -> str:
    """
    Validate generated bpy code syntax (`compile`) and render an MP4 clip at the script's
    configured `output_mp4_path` using FFmpeg testsrc2 for pipeline testing.
    """
    compile(code, "<generated_bpy_script>", "exec")
    out_match = re.search(r"output_mp4_path=['\"]([^'\"]+)['\"]", code)
    if not out_match:
        return json.dumps({"status": "executed", "note": "No output_mp4_path specified"})

    out_path = Path(out_match.group(1))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fps_match = re.search(r"fps=(\d+)", code)
    frames_match = re.search(r"total_frames=(\d+)", code)
    fps = int(fps_match.group(1)) if fps_match else 24
    total_frames = int(frames_match.group(1)) if frames_match else 48
    duration = max(1.0, min(total_frames / max(fps, 1), 3.0))

    ffmpeg = _find_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"testsrc2=size=640x360:rate={fps}:duration={duration:.2f}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg test harness failed: {proc.stderr[-400:]}")
    return json.dumps({"status": "ok", "output_mp4_path": str(out_path), "harness": "test_mcp"})


if __name__ == "__main__":
    server.run(transport="stdio")

