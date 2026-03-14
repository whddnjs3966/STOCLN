"use client";

import type { ScoreBreakdown } from "@/lib/api";

interface ScoreDetailProps {
  details: ScoreBreakdown;
  market: string;
}

// ── Format helpers ────────────────────────────────────────────────────────────

function fmt(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return value.toLocaleString("ko-KR", { maximumFractionDigits: 2 });
}

function formatPrice(value: number | null | undefined, market: string): string {
  if (value === null || value === undefined) return "-";
  if (market === "KR") {
    return value.toLocaleString("ko-KR") + " 원";
  }
  return "$" + value.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function formatMarketCap(
  value: number | null | undefined,
  market: string
): string {
  if (value === null || value === undefined) return "-";

  if (market === "KR") {
    const jo = 1_000_000_000_000; // 1조
    const eok = 100_000_000;      // 1억
    if (value >= jo) {
      const joVal = value / jo;
      return joVal.toLocaleString("ko-KR", { maximumFractionDigits: 1 }) + " 조원";
    }
    const eokVal = value / eok;
    return eokVal.toLocaleString("ko-KR", { maximumFractionDigits: 0 }) + " 억원";
  }

  // US market
  const billion = 1_000_000_000;
  const million = 1_000_000;
  if (value >= billion) {
    return (value / billion).toLocaleString("en-US", { maximumFractionDigits: 1 }) + "B";
  }
  return (value / million).toLocaleString("en-US", { maximumFractionDigits: 1 }) + "M";
}

// ── Sub-components ────────────────────────────────────────────────────────────

interface LabelValueProps {
  label: string;
  value: string;
  desc?: string;
}

function LabelValue({ label, value, desc }: LabelValueProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 border-b border-white/5 last:border-0">
      <div className="shrink-0">
        <span className="text-sm text-cyan/80">{label}</span>
        {desc && <span className="ml-1.5 text-[11px] text-foreground/30">{desc}</span>}
      </div>
      <span className="text-sm font-medium text-white text-right">{value}</span>
    </div>
  );
}

function AlignmentBadge({ value }: { value: string }) {
  let colorClass = "text-yellow";
  if (value === "정배열") colorClass = "text-green";
  else if (value === "역배열") colorClass = "text-red";

  return (
    <div className="flex items-center justify-between gap-4 py-1.5 border-b border-white/5">
      <div className="shrink-0">
        <span className="text-sm text-cyan/80">배열 상태</span>
        <span className="ml-1.5 text-[11px] text-foreground/30">이동평균선 정렬</span>
      </div>
      <span className={`text-sm font-semibold ${colorClass}`}>{value || "-"}</span>
    </div>
  );
}

function CrossBadge({ value }: { value: string }) {
  let colorClass = "text-foreground/40";
  if (value === "골든크로스") colorClass = "text-green";
  else if (value === "데드크로스") colorClass = "text-red";

  return (
    <div className="flex items-center justify-between gap-4 py-1.5 border-b border-white/5">
      <div className="shrink-0">
        <span className="text-sm text-cyan/80">MACD 크로스</span>
        <span className="ml-1.5 text-[11px] text-foreground/30">매매 신호</span>
      </div>
      <span className={`text-sm font-semibold ${colorClass}`}>{value || "-"}</span>
    </div>
  );
}

function RsiRow({ value }: { value: number | null }) {
  const display = value !== null && value !== undefined ? fmt(value) : "-";
  const pct = value !== null && value !== undefined ? Math.min(Math.max(value, 0), 100) : 0;

  // RSI zone colours: oversold < 30, overbought > 70
  let barColor = "bg-cyan";
  if (value !== null && value !== undefined) {
    if (value >= 70) barColor = "bg-red";
    else if (value <= 30) barColor = "bg-green";
  }

  return (
    <div className="space-y-1 py-1.5 border-b border-white/5 last:border-0">
      <div className="flex items-center justify-between gap-4">
        <div className="shrink-0">
          <span className="text-sm text-cyan/80">RSI</span>
          <span className="ml-1.5 text-[11px] text-foreground/30">과매수·과매도 지표</span>
        </div>
        <span className="text-sm font-medium text-white">{display}</span>
      </div>
      {value !== null && value !== undefined && (
        <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-surface-light">
          {/* 30 / 70 zone guides */}
          <div className="absolute inset-y-0 left-[30%] w-px bg-white/20" />
          <div className="absolute inset-y-0 left-[70%] w-px bg-white/20" />
          <div
            className={`h-full rounded-full ${barColor} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ScoreDetail({ details, market }: ScoreDetailProps) {
  const { technical, fundamental, sector } = details;

  return (
    <div className="glass rounded-2xl p-5">
      <h3 className="mb-4 text-sm font-semibold text-foreground/50">
        Score Details
      </h3>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Left: 기술적 분석 */}
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan/60">
            기술적 분석
          </p>
          <div className="space-y-0">
            <LabelValue
              label="MA5"
              desc="5일 이동평균"
              value={formatPrice(technical.ma5, market)}
            />
            <LabelValue
              label="MA20"
              desc="20일 이동평균"
              value={formatPrice(technical.ma20, market)}
            />
            <LabelValue
              label="MA60"
              desc="60일 이동평균"
              value={formatPrice(technical.ma60, market)}
            />
            <AlignmentBadge value={technical.ma_alignment} />
            <LabelValue label="MACD" desc="추세 전환 지표" value={fmt(technical.macd)} />
            <LabelValue label="Signal" desc="MACD 신호선" value={fmt(technical.macd_signal)} />
            <CrossBadge value={technical.macd_cross} />
            <RsiRow value={technical.rsi} />
          </div>
        </div>

        {/* Right: 펀더멘털 분석 */}
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan/60">
            펀더멘털 분석
          </p>
          <div className="space-y-0">
            <LabelValue
              label="PER"
              desc="주가수익비율"
              value={fundamental.per !== null && fundamental.per !== undefined ? fmt(fundamental.per) + " 배" : "-"}
            />
            <LabelValue
              label="PBR"
              desc="주가순자산비율"
              value={fundamental.pbr !== null && fundamental.pbr !== undefined ? fmt(fundamental.pbr) + " 배" : "-"}
            />
            <LabelValue
              label="ROE"
              desc="자기자본이익률"
              value={fundamental.roe !== null && fundamental.roe !== undefined ? fmt(fundamental.roe) + " %" : "-"}
            />
            <LabelValue
              label="시가총액"
              desc="기업의 총 시장가치"
              value={formatMarketCap(fundamental.market_cap, market)}
            />
            <LabelValue
              label="배당수익률"
              desc="주가 대비 배당금"
              value={fundamental.dividend_yield !== null && fundamental.dividend_yield !== undefined
                ? fmt(fundamental.dividend_yield) + " %"
                : "-"}
            />
          </div>
        </div>
      </div>

      {/* Sector tag */}
      <div className="mt-5 flex items-center gap-2 border-t border-white/5 pt-4">
        <span className="text-sm text-cyan/80">섹터</span>
        <span className="rounded-full bg-surface-light px-3 py-0.5 text-sm font-medium text-foreground/70">
          {sector || "-"}
        </span>
      </div>
    </div>
  );
}
