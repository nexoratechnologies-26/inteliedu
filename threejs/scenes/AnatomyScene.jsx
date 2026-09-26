import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import InteractiveHumanModel from '../models/human-anatomy/InteractiveHumanModel.jsx';
import { Layers, Activity, Heart, Eye, User, Sparkles } from 'lucide-react';

/**
 * AnatomyScene & 3D Interactive Human Teacher
 * Allows students to interactively explore human anatomy systems, dissect layers,
 * inspect organs (Brain, Heart, Lungs, Spine, Stomach), and engage with the 3D AI Teacher.
 */
export default function AnatomyScene({ 
  theme = 'light',
  onAskAiTutor, 
  onObjectSelect 
}) {
  const [selectedOrgan, setSelectedOrgan] = useState(null);
  const [activeLayer, setActiveLayer] = useState('all');

  const isLight = theme === 'light';

  const handleSelect = (organ) => {
    setSelectedOrgan(organ);
    if (onObjectSelect) {
      onObjectSelect(organ);
    }
  };

  const layers = [
    { id: 'all', label: 'All Systems', icon: User },
    { id: 'nervous', label: 'Nervous', icon: Eye },
    { id: 'circulatory', label: 'Circulatory', icon: Heart },
    { id: 'respiratory', label: 'Respiratory', icon: Activity },
    { id: 'skeletal', label: 'Skeletal', icon: Layers },
    { id: 'digestive', label: 'Digestive', icon: Layers },
  ];

  const hudBg = isLight
    ? 'bg-white/90 backdrop-blur-md border border-slate-200/90 shadow-xl shadow-slate-200/50 text-slate-700'
    : 'bg-slate-900/85 backdrop-blur-md border border-slate-800 shadow-xl text-slate-300';

  const buttonActive = isLight
    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/30'
    : 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20';

  const buttonInactive = isLight
    ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white';

  const speechCard = isLight
    ? 'bg-white/95 backdrop-blur-md border border-blue-200 shadow-xl text-slate-800'
    : 'bg-slate-950/85 backdrop-blur-md border border-cyan-500/30 shadow-xl text-slate-300';

  return (
    <div className="relative w-full h-full min-h-0 flex-1">
      <ModelViewer
        theme={theme}
        lightingPreset="laboratory"
        cameraPosition={[0, 1.5, 5]}
        cameraTarget={[0, 1.2, 0]}
        cameraFov={45}
        selectedObject={selectedOrgan}
        onSelectObject={handleSelect}
        onAskAiTutor={onAskAiTutor}
        enableShadows={true}
        className="w-full h-full"
      >
        <InteractiveHumanModel
          selectedId={selectedOrgan?.id}
          onSelect={handleSelect}
          activeLayer={activeLayer}
        />
      </ModelViewer>

      {/* Layer Filter Controls Overlay */}
      <div className={`absolute top-4 left-4 z-10 flex flex-wrap items-center gap-1.5 p-1.5 rounded-2xl ${hudBg}`}>
        <span className={`text-xs font-bold px-2 ${isLight ? 'text-blue-700' : 'text-cyan-400'}`}>
          Anatomy Layers:
        </span>
        {layers.map((layer) => {
          const Icon = layer.icon;
          return (
            <button
              key={layer.id}
              onClick={() => setActiveLayer(layer.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 active:scale-95 ${
                activeLayer === layer.id ? buttonActive : buttonInactive
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {layer.label}
            </button>
          );
        })}
      </div>

      {/* 3D Human Teacher Interactive Voice HUD Badge */}
      <div className={`absolute bottom-4 left-4 z-10 max-w-xs p-3 rounded-2xl text-xs flex items-start gap-2.5 transition-all ${speechCard}`}>
        <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping mt-1 flex-shrink-0" />
        <div>
          <span className={`font-bold flex items-center gap-1 ${isLight ? 'text-blue-700' : 'text-cyan-300'}`}>
            <Sparkles className="w-3 h-3 text-yellow-500" />
            Dr. Maya (3D Human Teacher):
          </span>
          <p className={`mt-1 text-[11px] leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            "Click on my Brain, Heart, Lungs, or Spine to see real-time anatomical data and trigger AI explanations."
          </p>
        </div>
      </div>
    </div>
  );
}
