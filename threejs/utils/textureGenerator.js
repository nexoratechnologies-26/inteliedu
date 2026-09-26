import * as THREE from 'three';

/**
 * Procedural Canvas Texture Generator
 * Generates dynamic, high-resolution procedural textures for planetary bodies,
 * biological tissues, and engineering metals with zero external asset dependencies.
 */

/**
 * Creates a procedural noise canvas texture
 */
function createNoiseCanvas(width, height, colorFn) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  const imgData = ctx.createImageData(width, height);
  const data = imgData.data;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const [r, g, b, a] = colorFn(x / width, y / height);
      data[idx] = r;
      data[idx + 1] = g;
      data[idx + 2] = b;
      data[idx + 3] = a !== undefined ? a : 255;
    }
  }

  ctx.putImageData(imgData, 0, 0);
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  return texture;
}

/**
 * Procedural Sun Texture (Solar flares & granulation)
 */
export function generateSunTexture() {
  return createNoiseCanvas(512, 256, (u, v) => {
    const n1 = Math.sin(u * 20) * Math.cos(v * 20);
    const n2 = Math.sin(u * 40 + v * 40) * 0.5;
    const val = 0.5 + 0.3 * n1 + 0.2 * n2;
    const r = 255;
    const g = Math.floor(180 * val + 50);
    const b = Math.floor(40 * val);
    return [r, g, b, 255];
  });
}

/**
 * Procedural Earth Texture (Oceans, Continents, Clouds)
 */
export function generateEarthTexture() {
  return createNoiseCanvas(1024, 512, (u, v) => {
    const lat = (v - 0.5) * Math.PI;
    const lon = u * Math.PI * 2;
    // Multi-octave sinusoidal continents approximation
    const continent = 
      Math.sin(lon * 3 + Math.sin(lat * 4)) * 0.4 +
      Math.sin(lon * 6 - lat * 5) * 0.3 +
      Math.cos(lat * 3) * 0.3;

    // Polar ice caps
    if (Math.abs(v - 0.5) > 0.42) {
      return [240, 248, 255, 255]; // Polar white
    }

    if (continent > 0.15) {
      // Land / Continents
      const elevation = (continent - 0.15) * 3;
      const r = Math.floor(34 + elevation * 40);
      const g = Math.floor(120 + elevation * 30);
      const b = Math.floor(45 + elevation * 20);
      return [r, g, b, 255];
    } else if (continent > 0.08) {
      // Coastlines / Sand
      return [194, 178, 128, 255];
    } else {
      // Ocean / Deep waters
      const depth = Math.max(0, 0.08 - continent) * 2;
      const r = Math.floor(10 + depth * 10);
      const g = Math.floor(50 + depth * 40);
      const b = Math.floor(140 + depth * 60);
      return [r, g, b, 255];
    }
  });
}

/**
 * Procedural Jupiter Bands Texture
 */
export function generateJupiterTexture() {
  return createNoiseCanvas(512, 256, (u, v) => {
    const band = Math.sin(v * 30 + Math.sin(u * 10) * 0.3) * 0.5 + 0.5;
    const stormDist = Math.hypot(u - 0.65, v - 0.65);
    const isGreatRedSpot = stormDist < 0.08;

    if (isGreatRedSpot) {
      return [200, 70, 40, 255];
    }

    const r = Math.floor(190 + band * 45);
    const g = Math.floor(140 + band * 35);
    const b = Math.floor(100 + band * 25);
    return [r, g, b, 255];
  });
}

/**
 * Procedural Mars Rust Texture
 */
export function generateMarsTexture() {
  return createNoiseCanvas(512, 256, (u, v) => {
    // Polar Caps
    if (Math.abs(v - 0.5) > 0.45) {
      return [245, 245, 255, 255];
    }
    const noise = Math.sin(u * 15) * Math.cos(v * 15) * 0.3 + 0.7;
    const r = Math.floor(185 * noise + 30);
    const g = Math.floor(75 * noise + 20);
    const b = Math.floor(40 * noise + 10);
    return [r, g, b, 255];
  });
}

/**
 * Procedural Moon Craters Texture
 */
export function generateMoonTexture() {
  return createNoiseCanvas(512, 256, (u, v) => {
    const noise = (Math.sin(u * 25) * Math.sin(v * 25) + Math.cos(u * 50 + v * 30) * 0.5) * 0.3 + 0.7;
    const grey = Math.floor(160 * noise);
    return [grey, grey, grey, 255];
  });
}

/**
 * Procedural Saturn Ring Texture (concentric rings with transparency)
 */
export function generateSaturnRingTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 64;
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 512, 0);

  gradient.addColorStop(0, 'rgba(0,0,0,0)');
  gradient.addColorStop(0.15, 'rgba(210,180,140,0.8)');
  gradient.addColorStop(0.3, 'rgba(180,150,110,0.9)');
  gradient.addColorStop(0.45, 'rgba(40,30,20,0.2)'); // Cassini Division gap
  gradient.addColorStop(0.55, 'rgba(200,170,130,0.85)');
  gradient.addColorStop(0.85, 'rgba(170,140,100,0.6)');
  gradient.addColorStop(1, 'rgba(0,0,0,0)');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 64);

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}

/**
 * Procedural Organic Muscle / Heart Tissue Texture
 */
export function generateTissueTexture() {
  return createNoiseCanvas(512, 512, (u, v) => {
    const striation = Math.sin(v * 60 + Math.sin(u * 20) * 2) * 0.3 + 0.7;
    const r = Math.floor(180 * striation + 30);
    const g = Math.floor(30 * striation);
    const b = Math.floor(40 * striation);
    return [r, g, b, 255];
  });
}

/**
 * Procedural Brushed Carbon / Titanium Texture for Engineering
 */
export function generateCarbonTexture() {
  return createNoiseCanvas(256, 256, (u, v) => {
    const gridX = Math.floor(u * 32) % 2;
    const gridY = Math.floor(v * 32) % 2;
    const isWeave = gridX === gridY;
    const val = isWeave ? 75 : 45;
    return [val, val + 2, val + 6, 255];
  });
}
