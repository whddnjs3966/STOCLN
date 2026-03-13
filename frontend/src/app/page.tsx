"use client";

import { useState, useCallback } from "react";
import type { StockAnalysis } from "@/lib/api";
import SearchBar from "@/components/SearchBar";
import LoadingScene from "@/components/LoadingScene";
import Dashboard from "@/components/Dashboard";

type AppState = "idle" | "loading" | "result" | "error";

export default function Home() {
  const [state, setState] = useState<AppState>("idle");
  const [result, setResult] = useState<StockAnalysis | null>(null);
  const [error, setError] = useState("");

  const handleResult = useCallback((data: StockAnalysis) => {
    setResult(data);
    setState("result");
  }, []);

  const handleLoading = useCallback((loading: boolean) => {
    if (loading) {
      setState("loading");
      setError("");
    }
  }, []);

  const handleError = useCallback((msg: string) => {
    setError(msg);
    setState("error");
  }, []);

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background">
      {/* Animated background gradient */}
      <div className="animate-gradient pointer-events-none fixed inset-0 bg-gradient-to-br from-cyan/[0.03] via-transparent to-green/[0.03]" />

      {/* Idle state: Hero */}
      {state === "idle" && (
        <div className="animate-fade-in flex min-h-screen flex-col items-center justify-center px-4">
          <div className="mb-12 text-center">
            <h1 className="glow-text-cyan mb-3 text-6xl font-black tracking-tight text-foreground sm:text-7xl">
              Stock
              <span className="text-cyan">Sight</span>
            </h1>
            <p className="text-lg text-foreground/40">
              AI 기반 3D 주식 예측 플랫폼
            </p>
          </div>
          <SearchBar
            onResult={handleResult}
            onLoading={handleLoading}
            onError={handleError}
          />
        </div>
      )}

      {/* Loading state */}
      {state === "loading" && (
        <div className="animate-fade-in flex min-h-screen flex-col items-center justify-center px-4">
          <LoadingScene />
        </div>
      )}

      {/* Error state: show search again */}
      {state === "error" && (
        <div className="animate-fade-in flex min-h-screen flex-col items-center justify-center gap-6 px-4">
          <div className="text-center">
            <h1 className="glow-text-cyan mb-3 text-4xl font-black tracking-tight text-foreground">
              Stock<span className="text-cyan">Sight</span>
            </h1>
          </div>
          <SearchBar
            onResult={handleResult}
            onLoading={handleLoading}
            onError={handleError}
          />
          {error && (
            <p className="max-w-md text-center text-sm text-red/80">{error}</p>
          )}
        </div>
      )}

      {/* Result state */}
      {state === "result" && result && (
        <div className="animate-fade-in min-h-screen">
          {/* Compact search bar at top */}
          <div className="sticky top-0 z-50 border-b border-foreground/5 bg-background/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
              <button
                onClick={() => setState("idle")}
                className="shrink-0 text-xl font-black tracking-tight text-foreground transition-colors hover:text-cyan"
              >
                S<span className="text-cyan">S</span>
              </button>
              <SearchBar
                onResult={handleResult}
                onLoading={handleLoading}
                onError={handleError}
                compact
              />
            </div>
          </div>

          {/* Dashboard */}
          <div className="pt-6">
            <Dashboard data={result} />
          </div>
        </div>
      )}
    </div>
  );
}
