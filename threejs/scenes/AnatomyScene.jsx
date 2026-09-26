import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import InteractiveHumanModel from '../models/human-anatomy/InteractiveHumanModel.jsx';
import { Layers, Activity, Heart, Eye, User } from 'lucide-react';

/**
 * AnatomyScene & 3D Interactive Human Teacher
 * Allows students to interactively explore human anatomy systems, dissect layers,
 * inspect organs (Brain, Heart, Lungs, Spine, Stomach), and engage with the 3D AI Teacher.
 */
export default function AnatomyScene({ onAskAiTutor, onObjectSelect }) {
  const [selectedOrgan, setSelectedOrgan] = useState(null);
  const [activeLayer, setActiveLayer] = useState('all');

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

  return (
    <div className="relative w-full h-full min-h-[550px]">
      <ModelViewer
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
      <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-1.5 p-1.5 bg-slate-900/85 backdrop-blur-md border border-slate-800 rounded-2xl shadow-xl text-slate-300">
        <span className="text-xs font-semibold text-cyan-400 px-2">Anatomy Layers:</span>
        {layers.map((layer) => {
          const Icon = layer.icon;
          return (
            <button
              key={layer.id}
              onClick={() => setActiveLayer(layer.id)}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-medium transition-all ${
                activeLayer === layer.id
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              <Icon className="w-3 h-3" />
              {layer.label}
            </button>
          );
        })}
      </div>

      {/* 3D Human Teacher Interactive Voice HUD Badge */}
      <div className="absolute top-16 left-4 z-10 max-w-xs p-2.5 bg-slate-950/80 backdrop-blur-md border border-cyan-500/30 rounded-2xl text-[11px] text-slate-300 flex items-start gap-2 shadow-lg">
        <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping mt-1 flex-shrink-0" />
        <div>
          <span className="font-semibold text-cyan-300">Dr. Maya (3D Human Teacher):</span>
          <p className="text-slate-400 mt-0.5">
            "Welcome! Click on my Brain, Heart, Lungs, or Spine to see real-time anatomical data and trigger AI explanations."
          </p>
        </div>
      </div>
    </div>
  );
}
