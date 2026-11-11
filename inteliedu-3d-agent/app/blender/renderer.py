"""Blender render configuration generator supporting EEVEE/Cycles and MP4/GLB output."""

from __future__ import annotations


BLENDER_RENDERER_SNIPPET = '''
def configure_and_render(output_mp4_path, width=1280, height=720, fps=30, total_frames=120, samples=16, preferred_engine="BLENDER_EEVEE_NEXT", export_glb_path=None):
    scene = bpy.context.scene
    available_engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    if preferred_engine in available_engines:
        scene.render.engine = preferred_engine
    elif "BLENDER_EEVEE_NEXT" in available_engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in available_engines:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = "CYCLES"

    if scene.render.engine == "CYCLES":
        scene.cycles.samples = samples
    elif hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples

    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.resolution_percentage = 100
    scene.render.fps = int(fps)
    scene.frame_start = 1
    scene.frame_end = int(total_frames)

    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.filepath = output_mp4_path

    if export_glb_path:
        os.makedirs(os.path.dirname(export_glb_path), exist_ok=True)
        try:
            bpy.ops.export_scene.gltf(filepath=export_glb_path, export_format="GLB")
        except Exception as glb_exc:
            print(f"[Inteliedu Blender] Optional GLB export skipped: {glb_exc}")

    bpy.ops.render.render(animation=True)
    print(f"[Inteliedu Blender] Rendered MP4 successfully to {output_mp4_path}")
'''

