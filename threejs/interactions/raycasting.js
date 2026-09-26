import * as THREE from 'three';

/**
 * Raycasting and intersection helper utilities
 */

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

/**
 * Performs raycast intersection test from camera against an array of objects
 * @param {THREE.Vector2} normalizedCoords 
 * @param {THREE.Camera} camera 
 * @param {Array<THREE.Object3D>} objects 
 * @param {boolean} recursive 
 * @returns {Array<THREE.Intersection>}
 */
export function getRaycastIntersections(normalizedCoords, camera, objects, recursive = true) {
  mouse.set(normalizedCoords.x, normalizedCoords.y);
  raycaster.setFromCamera(mouse, camera);
  return raycaster.intersectObjects(objects, recursive);
}
