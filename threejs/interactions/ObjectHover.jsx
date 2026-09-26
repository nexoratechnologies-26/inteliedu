import React, { useState } from 'react';

/**
 * ObjectHover wrapper
 * Injects hover state tracking and pointer styling into child 3D elements
 */
export default function ObjectHover({ children, onHoverChange }) {
  const [isHovered, setIsHovered] = useState(false);

  const handlePointerOver = (e) => {
    e.stopPropagation();
    setIsHovered(true);
    document.body.style.cursor = 'pointer';
    if (onHoverChange) onHoverChange(true);
  };

  const handlePointerOut = (e) => {
    e.stopPropagation();
    setIsHovered(false);
    document.body.style.cursor = 'auto';
    if (onHoverChange) onHoverChange(false);
  };

  return (
    <group onPointerOver={handlePointerOver} onPointerOut={handlePointerOut}>
      {typeof children === 'function' ? children({ isHovered }) : children}
    </group>
  );
}
