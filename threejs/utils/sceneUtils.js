import * as THREE from 'three';

/**
 * Scene utility functions for memory management, lighting presets, and environment setup
 */

/**
 * Recursively disposes of a Three.js object, geometry, and material to prevent WebGL memory leaks
 * @param {THREE.Object3D} obj
 */
export function disposeObjectTree(obj) {
  if (!obj) return;

  obj.traverse((child) => {
    if (child.geometry) {
      child.geometry.dispose();
    }

    if (child.material) {
      if (Array.isArray(child.material)) {
        child.material.forEach((mat) => disposeMaterial(mat));
      } else {
        disposeMaterial(child.material);
      }
    }
  });
}

/**
 * Disposes of a single Three.js material and associated texture maps
 * @param {THREE.Material} mat
 */
export function disposeMaterial(mat) {
  if (!mat) return;
  
  // Dispose all possible texture maps
  const textureKeys = [
    'map', 'roughnessMap', 'metalnessMap', 'normalMap', 
    'bumpMap', 'displacementMap', 'alphaMap', 'emissiveMap', 
    'aoMap', 'envMap', 'lightMap'
  ];

  textureKeys.forEach((key) => {
    if (mat[key] && typeof mat[key].dispose === 'function') {
      mat[key].dispose();
    }
  });

  if (typeof mat.dispose === 'function') {
    mat.dispose();
  }
}

/**
 * Lighting presets tailored for different educational scene genres
 */
export const LIGHTING_PRESETS = {
  studio: {
    ambient: { color: '#ffffff', intensity: 0.8 },
    directional: [
      { position: [10, 15, 10], intensity: 1.5, castShadow: true },
      { position: [-10, 10, -10], intensity: 0.5, castShadow: false },
    ],
    point: [{ position: [0, 5, 0], intensity: 0.8, color: '#93c5fd' }],
  },
  space: {
    ambient: { color: '#1e1b4b', intensity: 0.2 },
    directional: [
      { position: [0, 0, 0], intensity: 3.0, color: '#fef08a', castShadow: true }, // Sun central light
    ],
    point: [{ position: [0, 0, 0], intensity: 2.0, color: '#ffffff' }],
  },
  laboratory: {
    ambient: { color: '#f8fafc', intensity: 1.0 },
    directional: [
      { position: [5, 10, 7], intensity: 1.2, castShadow: true },
      { position: [-5, -5, -5], intensity: 0.4, castShadow: false },
    ],
    point: [],
  },
};
