import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import HumanTeacherModel from '../models/human-anatomy/HumanTeacherModel.jsx';
import { 
  Layers, 
  Activity, 
  Heart, 
  Eye, 
  User, 
  Sparkles, 
  Scan, 
  CheckCircle2,
  Stethoscope
} from 'lucide-react';

/**
 * AnatomyScene & 3D Interactive Human Teacher ("Dr. Maya")
 * Features full human teacher mode, X-Ray dissection mode, organ system filtering,
 * interactive body part selector, and direct 3D touching/clicking.
 */
export default function AnatomyScene({ 
  theme = 'light',
  onAskAiTutor, 
  onObjectSelect 
}) {
  const [selectedOrgan, setSelectedOrgan] = useState(null);
  const [activeMode, setActiveMode] = useState('teacher'); // 'teacher' | 'xray' | 'anatomy'
  const [activeLayer, setActiveLayer] = useState('all');

  const isLight = theme === 'light';

  const handleSelect = (organ) => {
    setSelectedOrgan(organ);
    if (onObjectSelect) {
      onObjectSelect(organ);
    }
  };

  const quickParts = [
    { id: 'head', name: 'Facial Anatomy', category: 'Human Anatomy' },
    { id: 'brain', name: 'Brain (Cerebrum)', category: 'Nervous System' },
    { id: 'heart', name: 'Heart & Aorta', category: 'Circulatory System' },
    { id: 'left-lung', name: 'Lungs (Respiratory)', category: 'Respiratory System' },
    { id: 'spine', name: 'Spine (Vertebrae)', category: 'Skeletal System' },
    { id: 'stomach', name: 'Stomach', category: 'Digestive System' },
    { id: 'hands', name: 'Articulated Hands', category: 'Musculoskeletal System' },
    { id: 'torso', name: 'Doctor Lab Coat', category: 'Human Body & Attire' },
  ];

  const layers = [
    { id: 'all', label: 'All Organs', icon: User },
    { id: 'nervous', label: 'Brain', icon: Eye },
    { id: 'circulatory', label: 'Heart', icon: Heart },
    { id: 'respiratory', label: 'Lungs', icon: Activity },
    { id: 'skeletal', label: 'Spine', icon: Layers },
    { id: 'digestive', label: 'Stomach', icon: Stethoscope },
  ];

  const hudBg = isLight
    ? 'bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-xl shadow-slate-200/50 text-slate-700'
    : 'bg-slate-900/90 backdrop-blur-md border border-slate-800 shadow-xl text-slate-300';

  const buttonActive = isLight
    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/25'
    : 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20';

  const buttonInactive = isLight
    ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900'
    : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white';

  return (
    <div className="relative w-full h-full min-h-0 flex-1 flex">
      {/* Main 3D Canvas */}
      <ModelViewer
        theme={theme}
        lightingPreset="laboratory"
        cameraPosition={[0, 1.8, 4.5]}
        cameraTarget={[0, 1.2, 0]}
        cameraFov={45}
        selectedObject={selectedOrgan}
        onSelectObject={handleSelect}
        onAskAiTutor={onAskAiTutor}
        enableShadows={true}
        className="w-full h-full flex-1"
      >
        <HumanTeacherModel
          theme={theme}
          selectedId={selectedOrgan?.id}
          onSelect={handleSelect}
          activeMode={activeMode}
          activeLayer={activeLayer}
        />
      </ModelViewer>

      {/* Top Left Controls: Mode Switcher & Anatomy Layer Filters */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 max-w-[calc(100vw-2rem)]">
        {/* 1. Mode Switcher (Teacher Mode vs X-Ray Dissection) */}
        <div className={`flex items-center gap-1.5 p-1.5 rounded-2xl ${hudBg}`}>
          <span className={`text-[11px] font-bold px-2 ${isLight ? 'text-blue-700' : 'text-cyan-400'}`}>
            View Mode:
          </span>
          <button
            onClick={() => setActiveMode('teacher')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold transition-all ${
              activeMode === 'teacher' ? buttonActive : buttonInactive
            }`}
          >
            <User className="w-3.5 h-3.5" />
            Human Teacher
          </button>
          <button
            onClick={() => setActiveMode('xray')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold transition-all ${
              activeMode === 'xray' ? buttonActive : buttonInactive
            }`}
          >
            <Scan className="w-3.5 h-3.5" />
            X-Ray / Organs
          </button>
        </div>

        {/* 2. Organ Layer Filter (When in X-Ray / Anatomy mode) */}
        {activeMode !== 'teacher' && (
          <div className={`flex flex-wrap items-center gap-1 p-1.5 rounded-2xl animate-in fade-in ${hudBg}`}>
            {layers.map((layer) => {
              const Icon = layer.icon;
              return (
                <button
                  key={layer.id}
                  onClick={() => setActiveLayer(layer.id)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-semibold transition-all ${
                    activeLayer === layer.id ? buttonActive : buttonInactive
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  {layer.label}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Interactive Quick-Select Body Parts List (Left Bottom) */}
      <div className={`absolute bottom-4 left-4 z-10 max-w-sm p-2.5 rounded-2xl ${hudBg} hidden sm:block`}>
        <div className="flex items-center gap-1.5 mb-1.5 px-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-200">
            Interactive Body Parts:
          </span>
        </div>
        <div className="flex flex-wrap gap-1">
          {quickParts.map((part) => {
            const isSelected = selectedOrgan?.id === part.id;
            return (
              <button
                key={part.id}
                onClick={() => {
                  if (activeMode === 'teacher' && ['brain', 'heart', 'left-lung', 'spine', 'stomach'].includes(part.id)) {
                    setActiveMode('xray');
                  }
                  handleSelect(part);
                }}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all active:scale-95 ${
                  isSelected
                    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/30'
                    : isLight
                    ? 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {part.name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
