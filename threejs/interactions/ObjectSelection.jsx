import React from 'react';

/**
 * ObjectSelection component
 * Manages active selection state for an educational object node
 */
export default function ObjectSelection({
  isSelected = false,
  children,
}) {
  return (
    <group name="selection-wrapper">
      {typeof children === 'function' ? children({ isSelected }) : children}
    </group>
  );
}
