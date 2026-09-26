import React, { useState } from 'react';
import ModelViewer from '../components/ModelViewer.jsx';
import InteractiveObject from '../components/InteractiveObject.jsx';
import AnimationController from '../animations/AnimationController.jsx';

/**
 * Educational Interactive Demonstration Scene
 * Features interactive celestial, mechanical, and physical 3D objects with click selection,
 * hover glow, spatial labels, OrbitControls, and AI Tutor information integration.
 */
export default function LearningScene({ onAskAiTutor, onObjectSelect }) {
  const [selectedObject, setSelectedObject] = useState(null);

  const handleSelect = (obj) => {
    setSelectedObject(obj);
    if (onObjectSelect) {
      onObjectSelect(obj);
    }
  };

  return (
    <ModelViewer
      lightingPreset="studio"
      cameraPosition={[0, 3, 7]}
      selectedObject={selectedObject}
      onSelectObject={handleSelect}
      onAskAiTutor={onAskAiTutor}
      enableShadows={true}
      className="w-full h-full min-h-[500px]"
    >
      {/* 1. Earth Planetary Body */}
      <AnimationController rotationSpeed={0.3} rotationAxis={[0, 1, 0]}>
        <InteractiveObject
          id="earth"
          name="Earth (Terra)"
          category="Astronomy"
          description="Earth is the third planet from the Sun and the only astronomical object known to harbor life. It has a dense iron core, liquid water oceans, and an active nitrogen-oxygen atmosphere."
          metadata={{
            diameter: '12,742 km',
            orbital_period: '365.25 days',
            gravity: '9.807 m/s²',
            atmosphere: '78% N₂, 21% O₂',
          }}
          position={[-2.2, 0.8, 0]}
          color="#0284c7"
          emissiveColor="#38bdf8"
          isSelected={selectedObject?.id === 'earth'}
          onSelect={handleSelect}
        >
          <mesh castShadow receiveShadow>
            <sphereGeometry args={[0.9, 32, 32]} />
            <meshStandardMaterial
              color="#0284c7"
              roughness={0.4}
              metalness={0.1}
              emissive={selectedObject?.id === 'earth' ? '#38bdf8' : '#000000'}
              emissiveIntensity={selectedObject?.id === 'earth' ? 0.6 : 0}
            />
          </mesh>
        </InteractiveObject>
      </AnimationController>

      {/* Orbiting Moon around Earth */}
      <AnimationController
        orbitRadius={1.6}
        orbitSpeed={0.8}
        rotationSpeed={0.5}
        orbitInclination={0.2}
      >
        <InteractiveObject
          id="moon"
          name="The Moon (Luna)"
          category="Astronomy"
          description="Earth's only natural satellite. In synchronous rotation with Earth, always showing the same near side."
          metadata={{
            diameter: '3,474 km',
            orbital_period: '27.3 days',
            gravity: '1.62 m/s²',
          }}
          position={[-2.2, 0.8, 0]}
          scale={[0.3, 0.3, 0.3]}
          color="#cbd5e1"
          emissiveColor="#f8fafc"
          isSelected={selectedObject?.id === 'moon'}
          onSelect={handleSelect}
        >
          <mesh castShadow receiveShadow>
            <sphereGeometry args={[0.4, 24, 24]} />
            <meshStandardMaterial
              color="#94a3b8"
              roughness={0.8}
              metalness={0.1}
              emissive={selectedObject?.id === 'moon' ? '#f8fafc' : '#000000'}
              emissiveIntensity={selectedObject?.id === 'moon' ? 0.5 : 0}
            />
          </mesh>
        </InteractiveObject>
      </AnimationController>

      {/* 2. Mechanical Gear / Engineering Rotor */}
      <AnimationController rotationSpeed={-0.6} rotationAxis={[0, 0, 1]}>
        <InteractiveObject
          id="engineering-rotor"
          name="Turbine Spur Gear"
          category="Engineering"
          description="A precision cylindrical mechanical gear used in aerospace turbines to transfer rotational torque and mechanical energy."
          metadata={{
            material: 'Titanium-Alloy 6Al-4V',
            tooth_count: '16 Teethed Spur',
            gear_ratio: '3.5:1',
            max_rpm: '12,000 RPM',
          }}
          position={[0, 0.8, 0]}
          color="#a855f7"
          emissiveColor="#c084fc"
          isSelected={selectedObject?.id === 'engineering-rotor'}
          onSelect={handleSelect}
        >
          <mesh castShadow receiveShadow>
            <torusGeometry args={[0.7, 0.22, 16, 24]} />
            <meshStandardMaterial
              color="#7c3aed"
              metalness={0.8}
              roughness={0.2}
              emissive={selectedObject?.id === 'engineering-rotor' ? '#c084fc' : '#000000'}
              emissiveIntensity={selectedObject?.id === 'engineering-rotor' ? 0.6 : 0}
            />
          </mesh>
        </InteractiveObject>
      </AnimationController>

      {/* 3. Biological Cellular Nucleus / Anatomy Core */}
      <AnimationController rotationSpeed={0.4} rotationAxis={[1, 1, 0]}>
        <InteractiveObject
          id="cell-nucleus"
          name="Cellular Nucleus"
          category="Human Anatomy / Biology"
          description="The membrane-bound organelle within eukaryotic cells that contains genetic chromosomes and regulates cellular metabolism, growth, and gene expression."
          metadata={{
            membrane_type: 'Double Phospholipid Bilayer',
            nuclear_pores: '~3,000 Pores',
            contents: 'DNA, Histones, Nucleolus',
          }}
          position={[2.2, 0.8, 0]}
          color="#10b981"
          emissiveColor="#34d399"
          isSelected={selectedObject?.id === 'cell-nucleus'}
          onSelect={handleSelect}
        >
          <mesh castShadow receiveShadow>
            <octahedronGeometry args={[0.8, 2]} />
            <meshStandardMaterial
              color="#059669"
              roughness={0.3}
              metalness={0.3}
              wireframe={false}
              emissive={selectedObject?.id === 'cell-nucleus' ? '#34d399' : '#000000'}
              emissiveIntensity={selectedObject?.id === 'cell-nucleus' ? 0.6 : 0}
            />
          </mesh>
        </InteractiveObject>
      </AnimationController>
    </ModelViewer>
  );
}
