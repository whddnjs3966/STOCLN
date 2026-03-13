from pydantic import BaseModel


class StockSearchRequest(BaseModel):
    query: str
    market: str = "KR"  # KR or US


class ScoreDetail(BaseModel):
    news_sentiment: float  # -100 ~ +100 -> normalized to 0~100
    fundamental: float  # 0 ~ 100
    technical: float  # 0 ~ 100
    macro_sector: float  # 0 ~ 100


class StockAnalysisResponse(BaseModel):
    stock_code: str
    stock_name: str
    market: str
    current_price: float
    price_change_pct: float
    total_score: float  # 0 ~ 100
    scores: ScoreDetail
    ai_summary: str  # 3-line AI briefing
    news_highlights: list[dict]
    analyzed_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
