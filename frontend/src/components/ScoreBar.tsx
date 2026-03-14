"use client";

import { useEffect, useState } from "react";
import type { ScoreDetail } from "@/lib/api";

interface ScoreBarProps {
  scores: ScoreDetail;
}

interface BarItemProps {
  label: string;
  desc: string;
  score: number;
  weight: number;
  delay: number;
}

function getBarColor(score: number): string {
  if (score >= 70) return "bg-green";
  if (score >= 40) return "bg-yellow";
  return "bg-red";
}

function getBarGlow(score: number): string {
  if (score >= 70) return "shadow-[0_0_12px_rgba(0,255,136,0.4)]";
  if (score >= 40) return "shadow-[0_0_12px_rgba(255,214,0,0.4)]";
  return "shadow-[0_0_12px_rgba(255,71,87,0.4)]";
}

function BarItem({ label, desc, score, weight, delay }: BarItemProps) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setWidth(score), delay);
    return () => clearTimeout(timer);
  }, [score, delay]);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-foreground/70">{label}</span>
          <span className="text-[11px] text-foreground/30">{desc}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-foreground/30">
            가중치 {weight}%
          </span>
          <span className="min-w-[2.5rem] text-right text-sm font-bold tabular-nums text-foreground">
            {score}
          </span>
        </div>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-light">
        <div
          className={`h-full rounded-full transition-all duration-1000 ease-out ${getBarColor(score)} ${getBarGlow(score)}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

export default function ScoreBar({ scores }: ScoreBarProps) {
  const factors = [
    { label: "뉴스 감성", desc: "뉴스 기반 시장 분위기", score: scores.news_sentiment, weight: 30 },
    { label: "펀더멘털", desc: "재무제표 기반 기업 가치", score: scores.fundamental, weight: 30 },
    { label: "기술적 모멘텀", desc: "차트 지표 기반 추세", score: scores.technical, weight: 25 },
    { label: "매크로/섹터", desc: "거시경제 및 업종 환경", score: scores.macro_sector, weight: 15 },
  ];

  return (
    <div className="glass flex h-full flex-col rounded-2xl p-5">
      <h3 className="mb-4 text-sm font-semibold text-foreground/50">
        Score Breakdown
      </h3>
      <div className="flex flex-1 flex-col justify-center gap-4">
        {factors.map((f, i) => (
          <BarItem
            key={f.label}
            label={f.label}
            desc={f.desc}
            score={f.score}
            weight={f.weight}
            delay={i * 150}
          />
        ))}
      </div>
    </div>
  );
}
