"""API 라우트 정의"""

import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    HealthResponse,
    ScoreDetail,
    StockAnalysisResponse,
    StockSearchRequest,
    TopPickItem,
    TopPicksResponse,
)
from app.services.ai_service import analyze_news_sentiment
from app.services.financial_service import get_stock_data
from app.services.macro_service import calculate_macro_score
from app.services.news_service import fetch_news
from app.services.scoring_service import (
    calculate_fundamental_score,
    calculate_technical_score,
    calculate_total_score,
)
from app.utils.sanitize import sanitize_stock_query

logger = logging.getLogger(__name__)

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
    logger.info("Fetching stock data for ticker: %s", ticker)
    stock_data = get_stock_data(ticker)
    if not stock_data:
        logger.warning("No stock data found for ticker: %s", ticker)
        raise HTTPException(status_code=404, detail="종목 데이터를 찾을 수 없습니다.")

    stock_name = stock_data["info"].get("shortName", query)
    sector = stock_data["info"].get("sector", "")

    # 2. 뉴스 수집 + 감성 분석 + 매크로 스코어를 병렬 실행
    logger.info("Running parallel analysis for %s (sector: %s)", stock_name, sector)
    try:
        news_items, macro_score = await asyncio.gather(
            fetch_news(stock_name),
            calculate_macro_score(sector),
        )
    except Exception:
        logger.exception("Error during parallel news/macro fetch for %s", ticker)
        news_items = []
        macro_score = 50.0

    # 감성 분석 (뉴스 결과에 의존)
    try:
        sentiment_result = await analyze_news_sentiment(news_items)
    except Exception:
        logger.exception("Error during sentiment analysis for %s", ticker)
        sentiment_result = {"score": 0, "summary": "감성 분석 중 오류가 발생했습니다."}

    # 3. 기술적/펀더멘털 분석 (동기 함수)
    technical_score = calculate_technical_score(stock_data["history"])
    fundamental_score = calculate_fundamental_score(stock_data["info"])

    # 4. 최종 스코어 합산
    total_score = calculate_total_score(
        news_score=sentiment_result["score"],
        fundamental_score=fundamental_score,
        technical_score=technical_score,
        macro_score=macro_score,
    )

    logger.info(
        "Analysis complete for %s: total=%.1f (tech=%.1f, fund=%.1f, macro=%.1f, news=%d)",
        ticker, total_score, technical_score, fundamental_score, macro_score,
        sentiment_result["score"],
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


@router.get("/top-picks", response_model=TopPicksResponse)
async def get_top_picks():
    """사전 계산된 추천 종목 리스트를 반환합니다.

    현재는 플레이스홀더 데이터를 반환합니다.
    향후 스케줄러가 주기적으로 분석 결과를 갱신할 예정입니다.
    """
    logger.info("Top picks endpoint called (returning placeholder data)")

    now = datetime.now(timezone.utc).isoformat()
    placeholder_items = [
        TopPickItem(
            stock_code="005930",
            stock_name="삼성전자",
            total_score=72.5,
            price_change_pct=1.2,
            analyzed_at=now,
        ),
        TopPickItem(
            stock_code="000660",
            stock_name="SK하이닉스",
            total_score=68.3,
            price_change_pct=0.8,
            analyzed_at=now,
        ),
        TopPickItem(
            stock_code="035420",
            stock_name="NAVER",
            total_score=64.1,
            price_change_pct=-0.5,
            analyzed_at=now,
        ),
    ]

    return TopPicksResponse(items=placeholder_items, generated_at=now)
