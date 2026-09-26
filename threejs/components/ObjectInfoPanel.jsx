import React from 'react';
import { Sparkles, X, Tag } from 'lucide-react';

/**
 * 3D Object Information Card & AI Tutor Handshake Interface
 * Displays educational metadata for selected parts and invokes cross-module callbacks in Light/Dark themes
 */
export default function ObjectInfoPanel({
  theme = 'light',
  selectedObject,
  onClose,
  onAskAiTutor,
  className = '',
}) {
  if (!selectedObject) return null;

  const isLight = theme === 'light';

  const {
    id = 'unknown',
    name = 'Selected 3D Object',
    description = 'No additional description available for this part.',
    category = 'General',
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

  const containerStyle = isLight
    ? 'bg-white/95 backdrop-blur-xl border border-slate-200/90 shadow-2xl shadow-slate-300/60 text-slate-800'
    : 'bg-slate-900/95 backdrop-blur-xl border border-slate-700/60 shadow-2xl text-slate-100';

  const headerBorder = isLight ? 'border-slate-100' : 'border-slate-800';
  const badgeStyle = isLight
    ? 'bg-blue-50 text-blue-700 border border-blue-200'
    : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20';
  const titleStyle = isLight ? 'text-slate-900' : 'text-white';
  const descStyle = isLight ? 'text-slate-600' : 'text-slate-300';
  const metaContainer = isLight
    ? 'bg-slate-50/80 border border-slate-200/80 text-slate-700'
    : 'bg-slate-950/60 border border-slate-800/80 text-slate-300';
  const metaKeyStyle = isLight ? 'text-slate-500' : 'text-slate-400';
  const metaValStyle = isLight ? 'text-slate-800 font-semibold' : 'text-slate-200 font-medium';

  return (
    <div
      className={`absolute top-4 right-4 z-20 w-80 max-w-[calc(100vw-2rem)] rounded-2xl p-4 transition-all duration-300 animate-in fade-in slide-in-from-top-2 ${containerStyle} ${className}`}
    >
      {/* Header */}
      <div className={`flex items-start justify-between gap-2 border-b ${headerBorder} pb-3 mb-3`}>
        <div>
          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider mb-1.5 ${badgeStyle}`}>
            <Tag className="w-2.5 h-2.5" />
            {category}
          </span>
          <h3 className={`text-base font-extrabold tracking-tight ${titleStyle}`}>
            {name}
          </h3>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className={`p-1.5 rounded-lg transition-colors ${
              isLight ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Close Panel"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Description */}
      <p className={`text-xs leading-relaxed mb-4 ${descStyle}`}>
        {description}
      </p>

      {/* Additional Metadata Attributes if available */}
      {metadata && Object.keys(metadata).length > 0 && (
        <div className={`rounded-xl p-3 mb-4 space-y-1.5 ${metaContainer}`}>
          {Object.entries(metadata).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between text-[11px]">
              <span className={`capitalize ${metaKeyStyle}`}>{key.replace(/_/g, ' ')}:</span>
              <span className={metaValStyle}>{String(value)}</span>
            </div>
          ))}
        </div>
      )}

      {/* AI Tutor Action Integration Button */}
      {onAskAiTutor && (
        <button
          onClick={handleAskAi}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-500/25 active:scale-[0.98] transition-all"
        >
          <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
          Ask AI Tutor About {name}
        </button>
      )}
    </div>
  );
}
