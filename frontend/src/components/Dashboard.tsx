"use client";

import { useEffect, useState } from "react";
import type { StockAnalysis } from "@/lib/api";
import StockHeader from "./StockHeader";
import ScoreSphere from "./ScoreSphere";
import ScoreRadar from "./ScoreRadar";
import ScoreBar from "./ScoreBar";
import AISummary from "./AISummary";
import NewsCard from "./NewsCard";
import ScoreDetail from "./ScoreDetail";
import PriceChart from "./PriceChart";
import SentimentDetail from "./SentimentDetail";

interface DashboardProps {
  data: StockAnalysis;
}

export default function Dashboard({ data }: DashboardProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className={`mx-auto w-full max-w-7xl space-y-4 px-4 pb-12 transition-all duration-700 ${
        mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
      }`}
    >
      {/* Top: Stock Header */}
      <StockHeader
        stockName={data.stock_name}
        stockNameSub={data.stock_name_sub}
        stockCode={data.stock_code}
        market={data.market}
        currentPrice={data.current_price}
        priceChangePct={data.price_change_pct}
        analyzedAt={data.analyzed_at}
      />

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Left: ScoreSphere */}
        <div className="min-h-[380px]">
          <ScoreSphere score={data.total_score} />
        </div>

        {/* Right top: ScoreRadar */}
        <div className="min-h-[380px]">
          <ScoreRadar scores={data.scores} />
        </div>
      </div>

      {/* Score bars full width */}
      <ScoreBar scores={data.scores} />

      {/* Price Chart */}
      <PriceChart priceHistory={data.price_history} market={data.market} />

      {/* Score detail metrics */}
      <ScoreDetail details={data.score_details} market={data.market} />

      {/* NLP Sentiment Detail */}
      <SentimentDetail nlp={data.nlp_sentiment} />

      {/* Bottom row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Bottom left: AI Summary */}
        <div className="min-h-[200px]">
          <AISummary summary={data.ai_summary} />
        </div>

        {/* Bottom right: News */}
        <div className="min-h-[200px]">
          <NewsCard news={data.news_highlights} />
        </div>
      </div>
    </div>
  );
}
