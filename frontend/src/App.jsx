import React from 'react';
import Learning3DView from './features/learning/Learning3DView.jsx';
import { Cuboid as Cube3d, Sparkles } from 'lucide-react';

/**
 * Inteliedu App Shell - 3D Interactive Learning Foundation Preview
 */
export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-start p-4 md:p-8">
      {/* Header */}
      <header className="max-w-5xl w-full flex flex-col md:flex-row items-center justify-between gap-4 pb-6 mb-4 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-1.5 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20">
              <Cube3d className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-blue-300 to-indigo-400 bg-clip-text text-transparent">
              Inteliedu 3D
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Foundation Active
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Interactive 3D Learning System • OrbitControls • Raycasting Selection • AI Tutor Handshake
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Click any 3D object to inspect metadata</span>
        </div>
      </header>

      {/* Main 3D Canvas Viewport */}
      <main className="max-w-5xl w-full">
        <Learning3DView />
      </main>
    </div>
  );
}
