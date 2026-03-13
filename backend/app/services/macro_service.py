"""매크로/섹터 스코어링 서비스

섹터별 매크로 환경을 반영한 스코어를 산출합니다.
"""

# TODO: Phase 3에서 실제 매크로 데이터를 통합할 예정
# - 금리 (한국은행 기준금리, 미국 Fed Funds Rate)
# - 환율 (USD/KRW, 원화 강세/약세)
# - 원자재 (유가, 구리, 반도체 소재 가격)
# 이 데이터를 기반으로 섹터별 가중치를 동적으로 조정

SECTOR_SCORES: dict[str, float] = {
    "Technology": 65.0,   # 약간 강세 (AI/반도체 수요)
    "Healthcare": 60.0,   # 소폭 강세 (고령화 추세)
    "Finance": 55.0,      # 약간 강세 (금리 환경)
    "Energy": 45.0,       # 소폭 약세 (탄소중립 전환)
}

DEFAULT_SCORE: float = 50.0  # 중립


async def calculate_macro_score(sector: str) -> float:
    """섹터 기반 매크로 스코어를 계산합니다.

    Args:
        sector: 종목이 속한 섹터 (예: "Technology", "Healthcare")

    Returns:
        0~100 사이의 매크로 스코어. 데이터 부족 시 50.0(중립) 반환.
    """
    if not sector:
        return DEFAULT_SCORE

    return SECTOR_SCORES.get(sector, DEFAULT_SCORE)
