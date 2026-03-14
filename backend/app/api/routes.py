"""API 라우트 정의"""

import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    HealthResponse,
    NlpSentimentDetail,
    PricePoint,
    ScoreBreakdown,
    ScoreDetail,
    StockAnalysisResponse,
    StockSearchRequest,
    StockSearchResponse,
    StockSearchResult,
    TopPickItem,
    TopPicksResponse,
)
from app.services.ai_service import analyze_news_sentiment
from app.services.financial_service import get_stock_data, resolve_kr_ticker, search_stocks
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


@router.get("/search", response_model=StockSearchResponse)
async def search_stock(
    q: str = Query(..., min_length=1, max_length=50, description="검색어 (종목명 일부)"),
    limit: int = Query(default=20, ge=1, le=100, description="최대 결과 수"),
):
    """종목명 자동완성 검색 엔드포인트.

    - 대소문자 무시 (sk, SK, Sk 모두 동일하게 처리)
    - 부분 일치 지원 (예: '카카오' → 카카오, 카카오뱅크, 카카오페이, 카카오게임즈, ...)
    - KOSPI/KOSDAQ 구분 정보 포함
    """
    sanitized = sanitize_stock_query(q)
    if not sanitized:
        raise HTTPException(status_code=400, detail="유효하지 않은 검색어입니다.")

    matches = search_stocks(sanitized, limit=limit)
    return StockSearchResponse(
        results=[StockSearchResult(**m) for m in matches],
        query=sanitized,
        total=len(matches),
    )


@router.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockSearchRequest):
    """종목을 분석하여 4-Factor 스코어를 반환합니다."""
    query = sanitize_stock_query(request.query)
    if not query:
        raise HTTPException(status_code=400, detail="유효하지 않은 검색어입니다.")

    # 종목 코드 변환
    if request.market == "KR":
        ticker = resolve_kr_ticker(query)
        if not ticker:
            raise HTTPException(
                status_code=404,
                detail=f"'{query}'에 해당하는 종목을 찾을 수 없습니다.",
            )
    else:
        ticker = query

    # 1. 주가 데이터 수집
    logger.info("Fetching stock data for ticker: %s", ticker)
    stock_data = get_stock_data(ticker)
    if not stock_data:
        logger.warning("No stock data found for ticker: %s", ticker)
        raise HTTPException(status_code=404, detail="종목 데이터를 찾을 수 없습니다.")

    stock_name_en = stock_data["info"].get("shortName", query)
    # 한국 시장: 원래 검색어(한글)를 메인 이름으로, 영문은 보조
    stock_name = query if request.market == "KR" else stock_name_en
    stock_name_sub = stock_name_en if request.market == "KR" else ""
    sector = stock_data["info"].get("sector", "")

    # 2. 기술적/펀더멘털 분석 (동기 함수) — AI 브리핑에 컨텍스트를 넘기기 위해 먼저 실행
    technical_score, technical_detail = calculate_technical_score(stock_data["history"])
    fundamental_score, fundamental_detail = calculate_fundamental_score(stock_data["info"])

    # 3. 주가 히스토리 추출 (차트용)
    price_history = []
    hist_df = stock_data["history"]
    for date_idx, row in hist_df.iterrows():
        price_history.append({
            "date": date_idx.strftime("%Y-%m-%d"),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]) if "Volume" in row else 0,
        })

    # 4. 뉴스 수집 + 매크로 스코어를 병렬 실행
    # 한국 시장: 원래 검색어(한글)로 뉴스 검색, 해외: yfinance shortName 사용
    news_query = query if request.market == "KR" else stock_name
    logger.info("Running parallel analysis for %s (news_query: %s, sector: %s)", stock_name, news_query, sector)
    try:
        news_items, macro_score = await asyncio.gather(
            fetch_news(news_query),
            calculate_macro_score(sector),
        )
    except Exception:
        logger.exception("Error during parallel news/macro fetch for %s", ticker)
        news_items = []
        macro_score = 50.0

    # 5. 감성 분석 — 기술적/펀더멘털 컨텍스트를 포함한 종합 투자 브리핑
    try:
        sentiment_result = await analyze_news_sentiment(
            news_items,
            stock_name=stock_name,
            technical_summary={
                "ma_alignment": technical_detail.ma_alignment,
                "rsi": technical_detail.rsi,
                "macd_cross": technical_detail.macd_cross,
            },
            fundamental_summary={
                "per": fundamental_detail.per,
                "pbr": fundamental_detail.pbr,
                "roe": fundamental_detail.roe,
            },
            sector=sector,
        )
    except Exception:
        logger.exception("Error during sentiment analysis for %s", ticker)
        sentiment_result = {
            "score": 0,
            "summary": "감성 분석 중 오류가 발생했습니다.",
            "nlp": {},
        }

    # 6. 최종 스코어 합산
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

    nlp_data = sentiment_result.get("nlp", {})

    return StockAnalysisResponse(
        stock_code=query,
        stock_name=stock_name,
        stock_name_sub=stock_name_sub,
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
        score_details=ScoreBreakdown(
            technical=technical_detail,
            fundamental=fundamental_detail,
            sector=sector,
        ),
        ai_summary=sentiment_result["summary"],
        news_highlights=news_items[:5],
        nlp_sentiment=NlpSentimentDetail(**nlp_data),
        price_history=[PricePoint(**p) for p in price_history],
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
