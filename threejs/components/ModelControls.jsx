import React from 'react';
import { 
  RotateCcw, 
  Play, 
  Pause, 
  Tag, 
  Layers, 
  ZoomIn, 
  ZoomOut,
} from 'lucide-react';

/**
 * 3D Viewport Floating Control Panel
 * Provides student/teacher user interface controls for camera manipulation, labels, and view modes in Light and Dark themes
 */
export default function ModelControls({
  theme = 'light',
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
  const isLight = theme === 'light';

  const containerStyle = isLight
    ? 'bg-white/90 backdrop-blur-md border border-slate-200 shadow-xl shadow-slate-200/60 text-slate-700'
    : 'bg-slate-900/90 backdrop-blur-md border border-slate-800 shadow-xl shadow-black/40 text-slate-300';

  const buttonHover = isLight
    ? 'hover:bg-slate-100 hover:text-slate-900 text-slate-600'
    : 'hover:bg-slate-800 hover:text-slate-100 text-slate-300';

  const dividerStyle = isLight ? 'bg-slate-200' : 'bg-slate-800';

  return (
    <div className={`absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1.5 p-1.5 rounded-2xl transition-all duration-200 ${containerStyle}`}>
      {/* Reset Camera */}
      {onResetCamera && (
        <button
          onClick={onResetCamera}
          title="Reset Camera View"
          className={`p-2 rounded-xl active:scale-95 transition-all ${buttonHover}`}
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
              ? (isLight ? 'bg-blue-100 text-blue-600 border border-blue-200' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30') 
              : buttonHover
          }`}
        >
          {isAutoRotating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
        </button>
      )}

      <div className={`w-[1px] h-4 my-auto ${dividerStyle}`} />

      {/* Labels Toggle */}
      {onToggleLabels && (
        <button
          onClick={onToggleLabels}
          title={showLabels ? 'Hide 3D Labels' : 'Show 3D Labels'}
          className={`p-2 rounded-xl transition-all active:scale-95 ${
            showLabels 
              ? (isLight ? 'bg-indigo-100 text-indigo-600 border border-indigo-200' : 'bg-blue-500/20 text-blue-400 border border-blue-500/30') 
              : (isLight ? 'hover:bg-slate-100 text-slate-400 opacity-60' : 'hover:bg-slate-800 text-slate-500 opacity-60')
          }`}
        >
          <Tag className="w-4 h-4" />
        </button>
      )}

      {/* Wireframe / Solid Toggle */}
      {onToggleWireframe && (
        <button
          onClick={onToggleWireframe}
          title={isWireframe ? 'Switch to Solid Material' : 'Switch to Wireframe Mode'}
          className={`p-2 rounded-xl transition-all active:scale-95 ${
            isWireframe 
              ? (isLight ? 'bg-purple-100 text-purple-600 border border-purple-200' : 'bg-purple-500/20 text-purple-400 border border-purple-500/30') 
              : buttonHover
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
          className={`p-2 rounded-xl active:scale-95 transition-all ${buttonHover}`}
        >
          <ZoomIn className="w-4 h-4" />
        </button>
      )}

      {onZoomOut && (
        <button
          onClick={onZoomOut}
          title="Zoom Out"
          className={`p-2 rounded-xl active:scale-95 transition-all ${buttonHover}`}
        >
          <ZoomOut className="w-4 h-4" />
        </button>
      )}

      {/* Clear Selection */}
      {hasSelection && onResetSelection && (
        <>
          <div className={`w-[1px] h-4 my-auto ${dividerStyle}`} />
          <button
            onClick={onResetSelection}
            title="Deselect Object"
            className={`px-2.5 py-1 text-xs font-semibold rounded-xl transition-all active:scale-95 ${
              isLight
                ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100'
                : 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'
            }`}
          >
            Clear Selection
          </button>
        </>
      )}
    </div>
  );
}
