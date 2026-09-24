import { Html } from '@react-three/drei';
import { useRef } from 'react';
import { Mesh, Group, MathUtils } from 'three';
import { useFrame } from '@react-three/fiber';
import { Vector3, Group } from 'three';
import { useMemo } from 'react';

interface WorkerProps {
  position: [number, number, number];
  riskLevel: string; // 'BAJO', 'MEDIO', 'ALTO'
  label: string;
  bpm?: number;
  fatigueIndex?: number;
}

export default function WorkerAvatar({ position, riskLevel, label, bpm = 85, fatigueIndex = 0.2 }: WorkerProps) {
  const groupRef = useRef<Group>(null);
  const haloRef = useRef<Mesh>(null);

  // Target position for smooth interpolation
  const targetPosition = useMemo(() => new Vector3(...position), [position]);

  // Color mapping
  let color = '#22c55e';
  if (riskLevel === 'MEDIO') color = '#eab308';
  if (riskLevel === 'ALTO') color = '#ef4444';

  useFrame(({ clock }, delta) => {
    // Animate halo
    if (haloRef.current && (riskLevel === 'MEDIO' || riskLevel === 'ALTO')) {
      const speed = riskLevel === 'ALTO' ? 8 : 3;
      const pulse = Math.sin(clock.elapsedTime * speed);
      haloRef.current.scale.x = 1 + pulse * 0.15;
      haloRef.current.scale.z = 1 + pulse * 0.15;
      (haloRef.current.material as any).opacity = 0.5 + pulse * 0.3;
    }

    // Smooth movement interpolation
    if (groupRef.current) {
      groupRef.current.position.lerp(targetPosition, delta * 3);
    }
  });

  const isFatigued = fatigueIndex > 0.5;

  return (
    <group ref={groupRef} position={position}>
      {/* Risk halo on the floor */}
      <mesh ref={haloRef} position={[0, 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.55, 0.85, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.6} />
      </mesh>

      {/* Body: torso */}
      <mesh position={[0, 0.75, 0]} castShadow>
        <cylinderGeometry args={[0.2, 0.2, 0.7, 12]} />
        <meshStandardMaterial color={color} roughness={0.4} metalness={0.1} />
      </mesh>

      {/* Head */}
      <mesh position={[0, 1.3, 0]} castShadow>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color={isFatigued ? "#f87171" : "#f5cba7"} roughness={0.8} />
      </mesh>

      {/* Helmet */}
      <mesh position={[0, 1.46, 0]} castShadow>
        <sphereGeometry args={[0.24, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial color={isFatigued ? "#ef4444" : "#facc15"} roughness={0.3} />
      </mesh>

      {/* Headlamp on helmet (Linterna de casco minero) */}
      <mesh position={[0, 1.5, 0.22]}>
        <boxGeometry args={[0.08, 0.08, 0.06]} />
        <meshStandardMaterial color="#ffffff" emissive="#fef08a" emissiveIntensity={2.0} />
      </mesh>
      <spotLight
        position={[0, 1.5, 0.25]}
        target-position={[0, 0.5, 6]}
        angle={0.45}
        penumbra={0.3}
        intensity={3.5}
        color="#fef3c7"
        distance={15}
      />

      {/* Left arm */}
      <mesh position={[-0.28, 0.85, 0]} rotation={[0, 0, 0.3]} castShadow>
        <cylinderGeometry args={[0.07, 0.07, 0.5, 8]} />
        <meshStandardMaterial color={color} roughness={0.5} />
      </mesh>

      {/* Right arm */}
      <mesh position={[0.28, 0.85, 0]} rotation={[0, 0, -0.3]} castShadow>
        <cylinderGeometry args={[0.07, 0.07, 0.5, 8]} />
        <meshStandardMaterial color={color} roughness={0.5} />
      </mesh>

      {/* Left leg */}
      <mesh position={[-0.12, 0.23, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.09, 0.45, 8]} />
        <meshStandardMaterial color="#374151" roughness={0.8} />
      </mesh>

      {/* Right leg */}
      <mesh position={[0.12, 0.23, 0]} castShadow>
        <cylinderGeometry args={[0.09, 0.09, 0.45, 8]} />
        <meshStandardMaterial color="#374151" roughness={0.8} />
      </mesh>

      {/* Label with Biometrics */}
      <Html position={[0, 2.0, 0]} center distanceFactor={8}>
        <div className={`flex flex-col items-center gap-0.5 px-2.5 py-1.5 rounded-lg text-xs font-bold text-white shadow-2xl backdrop-blur-md border whitespace-nowrap ${
          riskLevel === 'ALTO' ? 'bg-red-600/90 border-red-400' :
          riskLevel === 'MEDIO' ? 'bg-amber-500/90 border-amber-300 text-black' :
          'bg-emerald-600/90 border-emerald-400'
        }`}>
          <div className="flex items-center gap-1">
            <span>👷</span>
            <span>{label}</span>
          </div>
          <div className="text-[10px] font-medium opacity-95 flex items-center gap-1 border-t border-white/20 pt-0.5 w-full justify-center">
            <span>❤️ {Math.round(bpm)} BPM</span>
            <span>|</span>
            <span>⚡ Fatiga: {fatigueIndex.toFixed(2)}</span>
            {isFatigued && <span className="text-red-200 animate-pulse font-extrabold">⚠️ ALERTA</span>}
          </div>
        </div>
      </Html>
    </group>
  );
}

