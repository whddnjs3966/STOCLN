"use client";

import ReactECharts from "echarts-for-react";
import type { PricePoint } from "@/lib/api";

interface PriceChartProps {
  priceHistory: PricePoint[];
  market: string;
}

export default function PriceChart({ priceHistory, market }: PriceChartProps) {
  const isKR = market === "KR";
  const currencySymbol = isKR ? "₩" : "$";

  const dates = priceHistory.map((p) => {
    const d = new Date(p.date);
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    return `${mm}/${dd}`;
  });

  const closes = priceHistory.map((p) => p.close);
  const volumes = priceHistory.map((p) => p.volume);

  const formatPrice = (value: number) =>
    isKR
      ? `${currencySymbol}${value.toLocaleString("ko-KR")}`
      : `${currencySymbol}${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const formatVolume = (value: number) => {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
    return String(value);
  };

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "rgba(10,10,26,0.95)",
      borderColor: "rgba(0,212,255,0.3)",
      borderWidth: 1,
      textStyle: { color: "#e0e0f0", fontSize: 12 },
      axisPointer: {
        type: "cross" as const,
        crossStyle: { color: "rgba(0,212,255,0.3)" },
        lineStyle: { color: "rgba(0,212,255,0.2)" },
      },
      formatter: (params: Array<{ seriesName: string; value: number; axisValue: string }>) => {
        const date = params[0]?.axisValue ?? "";
        const lines = params.map((p) => {
          if (p.seriesName === "종가") {
            return `<span style="color:#00d4ff">종가</span>: <b>${formatPrice(p.value)}</b>`;
          }
          return `<span style="color:rgba(0,212,255,0.4)">거래량</span>: <b>${formatVolume(p.value)}</b>`;
        });
        return `<div style="margin-bottom:4px;color:rgba(224,224,240,0.5);font-size:11px">${date}</div>${lines.join("<br/>")}`;
      },
    },
    grid: [
      {
        left: "8%",
        right: "4%",
        top: "8%",
        bottom: "38%",
      },
      {
        left: "8%",
        right: "4%",
        top: "68%",
        bottom: "8%",
      },
    ],
    xAxis: [
      {
        type: "category" as const,
        data: dates,
        gridIndex: 0,
        axisLabel: { show: false },
        axisLine: { lineStyle: { color: "rgba(0,212,255,0.08)" } },
        axisTick: { show: false },
        splitLine: { show: false },
      },
      {
        type: "category" as const,
        data: dates,
        gridIndex: 1,
        axisLabel: {
          color: "rgba(224,224,240,0.3)",
          fontSize: 10,
          interval: Math.floor(dates.length / 6),
        },
        axisLine: { lineStyle: { color: "rgba(0,212,255,0.08)" } },
        axisTick: { show: false },
        splitLine: { show: false },
      },
    ],
    yAxis: [
      {
        type: "value" as const,
        gridIndex: 0,
        scale: true,
        axisLabel: {
          color: "rgba(224,224,240,0.3)",
          fontSize: 10,
          formatter: (value: number) =>
            isKR
              ? value.toLocaleString("ko-KR")
              : value.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 2 }),
        },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: "rgba(0,212,255,0.06)" } },
      },
      {
        type: "value" as const,
        gridIndex: 1,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "종가",
        type: "line" as const,
        data: closes,
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: true,
        symbol: "none",
        lineStyle: {
          color: "#00d4ff",
          width: 2,
        },
        areaStyle: {
          color: {
            type: "linear" as const,
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(0,212,255,0.25)" },
              { offset: 1, color: "rgba(0,212,255,0.00)" },
            ],
          },
        },
        animationDuration: 1200,
        animationEasing: "cubicOut" as const,
      },
      {
        name: "거래량",
        type: "bar" as const,
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: "rgba(0,212,255,0.18)",
          borderRadius: [2, 2, 0, 0],
        },
        emphasis: {
          itemStyle: { color: "rgba(0,212,255,0.35)" },
        },
        animationDuration: 1200,
        animationEasing: "cubicOut" as const,
      },
    ],
  };

  return (
    <div className="glass rounded-2xl p-5">
      <div className="mb-3 flex items-baseline gap-2">
        <h3 className="text-sm font-semibold text-foreground/50">주가 추이</h3>
        <span className="text-[11px] text-foreground/30">최근 3개월</span>
      </div>
      <ReactECharts
        option={option}
        style={{ height: "280px", width: "100%" }}
        opts={{ renderer: "svg" }}
      />
    </div>
  );
}
