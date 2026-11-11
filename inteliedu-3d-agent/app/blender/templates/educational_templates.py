"""Parameterized educational Blender Python template builders."""

from __future__ import annotations

import json
from typing import Any, Dict

from app.api.schemas import SceneSpec


SOLAR_SYSTEM_PLANETS = [
    {"name": "Mercury", "radius": 0.28, "orbit": 3.4, "speed": 2.2, "spin": 0.4, "rgba": (0.62, 0.64, 0.68, 1.0)},
    {"name": "Venus", "radius": 0.44, "orbit": 4.9, "speed": 1.6, "spin": -0.2, "rgba": (0.95, 0.85, 0.55, 1.0)},
    {"name": "Earth", "radius": 0.48, "orbit": 6.6, "speed": 1.0, "spin": 2.0, "rgba": (0.20, 0.52, 0.92, 1.0)},
    {"name": "Mars", "radius": 0.35, "orbit": 8.3, "speed": 0.8, "spin": 1.8, "rgba": (0.86, 0.34, 0.24, 1.0)},
    {"name": "Jupiter", "radius": 1.05, "orbit": 11.2, "speed": 0.45, "spin": 4.0, "rgba": (0.88, 0.68, 0.44, 1.0)},
    {"name": "Saturn", "radius": 0.88, "orbit": 14.4, "speed": 0.32, "spin": 3.6, "rgba": (0.93, 0.82, 0.62, 1.0), "ring": True},
    {"name": "Uranus", "radius": 0.62, "orbit": 17.2, "speed": 0.22, "spin": -2.4, "rgba": (0.45, 0.85, 0.92, 1.0)},
    {"name": "Neptune", "radius": 0.60, "orbit": 19.8, "speed": 0.16, "spin": 2.2, "rgba": (0.24, 0.42, 0.92, 1.0)},
]


def build_template_body(scene: SceneSpec, total_frames: int, asset_path: str | None = None) -> str:
    """Return the Blender `build_educational_scene()` function body for the scene's template."""
    template = scene.template_name
    scene_json = json.dumps(scene.model_dump())

    if template == "rotating_cube":
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    bpy.ops.mesh.primitive_cube_add(size=2.4, location=(0.0, 0.0, 0.0))
    cube = bpy.context.active_object
    cube.name = "EducationalCube"
    mat = make_pbr_material("CubeMat", (0.22, 0.56, 0.95, 1.0), roughness=0.25, metallic=0.15)
    cube.data.materials.append(mat)
    animate_spin(cube, axis_index=2, turns=1.0, start_frame=1, end_frame={total_frames})
    animate_spin(cube, axis_index=0, turns=0.5, start_frame=1, end_frame={total_frames})
    add_text_label(SCENE_SPEC.get("title", "Rotating 3D Cube"), location=(0.0, 0.0, 2.2), size=0.42, name="SceneTitle")
    setup_camera_rig(location=(0.0, -7.5, 3.6), target=(0.0, 0.0, 0.2), movement=SCENE_SPEC.get("camera_movement", "static"), total_frames={total_frames})
'''

    if template == "geometrical_shapes":
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    shapes = [
        ("Cube", "cube", (-4.5, 0.0, 0.0), (0.20, 0.55, 0.95, 1.0)),
        ("Sphere", "sphere", (-1.5, 0.0, 0.0), (0.95, 0.42, 0.28, 1.0)),
        ("Cone", "cone", (1.5, 0.0, 0.0), (0.25, 0.80, 0.52, 1.0)),
        ("Cylinder", "cylinder", (4.5, 0.0, 0.0), (0.92, 0.72, 0.22, 1.0)),
    ]
    for label, kind, loc, rgba in shapes:
        if kind == "cube":
            bpy.ops.mesh.primitive_cube_add(size=1.5, location=loc)
        elif kind == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=loc)
        elif kind == "cone":
            bpy.ops.mesh.primitive_cone_add(radius1=0.85, depth=1.7, location=loc)
        else:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=1.7, location=loc)
        obj = bpy.context.active_object
        obj.name = f"Shape_{{label}}"
        obj.data.materials.append(make_pbr_material(f"Mat_{{label}}", rgba, roughness=0.3, metallic=0.1))
        animate_spin(obj, axis_index=2, turns=1.0, start_frame=1, end_frame={total_frames})
        add_text_label(label, location=(loc[0], 0.0, 1.45), size=0.36, name=f"Label_{{label}}")
    add_text_label(SCENE_SPEC.get("title", "Geometrical Shapes"), location=(0.0, 0.0, 2.8), size=0.48, name="TitleLabel")
    setup_camera_rig(location=(0.0, -11.5, 4.5), target=(0.0, 0.0, 0.5), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template == "solar_system":
        planets_json = json.dumps(SOLAR_SYSTEM_PLANETS)
        return f'''
SCENE_SPEC = {scene_json}
PLANETS = {planets_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("space")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8, segments=36, ring_count=20, location=(0.0, 0.0, 0.0))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.materials.append(make_pbr_material("SunMat", (1.0, 0.78, 0.18, 1.0), roughness=0.2, emission_rgba=(1.0, 0.62, 0.12, 1.0), emission_strength=4.5))
    animate_spin(sun, axis_index=2, turns=0.5, start_frame=1, end_frame={total_frames})
    add_text_label("Sun", location=(0.0, 0.0, 2.35), size=0.55, color=(1.0, 0.92, 0.6, 1.0), name="Label_Sun")

    for p in PLANETS:
        add_orbit_ring(p["orbit"], name=f"Orbit_{{p['name']}}")
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
        pivot = bpy.context.active_object
        pivot.name = f"Pivot_{{p['name']}}"
        bpy.ops.mesh.primitive_uv_sphere_add(radius=p["radius"], segments=24, ring_count=16, location=(p["orbit"], 0.0, 0.0))
        planet = bpy.context.active_object
        planet.name = p["name"]
        planet.parent = pivot
        planet.data.materials.append(make_pbr_material(f"Mat_{{p['name']}}", tuple(p["rgba"]), roughness=0.48))
        animate_spin(planet, axis_index=2, turns=max(0.4, abs(p["spin"])), start_frame=1, end_frame={total_frames})
        animate_orbit(pivot, turns=p["speed"] * 0.45, start_frame=1, end_frame={total_frames})
        label = add_text_label(p["name"], location=(p["orbit"], 0.0, p["radius"] + 0.65), size=0.40, name=f"Label_{{p['name']}}")
        label.parent = pivot
        if p.get("ring"):
            bpy.ops.mesh.primitive_torus_add(major_radius=p["radius"] * 1.75, minor_radius=0.07, location=(p["orbit"], 0.0, 0.0))
            ring = bpy.context.active_object
            ring.name = "Saturn_Rings"
            ring.scale = (1.0, 1.0, 0.12)
            ring.rotation_euler = (math.radians(18), 0.0, 0.0)
            ring.parent = pivot
            ring.data.materials.append(make_pbr_material("SaturnRingMat", (0.86, 0.78, 0.65, 1.0), roughness=0.55))

    add_text_label("Note: Planet sizes & orbital distances are not to scale", location=(0.0, 0.0, -4.5), size=0.48, color=(0.75, 0.88, 1.0, 1.0), name="ScaleDisclosure")
    setup_camera_rig(location=(0.0, -28.0, 14.5), target=(0.0, 0.0, 0.0), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template == "water_cycle":
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    # Ocean basin
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.5, 0.0, -0.5))
    ocean = bpy.context.active_object
    ocean.name = "Ocean"
    ocean.scale = (6.5, 5.5, 0.8)
    ocean.data.materials.append(make_pbr_material("OceanMat", (0.10, 0.48, 0.88, 1.0), roughness=0.15, alpha=0.88))

    # Land / Mountain slope
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=3.5, depth=3.8, location=(3.5, 0.0, 1.4))
    mountain = bpy.context.active_object
    mountain.name = "MountainTerrain"
    mountain.data.materials.append(make_pbr_material("MountainMat", (0.34, 0.56, 0.28, 1.0), roughness=0.75))

    # Sun heating source
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.95, location=(-5.5, 1.5, 5.5))
    sun = bpy.context.active_object
    sun.name = "SunSource"
    sun.data.materials.append(make_pbr_material("SunCycleMat", (1.0, 0.82, 0.20, 1.0), emission_rgba=(1.0, 0.72, 0.15, 1.0), emission_strength=3.5))

    # Rising evaporation vapor droplets
    for idx in range(5):
        x = -4.8 + idx * 0.7
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(x, 0.0, 0.3))
        vapor = bpy.context.active_object
        vapor.name = f"EvaporationVapor_{{idx+1}}"
        vapor.data.materials.append(make_pbr_material(f"VaporMat_{{idx}}", (0.72, 0.90, 1.0, 1.0), alpha=0.75))
        animate_linear_cycle(vapor, (x, 0.0, 0.3), (x + 0.8, 0.0, 4.0), start_frame=1, end_frame={total_frames})

    # Condensation Cloud cluster
    cloud_parts = [(-0.8, 0.0, 4.4, 0.95), (0.3, 0.2, 4.6, 1.1), (1.4, -0.1, 4.4, 0.95)]
    for idx, (cx, cy, cz, rad) in enumerate(cloud_parts):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rad, location=(cx, cy, cz))
        cloud = bpy.context.active_object
        cloud.name = f"CondensationCloud_{{idx+1}}"
        cloud.data.materials.append(make_pbr_material("CloudMat", (0.92, 0.95, 0.99, 1.0), roughness=0.85))
        animate_linear_cycle(cloud, (cx - 0.8, cy, cz), (cx + 2.2, cy, cz), start_frame=1, end_frame={total_frames})

    # Precipitation rain droplets falling onto mountain
    for idx in range(6):
        rx = 1.6 + idx * 0.45
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.35, location=(rx, 0.0, 3.8))
        drop = bpy.context.active_object
        drop.name = f"RainDrop_{{idx+1}}"
        drop.data.materials.append(make_pbr_material("RainMat", (0.25, 0.68, 0.98, 1.0), emission_rgba=(0.25, 0.68, 0.98, 1.0), emission_strength=0.4))
        animate_linear_cycle(drop, (rx, 0.0, 3.8), (rx, 0.0, 1.2), start_frame=1, end_frame={total_frames})

    add_text_label("Evaporation", location=(-3.6, 0.0, 2.2), size=0.42, name="Label_Evaporation")
    add_text_label("Condensation", location=(0.2, 0.0, 5.9), size=0.42, name="Label_Condensation")
    add_text_label("Precipitation", location=(3.2, 0.0, 3.9), size=0.42, name="Label_Precipitation")
    add_text_label("Collection & Runoff", location=(-0.5, 0.0, -1.4), size=0.38, name="Label_Collection")
    setup_camera_rig(location=(0.0, -15.5, 5.2), target=(0.0, 0.0, 2.0), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template == "anatomy_asset":
        safe_asset = (asset_path or "").replace("\\", "/")
        return f'''
SCENE_SPEC = {scene_json}
ASSET_GLB_PATH = {json.dumps(safe_asset)}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    imported_objects = []
    if ASSET_GLB_PATH and os.path.isfile(ASSET_GLB_PATH):
        bpy.ops.import_scene.gltf(filepath=ASSET_GLB_PATH)
        imported_objects = [obj for obj in bpy.context.selected_objects]
    if not imported_objects:
        # Procedural simplified cardiac anatomical fallback only if asset missing at execution
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0.0, 0.0, 0.2))
        heart = bpy.context.active_object
        heart.name = "Heart_Chambers"
        heart.scale = (0.95, 0.85, 1.25)
        heart.data.materials.append(make_pbr_material("HeartTissueMat", (0.82, 0.14, 0.18, 1.0), roughness=0.35))
        animate_pulse(heart, base_scale=1.0, amplitude=0.09, pulses=5, start_frame=1, end_frame={total_frames})
    else:
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 1.0))
        root = bpy.context.active_object
        root.name = "AnatomyRoot"
        for obj in imported_objects:
            if obj.parent is None:
                obj.parent = root
        animate_spin(root, axis_index=2, turns=0.4, start_frame=1, end_frame={total_frames})

    # Highlight marker near thoracic/heart center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(0.12, -0.25, 1.25))
    marker = bpy.context.active_object
    marker.name = "Heart_Focus_Marker"
    marker.data.materials.append(make_pbr_material("HeartMarkerMat", (0.95, 0.18, 0.22, 1.0), emission_rgba=(0.95, 0.15, 0.2, 1.0), emission_strength=1.5))
    animate_pulse(marker, base_scale=1.0, amplitude=0.22, pulses=6, start_frame=1, end_frame={total_frames})

    add_text_label(SCENE_SPEC.get("title", "Human Heart & Circulation"), location=(0.0, 0.0, 2.8), size=0.38, name="Title_Anatomy")
    add_text_label("Aorta & Four Chambers", location=(1.4, 0.0, 1.4), size=0.30, name="Label_Heart")
    setup_camera_rig(location=(0.0, -4.8, 1.7), target=(0.0, 0.0, 1.2), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template == "atomic_structure":
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("space")
    # Protons & Neutrons in Nucleus
    nucleon_offsets = [(0.15, 0.0, 0.0), (-0.15, 0.12, 0.08), (0.0, -0.15, 0.10), (0.05, 0.08, -0.14)]
    for idx, off in enumerate(nucleon_offsets):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=off)
        nuc = bpy.context.active_object
        nuc.name = f"Nucleon_{{idx+1}}"
        rgba = (0.92, 0.25, 0.22, 1.0) if idx % 2 == 0 else (0.65, 0.72, 0.85, 1.0)
        nuc.data.materials.append(make_pbr_material(f"NucleonMat_{{idx}}", rgba, roughness=0.3))

    # Electron shells
    for shell_idx, radius in enumerate((2.2, 3.8)):
        ring = add_orbit_ring(radius, color=(0.30, 0.72, 0.98, 1.0), name=f"ElectronShell_{{shell_idx+1}}")
        ring.rotation_euler = (math.radians(35 * shell_idx), math.radians(20 * shell_idx), 0.0)
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
        pivot = bpy.context.active_object
        pivot.name = f"ElectronPivot_{{shell_idx+1}}"
        pivot.rotation_euler = ring.rotation_euler
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(radius, 0.0, 0.0))
        elec = bpy.context.active_object
        elec.name = f"Electron_{{shell_idx+1}}"
        elec.parent = pivot
        elec.data.materials.append(make_pbr_material(f"ElectronMat_{{shell_idx}}", (0.20, 0.85, 1.0, 1.0), emission_rgba=(0.2, 0.85, 1.0, 1.0), emission_strength=2.5))
        animate_orbit(pivot, turns=1.5 + shell_idx * 0.5, start_frame=1, end_frame={total_frames})

    add_text_label("Nucleus (Protons + Neutrons)", location=(0.0, 0.0, 1.0), size=0.35, name="Label_Nucleus")
    add_text_label("Orbiting Electrons", location=(2.6, 0.0, 1.8), size=0.35, name="Label_Electrons")
    setup_camera_rig(location=(0.0, -10.5, 4.2), target=(0.0, 0.0, 0.0), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template == "photosynthesis":
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    # Stem & Leaf
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=3.2, location=(0.0, 0.0, 0.0))
    stem = bpy.context.active_object
    stem.name = "PlantStem"
    stem.data.materials.append(make_pbr_material("StemMat", (0.22, 0.62, 0.25, 1.0), roughness=0.6))

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.4, location=(1.1, 0.0, 0.8))
    leaf = bpy.context.active_object
    leaf.name = "ChlorophyllLeaf"
    leaf.scale = (1.6, 0.75, 0.14)
    leaf.rotation_euler = (0.0, math.radians(-18), 0.0)
    leaf.data.materials.append(make_pbr_material("LeafMat", (0.16, 0.75, 0.28, 1.0), roughness=0.4))

    # Sun light source
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(-3.5, 0.0, 4.2))
    sun = bpy.context.active_object
    sun.name = "Sunlight"
    sun.data.materials.append(make_pbr_material("PhotosynSunMat", (1.0, 0.85, 0.2, 1.0), emission_rgba=(1.0, 0.8, 0.1, 1.0), emission_strength=3.5))

    # CO2 intake & O2 release markers
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(-2.5, 0.0, 1.2))
    co2 = bpy.context.active_object
    co2.name = "CO2_Molecule"
    co2.data.materials.append(make_pbr_material("CO2Mat", (0.65, 0.70, 0.78, 1.0)))
    animate_linear_cycle(co2, (-2.8, 0.0, 1.2), (0.8, 0.0, 0.85), start_frame=1, end_frame={total_frames})

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(1.5, 0.0, 1.2))
    o2 = bpy.context.active_object
    o2.name = "Oxygen_Release"
    o2.data.materials.append(make_pbr_material("O2Mat", (0.25, 0.85, 0.98, 1.0), emission_rgba=(0.25, 0.85, 0.98, 1.0), emission_strength=1.2))
    animate_linear_cycle(o2, (1.2, 0.0, 0.9), (3.4, 0.0, 2.8), start_frame=1, end_frame={total_frames})

    add_text_label("Sunlight + CO2 + Water -> Glucose + O2", location=(0.0, 0.0, 3.1), size=0.38, name="Label_Equation")
    setup_camera_rig(location=(0.0, -10.5, 3.2), target=(0.0, 0.0, 1.0), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    if template in ("electric_circuits", "volcano_formation"):
        # Parameterized STEM layout for circuits / volcano
        is_circuit = template == "electric_circuits"
        title = "Closed Electric Circuit" if is_circuit else "Volcano Formation & Eruption"
        return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    if {is_circuit}:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.3, location=(-2.6, 0.0, 0.4))
        bat = bpy.context.active_object
        bat.name = "BatterySource"
        bat.data.materials.append(make_pbr_material("BatteryMat", (0.95, 0.65, 0.15, 1.0), metallic=0.4))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(2.6, 0.0, 0.7))
        bulb = bpy.context.active_object
        bulb.name = "LightBulb"
        bulb.data.materials.append(make_pbr_material("BulbMat", (1.0, 0.94, 0.45, 1.0), emission_rgba=(1.0, 0.88, 0.25, 1.0), emission_strength=3.0))
        add_orbit_ring(2.6, color=(0.85, 0.45, 0.15, 1.0), name="CopperWireLoop")
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(2.6, 0.0, 0.0))
        charge = bpy.context.active_object
        charge.name = "CurrentCarrier"
        charge.data.materials.append(make_pbr_material("ChargeMat", (0.2, 0.85, 1.0, 1.0), emission_rgba=(0.2, 0.85, 1.0, 1.0), emission_strength=2.0))
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0.0, 0.0, 0.0))
        piv = bpy.context.active_object
        charge.parent = piv
        animate_orbit(piv, turns=2.0, start_frame=1, end_frame={total_frames})
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=3.2, radius2=0.65, depth=3.2, location=(0.0, 0.0, 1.6))
        cone = bpy.context.active_object
        cone.name = "VolcanoCone"
        cone.data.materials.append(make_pbr_material("RockMat", (0.32, 0.24, 0.20, 1.0), roughness=0.85))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0.0, 0.0, 0.35))
        magma = bpy.context.active_object
        magma.name = "MagmaChamber"
        magma.data.materials.append(make_pbr_material("MagmaMat", (1.0, 0.28, 0.05, 1.0), emission_rgba=(1.0, 0.25, 0.02, 1.0), emission_strength=3.5))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0.0, 0.0, 3.1))
        lava = bpy.context.active_object
        lava.name = "CraterEruption"
        lava.data.materials.append(make_pbr_material("LavaMat", (1.0, 0.38, 0.05, 1.0), emission_rgba=(1.0, 0.35, 0.04, 1.0), emission_strength=4.0))
        animate_linear_cycle(lava, (0.0, 0.0, 2.8), (0.0, 0.0, 5.2), start_frame=1, end_frame={total_frames})

    add_text_label("{title}", location=(0.0, 0.0, 3.9), size=0.44, name="Label_Main")
    setup_camera_rig(location=(0.0, -11.5, 4.2), target=(0.0, 0.0, 1.2), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

    # Generic STEM educational diagram generator driven by SceneSpec.objects & labels
    return f'''
SCENE_SPEC = {scene_json}

def build_educational_scene():
    clear_scene()
    setup_lighting("studio")
    objs = SCENE_SPEC.get("objects") or ["Core Concept", "Mechanism", "Outcome"]
    palette = [
        (0.22, 0.58, 0.96, 1.0),
        (0.20, 0.80, 0.56, 1.0),
        (0.95, 0.62, 0.20, 1.0),
        (0.82, 0.34, 0.62, 1.0),
    ]
    count = min(len(objs), 6)
    spacing = 2.8
    start_x = -0.5 * (count - 1) * spacing
    for idx in range(count):
        name = str(objs[idx])
        x = start_x + idx * spacing
        if idx % 3 == 0:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.85, location=(x, 0.0, 0.0))
        elif idx % 3 == 1:
            bpy.ops.mesh.primitive_cube_add(size=1.45, location=(x, 0.0, 0.0))
        else:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=1.5, location=(x, 0.0, 0.0))
        node = bpy.context.active_object
        node.name = f"Concept_{{idx+1}}"
        node.data.materials.append(make_pbr_material(f"ConceptMat_{{idx+1}}", palette[idx % len(palette)], roughness=0.35))
        animate_spin(node, axis_index=2, turns=0.75, start_frame=1, end_frame={total_frames})
        add_text_label(name, location=(x, 0.0, 1.45), size=0.34, name=f"Label_{{idx+1}}")

    add_text_label(SCENE_SPEC.get("title", "Educational 3D Scene"), location=(0.0, 0.0, 2.9), size=0.45, name="Label_SceneTitle")
    setup_camera_rig(location=(0.0, -12.0, 4.4), target=(0.0, 0.0, 0.5), movement=SCENE_SPEC.get("camera_movement", "smooth_orbit"), total_frames={total_frames})
'''

