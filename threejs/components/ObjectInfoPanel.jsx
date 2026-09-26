import React from 'react';
import { Sparkles, X, Info, Tag, Compass } from 'lucide-react';

/**
 * 3D Object Information Card & AI Tutor Handshake Interface
 * Displays educational metadata for selected parts and invokes cross-module callbacks
 */
export default function ObjectInfoPanel({
  selectedObject,
  onClose,
  onAskAiTutor,
  className = '',
}) {
  if (!selectedObject) return null;

  const {
    id = 'unknown',
    name = 'Selected 3D Object',
    description = 'No additional description available for this part.',
    category = 'General',
    modelPath = null,
    metadata = {},
  } = selectedObject;

  const handleAskAi = () => {
    if (onAskAiTutor) {
      onAskAiTutor({
        selectedObject: {
          id,
          name,
          category,
          description,
        },
      });
    }
  };

  return (
    <div
      className={`absolute top-4 right-4 z-20 w-80 max-w-[calc(100vw-2rem)] bg-slate-900/90 backdrop-blur-xl border border-slate-700/60 rounded-2xl shadow-2xl p-4 text-slate-100 transition-all duration-300 animate-in fade-in slide-in-from-top-2 ${className}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 border-b border-slate-800 pb-3 mb-3">
        <div>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase tracking-wider mb-1">
            <Tag className="w-2.5 h-2.5" />
            {category}
          </span>
          <h3 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
            {name}
          </h3>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Close Panel"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Description */}
      <p className="text-xs text-slate-300 leading-relaxed mb-4">
        {description}
      </p>

      {/* Additional Metadata Attributes if available */}
      {metadata && Object.keys(metadata).length > 0 && (
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-2.5 mb-4 space-y-1.5">
          {Object.entries(metadata).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}:</span>
              <span className="text-slate-200 font-medium">{String(value)}</span>
            </div>
          ))}
        </div>
      )}

      {/* AI Tutor Action Integration Button */}
      {onAskAiTutor && (
        <button
          onClick={handleAskAi}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-500/20 active:scale-[0.98] transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
          Ask AI Tutor About {name}
        </button>
      )}
    </div>
  );
}
