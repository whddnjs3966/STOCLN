"use client";

import { Suspense, useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { MeshDistortMaterial, OrbitControls, Html } from "@react-three/drei";
import type { Mesh } from "three";
import { Color } from "three";

interface ScoreSphereProps {
  score: number;
}

function getScoreColor(score: number): Color {
  if (score <= 30) {
    const t = score / 30;
    return new Color().setRGB(
      1,
      t * 0.84,
      t * 0.18
    );
  } else if (score <= 60) {
    const t = (score - 30) / 30;
    return new Color().setRGB(
      1 - t,
      0.84 + t * 0.16,
      0.18 - t * 0.18 + t * 0.53
    );
  } else {
    const t = (score - 60) / 40;
    return new Color().setRGB(
      0,
      1 - t * 0.0,
      0.53 + t * 0.47
    );
  }
}

function Sphere({ score }: { score: number }) {
  const meshRef = useRef<Mesh>(null);
  const color = useMemo(() => getScoreColor(score), [score]);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.3;
      meshRef.current.rotation.x += delta * 0.1;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[2, 64, 64]} />
      <MeshDistortMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.3}
        roughness={0.2}
        metalness={0.8}
        distort={0.25}
        speed={2}
        transparent
        opacity={0.85}
      />
      <Html center distanceFactor={5}>
        <div className="pointer-events-none select-none text-center">
          <div
            className="text-6xl font-black tracking-tighter text-white drop-shadow-[0_0_30px_rgba(0,212,255,0.5)]"
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {score}
          </div>
          <div className="mt-1 text-xs font-medium uppercase tracking-widest text-white/50">
            Total Score
          </div>
        </div>
      </Html>
    </mesh>
  );
}

function SphereScene({ score }: { score: number }) {
  return (
    <>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={1.5} color="#00d4ff" />
      <pointLight position={[-10, -10, -5]} intensity={0.8} color="#00ff88" />
      <Sphere score={score} />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.5}
      />
    </>
  );
}

function FallbackLoader() {
  return (
    <div className="flex h-full w-full items-center justify-center">
      <div className="h-16 w-16 animate-spin rounded-full border-2 border-cyan/20 border-t-cyan" />
    </div>
  );
}

export default function ScoreSphere({ score }: ScoreSphereProps) {
  return (
    <div className="glass relative h-full min-h-[350px] w-full overflow-hidden rounded-2xl">
      <Suspense fallback={<FallbackLoader />}>
        <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
          <SphereScene score={score} />
        </Canvas>
      </Suspense>
      <div className="pointer-events-none absolute bottom-4 left-0 right-0 text-center text-xs text-foreground/20">
        드래그하여 회전
      </div>
    </div>
  );
}
