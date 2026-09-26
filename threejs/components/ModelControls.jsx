import React from 'react';
import { 
  RotateCcw, 
  Play, 
  Pause, 
  Tag, 
  Eye, 
  Layers, 
  ZoomIn, 
  ZoomOut,
  Maximize2
} from 'lucide-react';

/**
 * 3D Viewport Floating Control Panel
 * Provides student/teacher user interface controls for camera manipulation, labels, and view modes
 */
export default function ModelControls({
  onResetCamera,
  isAutoRotating = false,
  onToggleAutoRotate,
  showLabels = true,
  onToggleLabels,
  isWireframe = false,
  onToggleWireframe,
  onZoomIn,
  onZoomOut,
  onResetSelection,
  hasSelection = false,
}) {
  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1.5 p-1.5 bg-slate-900/80 backdrop-blur-md border border-slate-800/80 rounded-2xl shadow-xl shadow-black/40 text-slate-300">
      {/* Reset Camera */}
      {onResetCamera && (
        <button
          onClick={onResetCamera}
          title="Reset Camera View"
          className="p-2 rounded-xl hover:bg-slate-800 hover:text-cyan-400 active:scale-95 transition-all text-slate-300"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      )}

      {/* Auto Rotate Toggle */}
      {onToggleAutoRotate && (
        <button
          onClick={onToggleAutoRotate}
          title={isAutoRotating ? 'Pause Auto Rotation' : 'Start Auto Rotation'}
          className={`p-2 rounded-xl transition-all active:scale-95 ${
            isAutoRotating 
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' 
              : 'hover:bg-slate-800 hover:text-slate-100'
          }`}
        >
          {isAutoRotating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
      )}

      <div className="w-[1px] h-4 bg-slate-800 my-auto" />

      {/* Labels Toggle */}
      {onToggleLabels && (
        <button
          onClick={onToggleLabels}
          title={showLabels ? 'Hide 3D Labels' : 'Show 3D Labels'}
          className={`p-2 rounded-xl transition-all active:scale-95 ${
            showLabels 
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
              : 'hover:bg-slate-800 hover:text-slate-400 opacity-60'
          }`}
        >
          <Tag className="w-4 h-4" />
        </button>
      )}

      {/* Wireframe / X-ray Toggle */}
      {onToggleWireframe && (
        <button
          onClick={onToggleWireframe}
          title={isWireframe ? 'Switch to Solid Material' : 'Switch to Wireframe Mode'}
          className={`p-2 rounded-xl transition-all active:scale-95 ${
            isWireframe 
              ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' 
              : 'hover:bg-slate-800 hover:text-slate-100'
          }`}
        >
          <Layers className="w-4 h-4" />
        </button>
      )}

      {/* Zoom In & Zoom Out */}
      {onZoomIn && (
        <button
          onClick={onZoomIn}
          title="Zoom In"
          className="p-2 rounded-xl hover:bg-slate-800 hover:text-slate-100 active:scale-95 transition-all"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
      )}

      {onZoomOut && (
        <button
          onClick={onZoomOut}
          title="Zoom Out"
          className="p-2 rounded-xl hover:bg-slate-800 hover:text-slate-100 active:scale-95 transition-all"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
      )}

      {/* Clear Selection */}
      {hasSelection && onResetSelection && (
        <>
          <div className="w-[1px] h-4 bg-slate-800 my-auto" />
          <button
            onClick={onResetSelection}
            title="Deselect Object"
            className="px-2.5 py-1 text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 rounded-xl transition-all active:scale-95"
          >
            Clear Selection
          </button>
        </>
      )}
    </div>
  );
}
