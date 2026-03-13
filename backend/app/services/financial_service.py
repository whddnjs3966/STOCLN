"""yfinance 및 OpenDart를 활용한 재무/기술적 데이터 수집 서비스"""

import aiohttp
import yfinance as yf

from app.core.config import settings


def get_stock_data(ticker: str) -> dict | None:
    """yfinance로 주가 및 기술적 지표 데이터를 가져옵니다."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo")

        if hist.empty:
            return None

        close = hist["Close"]
        current_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-2]) if len(close) > 1 else current_price

        return {
            "current_price": current_price,
            "price_change_pct": round((current_price - prev_price) / prev_price * 100, 2),
            "history": hist,
            "info": info,
        }
    except Exception:
        return None


async def fetch_dart_financials(corp_code: str) -> dict | None:
    """OpenDart API로 재무제표 데이터를 가져옵니다."""
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
    params = {
        "crtfc_key": settings.opendart_api_key,
        "corp_code": corp_code,
        "bsns_year": "2024",
        "reprt_code": "11011",  # 사업보고서
        "fs_div": "CFS",  # 연결재무제표
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if data.get("status") != "000":
                return None
            return data.get("list", [])
