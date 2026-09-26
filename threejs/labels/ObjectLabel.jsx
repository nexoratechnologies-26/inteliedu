import React, { useState } from 'react';
import { Html } from '@react-three/drei';

/**
 * 3D Spatial Pin & Object Label
 * Renders an accessible HTML tooltip attached to 3D mesh coordinates
 */
export default function ObjectLabel({
  position = [0, 0, 0],
  text = 'Object',
  subtitle = null,
  isSelected = false,
  visible = true,
  onClick = null,
  occlude = false,
  distanceFactor = 8,
}) {
  const [isHovered, setIsHovered] = useState(false);

  if (!visible) return null;

  return (
    <Html
      position={position}
      center
      distanceFactor={distanceFactor}
      occlude={occlude}
      zIndexRange={[10, 0]}
    >
      <div
        onClick={(e) => {
          e.stopPropagation();
          if (onClick) onClick();
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`group flex items-center gap-1.5 px-2.5 py-1 rounded-full cursor-pointer transition-all duration-200 select-none backdrop-blur-md shadow-lg ${
          isSelected
            ? 'bg-cyan-500 text-slate-950 font-bold scale-110 shadow-cyan-500/50 ring-2 ring-cyan-300'
            : isHovered
            ? 'bg-slate-800/90 text-cyan-300 scale-105 border border-cyan-500/50'
            : 'bg-slate-900/75 text-slate-200 border border-slate-700/60'
        }`}
      >
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            isSelected ? 'bg-slate-950 animate-ping' : 'bg-cyan-400'
          }`}
        />
        <span className="text-[11px] font-medium tracking-tight whitespace-nowrap">
          {text}
        </span>
        {subtitle && isHovered && (
          <span className="text-[9px] text-slate-400 border-l border-slate-700 pl-1 ml-0.5">
            {subtitle}
          </span>
        )}
      </div>
    </Html>
  );
}
