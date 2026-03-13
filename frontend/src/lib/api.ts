const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ScoreDetail {
  news_sentiment: number;
  fundamental: number;
  technical: number;
  macro_sector: number;
}

export interface StockAnalysis {
  stock_code: string;
  stock_name: string;
  market: string;
  current_price: number;
  price_change_pct: number;
  total_score: number;
  scores: ScoreDetail;
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
