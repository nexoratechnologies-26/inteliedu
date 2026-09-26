import * as THREE from 'three';

/**
 * Camera utility functions for framing objects, computing bounding spheres, and animating viewpoints
 */

/**
 * Calculates the optimal camera distance to frame a 3D object/model
 * @param {THREE.Object3D} object 
 * @param {number} fov Field of view in degrees (default 45)
 * @param {number} fitOffset Multiplier padding factor (default 1.25)
 * @returns {{ distance: number, center: THREE.Vector3, box: THREE.Box3, size: THREE.Vector3 }}
 */
export function calculateObjectBounds(object, fov = 45, fitOffset = 1.25) {
  const box = new THREE.Box3().setFromObject(object);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  
  box.getSize(size);
  box.getCenter(center);

  const maxSize = Math.max(size.x, size.y, size.z);
  const fovRad = (fov * Math.PI) / 180;
  let distance = maxSize / (2 * Math.tan(fovRad / 2));
  distance *= fitOffset;

  return { distance, center, box, size };
}

/**
 * Standard camera position presets
 */
export const CAMERA_PRESETS = {
  perspective: [0, 2, 5],
  isometric: [5, 5, 5],
  top: [0, 8, 0],
  front: [0, 0, 6],
  side: [6, 0, 0],
  closeUp: [0, 0.5, 2.5],
};
