/**
 * Inteliedu 3D Module - Main Public Exports
 * Domain Owner: Trivin (3D Developer)
 */

// Core 3D Components
export { default as ModelViewer } from './components/ModelViewer.jsx';
export { default as InteractiveObject } from './components/InteractiveObject.jsx';
export { default as ObjectInfoPanel } from './components/ObjectInfoPanel.jsx';
export { default as ModelControls } from './components/ModelControls.jsx';
export { default as LoadingScreen } from './components/LoadingScreen.jsx';
export { default as ErrorBoundary } from './components/ErrorBoundary.jsx';

// Interactive Learning Scenes
export { default as LearningScene } from './scenes/LearningScene.jsx';
export { default as SolarSystemScene } from './scenes/SolarSystemScene.jsx';
export { default as AnatomyScene } from './scenes/AnatomyScene.jsx';
export { default as EngineeringScene } from './scenes/EngineeringScene.jsx';

// Procedural 3D Models
export { default as SolarSystemModel } from './models/solar-system/SolarSystemModel.jsx';
export { default as InteractiveHumanModel } from './models/human-anatomy/InteractiveHumanModel.jsx';
export { default as EngineMechanicsModel } from './models/engineering/EngineMechanicsModel.jsx';

// Controls
export { default as CameraControls } from './controls/CameraControls.jsx';
export { default as OrbitControls } from './controls/OrbitControls.jsx';

// Labels
export { default as ObjectLabel } from './labels/ObjectLabel.jsx';
export { default as LabelManager } from './labels/LabelManager.jsx';

// Animations
export { default as AnimationController } from './animations/AnimationController.jsx';
export * from './animations/animationUtils.js';

// Loaders & Utilities
export { default as ModelLoader } from './loaders/ModelLoader.jsx';
export * from './loaders/modelUtils.js';
export * from './materials/materials.js';
export * from './utils/sceneUtils.js';
export * from './utils/cameraUtils.js';
export * from './utils/modelUtils.js';
export * from './utils/textureGenerator.js';
