/**
 * Interaction and pointer event handlers for 3D viewports
 */

/**
 * Normalizes touch and pointer event coordinates for raycasting
 * @param {PointerEvent|TouchEvent} event 
 * @param {HTMLElement} domElement 
 * @returns {{ x: number, y: number }} Normalized device coordinates (-1 to +1)
 */
export function getNormalizedPointerCoordinates(event, domElement) {
  const rect = domElement.getBoundingClientRect();
  const clientX = event.clientX || (event.touches && event.touches[0]?.clientX) || 0;
  const clientY = event.clientY || (event.touches && event.touches[0]?.clientY) || 0;

  return {
    x: ((clientX - rect.left) / rect.width) * 2 - 1,
    y: -((clientY - rect.top) / rect.height) * 2 + 1,
  };
}
