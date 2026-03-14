"""Naver News API를 활용한 뉴스 수집 서비스"""

import logging

import aiohttp

from app.core.config import settings

logger = logging.getLogger(__name__)


async def fetch_news(query: str, display: int = 10, enrich: bool = True) -> list[dict]:
    """네이버 검색 API로 뉴스 헤드라인을 수집합니다.

    Args:
        query: 검색 키워드
        display: 수집할 기사 수
        enrich: True일 경우 상위 5개 기사의 본문을 스크래핑하여 NLP 분석 품질을 향상
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": settings.naver_client_id,
        "X-Naver-Client-Secret": settings.naver_client_secret,
    }
    params = {"query": query, "display": display, "sort": "date"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            items = [
                {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "link": item.get("link", ""),
                    "pub_date": item.get("pubDate", ""),
                }
                for item in data.get("items", [])
            ]

    if enrich and items:
        try:
            from app.services.scraper_service import enrich_news_with_content
            items = await enrich_news_with_content(items, max_items=5)
        except Exception:
            logger.debug("Article enrichment skipped due to error")

    return items
