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
  CheckCircle2,
  HelpCircle,
  Maximize2
} from 'lucide-react';

/**
 * Enhanced Learning3DView Feature Component
 * Provides an interactive 3D curriculum switcher with real-time AI Tutor handshake simulation
 */
export default function Learning3DView() {
  const [activeTab, setActiveTab] = useState('human'); // default to the requested 3D Human Teacher!
  const [aiTutorPrompt, setAiTutorPrompt] = useState(null);
  const [selectedItemHistory, setSelectedItemHistory] = useState([]);

  const handleAskAiTutor = (data) => {
    const { selectedObject } = data;
    setAiTutorPrompt({
      object: selectedObject,
      timestamp: new Date().toLocaleTimeString(),
      sampleExplanation: generateSampleAiResponse(selectedObject),
    });
    setSelectedItemHistory((prev) => [selectedObject.name, ...prev.slice(0, 4)]);
  };

  const generateSampleAiResponse = (obj) => {
    return `Hello! As your AI Tutor, let's explore ${obj.name}. In ${obj.category}, ${obj.description} Would you like a step-by-step interactive quiz or deeper explanation on this component?`;
  };

  const sceneTabs = [
    {
      id: 'human',
      title: '3D Human Teacher & Anatomy',
      icon: User,
      badge: 'Interactive Avatar',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      id: 'solar',
      title: 'Solar System & Orbits',
      icon: Globe,
      badge: '8 Planets + Sun',
      color: 'from-amber-500 to-orange-500',
    },
    {
      id: 'engineering',
      title: 'Engineering Mechanics',
      icon: Cog,
      badge: '4-Cyl Engine & Gears',
      color: 'from-purple-500 to-indigo-500',
    },
    {
      id: 'overview',
      title: 'Concepts Overview',
      icon: Cube3d,
      badge: 'Multi-Disciplinary',
      color: 'from-emerald-500 to-teal-500',
    },
  ];

  return (
    <div className="w-full flex flex-col space-y-4">
      {/* 1. Scene Navigation Tabs Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-900/90 backdrop-blur-xl border border-slate-800 p-2 rounded-2xl shadow-xl">
        <div className="flex flex-wrap items-center gap-1.5">
          {sceneTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-200 select-none ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25 scale-[1.02]'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-300' : 'text-slate-400'}`} />
                <span>{tab.title}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                    isActive ? 'bg-white/20 text-white' : 'bg-slate-700/60 text-slate-400'
                  }`}
                >
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-950/60 border border-slate-800/80 rounded-xl text-[11px] text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>60 FPS WebGL Engine Active</span>
        </div>
      </div>

      {/* 2. Main 3D Viewport */}
      <div className="w-full h-[580px] relative rounded-3xl overflow-hidden shadow-2xl border border-slate-800/80 bg-slate-950">
        {activeTab === 'human' && <AnatomyScene onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'solar' && <SolarSystemScene onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'engineering' && <EngineeringScene onAskAiTutor={handleAskAiTutor} />}
        {activeTab === 'overview' && <LearningScene onAskAiTutor={handleAskAiTutor} />}
      </div>

      {/* 3. AI Tutor Interactive Conversation & Handshake Bridge */}
      {aiTutorPrompt && (
        <div className="w-full bg-gradient-to-r from-slate-900/90 via-indigo-950/80 to-slate-900/90 border border-indigo-500/40 rounded-2xl p-4 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-3 text-slate-100">
          <div className="flex items-start justify-between gap-4 mb-2">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <BrainCircuit className="w-5 h-5 text-cyan-300 animate-pulse" />
              </div>
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                  AI Tutor Handshake Active
                </h4>
                <p className="text-sm font-semibold text-white">
                  Context Linked: <span className="text-cyan-300">{aiTutorPrompt.object.name}</span> ({aiTutorPrompt.object.category})
                </p>
              </div>
            </div>

            <button
              onClick={() => setAiTutorPrompt(null)}
              className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 bg-slate-800/60 rounded-lg"
            >
              Dismiss
            </button>
          </div>

          <div className="bg-slate-950/70 border border-indigo-500/20 rounded-xl p-3 text-xs text-slate-300 leading-relaxed">
            <p>{aiTutorPrompt.sampleExplanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
