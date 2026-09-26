import React from 'react';
import ObjectLabel from './ObjectLabel.jsx';

/**
 * Label Manager
 * Orchestrates a collection of 3D spatial labels across educational scene nodes
 */
export default function LabelManager({
  labels = [],
  visible = true,
  selectedId = null,
  onSelect = null,
}) {
  if (!visible || !labels || labels.length === 0) return null;

  return (
    <group name="label-manager-group">
      {labels.map((item) => (
        <ObjectLabel
          key={item.id}
          position={item.position || [0, 0, 0]}
          text={item.name || item.text}
          subtitle={item.category || item.subtitle}
          isSelected={selectedId === item.id}
          visible={visible}
          onClick={() => onSelect && onSelect(item)}
        />
      ))}
    </group>
  );
}
