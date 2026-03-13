"""4-Factor Quant Engine: 최종 스코어 산출 서비스"""

import numpy as np
import pandas as pd

# 가중치 설정
WEIGHTS = {
    "news_sentiment": 0.30,
    "fundamental": 0.30,
    "technical": 0.25,
    "macro_sector": 0.15,
}


def calculate_technical_score(hist: pd.DataFrame) -> float:
    """기술적 모멘텀 스코어를 계산합니다. (이동평균, MACD, RSI)"""
    if hist is None or hist.empty or len(hist) < 26:
        return 50.0  # 데이터 부족 시 중립

    close = hist["Close"]
    score = 50.0

    # 이동평균선 정배열 체크 (5 > 20 > 60)
    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(min(60, len(close))).mean().iloc[-1]
    if ma5 > ma20 > ma60:
        score += 15  # 정배열
    elif ma5 < ma20 < ma60:
        score -= 15  # 역배열

    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        score += 15  # 골든크로스
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
        score -= 15  # 데드크로스

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain.iloc[-1] / loss.iloc[-1] if loss.iloc[-1] != 0 else 100
    rsi = 100 - (100 / (1 + rs))
    if rsi < 30:
        score += 10  # 과매도 -> 매수 기회
    elif rsi > 70:
        score -= 10  # 과매수 -> 주의

    return float(np.clip(score, 0, 100))


def calculate_fundamental_score(info: dict) -> float:
    """펀더멘털 스코어를 계산합니다. (PER, PBR, ROE)"""
    score = 50.0

    per = info.get("trailingPE")
    if per and per > 0:
        if per < 10:
            score += 20
        elif per < 15:
            score += 10
        elif per > 30:
            score -= 15

    pbr = info.get("priceToBook")
    if pbr and pbr > 0:
        if pbr < 1:
            score += 15
        elif pbr < 2:
            score += 5
        elif pbr > 5:
            score -= 10

    roe = info.get("returnOnEquity")
    if roe:
        roe_pct = roe * 100
        if roe_pct > 15:
            score += 15
        elif roe_pct > 10:
            score += 5
        elif roe_pct < 0:
            score -= 20

    return float(np.clip(score, 0, 100))


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
