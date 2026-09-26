import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import SolarSystemModel from '../models/solar-system/SolarSystemModel.jsx';

/**
 * SolarSystemScene
 * Complete interactive 3D Solar System with planetary orbits, rotation,
 * speed control, object selection, labels, and AI Tutor question generation.
 */
export default function SolarSystemScene({
  theme = 'light',
  onAskAiTutor,
  onObjectSelect,
  initialSpeed = 1.0,
}) {
  const [selectedPlanet, setSelectedPlanet] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [speedMultiplier, setSpeedMultiplier] = useState(initialSpeed);

  const isLight = theme === 'light';

  const handleSelect = (planet) => {
    setSelectedPlanet(planet);
    if (onObjectSelect) {
      onObjectSelect(planet);
    }
  };

  const hudBg = isLight
    ? 'bg-white/90 backdrop-blur-md border border-slate-200 shadow-xl shadow-slate-200/50 text-slate-700'
    : 'bg-slate-900/85 backdrop-blur-md border border-slate-800 shadow-xl text-slate-300';

  return (
    <div className="relative w-full h-full min-h-0 flex-1">
      <ModelViewer
        theme={theme}
        lightingPreset="space"
        cameraPosition={[0, 18, 30]}
        cameraFov={50}
        selectedObject={selectedPlanet}
        onSelectObject={handleSelect}
        onAskAiTutor={onAskAiTutor}
        enableShadows={false}
        className="w-full h-full"
      >
        <SolarSystemModel
          selectedId={selectedPlanet?.id}
          onSelect={handleSelect}
          isPaused={isPaused}
          speedMultiplier={speedMultiplier}
        />
      </ModelViewer>

      {/* Orbit Speed & Time Controls Overlay */}
      <div className={`absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-2 rounded-2xl text-xs ${hudBg}`}>
        <span className={`font-bold ${isLight ? 'text-blue-700' : 'text-cyan-400'}`}>
          Orbit Speed:
        </span>
        {[0.5, 1.0, 2.0, 4.0].map((spd) => (
          <button
            key={spd}
            onClick={() => setSpeedMultiplier(spd)}
            className={`px-2 py-0.5 rounded-lg font-semibold transition-all ${
              speedMultiplier === spd
                ? (isLight ? 'bg-blue-600 text-white font-bold' : 'bg-cyan-500 text-slate-950 font-bold')
                : (isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-slate-800 text-slate-400 hover:text-slate-200')
            }`}
          >
            {spd}x
          </button>
        ))}
        <div className={`w-[1px] h-3.5 mx-1 ${isLight ? 'bg-slate-200' : 'bg-slate-700'}`} />
        <button
          onClick={() => setIsPaused((prev) => !prev)}
          className={`px-2.5 py-0.5 rounded-lg text-xs font-semibold transition-all ${
            isPaused
              ? 'bg-amber-500/20 text-amber-600 border border-amber-500/30'
              : (isLight ? 'bg-slate-100 text-slate-700 hover:bg-slate-200' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')
          }`}
        >
          {isPaused ? '▶ Resume' : '⏸ Pause'}
        </button>
      </div>
    </div>
  );
}
