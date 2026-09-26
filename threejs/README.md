# 3D Graphics & WebGL Architecture (`threejs/`)

**Domain Owner**: Trivin (3D Developer)

## Overview
This module houses all 3D WebGL assets, React Three Fiber (R3F) scene graphs, procedural animations, camera controls, custom shaders, and interactive annotation systems for Inteliedu.

---

## Directory Organization

```
threejs/
├── components/         # Reusable R3F canvas components (CanvasWrapper, LightingRig, Environment)
├── scenes/             # Domain-specific 3D scenes (SolarSystemScene, AnatomyScene, EngineScene)
├── models/             # 3D model metadata, configs, and local low-poly previews
│   ├── solar-system/   # Planetary bodies, orbit rings, celestial textures
│   ├── human-anatomy/  # Skeletal, cardiovascular, organ system models
│   └── engineering/    # Mechanical engines, bridge structures, aerodynamic models
├── animations/         # Keyframe timelines, orbit rotations, camera tweening
├── controls/           # Orbit controls, first-person inspect controls, gizmos
├── materials/          # Custom Three.js shaders, PBR materials, x-ray translucent shaders
├── loaders/            # GLTF/GLB loaders with DRACO/KTX2 compression support
├── interactions/       # Raycasting, hover outlines, exploded-view part selectors
├── labels/             # 2D/3D HTML label overlays and info pin billboard helpers
├── utils/              # Math helpers, coordinate transforms, memory cleanup / disposal
└── README.md
```

---

## Integration Contracts
- **React Embedding**: 3D scene components in `scenes/` are exported as React components with standard prop signatures:
  ```jsx
  <InteractiveScene
    modelUrl={modelUrl}
    activeHotspotId={selectedId}
    onHotspotSelect={(id) => handleSelect(id)}
    isExploded={explodedState}
  />
  ```
- **Performance Guidelines**:
  - Target 60 FPS across desktop hardware.
  - Automatically dispose of textures, geometries, and materials upon unmounting.
  - Fetch full `.glb` binaries from Supabase Storage CDN rather than committing large binaries to git.
