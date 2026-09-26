import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { 
  generateSunTexture, 
  generateEarthTexture, 
  generateJupiterTexture, 
  generateMarsTexture, 
  generateMoonTexture, 
  generateSaturnRingTexture 
} from '../../utils/textureGenerator.js';
import InteractiveObject from '../../components/InteractiveObject.jsx';

/**
 * Procedural Planetary Body Component
 */
function PlanetaryBody({
  id,
  name,
  category = 'Planet',
  radius,
  orbitRadius,
  orbitSpeed,
  rotationSpeed,
  texture,
  color,
  emissiveColor,
  emissiveIntensity = 0,
  inclination = 0,
  tilt = 0,
  ring = null,
  description,
  metadata,
  isSelected,
  onSelect,
  isPaused,
  speedMultiplier,
}) {
  const orbitGroupRef = useRef(null);
  const meshRef = useRef(null);
  const angleRef = useRef(Math.random() * Math.PI * 2);

  useFrame((state, delta) => {
    if (!isPaused) {
      const activeDelta = delta * speedMultiplier;
      
      // Orbit revolution
      if (orbitRadius > 0 && orbitGroupRef.current) {
        angleRef.current += orbitSpeed * 0.1 * activeDelta;
        const x = Math.cos(angleRef.current) * orbitRadius;
        const z = Math.sin(angleRef.current) * orbitRadius;
        const y = Math.sin(angleRef.current) * orbitRadius * Math.sin(inclination);
        orbitGroupRef.current.position.set(x, y, z);
      }

      // Axial self rotation
      if (meshRef.current) {
        meshRef.current.rotation.y += rotationSpeed * 0.5 * activeDelta;
      }
    }
  });

  return (
    <group ref={orbitGroupRef} position={[orbitRadius, 0, 0]}>
      <InteractiveObject
        id={id}
        name={name}
        category={category}
        description={description}
        metadata={metadata}
        isSelected={isSelected}
        onSelect={onSelect}
      >
        <group rotation={[tilt, 0, 0]}>
          <mesh ref={meshRef} castShadow receiveShadow>
            <sphereGeometry args={[radius, 32, 32]} />
            <meshStandardMaterial
              map={texture}
              color={color}
              roughness={0.6}
              metalness={0.1}
              emissive={isSelected ? '#38bdf8' : emissiveColor || '#000000'}
              emissiveIntensity={isSelected ? 0.6 : emissiveIntensity}
            />
          </mesh>

          {/* Optional Planetary Rings (e.g., Saturn / Uranus) */}
          {ring && (
            <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
              <ringGeometry args={[ring.innerRadius, ring.outerRadius, 64]} />
              <meshStandardMaterial
                map={ring.texture}
                color={ring.color || '#e2d5ba'}
                side={THREE.DoubleSide}
                transparent={true}
                opacity={0.85}
              />
            </mesh>
          )}
        </group>
      </InteractiveObject>
    </group>
  );
}

/**
 * Orbit Line Visualizer Component
 */
function OrbitRing({ radius, color = '#334155' }) {
  const points = useMemo(() => {
    const pts = [];
    const segments = 128;
    for (let i = 0; i <= segments; i++) {
      const theta = (i / segments) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(theta) * radius, 0, Math.sin(theta) * radius));
    }
    return pts;
  }, [radius]);

  const lineGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial color={color} transparent opacity={0.25} />
    </line>
  );
}

/**
 * Complete Procedural Solar System Model
 * Features Sun, Mercury, Venus, Earth + Moon, Mars, Jupiter, Saturn with rings, Uranus, Neptune
 */
export default function SolarSystemModel({
  selectedId = null,
  onSelect = null,
  isPaused = false,
  speedMultiplier = 1.0,
}) {
  // Generate high-resolution procedural textures
  const textures = useMemo(() => ({
    sun: generateSunTexture(),
    earth: generateEarthTexture(),
    jupiter: generateJupiterTexture(),
    mars: generateMarsTexture(),
    moon: generateMoonTexture(),
    saturnRing: generateSaturnRingTexture(),
  }), []);

  const planets = [
    {
      id: 'mercury',
      name: 'Mercury',
      radius: 0.28,
      orbitRadius: 3.5,
      orbitSpeed: 2.2,
      rotationSpeed: 0.1,
      color: '#94a3b8',
      description: 'The smallest planet in the Solar System and the closest to the Sun. It has a cratered surface and extreme temperature swings.',
      metadata: {
        distance_from_sun: '57.9 million km',
        orbital_period: '88 Earth days',
        surface_temp: '-180°C to 430°C',
        moons: '0',
      },
    },
    {
      id: 'venus',
      name: 'Venus',
      radius: 0.45,
      orbitRadius: 5.2,
      orbitSpeed: 1.6,
      rotationSpeed: -0.05, // Retrograde rotation
      color: '#fef08a',
      description: 'The hottest planet in the Solar System due to a runaway greenhouse effect in its dense carbon dioxide atmosphere.',
      metadata: {
        distance_from_sun: '108.2 million km',
        orbital_period: '225 Earth days',
        surface_temp: '465°C',
        moons: '0',
      },
    },
    {
      id: 'earth',
      name: 'Earth',
      radius: 0.5,
      orbitRadius: 7.2,
      orbitSpeed: 1.0,
      rotationSpeed: 1.0,
      texture: textures.earth,
      color: '#ffffff',
      tilt: 0.41, // 23.5 degrees
      description: 'Our home planet, the only known celestial body to support life, featuring liquid water oceans and a protective magnetic field.',
      metadata: {
        distance_from_sun: '149.6 million km (1 AU)',
        orbital_period: '365.25 days',
        surface_temp: '15°C (average)',
        moons: '1 (Luna)',
      },
    },
    {
      id: 'mars',
      name: 'Mars',
      radius: 0.35,
      orbitRadius: 9.4,
      orbitSpeed: 0.8,
      rotationSpeed: 0.95,
      texture: textures.mars,
      color: '#f87171',
      tilt: 0.44,
      description: 'The Red Planet, named for its iron oxide-rich soil. Hosts Olympus Mons (largest volcano in the solar system) and polar ice caps.',
      metadata: {
        distance_from_sun: '227.9 million km',
        orbital_period: '687 Earth days',
        gravity: '3.72 m/s²',
        moons: '2 (Phobos, Deimos)',
      },
    },
    {
      id: 'jupiter',
      name: 'Jupiter',
      radius: 1.2,
      orbitRadius: 13.0,
      orbitSpeed: 0.43,
      rotationSpeed: 2.4, // Fast 10-hour rotation
      texture: textures.jupiter,
      color: '#fcd34d',
      description: 'The largest planet in the Solar System. A gas giant with iconic turbulent cloud bands and the Great Red Spot storm.',
      metadata: {
        distance_from_sun: '778.5 million km',
        mass: '318 Earth masses',
        orbital_period: '11.86 Earth years',
        moons: '95 known (Io, Europa, Ganymede, Callisto)',
      },
    },
    {
      id: 'saturn',
      name: 'Saturn',
      radius: 0.95,
      orbitRadius: 17.5,
      orbitSpeed: 0.32,
      rotationSpeed: 2.2,
      color: '#fed7aa',
      tilt: 0.47,
      ring: {
        innerRadius: 1.3,
        outerRadius: 2.5,
        texture: textures.saturnRing,
        color: '#e2d5ba',
      },
      description: 'Famous for its complex, prominent planetary ring system made of billions of icy particles and rock fragments.',
      metadata: {
        distance_from_sun: '1.43 billion km',
        orbital_period: '29.45 Earth years',
        ring_span: '282,000 km across',
        moons: '146 known (Titan, Enceladus)',
      },
    },
    {
      id: 'uranus',
      name: 'Uranus',
      radius: 0.65,
      orbitRadius: 21.5,
      orbitSpeed: 0.22,
      rotationSpeed: -1.4,
      color: '#67e8f9',
      tilt: 1.71, // 98-degree extreme axial tilt (rolls on its side)
      ring: {
        innerRadius: 0.9,
        outerRadius: 1.3,
        color: '#bae6fd',
      },
      description: 'An ice giant with a unique 98-degree axial tilt that causes it to orbit the Sun on its side.',
      metadata: {
        distance_from_sun: '2.87 billion km',
        orbital_period: '84 Earth years',
        atmosphere: 'Hydrogen, Helium, Methane',
        moons: '28 known (Miranda, Titania)',
      },
    },
    {
      id: 'neptune',
      name: 'Neptune',
      radius: 0.62,
      orbitRadius: 25.5,
      orbitSpeed: 0.18,
      rotationSpeed: 1.5,
      color: '#3b82f6',
      tilt: 0.49,
      description: 'The outermost major planet in our solar system, characterized by supersonic winds reaching over 2,000 km/h.',
      metadata: {
        distance_from_sun: '4.5 billion km',
        orbital_period: '164.8 Earth years',
        wind_speed: 'Up to 2,100 km/h',
        moons: '16 known (Triton)',
      },
    },
  ];

  return (
    <group name="solar-system-root">
      {/* 1. Central Sun */}
      <InteractiveObject
        id="sun"
        name="The Sun (Sol)"
        category="Star"
        description="The G-type main-sequence star at the center of the Solar System. It contains 99.86% of the total mass of the entire Solar System."
        metadata={{
          type: 'Yellow Dwarf (G2V)',
          surface_temp: '5,500°C',
          core_temp: '15,000,000°C',
          diameter: '1,392,700 km',
        }}
        isSelected={selectedId === 'sun'}
        onSelect={onSelect}
      >
        <mesh>
          <sphereGeometry args={[1.8, 32, 32]} />
          <meshBasicMaterial
            map={textures.sun}
            color="#fffbeb"
          />
        </mesh>
      </InteractiveObject>

      {/* Sun Emissive Flare Glow Halo */}
      <mesh>
        <sphereGeometry args={[2.2, 32, 32]} />
        <meshBasicMaterial
          color="#f59e0b"
          transparent
          opacity={0.2}
          side={THREE.BackSide}
        />
      </mesh>

      {/* 2. Planetary Orbits & Planets */}
      {planets.map((planet) => (
        <React.Fragment key={planet.id}>
          <OrbitRing radius={planet.orbitRadius} />
          <PlanetaryBody
            {...planet}
            isSelected={selectedId === planet.id}
            onSelect={onSelect}
            isPaused={isPaused}
            speedMultiplier={speedMultiplier}
          />
        </React.Fragment>
      ))}
    </group>
  );
}
