'use client';

import { DoubleSide } from 'three';

export default function TunnelGeometry() {
  // Arcos de soporte minero (Entribado de acero/madera a lo largo del socavón)
  const archPositions = [-30, -20, -10, 0, 10, 20, 30];

  return (
    <group>
      {/* Suelo rugoso del socavón minero */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[120, 120]} />
        <meshStandardMaterial color="#1c1917" roughness={0.95} metalness={0.1} />
      </mesh>

      {/* Paredes y Bóveda del Túnel Subterráneo */}
      <mesh position={[0, 0, 0]} receiveShadow castShadow>
        <cylinderGeometry args={[14, 14, 100, 32, 1, true, 0, Math.PI]} />
        <meshStandardMaterial color="#27272a" roughness={0.9} side={DoubleSide} />
      </mesh>

      {/* Manga de Ventilación Amarilla en el Techo del Túnel */}
      <mesh position={[-8, 11, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1.2, 1.2, 100, 16]} />
        <meshStandardMaterial color="#eab308" roughness={0.4} metalness={0.2} />
      </mesh>

      {/* Arcos Estructurales de Soporte Minero (Entribado) */}
      {archPositions.map((x, idx) => (
        <group key={idx} position={[x, 0, 0]}>
          {/* Arco de acero/viga */}
          <mesh rotation={[0, Math.PI / 2, 0]}>
            <torusGeometry args={[13.8, 0.35, 12, 24, Math.PI]} />
            <meshStandardMaterial color="#475569" metalness={0.7} roughness={0.3} />
          </mesh>
          
          {/* Lámpara de Socavón cálida en cada arco */}
          <mesh position={[0, 13.2, 0]}>
            <boxGeometry args={[0.5, 0.4, 0.5]} />
            <meshStandardMaterial color="#fef08a" emissive="#eab308" emissiveIntensity={1.5} />
          </mesh>
          <pointLight position={[0, 12.8, 0]} color="#fbbf24" intensity={1.8} distance={18} />
        </group>
      ))}

      {/* Tuberías de drenaje / cables laterales en la pared del socavón */}
      <mesh position={[0, 4, 13.5]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.15, 0.15, 100, 8]} />
        <meshStandardMaterial color="#3b82f6" roughness={0.5} />
      </mesh>
      <mesh position={[0, 3.7, 13.5]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.12, 0.12, 100, 8]} />
        <meshStandardMaterial color="#ef4444" roughness={0.5} />
      </mesh>
    </group>
  );
}
