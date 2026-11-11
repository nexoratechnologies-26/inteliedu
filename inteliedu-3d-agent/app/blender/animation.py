"""Reusable Blender keyframe animation helpers."""

from __future__ import annotations


BLENDER_ANIMATION_SNIPPET = '''
def set_linear_interpolation(obj):
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"


def animate_spin(obj, axis_index=2, turns=1.0, start_frame=1, end_frame=120):
    obj.rotation_euler = list(obj.rotation_euler)
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
    rot = list(obj.rotation_euler)
    rot[axis_index] += math.tau * turns
    obj.rotation_euler = rot
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    set_linear_interpolation(obj)


def animate_orbit(pivot_obj, turns=1.0, start_frame=1, end_frame=120):
    pivot_obj.rotation_euler = (0.0, 0.0, 0.0)
    pivot_obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
    pivot_obj.rotation_euler = (0.0, 0.0, math.tau * turns)
    pivot_obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    set_linear_interpolation(pivot_obj)


def animate_linear_cycle(obj, start_pos, end_pos, start_frame=1, end_frame=120):
    obj.location = start_pos
    obj.keyframe_insert(data_path="location", frame=start_frame)
    obj.location = end_pos
    obj.keyframe_insert(data_path="location", frame=end_frame)
    set_linear_interpolation(obj)


def animate_pulse(obj, base_scale=1.0, amplitude=0.12, pulses=4, start_frame=1, end_frame=120):
    step = max(2, int((end_frame - start_frame) / (pulses * 2)))
    frame = start_frame
    expand = True
    while frame <= end_frame:
        s = base_scale * (1.0 + amplitude if expand else 1.0)
        obj.scale = (s, s, s)
        obj.keyframe_insert(data_path="scale", frame=frame)
        expand = not expand
        frame += step
'''

