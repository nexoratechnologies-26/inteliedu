"""
Standalone GLB Asset Preview Renderer for Inteliedu existing 3D models.
Run inside Blender:
    blender --background --python blender_scripts/render_glb_preview.py -- --glb ../frontend/public/assets/models/real_human_anatomy.glb --output preview.mp4
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
    parser = argparse.ArgumentParser(description="Render orbital video from an existing GLB asset")
    parser.add_argument("--glb", required=True, help="Path to input .glb/.gltf model")
    parser.add_argument("--output", required=True, help="Output MP4 file path")
    parser.add_argument("--frames", type=int, default=120)
    return parser.parse_args(argv)


def main() -> None:
    if bpy is None:
        print("This script must be executed inside Blender's Python runtime.")
        sys.exit(1)

    args = parse_cli_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 1.0))
    rig = bpy.context.active_object
    bpy.ops.object.camera_add(location=(0.0, -4.5, 1.6))
    cam = bpy.context.active_object
    cam.parent = rig
    track = cam.constraints.new(type="TRACK_TO")
    track.target = rig
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=1)
    rig.rotation_euler = (0.0, 0.0, math.tau * 0.5)
    rig.keyframe_insert(data_path="rotation_euler", frame=args.frames)

    bpy.ops.object.light_add(type="SUN", location=(6.0, -6.0, 10.0))
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = args.frames
    scene.render.fps = 30
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

