"""API 라우트 정의"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    HealthResponse,
    ScoreDetail,
    StockAnalysisResponse,
    StockSearchRequest,
)
from app.services.ai_service import analyze_news_sentiment
from app.services.financial_service import get_stock_data
from app.services.news_service import fetch_news
from app.services.scoring_service import (
    calculate_fundamental_score,
    calculate_technical_score,
    calculate_total_score,
)
from app.utils.sanitize import sanitize_stock_query

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="0.1.0")


@router.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockSearchRequest):
    """종목을 분석하여 4-Factor 스코어를 반환합니다."""
    query = sanitize_stock_query(request.query)
    if not query:
        raise HTTPException(status_code=400, detail="유효하지 않은 검색어입니다.")

    # 종목 코드 변환 (한국 시장의 경우 .KS 또는 .KQ 접미사)
    ticker = query
    if request.market == "KR" and not query.endswith((".KS", ".KQ")):
        ticker = f"{query}.KS"

    # 1. 주가 데이터 수집
    stock_data = get_stock_data(ticker)
    if not stock_data:
        raise HTTPException(status_code=404, detail="종목 데이터를 찾을 수 없습니다.")

    stock_name = stock_data["info"].get("shortName", query)

    # 2. 병렬로 뉴스 수집 + 기술적/펀더멘털 분석
    import asyncio

    news_items = await fetch_news(stock_name)
    sentiment_task = asyncio.create_task(analyze_news_sentiment(news_items))

    technical_score = calculate_technical_score(stock_data["history"])
    fundamental_score = calculate_fundamental_score(stock_data["info"])

    sentiment_result = await sentiment_task

    # 3. 매크로 스코어 (Phase 1에서는 중립값 사용)
    macro_score = 50.0

    # 4. 최종 스코어 합산
    total_score = calculate_total_score(
        news_score=sentiment_result["score"],
        fundamental_score=fundamental_score,
        technical_score=technical_score,
        macro_score=macro_score,
    )

    return StockAnalysisResponse(
        stock_code=query,
        stock_name=stock_name,
        market=request.market,
        current_price=stock_data["current_price"],
        price_change_pct=stock_data["price_change_pct"],
        total_score=total_score,
        scores=ScoreDetail(
            news_sentiment=(sentiment_result["score"] + 100) / 2,
            fundamental=fundamental_score,
            technical=technical_score,
            macro_sector=macro_score,
        ),
        ai_summary=sentiment_result["summary"],
        news_highlights=news_items[:5],
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )
