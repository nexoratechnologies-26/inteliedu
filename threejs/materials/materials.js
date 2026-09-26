import * as THREE from 'three';

/**
 * Reusable PBR Materials, Highlighting Shaders & Educational Overlays
 */

export const THEME_COLORS = {
  selected: '#38bdf8',       // Bright cyan glow
  hover: '#818cf8',          // Light indigo highlight
  neutral: '#475569',        // Slate neutral
  accent: '#a855f7',         // Purple accent
  warning: '#f59e0b',        // Amber alert
  success: '#10b981',        // Emerald success
  wireframe: '#38bdf8',      // Cyan wireframe
};

/**
 * Creates a cloned material with selection emissive highlight
 * @param {THREE.Material} baseMaterial 
 * @param {string} highlightColor 
 * @param {number} intensity 
 */
export function createHighlightMaterial(baseMaterial, highlightColor = THEME_COLORS.hover, intensity = 0.4) {
  if (!baseMaterial) {
    return new THREE.MeshStandardMaterial({
      color: '#64748b',
      emissive: highlightColor,
      emissiveIntensity: intensity,
      roughness: 0.3,
      metalness: 0.2,
    });
  }

  const cloned = baseMaterial.clone();
  if (cloned.emissive) {
    cloned.emissive.set(highlightColor);
    cloned.emissiveIntensity = intensity;
  }
  return cloned;
}

/**
 * Standard Educational Material Presets
 */
export const MATERIAL_PRESETS = {
  metal: new THREE.MeshStandardMaterial({
    color: '#94a3b8',
    metalness: 0.8,
    roughness: 0.2,
  }),
  plastic: new THREE.MeshStandardMaterial({
    color: '#3b82f6',
    metalness: 0.1,
    roughness: 0.4,
  }),
  glass: new THREE.MeshPhysicalMaterial({
    color: '#ffffff',
    transparent: true,
    opacity: 0.4,
    roughness: 0.1,
    transmission: 0.9,
    thickness: 1.2,
  }),
  glowSun: new THREE.MeshBasicMaterial({
    color: '#fde047',
  }),
  xray: new THREE.MeshStandardMaterial({
    color: '#0284c7',
    transparent: true,
    opacity: 0.35,
    wireframe: false,
    roughness: 0.1,
  }),
};
