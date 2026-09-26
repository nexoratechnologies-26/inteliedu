import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import InteractiveObject from '../../components/InteractiveObject.jsx';
import { generateTissueTexture } from '../../utils/textureGenerator.js';

/**
 * Interactive 3D Human Model & AI Anatomy Teacher
 * Combines a 3D humanoid avatar with interactive anatomical systems (Nervous, Circulatory, Respiratory, Skeletal, Digestive)
 */
export default function InteractiveHumanModel({
  selectedId = null,
  onSelect = null,
  activeLayer = 'all', // 'all' | 'skeletal' | 'circulatory' | 'respiratory' | 'nervous' | 'digestive'
  isSpeaking = false,
}) {
  const avatarGroupRef = useRef(null);
  const heartRef = useRef(null);
  const leftLungRef = useRef(null);
  const rightLungRef = useRef(null);
  const headRef = useRef(null);
  const rightArmRef = useRef(null);

  const tissueTexture = useMemo(() => generateTissueTexture(), []);

  // Frame-rate independent human breathing, heartbeat, and teaching gestures
  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    // 1. Heartbeat Pulsation (~72 BPM = 1.2 Hz)
    if (heartRef.current) {
      const pulse = 1 + Math.sin(t * 7.5) * 0.08 + Math.sin(t * 15) * 0.04;
      heartRef.current.scale.set(pulse, pulse, pulse);
    }

    // 2. Respiratory Lung Expansion (~15 breaths/min = 0.25 Hz)
    if (leftLungRef.current && rightLungRef.current) {
      const breath = 1 + Math.sin(t * 2.0) * 0.05;
      leftLungRef.current.scale.set(breath, breath, 1 + Math.sin(t * 2.0) * 0.07);
      rightLungRef.current.scale.set(breath, breath, 1 + Math.sin(t * 2.0) * 0.07);
    }

    // 3. Natural Human Teacher Gestures (Idle sway, head tilt, gesturing arm)
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(t * 0.8) * 0.08;
      headRef.current.rotation.x = Math.sin(t * 0.5) * 0.04;
    }

    if (rightArmRef.current) {
      // Gentle explanatory teaching arm wave/gesture
      rightArmRef.current.rotation.z = -0.3 + Math.sin(t * 1.5) * 0.12;
      rightArmRef.current.rotation.x = 0.2 + Math.cos(t * 1.2) * 0.1;
    }

    if (avatarGroupRef.current) {
      // Subtle idle body breathing sway
      avatarGroupRef.current.position.y = Math.sin(t * 2.0) * 0.02;
    }
  });

  const showSkeletal = activeLayer === 'all' || activeLayer === 'skeletal';
  const showCirculatory = activeLayer === 'all' || activeLayer === 'circulatory';
  const showRespiratory = activeLayer === 'all' || activeLayer === 'respiratory';
  const showNervous = activeLayer === 'all' || activeLayer === 'nervous';
  const showDigestive = activeLayer === 'all' || activeLayer === 'digestive';

  return (
    <group ref={avatarGroupRef} position={[0, -1.8, 0]}>
      {/* ========================================================================= */}
      {/* 1. HEAD & NERVOUS SYSTEM (Brain & Cranium)                                */}
      {/* ========================================================================= */}
      <group ref={headRef} position={[0, 4.2, 0]}>
        {/* Semi-transparent Human Head / Face Silhouette */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.55, 32, 32]} />
          <meshStandardMaterial
            color="#38bdf8"
            transparent
            opacity={activeLayer === 'all' ? 0.35 : 0.15}
            roughness={0.2}
            wireframe={activeLayer === 'skeletal'}
          />
        </mesh>

        {/* Eyes / Face Indicators */}
        <mesh position={[-0.18, 0.05, 0.48]}>
          <sphereGeometry args={[0.07, 16, 16]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
        <mesh position={[0.18, 0.05, 0.48]}>
          <sphereGeometry args={[0.07, 16, 16]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>

        {/* The Brain (Cerebrum & Cerebellum) */}
        {showNervous && (
          <InteractiveObject
            id="brain"
            name="Human Brain (Cerebrum)"
            category="Nervous System"
            description="The central command organ of the human nervous system. Contains ~86 billion neurons responsible for cognition, motor control, memory, language, and sensory processing."
            metadata={{
              weight: '~1.4 kg',
              hemispheres: 'Left & Right Cerebral Hemispheres',
              lobes: 'Frontal, Parietal, Temporal, Occipital',
              energy_consumption: '20% of total body metabolic energy',
            }}
            position={[0, 0.08, -0.05]}
            scale={[0.42, 0.38, 0.48]}
            color="#f472b6"
            emissiveColor="#ec4899"
            isSelected={selectedId === 'brain'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <sphereGeometry args={[1, 32, 32]} />
              <meshStandardMaterial
                color="#f43f5e"
                roughness={0.4}
                metalness={0.1}
                emissive={selectedId === 'brain' ? '#fb7185' : '#000000'}
                emissiveIntensity={selectedId === 'brain' ? 0.6 : 0}
              />
            </mesh>
          </InteractiveObject>
        )}
      </group>

      {/* ========================================================================= */}
      {/* 2. SKELETAL SYSTEM (Spine, Ribcage, Shoulders, Pelvis)                    */}
      {/* ========================================================================= */}
      {showSkeletal && (
        <group name="skeletal-framework">
          {/* Vertebral Column / Spine */}
          <InteractiveObject
            id="spine"
            name="Vertebral Column (Spine)"
            category="Skeletal System"
            description="A flexible column of 33 vertebrae that encloses and protects the spinal cord while supporting the head, ribcage, and upper body weight."
            metadata={{
              vertebrae_count: '33 (7 Cervical, 12 Thoracic, 5 Lumbar, 5 Sacral, 4 Coccygeal)',
              primary_function: 'Spinal cord protection & axial posture support',
            }}
            position={[0, 2.5, -0.15]}
            scale={[0.15, 1.8, 0.15]}
            color="#e2e8f0"
            isSelected={selectedId === 'spine'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <cylinderGeometry args={[0.5, 0.6, 1, 16]} />
              <meshStandardMaterial color="#cbd5e1" roughness={0.5} />
            </mesh>
          </InteractiveObject>

          {/* Ribcage Protection Cage */}
          <InteractiveObject
            id="ribcage"
            name="Thoracic Ribcage"
            category="Skeletal System"
            description="Composed of 12 pairs of curved ribs attached to the thoracic vertebrae and sternum, safeguarding the heart, lungs, and major thoracic vessels."
            metadata={{
              pairs: '12 Pairs (7 True, 3 False, 2 Floating)',
              attached_to: 'Sternum & Thoracic Spine',
            }}
            position={[0, 2.9, 0]}
            scale={[0.75, 0.7, 0.5]}
            color="#94a3b8"
            isSelected={selectedId === 'ribcage'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <torusGeometry args={[0.9, 0.08, 16, 32]} />
              <meshStandardMaterial
                color="#cbd5e1"
                wireframe={true}
                transparent={true}
                opacity={0.7}
              />
            </mesh>
          </InteractiveObject>

          {/* Pelvis / Hip Girdle */}
          <InteractiveObject
            id="pelvis"
            name="Pelvic Girdle"
            category="Skeletal System"
            description="The basin-shaped complex of bones connecting the trunk to the legs and supporting abdominal visceral organs."
            metadata={{
              bones: 'Ilium, Ischium, Pubis, Sacrum',
              function: 'Weight bearing & locomotion leverage',
            }}
            position={[0, 1.6, 0]}
            scale={[0.65, 0.35, 0.45]}
            color="#cbd5e1"
            isSelected={selectedId === 'pelvis'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <boxGeometry args={[1, 0.8, 0.8]} />
              <meshStandardMaterial color="#94a3b8" roughness={0.4} />
            </mesh>
          </InteractiveObject>
        </group>
      )}

      {/* ========================================================================= */}
      {/* 3. CIRCULATORY SYSTEM (Pulsating Heart & Major Blood Vessels)              */}
      {/* ========================================================================= */}
      {showCirculatory && (
        <group name="circulatory-system">
          {/* Pulsating Anatomical Heart */}
          <group ref={heartRef} position={[-0.1, 2.95, 0.12]}>
            <InteractiveObject
              id="heart"
              name="Anatomical Human Heart"
              category="Circulatory System"
              description="A muscular four-chambered pump that circulates oxygenated blood throughout systemic arterial pathways and deoxygenated blood to the lungs."
              metadata={{
                chambers: '4 (Left/Right Atria, Left/Right Ventricles)',
                resting_heart_rate: '60–100 BPM',
                daily_beats: '~100,000 beats/day',
                output_volume: '~5 Liters of blood per minute',
              }}
              scale={[0.26, 0.3, 0.24]}
              color="#ef4444"
              emissiveColor="#f87171"
              isSelected={selectedId === 'heart'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <sphereGeometry args={[1, 32, 32]} />
                <meshStandardMaterial
                  map={tissueTexture}
                  color="#dc2626"
                  roughness={0.3}
                  emissive={selectedId === 'heart' ? '#f87171' : '#450a0a'}
                  emissiveIntensity={selectedId === 'heart' ? 0.7 : 0.2}
                />
              </mesh>
            </InteractiveObject>
          </group>

          {/* Ascending Aorta Arch */}
          <InteractiveObject
            id="aorta"
            name="Aorta Arch"
            category="Circulatory System"
            description="The largest and primary systemic artery carrying high-pressure oxygenated blood directly from the left ventricle to the entire body."
            metadata={{
              diameter: '~2.5 cm (1 inch)',
              origin: 'Left Ventricle',
              branches: 'Brachiocephalic, Left Common Carotid, Left Subclavian',
            }}
            position={[-0.08, 3.22, 0.1]}
            scale={[0.12, 0.2, 0.12]}
            color="#b91c1c"
            isSelected={selectedId === 'aorta'}
            onSelect={onSelect}
          >
            <mesh castShadow>
              <torusGeometry args={[0.7, 0.3, 16, 24, Math.PI]} />
              <meshStandardMaterial color="#ef4444" metalness={0.2} roughness={0.3} />
            </mesh>
          </InteractiveObject>

          {/* Vena Cava (Deoxygenated Return) */}
          <mesh position={[0.12, 2.9, 0.08]}>
            <cylinderGeometry args={[0.04, 0.04, 0.6, 16]} />
            <meshStandardMaterial color="#2563eb" metalness={0.1} />
          </mesh>
        </group>
      )}

      {/* ========================================================================= */}
      {/* 4. RESPIRATORY SYSTEM (Left & Right Lungs)                                */}
      {/* ========================================================================= */}
      {showRespiratory && (
        <group name="respiratory-system">
          {/* Left Lung */}
          <group ref={leftLungRef} position={[-0.32, 2.9, 0.02]}>
            <InteractiveObject
              id="left-lung"
              name="Left Lung"
              category="Respiratory System"
              description="Has two distinct lobes (Superior & Inferior) with a cardiac notch accommodating the heart's apex. Facilitates pulmonary gas exchange."
              metadata={{
                lobes: '2 Lobes (Superior & Inferior)',
                alveoli_count: '~300 million alveoli',
                surface_area: '~70 m² gas exchange area',
              }}
              scale={[0.22, 0.45, 0.25]}
              color="#f472b6"
              isSelected={selectedId === 'left-lung'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <capsuleGeometry args={[0.6, 1.2, 16, 16]} />
                <meshStandardMaterial
                  color="#fb7185"
                  transparent
                  opacity={0.8}
                  roughness={0.4}
                />
              </mesh>
            </InteractiveObject>
          </group>

          {/* Right Lung */}
          <group ref={rightLungRef} position={[0.32, 2.9, 0.02]}>
            <InteractiveObject
              id="right-lung"
              name="Right Lung"
              category="Respiratory System"
              description="Slightly larger than the left lung, divided into three anatomical lobes (Superior, Middle, Inferior)."
              metadata={{
                lobes: '3 Lobes (Superior, Middle, Inferior)',
                capacity: '~55% of total pulmonary volume',
              }}
              scale={[0.24, 0.45, 0.26]}
              color="#f472b6"
              isSelected={selectedId === 'right-lung'}
              onSelect={onSelect}
            >
              <mesh castShadow receiveShadow>
                <capsuleGeometry args={[0.6, 1.2, 16, 16]} />
                <meshStandardMaterial
                  color="#fb7185"
                  transparent
                  opacity={0.8}
                  roughness={0.4}
                />
              </mesh>
            </InteractiveObject>
          </group>
        </group>
      )}

      {/* ========================================================================= */}
      {/* 5. DIGESTIVE SYSTEM (Stomach & Liver)                                     */}
      {/* ========================================================================= */}
      {showDigestive && (
        <group name="digestive-system">
          {/* Stomach */}
          <InteractiveObject
            id="stomach"
            name="Stomach"
            category="Digestive System"
            description="A J-shaped muscular reservoir that secretes gastric hydrochloric acid and digestive enzymes (pepsin) to break down ingested food into chyme."
            metadata={{
              capacity: '1.0 to 1.5 Liters',
              gastric_ph: '1.5 to 3.5 (Highly Acidic)',
              primary_enzymes: 'Pepsin, Gastric Lipase',
            }}
            position={[-0.1, 2.3, 0.1]}
            scale={[0.22, 0.18, 0.16]}
            color="#fb923c"
            isSelected={selectedId === 'stomach'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <sphereGeometry args={[1, 24, 24]} />
              <meshStandardMaterial color="#f97316" roughness={0.4} />
            </mesh>
          </InteractiveObject>

          {/* Liver */}
          <InteractiveObject
            id="liver"
            name="Liver"
            category="Digestive & Metabolic System"
            description="The largest internal organ and gland. Performs over 500 vital metabolic functions including detoxification, protein synthesis, and bile production."
            metadata={{
              weight: '~1.5 kg',
              lobes: 'Right, Left, Caudate, Quadrate',
              functions: 'Bile synthesis, glycogen storage, drug metabolism',
            }}
            position={[0.2, 2.4, 0.08]}
            scale={[0.3, 0.22, 0.2]}
            color="#991b1b"
            isSelected={selectedId === 'liver'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <boxGeometry args={[1, 0.8, 0.8]} />
              <meshStandardMaterial color="#7f1d1d" roughness={0.5} />
            </mesh>
          </InteractiveObject>
        </group>
      )}

      {/* ========================================================================= */}
      {/* 6. HUMANOID LIMBS & TEACHING AVATAR GESTURES                              */}
      {/* ========================================================================= */}
      <group name="humanoid-limbs">
        {/* Left Arm (Relaxed) */}
        <group position={[-0.85, 3.4, 0]} rotation={[0, 0, 0.15]}>
          <mesh position={[0, -0.6, 0]} castShadow>
            <cylinderGeometry args={[0.08, 0.06, 1.2, 16]} />
            <meshStandardMaterial color="#38bdf8" transparent opacity={0.4} />
          </mesh>
        </group>

        {/* Right Arm (Teaching / Explanatory Gesture) */}
        <group ref={rightArmRef} position={[0.85, 3.4, 0]}>
          <mesh position={[0, -0.6, 0]} castShadow>
            <cylinderGeometry args={[0.08, 0.06, 1.2, 16]} />
            <meshStandardMaterial color="#38bdf8" transparent opacity={0.4} />
          </mesh>
          {/* Hand Pointing Pointer */}
          <mesh position={[0, -1.25, 0.1]}>
            <sphereGeometry args={[0.08, 16, 16]} />
            <meshStandardMaterial color="#38bdf8" />
          </mesh>
        </group>

        {/* Left Leg */}
        <mesh position={[-0.3, 0.7, 0]} castShadow>
          <cylinderGeometry args={[0.12, 0.08, 1.5, 16]} />
          <meshStandardMaterial color="#38bdf8" transparent opacity={0.3} />
        </mesh>

        {/* Right Leg */}
        <mesh position={[0.3, 0.7, 0]} castShadow>
          <cylinderGeometry args={[0.12, 0.08, 1.5, 16]} />
          <meshStandardMaterial color="#38bdf8" transparent opacity={0.3} />
        </mesh>
      </group>

      {/* ========================================================================= */}
      {/* 7. TRANSPARENT SKIN SILHOUETTE SHELL (Full Body Outer Layer)             */}
      {/* ========================================================================= */}
      {activeLayer === 'all' && (
        <mesh position={[0, 2.7, 0]}>
          <capsuleGeometry args={[0.62, 1.6, 16, 32]} />
          <meshStandardMaterial
            color="#60a5fa"
            transparent
            opacity={0.15}
            roughness={0.1}
            wireframe={false}
          />
        </mesh>
      )}
    </group>
  );
}
