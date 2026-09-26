import { useGLTF } from '@react-three/drei';

/**
 * Utility functions for GLTF/GLB asset loading and caching
 */

/**
 * Preloads a GLTF/GLB model into Drei's memory cache
 * @param {string} url 
 */
export function preloadModel(url) {
  if (url && typeof url === 'string') {
    useGLTF.preload(url);
  }
}

/**
 * Clears a model from Drei's memory cache
 * @param {string} url 
 */
export function clearModelCache(url) {
  if (url && typeof url === 'string') {
    useGLTF.clear(url);
  }
}
