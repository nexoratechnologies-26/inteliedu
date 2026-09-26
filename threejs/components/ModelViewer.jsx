import React, { Suspense, useState, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Center, ContactShadows, Float } from '@react-three/drei';
import ErrorBoundary from './ErrorBoundary.jsx';
import LoadingScreen from './LoadingScreen.jsx';
import CameraControls from '../controls/CameraControls.jsx';
import ModelControls from './ModelControls.jsx';
import ObjectInfoPanel from './ObjectInfoPanel.jsx';
import ModelLoader from '../loaders/ModelLoader.jsx';
import { LIGHTING_PRESETS } from '../utils/sceneUtils.js';

/**
 * Reusable Educational 3D Model Viewer
 * Supports Full-screen responsive viewport, Light & Dark themes, OrbitControls,
 * lighting rigs, floating HUD controls, spatial labels, and AI Tutor handshake integration.
 */
export default function ModelViewer({
  model = null,
  scale = 1,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  cameraPosition = [0, 2, 6],
  cameraTarget = [0, 0, 0],
  cameraFov = 45,
  lightingPreset = 'studio',
  enableShadows = true,
  enableFloat = false,
  showHUDControls = true,
  showLabels = true,
  autoCenter = true,
  theme = 'light', // 'light' | 'dark'
  onSelectObject = null,
  selectedObject = null,
  onAskAiTutor = null,
  className = '',
  children,
}) {
  const [internalSelected, setInternalSelected] = useState(null);
  const [isAutoRotating, setIsAutoRotating] = useState(false);
  const [isWireframe, setIsWireframe] = useState(false);
  const [labelsVisible, setLabelsVisible] = useState(showLabels);
  const controlsRef = useRef(null);

  const activeSelected = selectedObject !== undefined ? selectedObject : internalSelected;

  const handleObjectSelect = (obj) => {
    setInternalSelected(obj);
    if (onSelectObject) {
      onSelectObject(obj);
    }
  };

  const handleResetCamera = () => {
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  const activeLighting = LIGHTING_PRESETS[lightingPreset] || LIGHTING_PRESETS.studio;
  const isLightTheme = theme === 'light';

  const canvasBgColor = isLightTheme 
    ? (lightingPreset === 'space' ? '#090d16' : '#f8fafc')
    : '#020617';

  return (
    <div
      className={`relative w-full h-full flex-1 min-h-0 select-none overflow-hidden rounded-2xl transition-colors duration-300 ${
        isLightTheme 
          ? 'bg-slate-50 border border-slate-200/80 shadow-inner' 
          : 'bg-slate-950 border border-slate-800'
      } ${className}`}
    >
      <ErrorBoundary>
        <Canvas
          shadows={enableShadows}
          camera={{ position: cameraPosition, fov: cameraFov }}
          style={{ width: '100%', height: '100%', background: canvasBgColor }}
          gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
          resize={{ scroll: false, debounce: { scroll: 50, resize: 0 } }}
        >
          {/* Lighting Rig */}
          <ambientLight
            color={activeLighting.ambient.color}
            intensity={activeLighting.ambient.intensity}
          />
          {activeLighting.directional.map((dirLight, idx) => (
            <directionalLight
              key={idx}
              position={dirLight.position}
              intensity={dirLight.intensity}
              color={dirLight.color || '#ffffff'}
              castShadow={enableShadows && dirLight.castShadow}
              shadow-mapSize-width={1024}
              shadow-mapSize-height={1024}
            />
          ))}
          {activeLighting.point.map((ptLight, idx) => (
            <pointLight
              key={idx}
              position={ptLight.position}
              intensity={ptLight.intensity}
              color={ptLight.color || '#ffffff'}
            />
          ))}

          {/* Camera Controls */}
          <CameraControls
            defaultPosition={cameraPosition}
            defaultTarget={cameraTarget}
            autoRotate={isAutoRotating}
            controlsRef={controlsRef}
          />

          {/* Asynchronous Model Loading with Suspense */}
          <Suspense fallback={<LoadingScreen />}>
            <Center top>
              {enableFloat ? (
                <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
                  {model && (
                    <ModelLoader
                      url={model}
                      scale={scale}
                      position={position}
                      rotation={rotation}
                      autoCenter={autoCenter}
                      wireframe={isWireframe}
                      onSelectPart={handleObjectSelect}
                      selectedPartId={activeSelected?.id}
                    />
                  )}
                  {children}
                </Float>
              ) : (
                <>
                  {model && (
                    <ModelLoader
                      url={model}
                      scale={scale}
                      position={position}
                      rotation={rotation}
                      autoCenter={autoCenter}
                      wireframe={isWireframe}
                      onSelectPart={handleObjectSelect}
                      selectedPartId={activeSelected?.id}
                    />
                  )}
                  {children}
                </>
              )}
            </Center>

            {/* Subtle Ground Contact Shadow */}
            {enableShadows && (
              <ContactShadows
                position={[0, -0.05, 0]}
                opacity={isLightTheme ? 0.35 : 0.6}
                scale={12}
                blur={1.8}
                far={5}
                color={isLightTheme ? '#475569' : '#000000'}
              />
            )}
          </Suspense>
        </Canvas>
      </ErrorBoundary>

      {/* Floating HUD Control Toolbar */}
      {showHUDControls && (
        <ModelControls
          theme={theme}
          onResetCamera={handleResetCamera}
          isAutoRotating={isAutoRotating}
          onToggleAutoRotate={() => setIsAutoRotating((prev) => !prev)}
          showLabels={labelsVisible}
          onToggleLabels={() => setLabelsVisible((prev) => !prev)}
          isWireframe={isWireframe}
          onToggleWireframe={() => setIsWireframe((prev) => !prev)}
          hasSelection={Boolean(activeSelected)}
          onResetSelection={() => handleObjectSelect(null)}
        />
      )}

      {/* Object Metadata & AI Tutor Inspection Panel */}
      <ObjectInfoPanel
        theme={theme}
        selectedObject={activeSelected}
        onClose={() => handleObjectSelect(null)}
        onAskAiTutor={onAskAiTutor}
      />
    </div>
  );
}
