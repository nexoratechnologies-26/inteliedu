import React from 'react';
import { Html, useProgress } from '@react-three/drei';
import { Loader2 } from 'lucide-react';

/**
 * 3D Model Loading HUD Screen
 * Automatically tracks GLTF/GLB download and parsing progress
 */
export default function LoadingScreen({ message = 'Loading 3D Educational Assets...' }) {
  const { progress, active } = useProgress();

  if (!active && progress === 100) return null;

  return (
    <Html center>
      <div className="flex flex-col items-center justify-center p-5 bg-slate-950/80 border border-slate-800 backdrop-blur-md rounded-2xl shadow-2xl min-w-[220px] pointer-events-none select-none">
        <Loader2 className="w-7 h-7 text-cyan-400 animate-spin mb-3" />
        <span className="text-xs font-medium text-slate-200 mb-2">
          {message}
        </span>
        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-cyan-400 h-1.5 transition-all duration-300 rounded-full"
            style={{ width: `${Math.round(progress)}%` }}
          />
        </div>
        <span className="text-[10px] text-slate-400 mt-1.5 font-mono">
          {Math.round(progress)}%
        </span>
      </div>
    </Html>
  );
}
