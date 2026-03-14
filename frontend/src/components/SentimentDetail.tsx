"use client";

import { useEffect, useState } from "react";
import type { NlpSentimentDetail } from "@/lib/api";

interface SentimentDetailProps {
  nlp: NlpSentimentDetail;
}

// ── Sub-components ────────────────────────────────────────────────────────────

interface PctBarProps {
  label: string;
  pct: number;
  color: string;
  mounted: boolean;
}

function PctBar({ label, pct, color, mounted }: PctBarProps) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-sm text-foreground/60">{label}</span>
        <span className="text-sm font-medium text-white">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-light">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: mounted ? `${Math.min(pct, 100)}%` : "0%" }}
        />
      </div>
    </div>
  );
}

interface PolarityBarProps {
  polarity: number;
  mounted: boolean;
}

function PolarityBar({ polarity, mounted }: PolarityBarProps) {
  // Map polarity (-1 ~ +1) to a percentage offset from the left (0% ~ 100%)
  // Center (0) = 50%
  const markerPct = ((polarity + 1) / 2) * 100;

  const polarityColor =
    polarity > 0.1
      ? "text-green"
      : polarity < -0.1
        ? "text-red"
        : "text-foreground/60";

  return (
    <div className="space-y-2 py-1.5 border-b border-white/5">
      <div className="flex items-center justify-between gap-4">
        <div className="shrink-0">
          <span className="text-sm text-cyan/80">감성 극성</span>
          <span className="ml-1.5 text-[11px] text-foreground/30">
            뉴스 감정의 긍부정 정도
          </span>
        </div>
        <span className={`text-sm font-medium ${polarityColor}`}>
          {polarity >= 0 ? "+" : ""}
          {polarity.toFixed(2)}
        </span>
      </div>

      {/* Range track */}
      <div className="relative">
        {/* Track */}
        <div className="relative h-2 w-full overflow-hidden rounded-full bg-surface-light">
          {/* Negative half tint */}
          <div className="absolute inset-y-0 left-0 w-1/2 bg-red/10 rounded-l-full" />
          {/* Positive half tint */}
          <div className="absolute inset-y-0 right-0 w-1/2 bg-green/10 rounded-r-full" />
          {/* Center hairline */}
          <div className="absolute inset-y-0 left-1/2 w-px bg-white/20" />
        </div>
        {/* Marker dot — positioned with absolute, offset by -4px (half of w-2) */}
        <div
          className="absolute -top-0.5 h-3 w-3 -translate-x-1/2 rounded-full border-2 border-cyan bg-background shadow-[0_0_6px_rgba(0,212,255,0.7)] transition-all duration-700"
          style={{ left: mounted ? `${markerPct}%` : "50%" }}
        />
        {/* Axis labels */}
        <div className="mt-3 flex justify-between text-[10px] text-foreground/25">
          <span>-1</span>
          <span>0</span>
          <span>+1</span>
        </div>
      </div>
    </div>
  );
}

interface SubjectivityBarProps {
  subjectivity: number;
  mounted: boolean;
}

function SubjectivityBar({ subjectivity, mounted }: SubjectivityBarProps) {
  const pct = Math.min(Math.max(subjectivity, 0), 1) * 100;

  return (
    <div className="space-y-1 py-1.5 border-b border-white/5">
      <div className="flex items-center justify-between gap-4">
        <div className="shrink-0">
          <span className="text-sm text-cyan/80">주관성</span>
          <span className="ml-1.5 text-[11px] text-foreground/30">
            사실 vs 의견 비율
          </span>
        </div>
        <span className="text-sm font-medium text-white">
          {subjectivity.toFixed(2)}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-surface-light">
        <div
          className="h-full rounded-full bg-cyan transition-all duration-700"
          style={{ width: mounted ? `${pct}%` : "0%" }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-foreground/25">
        <span>객관적</span>
        <span>주관적</span>
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function SentimentDetail({ nlp }: SentimentDetailProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, [nlp]);

  return (
    <div className="glass rounded-2xl p-5">
      <h3 className="mb-4 text-sm font-semibold text-foreground/50">
        감성 분석 상세
      </h3>

      <div className="grid grid-cols-1 gap-x-8 gap-y-4 md:grid-cols-2">
        {/* Left: 감성 분포 */}
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan/60">
            감성 분포
          </p>
          <p className="mb-3 text-[11px] text-foreground/30">
            수집된 뉴스 기사를 NLP로 분석한 긍정·부정·중립 비율입니다
          </p>
          <div className="space-y-3">
            <PctBar
              label="긍정"
              pct={nlp.positive_pct}
              color="bg-green"
              mounted={mounted}
            />
            <PctBar
              label="부정"
              pct={nlp.negative_pct}
              color="bg-red"
              mounted={mounted}
            />
            <PctBar
              label="중립"
              pct={nlp.neutral_pct}
              color="bg-foreground/30"
              mounted={mounted}
            />
          </div>
        </div>

        {/* Right: 극성 + 주관성 */}
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan/60">
            심층 지표
          </p>
          <p className="mb-3 text-[11px] text-foreground/30">
            감성 극성은 전체 뉴스의 긍부정 강도(-1~+1), 주관성은 사실 대비 의견 비율(0~1)입니다
          </p>
          <div className="space-y-0">
            <PolarityBar polarity={nlp.polarity} mounted={mounted} />
            <SubjectivityBar subjectivity={nlp.subjectivity} mounted={mounted} />
          </div>
        </div>
      </div>

      {/* Footer: analyzed count */}
      <div className="mt-4 flex items-center gap-2 border-t border-white/5 pt-4">
        <span className="text-sm text-cyan/80">분석 기사 수</span>
        <span className="rounded-full bg-surface-light px-3 py-0.5 text-sm font-medium text-foreground/70">
          {nlp.analyzed_count} 건
        </span>
      </div>
    </div>
  );
}
