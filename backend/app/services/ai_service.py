"""Google Gemini + NLP 하이브리드 감성 분석 서비스"""

import json
import logging

from google import genai

from app.core.config import settings
from app.services.nlp_service import analyze_news_sentiment_nlp

logger = logging.getLogger(__name__)

# 클라이언트는 호출 시점에 지연 초기화합니다 (API 키 미설정 시 앱 로드 실패 방지)
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


async def analyze_news_sentiment(
    news_items: list[dict],
    stock_name: str = "",
    technical_summary: dict | None = None,
    fundamental_summary: dict | None = None,
    sector: str = "",
) -> dict:
    """뉴스 목록을 분석: NLP 기반 스코어링 + Gemini AI 종합 투자 브리핑."""
    if not news_items:
        return {
            "score": 0,
            "summary": "분석할 뉴스가 없습니다.",
            "nlp": {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "positive_pct": 0.0,
                "negative_pct": 0.0,
                "neutral_pct": 0.0,
                "analyzed_count": 0,
            },
        }

    # 1. NLP 분석 (항상 실행 — 무료, 즉시)
    nlp_result = analyze_news_sentiment_nlp(news_items)
    nlp_score = nlp_result["score"]

    # 2. Gemini AI 종합 투자 브리핑 시도
    gemini_summary = ""
    gemini_score = None
    if settings.gemini_api_key:
        try:
            news_text = "\n".join(
                f"- {item['title']}: {item.get('description', '')}"
                for item in news_items[:10]
            )
            display_name = stock_name or "해당 종목"
            prompt = (
                f"당신은 '{display_name}' 종목의 투자 분석 전문가입니다.\n"
                "아래 데이터를 종합하여 투자 브리핑을 작성하세요.\n"
                "반드시 제공된 데이터에 근거하여 분석하고, 존재하지 않는 정보를 지어내지 마세요.\n\n"
                f"[뉴스 동향]\n{news_text}\n\n"
            )

            if technical_summary:
                prompt += (
                    f"[기술적 지표]\n"
                    f"- 이동평균 배열: {technical_summary.get('ma_alignment', '정보없음')}\n"
                    f"- RSI: {technical_summary.get('rsi', '정보없음')}\n"
                    f"- MACD 크로스: {technical_summary.get('macd_cross', '없음') or '없음'}\n\n"
                )

            if fundamental_summary:
                per_str = f"{fundamental_summary['per']}배" if fundamental_summary.get('per') else "정보없음"
                pbr_str = f"{fundamental_summary['pbr']}배" if fundamental_summary.get('pbr') else "정보없음"
                roe_str = f"{fundamental_summary['roe']}%" if fundamental_summary.get('roe') else "정보없음"
                prompt += (
                    f"[펀더멘털]\n"
                    f"- PER: {per_str}\n"
                    f"- PBR: {pbr_str}\n"
                    f"- ROE: {roe_str}\n\n"
                )

            if sector:
                prompt += f"[섹터] {sector}\n\n"

            prompt += (
                "응답 형식 (JSON만 출력):\n"
                '{"score": -100~+100 사이의 정수, '
                '"summary": "종합 투자 브리핑 3~5줄 (한국어). '
                '뉴스/기술적/펀더멘털 관점을 종합한 투자 의견과 주요 리스크를 포함."}'
            )

            response = _get_client().models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.3,
                },
            )
            result = json.loads(response.text)
            # Gemini가 리스트로 반환할 수 있으므로 dict 추출
            if isinstance(result, list):
                result = result[0] if result else {}
            if not isinstance(result, dict):
                result = {}
            gemini_score = max(-100, min(100, int(result.get("score", 0))))
            gemini_summary = result.get("summary", "")
        except Exception:
            global _client
            _client = None  # 다음 호출 시 클라이언트 재생성
            logger.exception("Gemini sentiment analysis failed")

    # 3. 결과 합산
    if gemini_score is not None:
        # NLP 40% + Gemini 60% 가중 평균
        final_score = int(round(nlp_score * 0.4 + gemini_score * 0.6))
    else:
        final_score = nlp_score

    # NLP 기반 자동 요약 (Gemini 실패 시 fallback)
    if not gemini_summary:
        pos = nlp_result["positive_pct"]
        neg = nlp_result["negative_pct"]
        pol = nlp_result["polarity"]
        lines = []

        # NLP sentiment line
        if pol > 0.1:
            lines.append(f"뉴스 감성은 긍정적이며, 긍정 {pos}% / 부정 {neg}%입니다.")
        elif pol < -0.1:
            lines.append(f"뉴스 감성은 부정적이며, 긍정 {pos}% / 부정 {neg}%입니다.")
        else:
            lines.append(f"뉴스 감성은 중립적이며, 긍정 {pos}% / 부정 {neg}%입니다.")

        # Technical line
        if technical_summary:
            ma = technical_summary.get("ma_alignment", "")
            rsi = technical_summary.get("rsi")
            if ma == "정배열":
                lines.append("이동평균선이 정배열로 상승 추세입니다.")
            elif ma == "역배열":
                lines.append("이동평균선이 역배열로 하락 추세입니다.")
            if rsi and rsi < 30:
                lines.append(f"RSI {rsi:.0f}로 과매도 구간입니다.")
            elif rsi and rsi > 70:
                lines.append(f"RSI {rsi:.0f}로 과매수 구간에 주의가 필요합니다.")

        # Fundamental line
        if fundamental_summary and fundamental_summary.get("per"):
            per = fundamental_summary["per"]
            if per < 10:
                lines.append(f"PER {per}배로 저평가 구간입니다.")
            elif per > 30:
                lines.append(f"PER {per}배로 고평가 구간입니다.")

        gemini_summary = "\n".join(lines) if lines else "분석 데이터가 부족합니다."

    return {
        "score": max(-100, min(100, final_score)),
        "summary": gemini_summary,
        "nlp": {
            "polarity": nlp_result["polarity"],
            "subjectivity": nlp_result["subjectivity"],
            "positive_pct": nlp_result["positive_pct"],
            "negative_pct": nlp_result["negative_pct"],
            "neutral_pct": nlp_result["neutral_pct"],
            "analyzed_count": nlp_result["analyzed_count"],
        },
    }
