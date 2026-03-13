"use client";

import ReactECharts from "echarts-for-react";
import type { ScoreDetail } from "@/lib/api";

interface ScoreRadarProps {
  scores: ScoreDetail;
}

export default function ScoreRadar({ scores }: ScoreRadarProps) {
  const indicators = [
    { name: "뉴스 감성", max: 100 },
    { name: "펀더멘털", max: 100 },
    { name: "기술적 모멘텀", max: 100 },
    { name: "매크로/섹터", max: 100 },
  ];

  const values = [
    scores.news_sentiment,
    scores.fundamental,
    scores.technical,
    scores.macro_sector,
  ];

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item" as const,
      backgroundColor: "rgba(10,10,26,0.95)",
      borderColor: "rgba(0,212,255,0.3)",
      textStyle: { color: "#e0e0f0", fontSize: 12 },
      formatter: () => {
        return indicators
          .map(
            (ind, i) =>
              `<span style="color:#00d4ff">${ind.name}</span>: <b>${values[i]}</b>`
          )
          .join("<br/>");
      },
    },
    radar: {
      indicator: indicators,
      shape: "polygon" as const,
      splitNumber: 4,
      axisName: {
        color: "rgba(224,224,240,0.6)",
        fontSize: 11,
        fontWeight: 500,
      },
      splitLine: {
        lineStyle: { color: "rgba(0,212,255,0.08)" },
      },
      splitArea: {
        areaStyle: {
          color: [
            "rgba(0,212,255,0.02)",
            "rgba(0,212,255,0.04)",
            "rgba(0,212,255,0.02)",
            "rgba(0,212,255,0.04)",
          ],
        },
      },
      axisLine: {
        lineStyle: { color: "rgba(0,212,255,0.12)" },
      },
    },
    series: [
      {
        type: "radar" as const,
        data: [
          {
            value: values,
            name: "분석 점수",
            areaStyle: {
              color: "rgba(0,212,255,0.15)",
            },
            lineStyle: {
              color: "#00d4ff",
              width: 2,
            },
            itemStyle: {
              color: "#00d4ff",
              borderColor: "#00d4ff",
              borderWidth: 2,
            },
            symbol: "circle",
            symbolSize: 6,
          },
        ],
        animationDuration: 1200,
        animationEasing: "cubicOut" as const,
      },
    ],
  };

  return (
    <div className="glass flex h-full flex-col rounded-2xl p-4">
      <h3 className="mb-2 text-sm font-semibold text-foreground/50">
        Factor Analysis
      </h3>
      <div className="flex-1">
        <ReactECharts
          option={option}
          style={{ height: "100%", minHeight: "220px" }}
          opts={{ renderer: "svg" }}
        />
      </div>
    </div>
  );
}
