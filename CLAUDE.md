# StockSight - AI 기반 3D 주식 예측 플랫폼

## 프로젝트 구조
```
02-STOCLN/
├── PRD.md                    # 제품 요구사항 정의서
├── frontend/                 # Next.js (React + TypeScript)
│   ├── src/
│   │   ├── app/             # App Router 페이지
│   │   └── lib/             # API 클라이언트, 유틸리티
│   └── package.json
├── backend/                  # Python FastAPI
│   ├── app/
│   │   ├── main.py          # FastAPI 진입점
│   │   ├── api/routes.py    # API 라우트
│   │   ├── core/config.py   # 환경변수 설정
│   │   ├── models/schemas.py # Pydantic 모델
│   │   ├── services/        # 비즈니스 로직
│   │   │   ├── ai_service.py        # OpenAI 감성분석
│   │   │   ├── financial_service.py  # yfinance/OpenDart
│   │   │   ├── news_service.py       # Naver News API
│   │   │   └── scoring_service.py    # 4-Factor 스코어링
│   │   └── utils/sanitize.py # 입력값 검증
│   ├── requirements.txt
│   └── venv/
└── .gitignore
```

## 실행 방법

### Backend (FastAPI)
```bash
cd backend
source venv/Scripts/activate   # Windows
cp .env.example .env           # API 키 설정 필요
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)
```bash
cd frontend
cp .env.example .env.local     # API URL 설정
npm run dev
```

## 기술 스택
- **Frontend:** Next.js, React Three Fiber, Tailwind CSS, ECharts
- **Backend:** Python FastAPI, aiohttp, Celery
- **Database:** Supabase (httpx로 REST API 직접 호출)
- **Cache:** Redis
- **AI:** OpenAI GPT-4o

## 외부 API 키 필요
- OpenAI API Key
- OpenDart API Key (금융감독원)
- Naver Search API (Client ID / Secret)
- Supabase (URL / Key)
