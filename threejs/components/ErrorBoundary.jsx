import React, { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * 3D Viewport Error Boundary
 * Gracefully catches WebGL rendering exceptions or GLTF asset parse errors
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[3D ErrorBoundary] Caught WebGL/3D error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full min-h-[300px] flex flex-col items-center justify-center p-6 bg-slate-900/90 border border-red-500/30 rounded-2xl text-slate-200">
          <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4 text-red-400">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-slate-100 mb-1">
            Unable to load 3D Scene
          </h3>
          <p className="text-xs text-slate-400 max-w-sm text-center mb-4">
            {this.state.error?.message || 'A WebGL rendering error occurred while mounting the 3D model.'}
          </p>
          <button
            onClick={this.handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition-colors shadow-lg shadow-blue-500/20"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reload 3D Canvas
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
