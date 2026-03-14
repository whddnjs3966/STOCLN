"""뉴스 기사 본문 스크래핑 서비스

stocksight의 followlinks 기능을 차용:
링크를 따라가 기사 본문을 추출하여 더 정확한 감성 분석을 수행합니다.
"""

import logging

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def scrape_article_text(url: str, max_paragraphs: int = 15) -> str | None:
    """뉴스 기사 URL에서 본문 텍스트를 추출합니다."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        texts = []
        for p in paragraphs[:max_paragraphs]:
            text = p.get_text(strip=True)
            if len(text) > 30:  # Skip very short paragraphs
                texts.append(text)

        if not texts:
            return None

        return " ".join(texts)

    except Exception:
        logger.debug("Failed to scrape article: %s", url)
        return None


async def enrich_news_with_content(news_items: list[dict], max_items: int = 5) -> list[dict]:
    """뉴스 항목에 기사 본문을 추가합니다."""
    enriched = []
    for item in news_items[:max_items]:
        link = item.get("link", "")
        if link:
            content = await scrape_article_text(link)
            if content:
                item = {**item, "full_text": content[:2000]}  # Limit text length
        enriched.append(item)

    # Append remaining items beyond max_items unchanged
    enriched.extend(news_items[max_items:])
    return enriched
