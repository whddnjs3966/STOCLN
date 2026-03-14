from pydantic import BaseModel


class NlpSentimentDetail(BaseModel):
    polarity: float = 0.0       # -1.0 ~ +1.0 (감성 극성)
    subjectivity: float = 0.0   # 0.0 ~ 1.0 (주관성)
    positive_pct: float = 0.0   # 긍정 뉴스 비율
    negative_pct: float = 0.0   # 부정 뉴스 비율
    neutral_pct: float = 0.0    # 중립 뉴스 비율
    analyzed_count: int = 0     # 분석된 기사 수


class StockSearchRequest(BaseModel):
    query: str
    market: str = "KR"  # KR or US


class ScoreDetail(BaseModel):
    news_sentiment: float  # -100 ~ +100 -> normalized to 0~100
    fundamental: float  # 0 ~ 100
    technical: float  # 0 ~ 100
    macro_sector: float  # 0 ~ 100


class TechnicalDetail(BaseModel):
    ma5: float | None = None
    ma20: float | None = None
    ma60: float | None = None
    ma_alignment: str = ""  # "정배열", "역배열", "혼합"
    macd: float | None = None
    macd_signal: float | None = None
    macd_cross: str = ""  # "골든크로스", "데드크로스", ""
    rsi: float | None = None


class FundamentalDetail(BaseModel):
    per: float | None = None
    pbr: float | None = None
    roe: float | None = None
    market_cap: float | None = None
    dividend_yield: float | None = None


class ScoreBreakdown(BaseModel):
    technical: TechnicalDetail = TechnicalDetail()
    fundamental: FundamentalDetail = FundamentalDetail()
    sector: str = ""


class PricePoint(BaseModel):
    date: str
    close: float
    volume: int = 0


class StockAnalysisResponse(BaseModel):
    stock_code: str
    stock_name: str
    stock_name_sub: str = ""  # 보조 이름 (한국: 영문명, 해외: 빈값)
    market: str
    current_price: float
    price_change_pct: float
    total_score: float  # 0 ~ 100
    scores: ScoreDetail
    score_details: ScoreBreakdown
    ai_summary: str  # 3-line AI briefing
    news_highlights: list[dict]
    nlp_sentiment: NlpSentimentDetail = NlpSentimentDetail()
    price_history: list[PricePoint] = []
    analyzed_at: str


class HealthResponse(BaseModel):
    status: str
    version: str


class TopPickItem(BaseModel):
    stock_code: str
    stock_name: str
    total_score: float  # 0 ~ 100
    price_change_pct: float
    analyzed_at: str


class TopPicksResponse(BaseModel):
    items: list[TopPickItem]
    generated_at: str


class StockSearchResult(BaseModel):
    name: str    # 종목명 (한글)
    code: str    # 6자리 종목코드
    market: str  # "KOSPI" 또는 "KOSDAQ"


class StockSearchResponse(BaseModel):
    results: list[StockSearchResult]
    query: str
    total: int
