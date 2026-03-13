"""입력값 검증 및 프롬프트 인젝션 방지"""

import re


def sanitize_stock_query(query: str) -> str | None:
    """검색어를 검증하고 위험한 입력을 필터링합니다."""
    if not query or not query.strip():
        return None

    query = query.strip()

    # 최대 길이 제한
    if len(query) > 50:
        return None

    # 허용: 한글, 영문, 숫자, 점, 하이픈, 공백
    if not re.match(r"^[\w\s.\-가-힣]+$", query):
        return None

    # 프롬프트 인젝션 패턴 차단
    injection_patterns = [
        r"ignore\s+(previous|above)",
        r"system\s*:",
        r"you\s+are\s+a",
        r"pretend",
        r"act\s+as",
        r"<\s*script",
    ]
    lower = query.lower()
    for pattern in injection_patterns:
        if re.search(pattern, lower):
            return None

    return query
