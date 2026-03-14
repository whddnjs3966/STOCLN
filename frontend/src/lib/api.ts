const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ScoreDetail {
  news_sentiment: number;
  fundamental: number;
  technical: number;
  macro_sector: number;
}

export interface TechnicalDetail {
  ma5: number | null;
  ma20: number | null;
  ma60: number | null;
  ma_alignment: string;
  macd: number | null;
  macd_signal: number | null;
  macd_cross: string;
  rsi: number | null;
}

export interface FundamentalDetail {
  per: number | null;
  pbr: number | null;
  roe: number | null;
  market_cap: number | null;
  dividend_yield: number | null;
}

export interface ScoreBreakdown {
  technical: TechnicalDetail;
  fundamental: FundamentalDetail;
  sector: string;
}

export interface PricePoint {
  date: string;
  close: number;
  volume: number;
}

export interface NlpSentimentDetail {
  polarity: number;      // -1.0 ~ +1.0
  subjectivity: number;  // 0.0 ~ 1.0
  positive_pct: number;  // 0 ~ 100
  negative_pct: number;  // 0 ~ 100
  neutral_pct: number;   // 0 ~ 100
  analyzed_count: number;
}

export interface StockAnalysis {
  stock_code: string;
  stock_name: string;
  stock_name_sub: string;
  market: string;
  current_price: number;
  price_change_pct: number;
  total_score: number;
  scores: ScoreDetail;
  score_details: ScoreBreakdown;
  nlp_sentiment: NlpSentimentDetail;
  price_history: PricePoint[];
  ai_summary: string;
  news_highlights: Array<{
    title: string;
    description: string;
    link: string;
    pub_date: string;
  }>;
  analyzed_at: string;
}

export async function analyzeStock(
  query: string,
  market: string = "KR"
): Promise<StockAnalysis> {
  const res = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, market }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "분석 실패" }));
    throw new Error(error.detail || "분석 중 오류가 발생했습니다.");
  }

  return res.json();
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

export interface StockSuggestion {
  name: string;
  code: string;
  market: string;
}

export async function searchStocks(q: string): Promise<StockSuggestion[]> {
  if (!q.trim()) return [];

  const res = await fetch(
    `${API_URL}/search?q=${encodeURIComponent(q.trim())}`,
    { signal: AbortSignal.timeout(5000) }
  );

  if (!res.ok) {
    throw new Error("검색 중 오류가 발생했습니다.");
  }

  return res.json();
}
