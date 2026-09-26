import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import InteractiveObject from '../../components/InteractiveObject.jsx';

/**
 * Procedural 4-Cylinder Internal Combustion Engine & Gearbox Model
 * Simulates synchronized piston reciprocation, crankshaft rotation, and camshaft valve timing
 */
export default function EngineMechanicsModel({
  selectedId = null,
  onSelect = null,
  rpm = 60,
  isExploded = false,
  isPaused = false,
}) {
  const crankRef = useRef(null);
  const gear1Ref = useRef(null);
  const gear2Ref = useRef(null);
  const pistonRefs = [useRef(null), useRef(null), useRef(null), useRef(null)];
  const sparkRefs = [useRef(null), useRef(null), useRef(null), useRef(null)];

  // Firing order: 1 - 3 - 4 - 2 (Standard Inline-4)
  const cylinderOffsets = [0, Math.PI, Math.PI, 0]; // 180° flat-plane crankshaft

  useFrame((state, delta) => {
    if (!isPaused) {
      const angleDelta = (rpm * (2 * Math.PI) / 60) * delta;

      // 1. Crankshaft Rotation
      if (crankRef.current) {
        crankRef.current.rotation.x += angleDelta;
      }

      // 2. Transmission Gear Meshing
      if (gear1Ref.current && gear2Ref.current) {
        gear1Ref.current.rotation.z += angleDelta;
        gear2Ref.current.rotation.z -= angleDelta * 0.5; // 2:1 gear ratio
      }

      // 3. Piston Reciprocation & Connecting Rod Kinematics
      const curAngle = crankRef.current ? crankRef.current.rotation.x : 0;
      const stroke = isExploded ? 0.3 : 0.6;

      pistonRefs.forEach((ref, idx) => {
        if (ref.current) {
          const pistonPhase = curAngle + cylinderOffsets[idx];
          const yPos = Math.sin(pistonPhase) * stroke;
          ref.current.position.y = (isExploded ? 1.8 : 0.9) + yPos;

          // Spark ignition flash near top-dead-center
          if (sparkRefs[idx].current) {
            const isNearTDC = Math.sin(pistonPhase) > 0.92;
            sparkRefs[idx].current.material.opacity = isNearTDC ? 0.9 : 0.05;
          }
        }
      });
    }
  });

  const cylinderSpacing = isExploded ? 1.5 : 0.9;
  const explodeFactor = isExploded ? 1.8 : 1.0;

  return (
    <group position={[0, -0.6, 0]}>
      {/* 1. Engine Block Base / Chassis */}
      <InteractiveObject
        id="engine-block"
        name="Engine Crankcase & Cylinder Block"
        category="Mechanical Engineering"
        description="The primary cast structure containing 4 inline cylinder bores, coolant jackets, and main crankshaft bearing journals."
        metadata={{
          configuration: 'Inline-4 (I4)',
          displacement: '2.0 Liters (1,998 cc)',
          material: 'A356-T6 Cast Aluminum Alloy',
          cooling: 'Closed-loop Liquid Jacket',
        }}
        position={[0, isExploded ? -0.8 : 0, 0]}
        scale={[1.8 * explodeFactor, 0.7, 1.1]}
        isSelected={selectedId === 'engine-block'}
        onSelect={onSelect}
      >
        <mesh castShadow receiveShadow>
          <boxGeometry args={[2.2, 0.8, 1.2]} />
          <meshStandardMaterial
            color="#475569"
            metalness={0.7}
            roughness={0.3}
            transparent={isExploded}
            opacity={isExploded ? 0.5 : 0.9}
          />
        </mesh>
      </InteractiveObject>

      {/* 2. Synchronized Crankshaft */}
      <group ref={crankRef} position={[0, isExploded ? -0.4 : 0.2, 0]}>
        <InteractiveObject
          id="crankshaft"
          name="Counterweighted Crankshaft"
          category="Powertrain Mechanics"
          description="Converts reciprocating linear piston motion into rotational torque to drive the flywheel and transmission drivetrain."
          metadata={{
            crank_throw: '44 mm (88 mm total stroke)',
            journals: '5 Main Bearings, 4 Rod Journals',
            material: 'Forged 4340 Chromoly Steel',
          }}
          scale={[2.2 * explodeFactor, 0.2, 0.2]}
          isSelected={selectedId === 'crankshaft'}
          onSelect={onSelect}
        >
          <mesh castShadow>
            <cylinderGeometry args={[0.15, 0.15, 1.8, 16]} rotation={[0, 0, Math.PI / 2]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.15} />
          </mesh>
        </InteractiveObject>
      </group>

      {/* 3. 4 Inline Pistons & Spark Plugs */}
      {[-1.5, -0.5, 0.5, 1.5].map((xOffset, idx) => {
        const posX = xOffset * cylinderSpacing;
        return (
          <group key={idx} position={[posX, 0, 0]}>
            {/* Cylinder Liner Cylinder */}
            <mesh position={[0, isExploded ? 1.5 : 0.9, 0]}>
              <cylinderGeometry args={[0.38, 0.38, 1.2, 24, 1, true]} />
              <meshStandardMaterial
                color="#64748b"
                wireframe={true}
                transparent={true}
                opacity={0.4}
              />
            </mesh>

            {/* Reciprocating Piston Head */}
            <group ref={pistonRefs[idx]} position={[0, 0.9, 0]}>
              <InteractiveObject
                id={`piston-${idx + 1}`}
                name={`Piston #${idx + 1} & Connecting Rod`}
                category="Combustion Mechanics"
                description={`Piston cylinder #${idx + 1}. Transmits expanding combustion gas pressure down through the connecting rod to rotate the crankshaft.`}
                metadata={{
                  bore: '85 mm',
                  compression_ratio: '10.5:1',
                  ring_count: '2 Compression Rings, 1 Oil Control Ring',
                }}
                isSelected={selectedId === `piston-${idx + 1}`}
                onSelect={onSelect}
              >
                <mesh castShadow receiveShadow>
                  <cylinderGeometry args={[0.34, 0.34, 0.45, 24]} />
                  <meshStandardMaterial
                    color="#e2e8f0"
                    metalness={0.85}
                    roughness={0.2}
                    emissive={selectedId === `piston-${idx + 1}` ? '#38bdf8' : '#000000'}
                    emissiveIntensity={0.5}
                  />
                </mesh>

                {/* Connecting Rod */}
                <mesh position={[0, -0.5, 0]} castShadow>
                  <cylinderGeometry args={[0.06, 0.08, 0.7, 16]} />
                  <meshStandardMaterial color="#64748b" metalness={0.8} />
                </mesh>
              </InteractiveObject>
            </group>

            {/* Spark Plug & Ignition Flash */}
            <group position={[0, isExploded ? 2.5 : 1.7, 0]}>
              <InteractiveObject
                id={`spark-plug-${idx + 1}`}
                name={`Spark Plug #${idx + 1}`}
                category="Electrical / Ignition"
                description="Delivers an electric spark to ignite the compressed fuel-air mixture within the combustion chamber."
                metadata={{
                  gap: '0.8 mm',
                  voltage: '25,000–40,000 Volts',
                }}
                scale={[0.08, 0.3, 0.08]}
                isSelected={selectedId === `spark-plug-${idx + 1}`}
                onSelect={onSelect}
              >
                <mesh castShadow>
                  <cylinderGeometry args={[0.8, 0.8, 1, 12]} />
                  <meshStandardMaterial color="#f59e0b" metalness={0.5} />
                </mesh>
              </InteractiveObject>

              {/* Combustion Spark Glow Mesh */}
              <mesh ref={sparkRefs[idx]} position={[0, -0.25, 0]}>
                <sphereGeometry args={[0.18, 16, 16]} />
                <meshBasicMaterial color="#fef08a" transparent opacity={0.05} />
              </mesh>
            </group>
          </group>
        );
      })}

      {/* 4. Transmission Spur Gearbox Assembly */}
      <group position={[2.2 * explodeFactor, isExploded ? 0.5 : 0, 0]}>
        {/* Drive Gear */}
        <group ref={gear1Ref} position={[0, 0.4, 0]}>
          <InteractiveObject
            id="drive-gear"
            name="Primary Drive Spur Gear"
            category="Transmission Mechanics"
            description="High-torque input pinion gear transferring engine power directly into the reduction transmission."
            metadata={{
              teeth: '20 Teeth',
              module: '2.5 mm',
              material: 'Case-Hardened Carbon Steel',
            }}
            isSelected={selectedId === 'drive-gear'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <cylinderGeometry args={[0.6, 0.6, 0.2, 20]} rotation={[Math.PI / 2, 0, 0]} />
              <meshStandardMaterial color="#38bdf8" metalness={0.9} roughness={0.2} />
            </mesh>
          </InteractiveObject>
        </group>

        {/* Driven Gear */}
        <group ref={gear2Ref} position={[0, -0.6, 0]}>
          <InteractiveObject
            id="driven-gear"
            name="Secondary Reduction Gear"
            category="Transmission Mechanics"
            description="Driven bull gear providing a 2:1 mechanical torque multiplication ratio."
            metadata={{
              teeth: '40 Teeth',
              reduction_ratio: '2.0:1',
              torque_gain: '+100% Output Torque',
            }}
            isSelected={selectedId === 'driven-gear'}
            onSelect={onSelect}
          >
            <mesh castShadow receiveShadow>
              <cylinderGeometry args={[0.9, 0.9, 0.2, 32]} rotation={[Math.PI / 2, 0, 0]} />
              <meshStandardMaterial color="#a855f7" metalness={0.9} roughness={0.2} />
            </mesh>
          </InteractiveObject>
        </group>
      </group>
    </group>
  );
}
