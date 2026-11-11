"""Common Blender scene bootstrap, label placement, and orbit ring utilities."""

from __future__ import annotations


BLENDER_COMMON_SNIPPET = '''
import bpy
import math
import os
import json

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def add_text_label(text, location=(0.0, 0.0, 1.5), size=0.45, color=(0.95, 0.97, 1.0, 1.0), name="Label"):
    bpy.ops.object.text_add(location=location)
    txt = bpy.context.active_object
    txt.name = name
    txt.data.body = str(text)
    txt.data.size = size
    txt.data.align_x = "CENTER"
    txt.rotation_euler = (math.radians(78), 0.0, 0.0)
    mat = make_pbr_material(f"{name}_Mat", color, roughness=0.3, emission_rgba=color, emission_strength=0.6)
    txt.data.materials.append(mat)
    return txt

def add_orbit_ring(radius, color=(0.45, 0.55, 0.75, 1.0), name="OrbitRing"):
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=(0.0, 0.0, 0.0))
    ring = bpy.context.active_object
    ring.name = name
    ring.data.bevel_depth = 0.025
    mat = make_pbr_material(f"{name}_Mat", color, roughness=0.4, emission_rgba=color, emission_strength=0.25)
    ring.data.materials.append(mat)
    return ring
'''

