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
 * Unifies R3F Canvas, GLTF/GLB loading, OrbitControls, lighting rigs, 
 * HUD controls, spatial labels, and AI Tutor handshake integration.
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
  backgroundColor = 'transparent',
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

  return (
    <div className={`relative w-full h-full min-h-[400px] select-none overflow-hidden rounded-2xl bg-slate-950/90 border border-slate-800 ${className}`}>
      <ErrorBoundary>
        <Canvas
          shadows={enableShadows}
          camera={{ position: cameraPosition, fov: cameraFov }}
          style={{ background: backgroundColor }}
          gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
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
                opacity={0.5}
                scale={10}
                blur={1.5}
                far={4}
              />
            )}
          </Suspense>
        </Canvas>
      </ErrorBoundary>

      {/* Floating HUD Control Toolbar */}
      {showHUDControls && (
        <ModelControls
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
        selectedObject={activeSelected}
        onClose={() => handleObjectSelect(null)}
        onAskAiTutor={onAskAiTutor}
      />
    </div>
  );
}
