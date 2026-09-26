import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import EngineMechanicsModel from '../models/engineering/EngineMechanicsModel.jsx';
import { Gauge, Split, Play, Pause, Sparkles } from 'lucide-react';

/**
 * EngineeringScene
 * Interactive 4-Cylinder Engine & Gearbox 3D Learning Scene with RPM speed control,
 * Exploded View dissection, piston kinematics, and AI Tutor question triggers in Light/Dark themes.
 */
export default function EngineeringScene({ 
  theme = 'light',
  onAskAiTutor, 
  onObjectSelect 
}) {
  const [selectedPart, setSelectedPart] = useState(null);
  const [isExploded, setIsExploded] = useState(false);
  const [rpm, setRpm] = useState(60);
  const [isPaused, setIsPaused] = useState(false);

  const isLight = theme === 'light';

  const handleSelect = (part) => {
    setSelectedPart(part);
    if (onObjectSelect) {
      onObjectSelect(part);
    }
  };

  const engineParts = [
    { id: 'engine-block', name: 'Engine Block', category: 'Mechanical Engineering' },
    { id: 'crankshaft', name: 'Crankshaft', category: 'Powertrain Mechanics' },
    { id: 'piston-1', name: 'Piston #1', category: 'Combustion Mechanics' },
    { id: 'piston-2', name: 'Piston #2', category: 'Combustion Mechanics' },
    { id: 'piston-3', name: 'Piston #3', category: 'Combustion Mechanics' },
    { id: 'piston-4', name: 'Piston #4', category: 'Combustion Mechanics' },
    { id: 'spark-plug-1', name: 'Spark Plug #1', category: 'Electrical / Ignition' },
    { id: 'drive-gear', name: 'Drive Spur Gear', category: 'Transmission Mechanics' },
    { id: 'driven-gear', name: 'Driven Reduction Gear', category: 'Transmission Mechanics' },
  ];

  const hudBg = isLight
    ? 'bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-xl shadow-slate-200/50 text-slate-700'
    : 'bg-slate-900/85 backdrop-blur-md border border-slate-800 shadow-xl text-slate-300';

  return (
    <div className="relative w-full h-full min-h-0 flex-1 flex">
      <ModelViewer
        theme={theme}
        lightingPreset="studio"
        cameraPosition={[3, 3, 5]}
        cameraTarget={[0, 0.5, 0]}
        cameraFov={45}
        selectedObject={selectedPart}
        onSelectObject={handleSelect}
        onAskAiTutor={onAskAiTutor}
        enableShadows={true}
        className="w-full h-full flex-1"
      >
        <EngineMechanicsModel
          selectedId={selectedPart?.id}
          onSelect={handleSelect}
          rpm={rpm}
          isExploded={isExploded}
          isPaused={isPaused}
        />
      </ModelViewer>

      {/* Engineering Control HUD Overlay (Top Left) */}
      <div className={`absolute top-4 left-4 z-10 flex flex-wrap items-center gap-2 px-3.5 py-2 rounded-2xl text-xs ${hudBg}`}>
        {/* RPM Speed Control */}
        <div className="flex items-center gap-1.5">
          <Gauge className={`w-3.5 h-3.5 ${isLight ? 'text-blue-600' : 'text-cyan-400'}`} />
          <span className={`font-bold ${isLight ? 'text-blue-700' : 'text-cyan-400'}`}>RPM:</span>
          {[30, 60, 120, 240].map((speed) => (
            <button
              key={speed}
              onClick={() => setRpm(speed)}
              className={`px-2 py-0.5 rounded-lg font-semibold transition-all ${
                rpm === speed
                  ? (isLight ? 'bg-blue-600 text-white font-bold' : 'bg-cyan-500 text-slate-950 font-bold')
                  : (isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-slate-800 text-slate-400 hover:text-slate-200')
              }`}
            >
              {speed}
            </button>
          ))}
        </div>

        <div className={`w-[1px] h-3.5 mx-1 ${isLight ? 'bg-slate-200' : 'bg-slate-700'}`} />

        {/* Exploded View Dissection Toggle */}
        <button
          onClick={() => setIsExploded((prev) => !prev)}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-xl font-bold transition-all ${
            isExploded
              ? 'bg-purple-600 text-white shadow-md shadow-purple-500/25'
              : (isLight ? 'bg-slate-100 text-slate-700 hover:bg-slate-200' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')
          }`}
        >
          <Split className="w-3.5 h-3.5" />
          {isExploded ? 'Exploded View (ON)' : 'Explode Engine'}
        </button>

        <div className={`w-[1px] h-3.5 mx-1 ${isLight ? 'bg-slate-200' : 'bg-slate-700'}`} />

        {/* Play / Pause Toggle */}
        <button
          onClick={() => setIsPaused((prev) => !prev)}
          className={`p-1.5 rounded-lg transition-colors ${
            isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
          }`}
          title={isPaused ? 'Resume Engine' : 'Pause Engine'}
        >
          {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Interactive Quick-Select Engine Parts List (Bottom Left) */}
      <div className={`absolute bottom-4 left-4 z-10 max-w-md p-2.5 rounded-2xl ${hudBg} hidden sm:block`}>
        <div className="flex items-center gap-1.5 mb-1.5 px-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-200">
            Inspect Engine Components:
          </span>
        </div>
        <div className="flex flex-wrap gap-1">
          {engineParts.map((part) => {
            const isSelected = selectedPart?.id === part.id;
            return (
              <button
                key={part.id}
                onClick={() => handleSelect(part)}
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
