import React, { useState } from 'react';
import { 
  SolarSystemScene, 
  AnatomyScene, 
  EngineeringScene, 
  LearningScene 
} from '@threejs';
import { 
  Globe, 
  User, 
  Cog, 
  Sparkles, 
  Cuboid as Cube3d, 
  BrainCircuit, 
  X
} from 'lucide-react';

/**
 * Enhanced Learning3DView Feature Component
 * Provides an interactive 3D curriculum switcher with Light Theme aesthetics and real-time AI Tutor handshake simulation
 */
export default function Learning3DView({ theme = 'light' }) {
  const [activeTab, setActiveTab] = useState('human'); // Defaults to the 3D Human Teacher & Anatomy!
  const [aiTutorPrompt, setAiTutorPrompt] = useState(null);

  const isLight = theme === 'light';

  const handleAskAiTutor = (data) => {
    const { selectedObject } = data;
    setAiTutorPrompt({
      object: selectedObject,
      timestamp: new Date().toLocaleTimeString(),
      sampleExplanation: generateSampleAiResponse(selectedObject),
    });
  };

  const generateSampleAiResponse = (obj) => {
    return `Hello! I am your Inteliedu AI Tutor. Let's analyze ${obj.name}. In ${obj.category}, ${obj.description} Would you like an interactive step-by-step quiz or an in-depth Socratic breakdown?`;
  };

  const sceneTabs = [
    {
      id: 'human',
      title: '3D Human Teacher & Anatomy',
      icon: User,
      badge: 'Interactive Avatar',
    },
    {
      id: 'solar',
      title: 'Solar System & Orbits',
      icon: Globe,
      badge: '8 Planets + Sun',
    },
    {
      id: 'engineering',
      title: 'Engineering Mechanics',
      icon: Cog,
      badge: '4-Cyl Engine & Gears',
    },
    {
      id: 'overview',
      title: 'Concepts Overview',
      icon: Cube3d,
      badge: 'Multi-Disciplinary',
    },
  ];

  const tabContainerStyle = isLight
    ? 'bg-white/90 backdrop-blur-xl border border-slate-200/90 shadow-sm'
    : 'bg-slate-900/90 backdrop-blur-xl border border-slate-800 shadow-xl';

  const activeTabStyle = isLight
    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25 scale-[1.01]'
    : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25 scale-[1.01]';

  const inactiveTabStyle = isLight
    ? 'bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200/80'
    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800';

  return (
    <div className="w-full h-full flex flex-col min-h-0 flex-1 space-y-2 p-2 sm:p-4">
      {/* 1. Scene Navigation Tabs Bar */}
      <div className={`flex flex-wrap items-center justify-between gap-2 p-2 rounded-2xl transition-colors duration-200 ${tabContainerStyle}`}>
        <div className="flex flex-wrap items-center gap-1.5">
          {sceneTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 select-none ${
                  isActive ? activeTabStyle : inactiveTabStyle
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : (isLight ? 'text-slate-500' : 'text-slate-400')}`} />
                <span>{tab.title}</span>
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    isActive 
                      ? 'bg-white/20 text-white' 
                      : (isLight ? 'bg-slate-200/80 text-slate-600' : 'bg-slate-700/60 text-slate-400')
                  }`}
                >
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </div>

        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-[11px] font-semibold ${
          isLight ? 'bg-slate-100 text-slate-600 border border-slate-200' : 'bg-slate-950/60 text-slate-400 border border-slate-800/80'
        }`}>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>60 FPS WebGL Engine Active</span>
        </div>
      </div>

      {/* 2. Responsive Full-Height 3D Viewport */}
      <div className="w-full flex-1 min-h-0 relative rounded-2xl overflow-hidden shadow-xl border border-slate-200/80 bg-slate-50 flex">
        {activeTab === 'human' && <AnatomyScene theme={theme} onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'solar' && <SolarSystemScene theme={theme} onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'engineering' && <EngineeringScene theme={theme} onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'overview' && <LearningScene theme={theme} onAskAiTutor={handleAskAiTutor} />}
      </div>

      {/* 3. AI Tutor Interactive Conversation & Handshake Bridge */}
      {aiTutorPrompt && (
        <div className={`w-full rounded-2xl p-3.5 shadow-xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-2 transition-all ${
          isLight
            ? 'bg-white/95 border border-indigo-200 shadow-indigo-100 text-slate-800'
            : 'bg-slate-900/90 border border-indigo-500/40 text-slate-100'
        }`}>
          <div className="flex items-start justify-between gap-4 mb-2">
            <div className="flex items-center gap-2">
              <div className={`p-2 rounded-xl ${isLight ? 'bg-indigo-100 text-indigo-700' : 'bg-indigo-500/20 text-indigo-400'}`}>
                <BrainCircuit className="w-4 h-4 text-indigo-600 animate-pulse" />
              </div>
              <div>
                <h4 className={`text-[11px] font-extrabold uppercase tracking-wider flex items-center gap-1.5 ${isLight ? 'text-indigo-700' : 'text-indigo-300'}`}>
                  <Sparkles className="w-3.5 h-3.5 text-yellow-500" />
                  AI Tutor Handshake Active
                </h4>
                <p className="text-xs font-bold">
                  Context Linked: <span className={isLight ? 'text-blue-600' : 'text-cyan-300'}>{aiTutorPrompt.object.name}</span> ({aiTutorPrompt.object.category})
                </p>
              </div>
            </div>

            <button
              onClick={() => setAiTutorPrompt(null)}
              className={`p-1 rounded-lg text-xs transition-colors ${
                isLight ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
              title="Dismiss AI Prompt"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className={`rounded-xl p-2.5 text-xs leading-relaxed font-medium ${
            isLight ? 'bg-slate-50 border border-slate-200/80 text-slate-700' : 'bg-slate-950/70 border border-indigo-500/20 text-slate-300'
          }`}>
            <p>{aiTutorPrompt.sampleExplanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
