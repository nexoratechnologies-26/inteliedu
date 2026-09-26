import React, { useState } from 'react';
import Learning3DView from './features/learning/Learning3DView.jsx';
import { Cuboid as Cube3d, Sun, Moon, Sparkles } from 'lucide-react';

/**
 * Inteliedu Main App Shell
 * Responsive full-screen 3D viewport with Light Theme and Theme Switcher
 */
export default function App() {
  const [theme, setTheme] = useState('light'); // Defaults to Light Theme!

  const isLight = theme === 'light';

  return (
    <div className={`w-screen h-screen overflow-hidden flex flex-col transition-colors duration-300 ${
      isLight ? 'bg-slate-50 text-slate-900' : 'bg-slate-950 text-slate-50'
    }`}>
      {/* 1. Sleek Compact Top Bar */}
      <header className={`w-full flex items-center justify-between px-4 py-2.5 border-b transition-colors duration-200 z-30 ${
        isLight ? 'bg-white border-slate-200/90 shadow-sm' : 'bg-slate-900 border-slate-800'
      }`}>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 text-white shadow-md shadow-blue-500/20">
            <Cube3d className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 bg-clip-text text-transparent">
                Inteliedu 3D
              </h1>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                isLight ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              }`}>
                Light Mode Active
              </span>
            </div>
            <p className={`text-[11px] font-medium hidden sm:block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              Interactive 3D Learning Platform • 3D Human Teacher • Solar System • Engineering Mechanics
            </p>
          </div>
        </div>

        {/* Right Action Controls & Theme Toggle */}
        <div className="flex items-center gap-2">
          <div className={`hidden md:flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl border ${
            isLight ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-slate-800 border-slate-700 text-slate-300'
          }`}>
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Click any 3D part to inspect</span>
          </div>

          <button
            onClick={() => setTheme(isLight ? 'dark' : 'light')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 border ${
              isLight
                ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
            }`}
            title="Toggle Light / Dark Theme"
          >
            {isLight ? <Moon className="w-4 h-4 text-indigo-600" /> : <Sun className="w-4 h-4 text-yellow-400" />}
            <span>{isLight ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
        </div>
      </header>

      {/* 2. Responsive Full-Screen 3D Workspace */}
      <main className="flex-1 w-full h-full min-h-0 flex flex-col overflow-hidden">
        <Learning3DView theme={theme} />
      </main>
    </div>
  );
}
