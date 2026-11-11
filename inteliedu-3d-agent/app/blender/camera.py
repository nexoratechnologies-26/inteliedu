"""Reusable Blender camera rig and lighting setup generators."""

from __future__ import annotations


BLENDER_CAMERA_SNIPPET = '''
def setup_lighting(preset="studio"):
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("IntelieduWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        if preset == "space":
            bg.inputs[0].default_value = (0.015, 0.02, 0.045, 1.0)
            bg.inputs[1].default_value = 0.8
        else:
            bg.inputs[0].default_value = (0.08, 0.11, 0.18, 1.0)
            bg.inputs[1].default_value = 1.0

    bpy.ops.object.light_add(type="SUN", location=(8.0, -8.0, 12.0))
    sun = bpy.context.active_object
    sun.name = "KeySunLight"
    sun.data.energy = 3.0 if preset != "space" else 2.2
    sun.rotation_euler = (math.radians(45), 0.0, math.radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-7.0, 7.0, 6.0))
    fill = bpy.context.active_object
    fill.name = "FillAreaLight"
    fill.data.energy = 180.0
    fill.data.size = 6.0


def setup_camera_rig(location=(0.0, -14.0, 6.0), target=(0.0, 0.0, 0.0), movement="smooth_orbit", total_frames=120):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=target)
    rig = bpy.context.active_object
    rig.name = "CameraTargetRig"

    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = "EducationalCamera"
    cam.parent = rig

    track = cam.constraints.new(type="TRACK_TO")
    track.target = rig
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=1)
    if "orbit" in movement.lower():
        rig.rotation_euler = (0.0, 0.0, math.radians(55.0))
        rig.keyframe_insert(data_path="rotation_euler", frame=total_frames)
    elif "zoom" in movement.lower():
        cam.location = location
        cam.keyframe_insert(data_path="location", frame=1)
        cam.location = (location[0] * 0.65, location[1] * 0.65, location[2] * 0.7)
        cam.keyframe_insert(data_path="location", frame=total_frames)
    elif "pan" in movement.lower():
        rig.location = (-1.5, 0.0, 0.0)
        rig.keyframe_insert(data_path="location", frame=1)
        rig.location = (1.5, 0.0, 0.0)
        rig.keyframe_insert(data_path="location", frame=total_frames)
    return cam, rig
'''

