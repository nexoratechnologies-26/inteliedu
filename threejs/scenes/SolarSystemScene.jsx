import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import SolarSystemModel from '../models/solar-system/SolarSystemModel.jsx';
import { Sparkles } from 'lucide-react';

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

  const planetList = [
    { id: 'sun', name: 'Sun', category: 'Star' },
    { id: 'mercury', name: 'Mercury', category: 'Planet' },
    { id: 'venus', name: 'Venus', category: 'Planet' },
    { id: 'earth', name: 'Earth', category: 'Planet' },
    { id: 'mars', name: 'Mars', category: 'Planet' },
    { id: 'jupiter', name: 'Jupiter', category: 'Planet' },
    { id: 'saturn', name: 'Saturn', category: 'Planet' },
    { id: 'uranus', name: 'Uranus', category: 'Planet' },
    { id: 'neptune', name: 'Neptune', category: 'Planet' },
  ];

  const hudBg = isLight
    ? 'bg-white/95 backdrop-blur-md border border-slate-200/90 shadow-xl shadow-slate-200/50 text-slate-700'
    : 'bg-slate-900/85 backdrop-blur-md border border-slate-800 shadow-xl text-slate-300';

  return (
    <div className="relative w-full h-full min-h-0 flex-1 flex">
      <ModelViewer
        theme={theme}
        lightingPreset="space"
        cameraPosition={[0, 18, 30]}
        cameraFov={50}
        selectedObject={selectedPlanet}
        onSelectObject={handleSelect}
        onAskAiTutor={onAskAiTutor}
        enableShadows={false}
        className="w-full h-full flex-1"
      >
        <SolarSystemModel
          selectedId={selectedPlanet?.id}
          onSelect={handleSelect}
          isPaused={isPaused}
          speedMultiplier={speedMultiplier}
        />
      </ModelViewer>

      {/* Orbit Speed & Time Controls Overlay (Top Left) */}
      <div className={`absolute top-4 left-4 z-10 flex items-center gap-2 px-3.5 py-2 rounded-2xl text-xs ${hudBg}`}>
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

      {/* Interactive Quick-Select Planets List (Bottom Left) */}
      <div className={`absolute bottom-4 left-4 z-10 max-w-md p-2.5 rounded-2xl ${hudBg} hidden sm:block`}>
        <div className="flex items-center gap-1.5 mb-1.5 px-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-200">
            Select Celestial Body:
          </span>
        </div>
        <div className="flex flex-wrap gap-1">
          {planetList.map((planet) => {
            const isSelected = selectedPlanet?.id === planet.id;
            return (
              <button
                key={planet.id}
                onClick={() => handleSelect(planet)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all active:scale-95 ${
                  isSelected
                    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/30'
                    : isLight
                    ? 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                }`}
              >
                {planet.name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
