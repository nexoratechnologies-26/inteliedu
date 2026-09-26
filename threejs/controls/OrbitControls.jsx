import React, { forwardRef } from 'react';
import { OrbitControls as DreiOrbitControls } from '@react-three/drei';

/**
 * Reusable OrbitControls wrapper configured with smooth damping and educational navigation defaults
 */
const OrbitControls = forwardRef(function OrbitControls(
  {
    enableDamping = true,
    dampingFactor = 0.05,
    minDistance = 1,
    maxDistance = 50,
    maxPolarAngle = Math.PI / 1.8,
    minPolarAngle = 0.1,
    autoRotate = false,
    autoRotateSpeed = 1.0,
    enableZoom = true,
    enablePan = true,
    enableRotate = true,
    makeDefault = true,
    ...props
  },
  ref
) {
  return (
    <DreiOrbitControls
      ref={ref}
      makeDefault={makeDefault}
      enableDamping={enableDamping}
      dampingFactor={dampingFactor}
      minDistance={minDistance}
      maxDistance={maxDistance}
      maxPolarAngle={maxPolarAngle}
      minPolarAngle={minPolarAngle}
      autoRotate={autoRotate}
      autoRotateSpeed={autoRotateSpeed}
      enableZoom={enableZoom}
      enablePan={enablePan}
      enableRotate={enableRotate}
      {...props}
    />
  );
});

export default OrbitControls;
