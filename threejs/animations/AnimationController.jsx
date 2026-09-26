import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { calculateOrbitPosition } from './animationUtils.js';

/**
 * AnimationController
 * Applies frame-rate-independent rotation and orbital revolution transforms to child 3D nodes
 */
export default function AnimationController({
  isPlaying = true,
  speed = 1.0,
  rotationSpeed = 0.5,
  rotationAxis = [0, 1, 0],
  orbitRadius = 0,
  orbitSpeed = 0.2,
  orbitInclination = 0,
  initialAngle = 0,
  children,
}) {
  const groupRef = useRef(null);
  const angleRef = useRef(initialAngle);

  useFrame((state, delta) => {
    if (!isPlaying || !groupRef.current) return;

    const activeDelta = delta * speed;

    // Self Rotation
    if (rotationSpeed !== 0) {
      groupRef.current.rotation.x += rotationAxis[0] * rotationSpeed * activeDelta;
      groupRef.current.rotation.y += rotationAxis[1] * rotationSpeed * activeDelta;
      groupRef.current.rotation.z += rotationAxis[2] * rotationSpeed * activeDelta;
    }

    // Orbital Translation
    if (orbitRadius > 0 && orbitSpeed !== 0) {
      angleRef.current += orbitSpeed * activeDelta;
      const [x, y, z] = calculateOrbitPosition(orbitRadius, angleRef.current, orbitInclination);
      groupRef.current.position.set(x, y, z);
    }
  });

  return <group ref={groupRef}>{children}</group>;
}
