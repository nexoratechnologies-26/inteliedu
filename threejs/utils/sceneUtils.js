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
 * Lighting presets tailored for Light and Dark themes
 */
export const LIGHTING_PRESETS = {
  studio: {
    ambient: { color: '#ffffff', intensity: 1.2 },
    directional: [
      { position: [8, 12, 8], intensity: 1.8, castShadow: true, color: '#ffffff' },
      { position: [-8, 8, -6], intensity: 0.8, castShadow: false, color: '#e0f2fe' },
    ],
    point: [{ position: [0, 4, 3], intensity: 0.6, color: '#ffffff' }],
  },
  laboratory: {
    ambient: { color: '#f8fafc', intensity: 1.4 },
    directional: [
      { position: [6, 12, 8], intensity: 1.6, castShadow: true, color: '#ffffff' },
      { position: [-6, -4, -4], intensity: 0.6, castShadow: false, color: '#bae6fd' },
    ],
    point: [{ position: [0, 2, 4], intensity: 0.8, color: '#38bdf8' }],
  },
  space: {
    ambient: { color: '#1e293b', intensity: 0.4 },
    directional: [
      { position: [0, 0, 0], intensity: 3.5, color: '#fef08a', castShadow: true },
    ],
    point: [{ position: [0, 0, 0], intensity: 2.5, color: '#ffffff' }],
  },
};
