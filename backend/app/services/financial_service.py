"""yfinance 및 OpenDart를 활용한 재무/기술적 데이터 수집 서비스"""

import logging
import re
from typing import NamedTuple

import aiohttp
import yfinance as yf

from app.core.config import settings

logger = logging.getLogger(__name__)


class StockInfo(NamedTuple):
    code: str        # 6자리 종목코드 (예: "005930")
    market: str      # "KS" (KOSPI) 또는 "KQ" (KOSDAQ)


# 주요 한국 종목 매핑 (종목명 → StockInfo(code, market))
# KOSPI: market="KS", KOSDAQ: market="KQ"
KR_STOCK_MAP: dict[str, StockInfo] = {

    # ── 삼성 그룹 ────────────────────────────────────────────────────────────
    "삼성전자":             StockInfo("005930", "KS"),
    "삼성전자우":           StockInfo("005935", "KS"),
    "삼성SDI":             StockInfo("006400", "KS"),
    "삼성전기":             StockInfo("009150", "KS"),
    "삼성물산":             StockInfo("028260", "KS"),
    "삼성생명":             StockInfo("032830", "KS"),
    "삼성화재":             StockInfo("000810", "KS"),
    "삼성증권":             StockInfo("016360", "KS"),
    "삼성바이오로직스":     StockInfo("207940", "KS"),
    "삼성카드":             StockInfo("029780", "KS"),
    "삼성엔지니어링":       StockInfo("028050", "KS"),
    "제일기획":             StockInfo("030000", "KS"),
    "에스원":               StockInfo("012750", "KS"),
    "호텔신라":             StockInfo("008770", "KS"),

    # ── SK 그룹 ──────────────────────────────────────────────────────────────
    "SK":                   StockInfo("034730", "KS"),
    "SK하이닉스":           StockInfo("000660", "KS"),
    "SK이노베이션":         StockInfo("096770", "KS"),
    "SK텔레콤":             StockInfo("017670", "KS"),
    "SKC":                  StockInfo("011790", "KS"),
    "SK스퀘어":             StockInfo("402340", "KS"),
    "SK바이오팜":           StockInfo("326030", "KS"),
    "SK바이오사이언스":     StockInfo("302440", "KS"),
    "SK아이이테크놀로지":   StockInfo("361610", "KS"),
    "SK네트웍스":           StockInfo("001740", "KS"),
    "SK가스":               StockInfo("018670", "KS"),

    # ── LG 그룹 ──────────────────────────────────────────────────────────────
    "LG":                   StockInfo("003550", "KS"),
    "LG전자":               StockInfo("066570", "KS"),
    "LG화학":               StockInfo("051910", "KS"),
    "LG에너지솔루션":       StockInfo("373220", "KS"),
    "LG디스플레이":         StockInfo("034220", "KS"),
    "LG이노텍":             StockInfo("011070", "KS"),
    "LG유플러스":           StockInfo("032640", "KS"),
    "LG생활건강":           StockInfo("051900", "KS"),
    "LG헬로비전":           StockInfo("037560", "KS"),
    "HS애드":               StockInfo("016380", "KS"),

    # ── 현대 / 기아 그룹 ─────────────────────────────────────────────────────
    "현대자동차":           StockInfo("005380", "KS"),
    "기아":                 StockInfo("000270", "KS"),
    "현대모비스":           StockInfo("012330", "KS"),
    "현대글로비스":         StockInfo("086280", "KS"),
    "현대위아":             StockInfo("011210", "KS"),
    "현대건설":             StockInfo("000720", "KS"),
    "현대제철":             StockInfo("004020", "KS"),
    "현대로템":             StockInfo("064350", "KS"),
    "현대오토에버":         StockInfo("307950", "KS"),
    "현대에너지솔루션":     StockInfo("322000", "KS"),
    "현대백화점":           StockInfo("069960", "KS"),
    "현대홈쇼핑":           StockInfo("057050", "KS"),
    "이노션":               StockInfo("214320", "KS"),
    "HMM":                  StockInfo("011200", "KS"),

    # ── HD 그룹 (한국조선·현대중공업) ────────────────────────────────────────
    "HD현대":               StockInfo("267250", "KS"),
    "HD현대중공업":         StockInfo("329180", "KS"),
    "HD한국조선해양":       StockInfo("009540", "KS"),
    "HD현대일렉트릭":       StockInfo("267260", "KS"),
    "HD현대마린솔루션":     StockInfo("443060", "KS"),
    "HD현대오일뱅크":       StockInfo("095585", "KS"),

    # ── 카카오 그룹 ──────────────────────────────────────────────────────────
    "카카오":               StockInfo("035720", "KS"),
    "카카오뱅크":           StockInfo("323410", "KS"),
    "카카오페이":           StockInfo("377300", "KS"),
    "카카오게임즈":         StockInfo("293490", "KQ"),
    "카카오엔터테인먼트":   StockInfo("293490", "KQ"),   # 상장 전 예비코드 동일 처리

    # ── NAVER ────────────────────────────────────────────────────────────────
    "NAVER":                StockInfo("035420", "KS"),
    "네이버":               StockInfo("035420", "KS"),

    # ── 한화 그룹 ─────────────────────────────────────────────────────────────
    "한화에어로스페이스":   StockInfo("012450", "KS"),
    "한화오션":             StockInfo("042660", "KS"),
    "한화솔루션":           StockInfo("009830", "KS"),
    "한화시스템":           StockInfo("272210", "KS"),
    "한화":                 StockInfo("000880", "KS"),
    "한화생명":             StockInfo("088350", "KS"),
    "한화손해보험":         StockInfo("000370", "KS"),
    "한화투자증권":         StockInfo("003530", "KS"),
    "한화갤러리아":         StockInfo("452260", "KS"),

    # ── 두산 그룹 ─────────────────────────────────────────────────────────────
    "두산에너빌리티":       StockInfo("034020", "KS"),
    "두산밥캣":             StockInfo("241560", "KS"),
    "두산로보틱스":         StockInfo("454910", "KS"),
    "두산퓨얼셀":           StockInfo("336260", "KS"),
    "두산":                 StockInfo("000150", "KS"),

    # ── 에코프로 그룹 ────────────────────────────────────────────────────────
    "에코프로":             StockInfo("086520", "KQ"),
    "에코프로비엠":         StockInfo("247540", "KQ"),
    "에코프로에이치엔":     StockInfo("383310", "KQ"),
    "에코프로머티리얼즈":   StockInfo("450080", "KQ"),

    # ── 포스코 그룹 ──────────────────────────────────────────────────────────
    "POSCO홀딩스":          StockInfo("005490", "KS"),
    "포스코홀딩스":         StockInfo("005490", "KS"),
    "포스코퓨처엠":         StockInfo("003670", "KS"),
    "포스코인터내셔널":     StockInfo("047050", "KS"),
    "포스코DX":             StockInfo("022100", "KS"),

    # ── CJ 그룹 ──────────────────────────────────────────────────────────────
    "CJ":                   StockInfo("001040", "KS"),
    "CJ제일제당":           StockInfo("097950", "KS"),
    "CJ대한통운":           StockInfo("000120", "KS"),
    "CJ ENM":               StockInfo("035760", "KQ"),
    "CJ CGV":               StockInfo("079160", "KS"),
    "CJ올리브영":           StockInfo("438000", "KS"),

    # ── 롯데 그룹 ─────────────────────────────────────────────────────────────
    "롯데케미칼":           StockInfo("011170", "KS"),
    "롯데쇼핑":             StockInfo("023530", "KS"),
    "롯데웰푸드":           StockInfo("280360", "KS"),
    "롯데지주":             StockInfo("004990", "KS"),
    "롯데칠성":             StockInfo("005300", "KS"),
    "롯데정밀화학":         StockInfo("004000", "KS"),
    "롯데호텔":             StockInfo("071840", "KS"),

    # ── KT / 통신 ─────────────────────────────────────────────────────────────
    "KT":                   StockInfo("030200", "KS"),
    "KT&G":                 StockInfo("033780", "KS"),
    "KT스카이라이프":       StockInfo("053210", "KS"),

    # ── 금융 ──────────────────────────────────────────────────────────────────
    "KB금융":               StockInfo("105560", "KS"),
    "신한지주":             StockInfo("055550", "KS"),
    "하나금융지주":         StockInfo("086790", "KS"),
    "우리금융지주":         StockInfo("316140", "KS"),
    "메리츠금융지주":       StockInfo("138040", "KS"),
    "NH투자증권":           StockInfo("005940", "KS"),
    "미래에셋증권":         StockInfo("006800", "KS"),
    "키움증권":             StockInfo("039490", "KS"),
    "한국투자금융지주":     StockInfo("071050", "KS"),
    "삼성화재해상보험":     StockInfo("000810", "KS"),
    "DB손해보험":           StockInfo("005830", "KS"),
    "현대해상":             StockInfo("001450", "KS"),
    "교보생명":             StockInfo("456040", "KS"),
    "카카오페이증권":       StockInfo("377300", "KS"),

    # ── 반도체·전자부품 ──────────────────────────────────────────────────────
    "한미반도체":           StockInfo("042700", "KS"),
    "리노공업":             StockInfo("058470", "KQ"),
    "HPSP":                 StockInfo("403870", "KQ"),
    "ISC":                  StockInfo("095340", "KQ"),
    "원익IPS":              StockInfo("240810", "KQ"),
    "피에스케이":           StockInfo("319660", "KQ"),
    "하나마이크론":         StockInfo("067310", "KQ"),
    "에스티아이":           StockInfo("039440", "KQ"),
    "DB하이텍":             StockInfo("000990", "KS"),
    "네패스":               StockInfo("033640", "KQ"),
    "SFA반도체":            StockInfo("036540", "KQ"),
    "심텍":                 StockInfo("222800", "KQ"),
    "이수페타시스":         StockInfo("007660", "KS"),

    # ── 2차전지·소재 ─────────────────────────────────────────────────────────
    "포스코퓨처엠":         StockInfo("003670", "KS"),
    "엘앤에프":             StockInfo("066970", "KQ"),
    "코스모신소재":         StockInfo("005070", "KQ"),
    "솔루스첨단소재":       StockInfo("336370", "KQ"),
    "동화기업":             StockInfo("025900", "KS"),
    "천보":                 StockInfo("278280", "KQ"),
    "후성":                 StockInfo("093370", "KQ"),
    "SK아이이테크놀로지":   StockInfo("361610", "KS"),
    "나노신소재":           StockInfo("121600", "KQ"),
    "일진머티리얼즈":       StockInfo("020150", "KS"),
    "원익머트리얼즈":       StockInfo("104830", "KQ"),

    # ── 바이오·헬스케어 ──────────────────────────────────────────────────────
    "셀트리온":             StockInfo("068270", "KS"),
    "셀트리온헬스케어":     StockInfo("091990", "KS"),
    "셀트리온제약":         StockInfo("068760", "KQ"),
    "HLB":                  StockInfo("028300", "KQ"),
    "HLB생명과학":          StockInfo("067630", "KQ"),
    "유한양행":             StockInfo("000100", "KS"),
    "종근당":               StockInfo("185750", "KS"),
    "대웅제약":             StockInfo("069620", "KS"),
    "한미약품":             StockInfo("128940", "KS"),
    "보령":                 StockInfo("003850", "KS"),
    "동아에스티":           StockInfo("170900", "KS"),
    "GC녹십자":             StockInfo("006280", "KS"),
    "알테오젠":             StockInfo("196170", "KQ"),
    "레고켐바이오":         StockInfo("141080", "KQ"),
    "오스코텍":             StockInfo("039200", "KQ"),
    "에이비엘바이오":       StockInfo("298380", "KQ"),
    "메디톡스":             StockInfo("086900", "KQ"),
    "휴젤":                 StockInfo("145020", "KQ"),
    "클래시스":             StockInfo("214150", "KQ"),
    "인피니트헬스케어":     StockInfo("071200", "KQ"),

    # ── 게임·엔터·미디어 ─────────────────────────────────────────────────────
    "크래프톤":             StockInfo("259960", "KS"),
    "넥슨게임즈":           StockInfo("225570", "KQ"),
    "엔씨소프트":           StockInfo("036570", "KS"),
    "넷마블":               StockInfo("251270", "KS"),
    "펄어비스":             StockInfo("263750", "KQ"),
    "컴투스":               StockInfo("078340", "KQ"),
    "위메이드":             StockInfo("112040", "KQ"),
    "하이브":               StockInfo("352820", "KS"),
    "SM엔터테인먼트":       StockInfo("041510", "KQ"),
    "YG엔터테인먼트":       StockInfo("122870", "KQ"),
    "JYP엔터테인먼트":      StockInfo("035900", "KQ"),
    "스튜디오드래곤":       StockInfo("253450", "KQ"),
    "콘텐츠리퍼블릭":       StockInfo("016170", "KQ"),

    # ── IT·소프트웨어 ─────────────────────────────────────────────────────────
    "NICE평가정보":          StockInfo("030190", "KS"),
    "더존비즈온":           StockInfo("012510", "KQ"),
    "카카오엔터":           StockInfo("293490", "KQ"),
    "크래프톤":             StockInfo("259960", "KS"),
    "솔트룩스":             StockInfo("304100", "KQ"),
    "비트나인":             StockInfo("357880", "KQ"),
    "레인보우로보틱스":     StockInfo("277810", "KQ"),

    # ── 에너지·유틸리티 ──────────────────────────────────────────────────────
    "한국전력":             StockInfo("015760", "KS"),
    "한국가스공사":         StockInfo("036460", "KS"),
    "한국수력원자력":       StockInfo("015760", "KS"),   # 비상장(전력 대체)
    "S-Oil":               StockInfo("010950", "KS"),
    "GS":                   StockInfo("078930", "KS"),
    "GS칼텍스":             StockInfo("078930", "KS"),
    "HD현대오일뱅크":       StockInfo("095585", "KS"),

    # ── 건설·부동산 ──────────────────────────────────────────────────────────
    "DL이앤씨":             StockInfo("375500", "KS"),
    "GS건설":               StockInfo("006360", "KS"),
    "대우건설":             StockInfo("047040", "KS"),
    "HDC현대산업개발":      StockInfo("294870", "KS"),
    "삼성물산":             StockInfo("028260", "KS"),

    # ── 자동차·부품 ──────────────────────────────────────────────────────────
    "현대오토에버":         StockInfo("307950", "KS"),
    "만도":                 StockInfo("204320", "KS"),
    "한온시스템":           StockInfo("018880", "KS"),
    "HL만도":               StockInfo("204320", "KS"),
    "현대트랜시스":         StockInfo("000500", "KS"),

    # ── 철강·소재 ─────────────────────────────────────────────────────────────
    "현대제철":             StockInfo("004020", "KS"),
    "고려아연":             StockInfo("010130", "KS"),
    "풍산":                 StockInfo("103140", "KS"),
    "세아베스틸지주":       StockInfo("001430", "KS"),
    "동국제강":             StockInfo("460860", "KS"),

    # ── 화학·정유 ─────────────────────────────────────────────────────────────
    "롯데케미칼":           StockInfo("011170", "KS"),
    "금호석유화학":         StockInfo("011780", "KS"),
    "OCI홀딩스":            StockInfo("010060", "KS"),
    "한화솔루션":           StockInfo("009830", "KS"),
    "효성첨단소재":         StockInfo("298050", "KS"),
    "효성화학":             StockInfo("298000", "KS"),

    # ── 유통·소비재 ──────────────────────────────────────────────────────────
    "이마트":               StockInfo("139480", "KS"),
    "GS리테일":             StockInfo("007070", "KS"),
    "BGF리테일":            StockInfo("282330", "KS"),
    "CU":                   StockInfo("282330", "KS"),
    "신세계":               StockInfo("004170", "KS"),
    "신세계인터내셔날":     StockInfo("031430", "KS"),
    "아모레퍼시픽":         StockInfo("090430", "KS"),
    "LG생활건강":           StockInfo("051900", "KS"),
    "오리온":               StockInfo("271560", "KS"),
    "농심":                 StockInfo("004370", "KS"),
    "빙그레":               StockInfo("005180", "KS"),
    "하이트진로":           StockInfo("000080", "KS"),
    "KT&G":                 StockInfo("033780", "KS"),

    # ── 운송·물류·항공 ────────────────────────────────────────────────────────
    "대한항공":             StockInfo("003490", "KS"),
    "아시아나항공":         StockInfo("020560", "KS"),
    "제주항공":             StockInfo("089590", "KS"),
    "진에어":               StockInfo("272450", "KS"),
    "HMM":                  StockInfo("011200", "KS"),
    "팬오션":               StockInfo("028670", "KS"),
    "한국조선해양":         StockInfo("009540", "KS"),

    # ── 방산·우주 ─────────────────────────────────────────────────────────────
    "한화에어로스페이스":   StockInfo("012450", "KS"),
    "LIG넥스원":            StockInfo("079550", "KS"),
    "현대로템":             StockInfo("064350", "KS"),
    "한국항공우주":         StockInfo("047810", "KS"),

    # ── 중공업·기계 ──────────────────────────────────────────────────────────
    "두산에너빌리티":       StockInfo("034020", "KS"),
    "LS":                   StockInfo("006260", "KS"),
    "LS ELECTRIC":          StockInfo("010120", "KS"),
    "효성중공업":           StockInfo("298040", "KS"),

    # ── 기타 KOSPI 대형주 ─────────────────────────────────────────────────────
    "한국타이어앤테크놀로지": StockInfo("161390", "KS"),
    "넥센타이어":           StockInfo("002350", "KS"),
    "OCI":                  StockInfo("010060", "KS"),
    "한국조선해양":         StockInfo("009540", "KS"),
    "쌍용C&E":              StockInfo("003410", "KS"),
    "KCC":                  StockInfo("002380", "KS"),
    "율촌화학":             StockInfo("008730", "KS"),

    # ── KOSDAQ 대형주 ─────────────────────────────────────────────────────────
    "셀트리온제약":         StockInfo("068760", "KQ"),
    "위메이드":             StockInfo("112040", "KQ"),
    "파라다이스":           StockInfo("034230", "KQ"),
    "케이엠더블유":         StockInfo("032500", "KQ"),
    "오스템임플란트":       StockInfo("048260", "KQ"),
    "메가스터디교육":       StockInfo("215200", "KQ"),
    "엠씨넥스":             StockInfo("097520", "KQ"),
    "고영":                 StockInfo("098460", "KQ"),
    "씨젠":                 StockInfo("096530", "KQ"),
    "테스":                 StockInfo("095610", "KQ"),
    "에스에프에이":         StockInfo("056190", "KQ"),
    "덴티움":               StockInfo("145720", "KQ"),
    "솔브레인":             StockInfo("357780", "KQ"),
    "하나머티리얼즈":       StockInfo("166090", "KQ"),
    "피에스케이홀딩스":     StockInfo("319660", "KQ"),
    "루닛":                 StockInfo("328130", "KQ"),
    "뷰노":                 StockInfo("338220", "KQ"),
    "제이엘케이":           StockInfo("322510", "KQ"),
    "셀바스AI":             StockInfo("108860", "KQ"),
    "수젠텍":               StockInfo("253840", "KQ"),
    "지트리비앤티":         StockInfo("115450", "KQ"),
    "엑세스바이오":         StockInfo("950130", "KQ"),
    "바이오니아":           StockInfo("064550", "KQ"),
    "파마리서치":           StockInfo("214450", "KQ"),
    "제테마":               StockInfo("216080", "KQ"),
    "코미팜":               StockInfo("041960", "KQ"),
    "박셀바이오":           StockInfo("323990", "KQ"),
    "셀리드":               StockInfo("299660", "KQ"),
    "원바이오젠":           StockInfo("304360", "KQ"),
}


def search_stocks(query: str, limit: int = 20) -> list[dict]:
    """종목명 부분 일치 검색 (대소문자 무시).

    Returns:
        [{"name": str, "code": str, "market": str}, ...]
        market은 "KOSPI" 또는 "KOSDAQ"
    """
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    results: list[dict] = []
    seen_codes: set[str] = set()

    for name, info in KR_STOCK_MAP.items():
        if query_lower in name.lower():
            if info.code not in seen_codes:
                seen_codes.add(info.code)
                results.append({
                    "name": name,
                    "code": info.code,
                    "market": "KOSPI" if info.market == "KS" else "KOSDAQ",
                })

    # 정확히 일치하는 항목을 앞으로 정렬
    results.sort(key=lambda x: (not x["name"].lower().startswith(query_lower), x["name"]))
    return results[:limit]


def resolve_kr_ticker(query: str) -> str | None:
    """한국 종목명 또는 종목코드를 yfinance 티커 형식으로 변환합니다.

    - 숫자 6자리 종목코드 → 기본적으로 .KS 붙임 (KOSDAQ은 검색으로 식별)
    - 한글/영문 종목명 → KR_STOCK_MAP에서 조회하여 올바른 suffix 사용
    - 이미 .KS/.KQ 접미사가 있으면 그대로 반환
    """
    query = query.strip()

    # 이미 yfinance 형식인 경우
    if query.endswith((".KS", ".KQ")):
        return query

    # 6자리 숫자 종목코드인 경우 — 맵에서 정확한 market suffix 탐색
    if re.match(r"^\d{6}$", query):
        for info in KR_STOCK_MAP.values():
            if info.code == query:
                return f"{query}.{info.market}"
        # 맵에 없으면 KOSPI로 기본 처리
        return f"{query}.KS"

    # 정확한 종목명 매핑 조회
    info = KR_STOCK_MAP.get(query)
    if info:
        logger.info("Resolved '%s' → %s.%s", query, info.code, info.market)
        return f"{info.code}.{info.market}"

    # 대소문자 무시 정확 매핑 조회
    query_lower = query.lower()
    for name, info in KR_STOCK_MAP.items():
        if name.lower() == query_lower:
            logger.info("Case-insensitive match: '%s' → %s.%s", query, info.code, info.market)
            return f"{info.code}.{info.market}"

    # 부분 매칭 시도
    for name, info in KR_STOCK_MAP.items():
        if query_lower in name.lower() or name.lower() in query_lower:
            logger.info("Partial match: '%s' → %s (%s.%s)", query, name, info.code, info.market)
            return f"{info.code}.{info.market}"

    logger.warning("Could not resolve Korean stock name: '%s'", query)
    return None


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

        # bookValue가 없는 경우 balance sheet에서 BPS 계산
        if not info.get("bookValue"):
            try:
                bs = stock.balance_sheet
                if not bs.empty:
                    equity = None
                    for label in bs.index:
                        if "Stockholders Equity" in str(label):
                            equity = float(bs.loc[label].iloc[0])
                            break
                    shares = info.get("sharesOutstanding")
                    if equity and shares and shares > 0:
                        info["bookValue"] = round(equity / shares, 2)
                        logger.info("Calculated bookValue=%.2f from balance sheet", info["bookValue"])
            except Exception:
                logger.debug("Could not calculate bookValue from balance sheet")

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
