"use client";

import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import type { Mesh } from "three";

function WireframeSphere() {
  const meshRef = useRef<Mesh>(null);

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.8;
      meshRef.current.rotation.x += delta * 0.3;
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
      meshRef.current.scale.setScalar(scale);
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1.5, 24, 24]} />
      <meshBasicMaterial color="#00d4ff" wireframe transparent opacity={0.3} />
    </mesh>
  );
}

function LoadingCanvas() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <WireframeSphere />
    </>
  );
}

export default function LoadingScene() {
  return (
    <div className="flex h-[60vh] w-full flex-col items-center justify-center gap-6">
      <div className="h-64 w-64">
        <Suspense fallback={null}>
          <Canvas camera={{ position: [0, 0, 4] }}>
            <LoadingCanvas />
          </Canvas>
        </Suspense>
      </div>
      <div className="flex flex-col items-center gap-2">
        <p className="animate-pulse text-lg font-medium text-cyan glow-text-cyan">
          분석 중...
        </p>
        <p className="text-sm text-foreground/30">
          AI가 종목을 분석하고 있습니다
        </p>
      </div>
    </div>
  );
}
