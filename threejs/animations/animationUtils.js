/**
 * Mathematical utilities for procedural 3D educational animations
 */

/**
 * Computes orbital 3D Cartesian coordinates from polar orbit radius and angle
 * @param {number} radius Orbit distance
 * @param {number} angle Current orbital radian
 * @param {number} inclination Incline angle in radians (default 0)
 * @returns {[number, number, number]} [x, y, z]
 */
export function calculateOrbitPosition(radius, angle, inclination = 0) {
  const x = Math.cos(angle) * radius;
  const z = Math.sin(angle) * radius;
  const y = Math.sin(angle) * radius * Math.sin(inclination);
  return [x, y, z];
}

/**
 * Ease in-out quadratic interpolation
 * @param {number} t Normalized time (0 to 1)
 */
export function easeInOutQuad(t) {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}
