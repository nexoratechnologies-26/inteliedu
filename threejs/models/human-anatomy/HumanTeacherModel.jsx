import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import InteractiveObject from '../../components/InteractiveObject.jsx';
import { generateTissueTexture } from '../../utils/textureGenerator.js';

/**
 * High-Fidelity 3D Human Teacher & Anatomy Model ("Dr. Maya")
 * Features realistic human facial anatomy, styled hair, doctor lab coat / teacher attire,
 * articulated hands with fingers, animated teaching gestures, heartbeat, and dissectible organ systems.
 */
export default function HumanTeacherModel({
  selectedId = null,
  onSelect = null,
  activeMode = 'teacher', // 'teacher' | 'xray' | 'anatomy'
  activeLayer = 'all',   // 'all' | 'nervous' | 'circulatory' | 'respiratory' | 'skeletal' | 'digestive'
  theme = 'light',
}) {
  const avatarRef = useRef(null);
  const headRef = useRef(null);
  const rightArmRef = useRef(null);
  const leftArmRef = useRef(null);
  const heartRef = useRef(null);
  const lungsRef = useRef(null);

  const tissueTexture = useMemo(() => generateTissueTexture(), []);

  // Frame-rate independent human breathing, heartbeat pulse, and teacher conversational gestures
  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    // 1. Natural Breathing Sway
    if (avatarRef.current) {
      avatarRef.current.position.y = Math.sin(t * 1.8) * 0.015 - 1.8;
    }

    // 2. Head Speaking Tilt & Eye Tracking
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(t * 0.7) * 0.08;
      headRef.current.rotation.x = Math.sin(t * 1.1) * 0.03;
      headRef.current.rotation.z = Math.sin(t * 0.5) * 0.02;
    }

    // 3. Right Hand Explanatory Teaching Gestures
    if (rightArmRef.current) {
      rightArmRef.current.rotation.z = -0.35 + Math.sin(t * 1.4) * 0.12;
      rightArmRef.current.rotation.x = 0.25 + Math.cos(t * 1.1) * 0.08;
    }

    // 4. Left Arm Subtle Posture
    if (leftArmRef.current) {
      leftArmRef.current.rotation.z = 0.25 + Math.sin(t * 0.9) * 0.04;
    }

    // 5. Cardiac Heartbeat Pulse (~72 BPM)
    if (heartRef.current) {
      const pulse = 1 + Math.sin(t * 7.5) * 0.07 + Math.sin(t * 15) * 0.03;
      heartRef.current.scale.set(pulse, pulse, pulse);
    }

    // 6. Lungs Respiratory Expansion
    if (lungsRef.current) {
      const breath = 1 + Math.sin(t * 1.8) * 0.06;
      lungsRef.current.scale.set(breath, breath, 1 + Math.sin(t * 1.8) * 0.08);
    }
  });

  const isAnatomyMode = activeMode === 'anatomy' || activeMode === 'xray';
  const skinOpacity = activeMode === 'teacher' ? 1.0 : activeMode === 'xray' ? 0.35 : 0.05;

  const showNervous = isAnatomyMode && (activeLayer === 'all' || activeLayer === 'nervous');
  const showCirculatory = isAnatomyMode && (activeLayer === 'all' || activeLayer === 'circulatory');
  const showRespiratory = isAnatomyMode && (activeLayer === 'all' || activeLayer === 'respiratory');
  const showSkeletal = isAnatomyMode && (activeLayer === 'all' || activeLayer === 'skeletal');
  const showDigestive = isAnatomyMode && (activeLayer === 'all' || activeLayer === 'digestive');

  // Realistic Human PBR Skin Material
  const skinMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#f3c7a7', // Warm realistic human skin tone
    roughness: 0.55,
    metalness: 0.05,
    transparent: skinOpacity < 1.0,
    opacity: skinOpacity,
  }), [skinOpacity]);

  // Dark Brown Hair Material
  const hairMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#2a1a12',
    roughness: 0.7,
    metalness: 0.1,
    transparent: skinOpacity < 1.0,
    opacity: skinOpacity,
  }), [skinOpacity]);

  // Teacher Doctor Lab Coat Material (Crisp White)
  const coatMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#ffffff',
    roughness: 0.6,
    metalness: 0.05,
    transparent: skinOpacity < 1.0,
    opacity: skinOpacity < 1.0 ? skinOpacity * 0.5 : 1.0,
  }), [skinOpacity]);

  // Professional Slacks / Trousers Material
  const pantsMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#1e293b',
    roughness: 0.6,
    metalness: 0.1,
    transparent: skinOpacity < 1.0,
    opacity: skinOpacity < 1.0 ? skinOpacity * 0.5 : 1.0,
  }), [skinOpacity]);

  return (
    <group ref={avatarRef} position={[0, -1.8, 0]}>
      {/* ========================================================================= */}
      {/* 1. HEAD, FACE & BRAIN (Realistic Human Features)                           */}
      {/* ========================================================================= */}
      <group ref={headRef} position={[0, 4.3, 0]}>
        {/* Head Cranium & Face */}
        <InteractiveObject
          id="head"
          name="Human Head & Facial Anatomy"
          category="Human Anatomy"
          description="Houses the brain, sensory organs (eyes, ears, nose, tongue), facial muscles for expression, and cranial nerves."
          metadata={{
            facial_muscles: '43 muscles responsible for expressions',
            cranial_bones: '8 Cranial, 14 Facial bones',
            sensory_inputs: 'Vision, Hearing, Olfaction, Gustation',
          }}
          isSelected={selectedId === 'head'}
          onSelect={onSelect}
        >
          <group>
            {/* Cranium Skull & Face */}
            <mesh position={[0, 0, 0]} material={skinMaterial} castShadow receiveShadow>
              <sphereGeometry args={[0.48, 32, 32]} />
            </mesh>

            {/* Jawline & Chin Contour */}
            <mesh position={[0, -0.22, 0.12]} material={skinMaterial} castShadow>
              <cylinderGeometry args={[0.32, 0.22, 0.35, 24]} />
            </mesh>

            {/* Nose Bridge & Tip */}
            <mesh position={[0, -0.04, 0.48]} rotation={[0.4, 0, 0]} material={skinMaterial} castShadow>
              <coneGeometry args={[0.07, 0.2, 16]} />
            </mesh>

            {/* Left Eye & Pupil */}
            <group position={[-0.15, 0.05, 0.42]}>
              <mesh>
                <sphereGeometry args={[0.07, 16, 16]} />
                <meshStandardMaterial color="#ffffff" roughness={0.1} />
              </mesh>
              <mesh position={[0, 0, 0.055]}>
                <sphereGeometry args={[0.035, 16, 16]} />
                <meshStandardMaterial color="#0284c7" roughness={0.1} />
              </mesh>
              <mesh position={[0, 0, 0.07]}>
                <sphereGeometry args={[0.018, 16, 16]} />
                <meshBasicMaterial color="#000000" />
              </mesh>
              {/* Eyebrow */}
              <mesh position={[0, 0.09, 0.03]} rotation={[0, 0, -0.1]}>
                <boxGeometry args={[0.12, 0.025, 0.03]} />
                <primitive object={hairMaterial} attach="material" />
              </mesh>
            </group>

            {/* Right Eye & Pupil */}
            <group position={[0.15, 0.05, 0.42]}>
              <mesh>
                <sphereGeometry args={[0.07, 16, 16]} />
                <meshStandardMaterial color="#ffffff" roughness={0.1} />
              </mesh>
              <mesh position={[0, 0, 0.055]}>
                <sphereGeometry args={[0.035, 16, 16]} />
                <meshStandardMaterial color="#0284c7" roughness={0.1} />
              </mesh>
              <mesh position={[0, 0, 0.07]}>
                <sphereGeometry args={[0.018, 16, 16]} />
                <meshBasicMaterial color="#000000" />
              </mesh>
              {/* Eyebrow */}
              <mesh position={[0, 0.09, 0.03]} rotation={[0, 0, 0.1]}>
                <boxGeometry args={[0.12, 0.025, 0.03]} />
                <primitive object={hairMaterial} attach="material" />
              </mesh>
            </group>

            {/* Lips / Mouth */}
            <mesh position={[0, -0.22, 0.42]} rotation={[0, 0, 0]}>
              <capsuleGeometry args={[0.03, 0.14, 8, 16]} />
              <meshStandardMaterial color="#c2716b" roughness={0.4} />
            </mesh>

            {/* Ears */}
            <mesh position={[-0.48, 0, 0]} rotation={[0, 0, 0.2]} material={skinMaterial}>
              <capsuleGeometry args={[0.06, 0.14, 8, 16]} />
            </mesh>
            <mesh position={[0.48, 0, 0]} rotation={[0, 0, -0.2]} material={skinMaterial}>
              <capsuleGeometry args={[0.06, 0.14, 8, 16]} />
            </mesh>

            {/* Styled Hair / Haircut */}
            <mesh position={[0, 0.22, -0.05]} material={hairMaterial} castShadow>
              <sphereGeometry args={[0.52, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.65]} />
            </mesh>
            <mesh position={[0, 0.35, -0.25]} material={hairMaterial} castShadow>
              <sphereGeometry args={[0.25, 16, 16]} />
            </mesh>
          </group>
        </InteractiveObject>

        {/* The Human Brain (Revealed in Anatomy/X-Ray Mode or on direct click) */}
        {showNervous && (
          <InteractiveObject
            id="brain"
            name="Human Brain (Cerebrum & Cerebellum)"
            category="Nervous System"
            description="The central command organ of the human nervous system. Houses ~86 billion neurons controlling thoughts, motor skills, sensory perception, and cognitive reasoning."
            metadata={{
              weight: '1.4 kg (3 lbs)',
              hemispheres: 'Left (Analytical) & Right (Creative)',
              lobes: 'Frontal, Parietal, Temporal, Occipital',
              blood_supply: '20% of total cardiac output',
            }}
            position={[0, 0.08, -0.02]}
            scale={[0.42, 0.38, 0.46]}
            isSelected={selectedId === 'brain'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <sphereGeometry args={[1, 32, 32]} />
              <meshStandardMaterial
                color="#f43f5e"
                roughness={0.3}
                metalness={0.1}
                emissive={selectedId === 'brain' ? '#fb7185' : '#881337'}
                emissiveIntensity={selectedId === 'brain' ? 0.8 : 0.2}
              />
            </mesh>
          </InteractiveObject>
        )}
      </group>

      {/* ========================================================================= */}
      {/* 2. NECK & COLLAR                                                          */}
      {/* ========================================================================= */}
      <mesh position={[0, 3.75, 0]} material={skinMaterial} castShadow>
        <cylinderGeometry args={[0.2, 0.24, 0.35, 24]} />
      </mesh>

      {/* ========================================================================= */}
      {/* 3. TORSO, LAB COAT & INTERNAL ORGANS                                      */}
      {/* ========================================================================= */}
      <group position={[0, 2.7, 0]}>
        {/* Doctor Lab Coat / Professional Jacket Torso */}
        <InteractiveObject
          id="torso"
          name="Thorax & Doctor's Lab Coat"
          category="Human Body & Attire"
          description="The upper human trunk containing vital cardiopulmonary organs protected by the ribcage, sternum, and medical garment."
          metadata={{
            chest_circumference: '~95 cm',
            key_contents: 'Heart, Lungs, Esophagus, Trachea, Thymus',
          }}
          isSelected={selectedId === 'torso'}
          onSelect={onSelect}
        >
          <group>
            {/* Main Torso */}
            <mesh material={coatMaterial} castShadow receiveShadow>
              <cylinderGeometry args={[0.62, 0.5, 1.6, 24]} />
            </mesh>

            {/* Coat Lapels / Collar */}
            <mesh position={[0, 0.6, 0.45]} rotation={[0.3, 0, 0]}>
              <boxGeometry args={[0.38, 0.35, 0.08]} />
              <meshStandardMaterial color="#f1f5f9" metalness={0.1} />
            </mesh>

            {/* Doctor Stethoscope Accessory */}
            <mesh position={[0, 0.3, 0.42]} rotation={[0, 0, 0]}>
              <torusGeometry args={[0.32, 0.03, 16, 32, Math.PI * 1.2]} />
              <meshStandardMaterial color="#0284c7" metalness={0.8} roughness={0.2} />
            </mesh>
          </group>
        </InteractiveObject>

        {/* ----------------------------------------------------------------------- */}
        {/* INTERNAL ANATOMY: HEART, LUNGS, SPINE, STOMACH                          */}
        {/* ----------------------------------------------------------------------- */}

        {/* Pulsating Anatomical Heart */}
        {showCirculatory && (
          <group ref={heartRef} position={[-0.1, 0.25, 0.15]}>
            <InteractiveObject
              id="heart"
              name="Anatomical Human Heart"
              category="Circulatory System"
              description="A hollow muscular pump featuring 4 chambers (Left/Right Atria, Left/Right Ventricles) beating ~100,000 times daily to circulate blood throughout the body."
              metadata={{
                chambers: '4 (2 Atria, 2 Ventricles)',
                resting_bpm: '60–100 Beats Per Minute',
                stroke_volume: '70 mL per beat',
                blood_pumped: '~7,200 Liters / Day',
              }}
              scale={[0.26, 0.32, 0.24]}
              isSelected={selectedId === 'heart'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <sphereGeometry args={[1, 32, 32]} />
                <meshStandardMaterial
                  map={tissueTexture}
                  color="#dc2626"
                  roughness={0.25}
                  emissive={selectedId === 'heart' ? '#f87171' : '#7f1d1d'}
                  emissiveIntensity={selectedId === 'heart' ? 0.8 : 0.3}
                />
              </mesh>
            </InteractiveObject>
          </group>
        )}

        {/* Aorta Blood Vessel Arch */}
        {showCirculatory && (
          <InteractiveObject
            id="aorta"
            name="Ascending Aorta Arch"
            category="Circulatory System"
            description="The body's primary arterial trunk delivering oxygen-rich blood from the left ventricle to systemic tissue networks."
            metadata={{
              origin: 'Left Ventricle',
              diameter: '2.5 cm (1 inch)',
              branches: 'Brachiocephalic, Carotid, Subclavian',
            }}
            position={[-0.08, 0.55, 0.12]}
            scale={[0.14, 0.22, 0.14]}
            isSelected={selectedId === 'aorta'}
            onSelect={onSelect}
          >
            <mesh castShadow>
              <torusGeometry args={[0.7, 0.3, 16, 24, Math.PI]} />
              <meshStandardMaterial color="#ef4444" metalness={0.2} roughness={0.3} />
            </mesh>
          </InteractiveObject>
        )}

        {/* Expanding Respiratory Lungs */}
        {showRespiratory && (
          <group ref={lungsRef} position={[0, 0.2, 0.05]}>
            {/* Left Lung */}
            <InteractiveObject
              id="left-lung"
              name="Left Lung (2 Lobes)"
              category="Respiratory System"
              description="Accommodates the cardiac notch for the heart. Contains millions of alveoli for vital oxygen intake and carbon dioxide expulsion."
              metadata={{
                lobes: '2 (Superior & Inferior)',
                alveoli: '~300 Million',
                capacity: '2.5 Liters',
              }}
              position={[-0.32, 0, 0]}
              scale={[0.22, 0.45, 0.24]}
              isSelected={selectedId === 'left-lung'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <capsuleGeometry args={[0.6, 1.2, 16, 16]} />
                <meshStandardMaterial
                  color="#fb7185"
                  roughness={0.35}
                  emissive={selectedId === 'left-lung' ? '#fda4af' : '#4c0519'}
                  emissiveIntensity={selectedId === 'left-lung' ? 0.7 : 0.15}
                />
              </mesh>
            </InteractiveObject>

            {/* Right Lung */}
            <InteractiveObject
              id="right-lung"
              name="Right Lung (3 Lobes)"
              category="Respiratory System"
              description="Slightly larger than the left lung, divided into Superior, Middle, and Inferior anatomical lobes."
              metadata={{
                lobes: '3 (Superior, Middle, Inferior)',
                share_of_breathing: '55% of total capacity',
              }}
              position={[0.32, 0, 0]}
              scale={[0.24, 0.45, 0.25]}
              isSelected={selectedId === 'right-lung'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <capsuleGeometry args={[0.6, 1.2, 16, 16]} />
                <meshStandardMaterial
                  color="#fb7185"
                  roughness={0.35}
                  emissive={selectedId === 'right-lung' ? '#fda4af' : '#4c0519'}
                  emissiveIntensity={selectedId === 'right-lung' ? 0.7 : 0.15}
                />
              </mesh>
            </InteractiveObject>
          </group>
        )}

        {/* Vertebral Spine & Skeletal Framework */}
        {showSkeletal && (
          <InteractiveObject
            id="spine"
            name="Vertebral Column (Spine)"
            category="Skeletal System"
            description="The central skeletal support pillar of 33 interlocking vertebrae that protects the spinal cord and maintains upright posture."
            metadata={{
              vertebrae: '33 Bones (Cervical, Thoracic, Lumbar, Sacral, Coccyx)',
              function: 'Axial weight support & nerve protection',
            }}
            position={[0, 0, -0.18]}
            scale={[0.15, 1.7, 0.15]}
            isSelected={selectedId === 'spine'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <cylinderGeometry args={[0.5, 0.6, 1, 16]} />
              <meshStandardMaterial
                color="#e2e8f0"
                roughness={0.4}
                emissive={selectedId === 'spine' ? '#38bdf8' : '#000000'}
                emissiveIntensity={0.5}
              />
            </mesh>
          </InteractiveObject>
        )}

        {/* Stomach & Digestive System */}
        {showDigestive && (
          <InteractiveObject
            id="stomach"
            name="Stomach & Digestive Tract"
            category="Digestive System"
            description="A muscular organ that breaks down ingested nutrients using hydrochloric acid and proteolytic enzymes before intestinal absorption."
            metadata={{
              capacity: '1.0 to 1.5 Liters',
              ph_level: '1.5 to 3.5 (Gastric Acid)',
              digestive_phase: 'Mechanical churning & protein breakdown',
            }}
            position={[-0.1, -0.4, 0.12]}
            scale={[0.22, 0.18, 0.18]}
            isSelected={selectedId === 'stomach'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <sphereGeometry args={[1, 24, 24]} />
              <meshStandardMaterial color="#f97316" roughness={0.4} />
            </mesh>
          </InteractiveObject>
        )}
      </group>

      {/* ========================================================================= */}
      {/* 4. ARMS & HANDS WITH GESTURING TEACHER HANDS                              */}
      {/* ========================================================================= */}

      {/* Left Arm & Hand */}
      <group ref={leftArmRef} position={[-0.8, 3.4, 0]}>
        {/* Upper Arm with Lab Coat Sleeve */}
        <mesh position={[0, -0.5, 0]} material={coatMaterial} castShadow>
          <cylinderGeometry args={[0.16, 0.14, 0.9, 16]} />
        </mesh>
        {/* Forearm (Skin) */}
        <mesh position={[0, -1.05, 0.05]} material={skinMaterial} castShadow>
          <cylinderGeometry args={[0.12, 0.09, 0.7, 16]} />
        </mesh>
        {/* Left Hand */}
        <mesh position={[0, -1.45, 0.08]} material={skinMaterial} castShadow>
          <boxGeometry args={[0.12, 0.16, 0.06]} />
        </mesh>
      </group>

      {/* Right Arm & Hand (Teaching Gesture) */}
      <group ref={rightArmRef} position={[0.8, 3.4, 0]}>
        {/* Upper Arm with Lab Coat Sleeve */}
        <mesh position={[0, -0.5, 0]} material={coatMaterial} castShadow>
          <cylinderGeometry args={[0.16, 0.14, 0.9, 16]} />
        </mesh>
        {/* Forearm (Skin) */}
        <mesh position={[0, -1.05, 0.05]} material={skinMaterial} castShadow>
          <cylinderGeometry args={[0.12, 0.09, 0.7, 16]} />
        </mesh>
        {/* Right Hand & Pointer Finger Gesture */}
        <InteractiveObject
          id="hands"
          name="Articulated Human Hand"
          category="Musculoskeletal System"
          description="Highly dexterous multi-fingered extremity with opposable thumb, enabling precision grasping, tool usage, and educational gestures."
          metadata={{
            bones_per_hand: '27 Bones (8 Carpals, 5 Metacarpals, 14 Phalanges)',
            grip_types: 'Power Grip & Precision Pinch',
          }}
          position={[0, -1.45, 0.08]}
          isSelected={selectedId === 'hands'}
          onSelect={onSelect}
        >
          <group>
            {/* Palm */}
            <mesh material={skinMaterial} castShadow>
              <boxGeometry args={[0.12, 0.16, 0.06]} />
            </mesh>
            {/* Index Pointer Finger */}
            <mesh position={[0.04, -0.12, 0.02]} rotation={[0.2, 0, 0]} material={skinMaterial} castShadow>
              <cylinderGeometry args={[0.02, 0.018, 0.12, 8]} />
            </mesh>
          </group>
        </InteractiveObject>
      </group>

      {/* ========================================================================= */}
      {/* 5. LEGS & POLISHED SHOES (Ground Stance)                                  */}
      {/* ========================================================================= */}
      <group position={[0, 0, 0]}>
        {/* Pelvis & Upper Pants */}
        <mesh position={[0, 1.75, 0]} material={pantsMaterial} castShadow>
          <boxGeometry args={[0.7, 0.45, 0.4]} />
        </mesh>

        {/* Left Leg */}
        <mesh position={[-0.22, 0.9, 0]} material={pantsMaterial} castShadow>
          <cylinderGeometry args={[0.16, 0.12, 1.6, 16]} />
        </mesh>
        {/* Left Shoe */}
        <mesh position={[-0.22, 0.05, 0.08]} castShadow>
          <boxGeometry args={[0.18, 0.12, 0.38]} />
          <meshStandardMaterial color="#0f172a" roughness={0.2} metalness={0.3} />
        </mesh>

        {/* Right Leg */}
        <mesh position={[0.22, 0.9, 0]} material={pantsMaterial} castShadow>
          <cylinderGeometry args={[0.16, 0.12, 1.6, 16]} />
        </mesh>
        {/* Right Shoe */}
        <mesh position={[0.22, 0.05, 0.08]} castShadow>
          <boxGeometry args={[0.18, 0.12, 0.38]} />
          <meshStandardMaterial color="#0f172a" roughness={0.2} metalness={0.3} />
        </mesh>
      </group>
    </group>
  );
}
