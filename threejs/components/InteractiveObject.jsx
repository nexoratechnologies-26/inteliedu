import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import ObjectLabel from '../labels/ObjectLabel.jsx';

/**
 * InteractiveObject
 * Encapsulates an interactive 3D mesh with hover highlights, selection state, spatial labels, and educational metadata
 */
export default function InteractiveObject({
  id,
  name,
  description,
  category = 'General',
  metadata = {},
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = [1, 1, 1],
  geometry = null,
  material = null,
  color = '#3b82f6',
  emissiveColor = '#38bdf8',
  isSelected = false,
  showLabel = true,
  labelPosition = null,
  onSelect = null,
  children,
}) {
  const meshRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);

  // Smooth scale animation on hover/selection
  useFrame(() => {
    if (meshRef.current) {
      const targetScale = isSelected ? 1.08 : isHovered ? 1.04 : 1.0;
      meshRef.current.scale.lerp(
        new THREE.Vector3(scale[0] * targetScale, scale[1] * targetScale, scale[2] * targetScale),
        0.1
      );
    }
  });

  const handleClick = (e) => {
    e.stopPropagation();
    if (onSelect) {
      onSelect({
        id,
        name,
        description,
        category,
        metadata,
      });
    }
  };

  const handlePointerOver = (e) => {
    e.stopPropagation();
    setIsHovered(true);
    document.body.style.cursor = 'pointer';
  };

  const handlePointerOut = (e) => {
    e.stopPropagation();
    setIsHovered(false);
    document.body.style.cursor = 'auto';
  };

  const computedLabelPos = labelPosition || [
    position[0],
    position[1] + (scale[1] || 1) * 0.9 + 0.3,
    position[2],
  ];

  return (
    <group position={position} rotation={rotation}>
      {/* 3D Interactive Mesh / Group */}
      <group
        ref={meshRef}
        onClick={handleClick}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
      >
        {children ? (
          children
        ) : (
          <mesh castShadow receiveShadow>
            {geometry || <sphereGeometry args={[0.8, 32, 32]} />}
            {material || (
              <meshStandardMaterial
                color={color}
                roughness={0.3}
                metalness={0.2}
                emissive={isSelected ? '#38bdf8' : isHovered ? emissiveColor : '#000000'}
                emissiveIntensity={isSelected ? 0.6 : isHovered ? 0.3 : 0}
              />
            )}
          </mesh>
        )}
      </group>

      {/* 3D Spatial Label */}
      {showLabel && (
        <ObjectLabel
          position={computedLabelPos}
          text={name}
          subtitle={category}
          isSelected={isSelected}
          visible={showLabel}
          onClick={handleClick}
        />
      )}
    </group>
  );
}
