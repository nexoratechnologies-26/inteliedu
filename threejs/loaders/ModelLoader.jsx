import React, { useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import { normalizeModelTransform } from '../utils/modelUtils.js';

/**
 * Robust GLTF/GLB 3D Model Loader
 * Loads, clones, enables shadows, and wires raycast part selection for external educational 3D models
 */
export default function ModelLoader({
  url,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  autoCenter = true,
  targetBoundingSize = 3,
  onSelectPart = null,
  selectedPartId = null,
  wireframe = false,
}) {
  const { scene } = useGLTF(url);

  // Clone scene so multiple instances don't mutate shared scene graph
  const clonedScene = useMemo(() => {
    const clone = scene.clone(true);

    if (autoCenter) {
      normalizeModelTransform(clone, targetBoundingSize);
    }

    clone.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;

        if (wireframe && child.material) {
          if (Array.isArray(child.material)) {
            child.material = child.material.map((m) => {
              const wm = m.clone();
              wm.wireframe = true;
              return wm;
            });
          } else {
            const wm = child.material.clone();
            wm.wireframe = true;
            child.material = wm;
          }
        }
      }
    });

    return clone;
  }, [scene, autoCenter, targetBoundingSize, wireframe]);

  const handlePointerDown = (e) => {
    e.stopPropagation();
    if (onSelectPart && e.object) {
      const mesh = e.object;
      onSelectPart({
        id: mesh.userData?.id || mesh.name?.toLowerCase().replace(/\s+/g, '-') || `part-${mesh.id}`,
        name: mesh.name || `3D Part #${mesh.id}`,
        description: mesh.userData?.description || `Inspecting structural element: ${mesh.name || 'Component'}`,
        category: mesh.userData?.category || '3D Component',
        modelPath: url,
        metadata: {
          vertices: mesh.geometry?.attributes?.position?.count || 0,
          material: mesh.material?.name || 'Standard',
        },
      });
    }
  };

  return (
    <primitive
      object={clonedScene}
      scale={scale}
      position={position}
      rotation={rotation}
      onPointerDown={handlePointerDown}
      onPointerOver={(e) => {
        e.stopPropagation();
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={(e) => {
        e.stopPropagation();
        document.body.style.cursor = 'auto';
      }}
    />
  );
}
