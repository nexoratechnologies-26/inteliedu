import React, { useRef, useEffect } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import OrbitControls from './OrbitControls.jsx';

/**
 * Reusable Camera Controls manager that synchronizes OrbitControls with camera resets and focus transitions
 */
export default function CameraControls({
  defaultPosition = [0, 2, 6],
  defaultTarget = [0, 0, 0],
  focusTarget = null,
  autoRotate = false,
  autoRotateSpeed = 1.0,
  controlsRef = null,
}) {
  const { camera } = useThree();
  const internalControlsRef = useRef(null);
  const activeControls = controlsRef || internalControlsRef;

  // Set initial position
  useEffect(() => {
    camera.position.set(...defaultPosition);
    camera.lookAt(...defaultTarget);
    if (activeControls.current) {
      activeControls.current.target.set(...defaultTarget);
      activeControls.current.update();
    }
  }, [camera, defaultPosition, defaultTarget]);

  // Smooth lerp towards focus target if specified
  useFrame(() => {
    if (focusTarget && activeControls.current) {
      const targetVec = new THREE.Vector3(...focusTarget);
      activeControls.current.target.lerp(targetVec, 0.05);
      activeControls.current.update();
    }
  });

  return (
    <OrbitControls
      ref={activeControls}
      autoRotate={autoRotate}
      autoRotateSpeed={autoRotateSpeed}
    />
  );
}
