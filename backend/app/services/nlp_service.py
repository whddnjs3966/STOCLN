"""VADER + TextBlob 하이브리드 NLP 감성 분석 서비스

stocksight(shirosaidev/stocksight) 프로젝트의 접근법을 차용:
- TextBlob: polarity(-1~+1) + subjectivity(0~1)
- VADER: compound score(-1~+1) + neg/neu/pos breakdown
- 두 엔진의 결과를 결합하여 최종 감성 판정
"""

import logging
import re

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

_vader = SentimentIntensityAnalyzer()


def clean_text(text: str) -> str:
    """HTML 태그, URL 등을 제거하여 텍스트를 정리합니다."""
    text = text.replace("\n", " ")
    text = re.sub(r"https?\S+", "", text)
    text = re.sub(r"&.*?;", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"<b>|</b>", "", text)
    text = text.strip()
    return text


def analyze_sentiment_nlp(text: str) -> dict:
    """단일 텍스트에 대해 VADER + TextBlob 하이브리드 감성 분석을 수행합니다.

    Returns:
        {
            "polarity": float,       # -1.0 ~ +1.0 (TextBlob + VADER 평균)
            "subjectivity": float,   # 0.0 ~ 1.0 (TextBlob)
            "vader_compound": float, # -1.0 ~ +1.0
            "vader_pos": float,      # 0.0 ~ 1.0
            "vader_neg": float,      # 0.0 ~ 1.0
            "vader_neu": float,      # 0.0 ~ 1.0
            "sentiment": str,        # "positive", "negative", "neutral"
        }
    """
    cleaned = clean_text(text)
    if not cleaned:
        return _neutral_result()

    # TextBlob analysis
    blob = TextBlob(cleaned)
    tb_polarity = blob.sentiment.polarity      # -1.0 ~ +1.0
    tb_subjectivity = blob.sentiment.subjectivity  # 0.0 ~ 1.0

    # VADER analysis
    vs = _vader.polarity_scores(cleaned)

    # Hybrid sentiment determination (stocksight algorithm)
    if tb_polarity < 0 and vs["compound"] <= -0.05:
        sentiment = "negative"
    elif tb_polarity > 0 and vs["compound"] >= 0.05:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    # Combined polarity (average of TextBlob and VADER)
    polarity = (tb_polarity + vs["compound"]) / 2

    return {
        "polarity": round(polarity, 4),
        "subjectivity": round(tb_subjectivity, 4),
        "vader_compound": round(vs["compound"], 4),
        "vader_pos": round(vs["pos"], 4),
        "vader_neg": round(vs["neg"], 4),
        "vader_neu": round(vs["neu"], 4),
        "sentiment": sentiment,
    }


def analyze_news_sentiment_nlp(news_items: list[dict]) -> dict:
    """뉴스 목록에 대해 NLP 기반 감성 분석을 수행합니다.

    Returns:
        {
            "score": int,            # -100 ~ +100
            "polarity": float,       # -1.0 ~ +1.0 (평균)
            "subjectivity": float,   # 0.0 ~ 1.0 (평균)
            "positive_pct": float,   # 긍정 뉴스 비율 (%)
            "negative_pct": float,   # 부정 뉴스 비율 (%)
            "neutral_pct": float,    # 중립 뉴스 비율 (%)
            "analyzed_count": int,   # 분석된 기사 수
        }
    """
    if not news_items:
        return {
            "score": 0,
            "polarity": 0.0,
            "subjectivity": 0.0,
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 0.0,
            "analyzed_count": 0,
        }

    results = []
    for item in news_items[:10]:
        # Prefer full_text if available (from scraper), fall back to title + description
        full_text = item.get("full_text", "")
        if full_text:
            text = full_text
        else:
            text = f"{item.get('title', '')} {item.get('description', '')}"
        result = analyze_sentiment_nlp(text)
        results.append(result)

    # Aggregate
    total = len(results)
    avg_polarity = sum(r["polarity"] for r in results) / total
    avg_subjectivity = sum(r["subjectivity"] for r in results) / total
    pos_count = sum(1 for r in results if r["sentiment"] == "positive")
    neg_count = sum(1 for r in results if r["sentiment"] == "negative")
    neu_count = total - pos_count - neg_count

    # Convert polarity (-1~+1) to score (-100~+100)
    score = int(round(avg_polarity * 100))
    score = max(-100, min(100, score))

    return {
        "score": score,
        "polarity": round(avg_polarity, 4),
        "subjectivity": round(avg_subjectivity, 4),
        "positive_pct": round(pos_count / total * 100, 1),
        "negative_pct": round(neg_count / total * 100, 1),
        "neutral_pct": round(neu_count / total * 100, 1),
        "analyzed_count": total,
    }


def _neutral_result() -> dict:
    return {
        "polarity": 0.0,
        "subjectivity": 0.0,
        "vader_compound": 0.0,
        "vader_pos": 0.0,
        "vader_neg": 0.0,
        "vader_neu": 1.0,
        "sentiment": "neutral",
    }
