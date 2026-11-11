"""
Standalone Reusable Blender Base Scene CLI Script
Run directly inside Blender:
    blender --background --python blender_scripts/base_scene.py -- --output out.mp4 --title "Demo"
"""

from __future__ import annotations

import argparse
import math
import os
import sys

try:
    import bpy  # type: ignore
except ImportError:
    bpy = None


def parse_cli_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Inteliedu Reusable Blender Base Scene")
    parser.add_argument("--output", default="./generated/renders/cube_demo.mp4")
    parser.add_argument("--title", default="Rotating 3D Cube")
    parser.add_argument("--frames", type=int, default=90)
    parser.add_argument("--fps", type=int, default=30)
    return parser.parse_args(argv)


def main() -> None:
    if bpy is None:
        print("This script must be executed inside Blender's Python runtime.")
        sys.exit(1)

    args = parse_cli_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
    cube = bpy.context.active_object
    cube.rotation_euler = (0.0, 0.0, 0.0)
    cube.keyframe_insert(data_path="rotation_euler", frame=1)
    cube.rotation_euler = (math.tau * 0.5, 0.0, math.tau)
    cube.keyframe_insert(data_path="rotation_euler", frame=args.frames)

    bpy.ops.object.light_add(type="SUN", location=(6.0, -6.0, 8.0))
    bpy.ops.object.camera_add(location=(0.0, -7.0, 3.0))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(68), 0.0, 0.0)
    bpy.context.scene.camera = cam

    scene = bpy.context.scene
    scene.render.fps = args.fps
    scene.frame_start = 1
    scene.frame_end = args.frames
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    scene.render.filepath = os.path.abspath(args.output)
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()

