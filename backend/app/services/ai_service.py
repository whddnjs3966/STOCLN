"""OpenAI API를 활용한 뉴스 감성 분석 및 요약 서비스"""

from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def analyze_news_sentiment(news_items: list[dict]) -> dict:
    """뉴스 목록을 분석하여 감성 스코어와 3줄 요약을 반환합니다."""
    if not news_items:
        return {"score": 0, "summary": "분석할 뉴스가 없습니다."}

    news_text = "\n".join(
        f"- {item['title']}: {item['description']}" for item in news_items[:10]
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 주식 뉴스 감성 분석 전문가입니다. "
                    "반드시 수집된 기사 텍스트 내에서만 근거를 찾고, "
                    "정보가 부족하면 0점(중립) 처리하세요. "
                    "절대 존재하지 않는 정보를 지어내지 마세요."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"다음 뉴스들을 분석해주세요:\n{news_text}\n\n"
                    "응답 형식 (JSON):\n"
                    '{"score": -100~+100 사이의 정수, '
                    '"summary": "핵심 3줄 요약 (한국어)"}'
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    import json

    result = json.loads(response.choices[0].message.content)
    return {
        "score": max(-100, min(100, int(result.get("score", 0)))),
        "summary": result.get("summary", ""),
    }
