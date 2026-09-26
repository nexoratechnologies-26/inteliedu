import React, { useState } from 'react';
import { Html } from '@react-three/drei';

/**
 * 3D Spatial Pin & Object Label
 * Renders an accessible HTML tooltip attached to 3D mesh coordinates with Light/Dark theme support
 */
export default function ObjectLabel({
  position = [0, 0, 0],
  text = 'Object',
  subtitle = null,
  isSelected = false,
  visible = true,
  theme = 'light',
  onClick = null,
  occlude = false,
  distanceFactor = 8,
}) {
  const [isHovered, setIsHovered] = useState(false);

  if (!visible) return null;

  const isLight = theme === 'light';

  let badgeStyle = '';
  if (isSelected) {
    badgeStyle = 'bg-blue-600 text-white font-bold scale-110 shadow-lg shadow-blue-500/40 ring-2 ring-blue-300';
  } else if (isHovered) {
    badgeStyle = isLight
      ? 'bg-blue-50 text-blue-800 scale-105 border border-blue-300 shadow-md'
      : 'bg-slate-800/90 text-cyan-300 scale-105 border border-cyan-500/50 shadow-md';
  } else {
    badgeStyle = isLight
      ? 'bg-white/95 text-slate-800 border border-slate-200 shadow-sm hover:border-blue-300'
      : 'bg-slate-900/85 text-slate-200 border border-slate-700/60';
  }

  return (
    <Html
      position={position}
      center
      distanceFactor={distanceFactor}
      occlude={occlude}
      zIndexRange={[10, 0]}
      style={{ pointerEvents: 'auto' }}
    >
      <div
        onClick={(e) => {
          e.stopPropagation();
          if (onClick) onClick();
        }}
        onPointerDown={(e) => e.stopPropagation()}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`group flex items-center gap-1.5 px-3 py-1 rounded-full cursor-pointer transition-all duration-200 select-none backdrop-blur-md pointer-events-auto ${badgeStyle}`}
      >
        <div
          className={`w-2 h-2 rounded-full ${
            isSelected
              ? 'bg-white animate-ping'
              : isLight ? 'bg-blue-500' : 'bg-cyan-400'
          }`}
        />
        <span className="text-[11px] font-bold tracking-tight whitespace-nowrap">
          {text}
        </span>
        {subtitle && isHovered && (
          <span className={`text-[9px] border-l pl-1.5 ml-0.5 ${isLight ? 'text-slate-500 border-slate-200' : 'text-slate-400 border-slate-700'}`}>
            {subtitle}
          </span>
        )}
      </div>
    </Html>
  );
}
