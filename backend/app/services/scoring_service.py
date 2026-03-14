"""4-Factor Quant Engine: 최종 스코어 산출 서비스

가중치: 뉴스감성 30% | 펀더멘털 30% | 기술적 25% | 매크로/섹터 15%
"""

import numpy as np
import pandas as pd

from app.models.schemas import FundamentalDetail, TechnicalDetail

# 가중치 설정
WEIGHTS = {
    "news_sentiment": 0.30,
    "fundamental": 0.30,
    "technical": 0.25,
    "macro_sector": 0.15,
}


def calculate_technical_score(hist: pd.DataFrame) -> tuple[float, TechnicalDetail]:
    """기술적 모멘텀 스코어를 계산합니다. (이동평균, MACD, RSI)

    Returns:
        (score 0~100, TechnicalDetail with raw metrics)
    """
    if hist is None or hist.empty or len(hist) < 26:
        return 50.0, TechnicalDetail()  # 데이터 부족 시 중립

    close = hist["Close"]
    score = 50.0

    # 이동평균선 정배열 체크 (5 > 20 > 60)
    ma5_val = round(float(close.rolling(5).mean().iloc[-1]), 2)
    ma20_val = round(float(close.rolling(20).mean().iloc[-1]), 2)
    ma60_val = round(float(close.rolling(min(60, len(close))).mean().iloc[-1]), 2)

    if ma5_val > ma20_val > ma60_val:
        score += 15
        ma_alignment = "정배열"
    elif ma5_val < ma20_val < ma60_val:
        score -= 15
        ma_alignment = "역배열"
    else:
        ma_alignment = "혼합"

    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd_series = ema12 - ema26
    signal_series = macd_series.ewm(span=9).mean()

    macd_val = round(float(macd_series.iloc[-1]), 2)
    signal_val = round(float(signal_series.iloc[-1]), 2)

    if macd_series.iloc[-1] > signal_series.iloc[-1] and macd_series.iloc[-2] <= signal_series.iloc[-2]:
        score += 15
        macd_cross = "골든크로스"
    elif macd_series.iloc[-1] < signal_series.iloc[-1] and macd_series.iloc[-2] >= signal_series.iloc[-2]:
        score -= 15
        macd_cross = "데드크로스"
    else:
        macd_cross = ""

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 100
    rsi_val = round(float(100 - (100 / (1 + rs))), 2)

    if rsi_val < 30:
        score += 10  # 과매도 -> 매수 기회
    elif rsi_val > 70:
        score -= 10  # 과매수 -> 주의

    detail = TechnicalDetail(
        ma5=ma5_val,
        ma20=ma20_val,
        ma60=ma60_val,
        ma_alignment=ma_alignment,
        macd=macd_val,
        macd_signal=signal_val,
        macd_cross=macd_cross,
        rsi=rsi_val,
    )

    return float(np.clip(score, 0, 100)), detail


def calculate_fundamental_score(info: dict) -> tuple[float, FundamentalDetail]:
    """펀더멘털 스코어를 계산합니다. (PER, PBR, ROE)

    Returns:
        (score 0~100, FundamentalDetail with raw metrics)
    """
    score = 50.0

    # PER: trailingPE 우선, 없으면 forwardPE 또는 priceEpsCurrentYear 사용
    raw_per = info.get("trailingPE") or info.get("forwardPE") or info.get("priceEpsCurrentYear")
    per_val: float | None = None
    if raw_per and raw_per > 0:
        per_val = round(float(raw_per), 2)
        if per_val < 10:
            score += 20
        elif per_val < 15:
            score += 10
        elif per_val > 30:
            score -= 15

    # PBR: priceToBook 우선, 없으면 currentPrice / bookValue로 계산
    raw_pbr = info.get("priceToBook")
    if not raw_pbr:
        book_val = info.get("bookValue")
        cur_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if book_val and book_val > 0 and cur_price:
            raw_pbr = cur_price / book_val
    pbr_val: float | None = None
    if raw_pbr and raw_pbr > 0:
        pbr_val = round(float(raw_pbr), 2)
        if pbr_val < 1:
            score += 15
        elif pbr_val < 2:
            score += 5
        elif pbr_val > 5:
            score -= 10

    raw_roe = info.get("returnOnEquity")
    roe_val: float | None = None
    if raw_roe:
        roe_pct = raw_roe * 100
        roe_val = round(float(roe_pct), 2)
        if roe_pct > 15:
            score += 15
        elif roe_pct > 10:
            score += 5
        elif roe_pct < 0:
            score -= 20

    raw_cap = info.get("marketCap")
    market_cap_val: float | None = round(float(raw_cap), 2) if raw_cap else None

    raw_div = info.get("dividendYield")
    # yfinance KR stocks: dividendYield may already be in percent (e.g. 1.2 = 1.2%)
    # US stocks: dividendYield is a ratio (e.g. 0.012 = 1.2%)
    div_val: float | None = None
    if raw_div:
        div_val = round(float(raw_div * 100), 2) if raw_div < 1 else round(float(raw_div), 2)

    detail = FundamentalDetail(
        per=per_val,
        pbr=pbr_val,
        roe=roe_val,
        market_cap=market_cap_val,
        dividend_yield=div_val,
    )

    return float(np.clip(score, 0, 100)), detail


def calculate_total_score(
    news_score: float,
    fundamental_score: float,
    technical_score: float,
    macro_score: float,
) -> float:
    """4개 팩터를 가중 합산하여 최종 스코어(0~100)를 산출합니다."""
    # news_score는 -100~+100 범위 -> 0~100으로 정규화
    normalized_news = (news_score + 100) / 2

    total = (
        normalized_news * WEIGHTS["news_sentiment"]
        + fundamental_score * WEIGHTS["fundamental"]
        + technical_score * WEIGHTS["technical"]
        + macro_score * WEIGHTS["macro_sector"]
    )
    return round(float(np.clip(total, 0, 100)), 1)
