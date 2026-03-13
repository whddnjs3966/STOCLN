"""Naver News API를 활용한 뉴스 수집 서비스"""

import aiohttp

from app.core.config import settings


async def fetch_news(query: str, display: int = 10) -> list[dict]:
    """네이버 검색 API로 뉴스 헤드라인을 수집합니다."""
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
            return [
                {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "link": item.get("link", ""),
                    "pub_date": item.get("pubDate", ""),
                }
                for item in data.get("items", [])
            ]
