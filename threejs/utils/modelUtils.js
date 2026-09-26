import * as THREE from 'three';

/**
 * 3D Model utility functions for geometry normalization, bounding box centering, and mesh cloning
 */

/**
 * Normalizes a loaded 3D model: centers its pivot and scales it to fit within a target bounding radius
 * @param {THREE.Object3D} model 
 * @param {number} targetSize Target maximum bounding box dimension
 */
export function normalizeModelTransform(model, targetSize = 3) {
  if (!model) return;

  const box = new THREE.Box3().setFromObject(model);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();

  box.getSize(size);
  box.getCenter(center);

  // Center model origin
  model.position.x -= center.x;
  model.position.y -= center.y;
  model.position.z -= center.z;

  // Compute scale factor
  const maxAxis = Math.max(size.x, size.y, size.z);
  if (maxAxis > 0) {
    const scaleFactor = targetSize / maxAxis;
    model.scale.multiplyScalar(scaleFactor);
  }
}

/**
 * Traverses a model to extract interactive mesh parts and attach metadata
 * @param {THREE.Object3D} model 
 * @returns {Array<{ name: string, uuid: string, isMesh: boolean }>}
 */
export function extractModelParts(model) {
  const parts = [];
  if (!model) return parts;

  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      parts.push({
        name: child.name || `Part_${child.id}`,
        uuid: child.uuid,
        id: child.userData?.id || child.name?.toLowerCase().replace(/\s+/g, '-') || `part-${child.id}`,
        category: child.userData?.category || 'component',
        description: child.userData?.description || `Interactive 3D part: ${child.name || child.id}`,
      });
    }
  });

  return parts;
}
