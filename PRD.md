# [PRD] StockSight: AI 기반 3D 주식 예측 및 유망 종목 발굴 플랫폼

## 1. 프로젝트 개요 (Project Overview)
**StockSight**는 직관과 소문에 의존하는 주식 투자를 넘어, 방대한 기업 데이터(재무, 차트, 거시경제, 실시간 뉴스)를 AI가 종합 분석하여 '신뢰할 수 있는 단일 예측 스코어(0~100점)'로 시각화해 주는 웹 플랫폼입니다. 복잡한 수치를 미래지향적인 3D 인터랙티브 UI로 제공하여 사용자의 인지 부하를 줄이고, 즉각적인 투자 판단을 돕습니다.

---

## 2. 제품 목표 (Goals & Success Metrics)
* **핵심 목표 (What):** 사용자가 직접 종목을 분석하는 시간을 1시간에서 1분 이내로 압축하고, 데이터 기반으로 즉각적이고 정확한 투자 의사결정을 내릴 수 있도록 돕습니다.
* **비전 (Why):** 수동적인 종목 검색을 넘어, 플랫폼이 선제적으로 '오를 기업(유망 종목)'을 스크리닝하여 추천하는 자동 발굴 생태계를 구축합니다.
* **성공 지표 (Success Metrics):**
  * 검색부터 분석 결과 도출까지의 응답 시간(Latency) 2초 이내 달성.
  * 캐시 히트율(Cache Hit Ratio) 70% 이상 유지.

---

## 3. 기술 스택 (Tech Stack)
프론트엔드와 데이터 처리 백엔드를 분리하여 유연성과 성능을 극대화합니다.

* **Frontend:** Next.js (React), React Three Fiber (3D WebGL UI), Tailwind CSS, ECharts
* **Backend (Data & AI):** Python (FastAPI), aiohttp (비동기 처리), Celery/RQ (작업 큐)
* **Database & Auth:** Supabase (PostgreSQL, Row Level Security 적용), Redis (In-memory 캐싱)
* **Hosting & CI/CD:** Vercel (프론트엔드 배포 및 Edge Caching)

---

## 4. 목표 달성을 위한 핵심 스코어링 알고리즘 (4-Factor Quant Engine)
AI가 아래 4가지 팩터를 수집하고 가중치를 합산하여 0~100점의 최종 예측 스코어를 도출합니다.

1. **뉴스 감성 스코어 (News Sentiment) - 가중치 30%**
   * 최근 3~7일간의 기사 요약을 LLM이 분석하여 노이즈(찌라시)를 필터링하고, 팩트(실적, 계약 등) 기반의 호재/악재를 -100~+100으로 수치화합니다.
2. **펀더멘털 스코어 (Fundamental) - 가중치 30%**
   * 동종 업계 평균 대비 PER, PBR의 저평가 여부와 ROE, EPS 증감률을 연산하여 재무적 안정성과 가치를 평가합니다.
3. **기술적 모멘텀 스코어 (Technical) - 가중치 25%**
   * 이동평균선(정배열/역배열), MACD 골든크로스/데드크로스, RSI(과매도/과매수)를 분석하여 현재의 단기 매매 타이밍을 판별합니다.
4. **매크로 및 섹터 스코어 (Macro & Sector) - 가중치 15%**
   * 금리, 환율, 원자재 가격(리튬, 유가 등) 등 거시 경제 흐름과 해당 기업 섹터 간의 상관관계를 분석하여 환경적 우호도를 평가합니다.

---

## 5. 데이터 수집 및 API 활용 방안 (API Integration Plan)
FastAPI 서버에서 `aiohttp`를 활용해 아래 API들을 100% 비동기로 동시 호출하여 병목을 제거합니다.

* **OpenDart API (금융감독원):** 분기별/연간 재무제표(PER, ROE 등 계산용 기초 데이터) 및 주요 공시 수집.
* **yfinance API:** 글로벌/국내 주가 시계열 데이터 및 기술적 보조지표(MACD, RSI, 이동평균선) 추출.
* **Naver Search API (News):** 기업명 검색을 통한 최신 뉴스 헤드라인 및 본문 링크 크롤링.
* **OpenAI API (gpt-4o):** 뉴스 텍스트 및 증권사 리포트 감성 분석, 핵심 요약 브리핑(3줄 요약) 생성. 비용 절감을 위해 원문 전체가 아닌 TF-IDF 기반의 핵심 문장만 추출하여 프롬프트로 전송.

---

## 6. 성능 최적화 방안 (Performance Optimization)

* **Multi-tier Caching (계층형 캐싱):**
  * 분석이 완료된 결과는 Vercel Edge Cache를 통해 즉각 반환(Stale-While-Revalidate 패턴 적용).
  * 빈번한 요청은 DB 조회 전 Redis에서 1차로 응답하여 Supabase 부하 최소화.
* **Pre-computing (사전 연산 스케줄링):**
  * 코스피/코스닥 시가총액 상위 200위 종목 등 검색 빈도가 높은 주식은 장 마감 후 또는 새벽에 백그라운드(Cron Jobs)로 일괄 분석하여 Supabase에 미리 적재해 둡니다.
* **비동기 큐 (Async Task Queue):**
  * 캐시가 없는 신규 종목 검색 시, 클라이언트에는 3D 로딩 UI를 띄우고 백엔드 작업 큐(Celery)에서 API 호출 및 AI 분석을 병렬 처리 후 WebSocket/SSE로 결과를 푸시합니다.

---

## 7. 보안 및 리스크 관리 (Security & FMEA)
시스템의 잠재적 실패 모드(Failure Mode)를 선제적으로 방어합니다.

* **LLM 환각(Hallucination) 통제:** AI가 존재하지 않는 이슈를 지어내는 것을 막기 위해, 시스템 프롬프트에 "반드시 수집된 기사 텍스트 내에서만 근거를 찾고, 정보가 부족하면 0점(중립) 처리할 것"을 강제합니다.
* **데이터베이스 보안 (Supabase RLS):** 사용자 개인의 포트폴리오 데이터는 Row Level Security 정책을 적용하여 타인의 접근을 원천 차단합니다.
* **외부 API 장애 대응 (Circuit Breaker):** 외부 데이터(예: Naver API) 장애 시 전체 서비스가 다운되지 않도록 예외 처리(Try-Catch)를 구성하고, 과거 캐시 데이터를 제공하며 "일부 데이터 지연" 상태를 UI에 표시합니다.
* **프롬프트 인젝션 방지:** 검색창에 기업명이 아닌 시스템 명령어 조작(Prompt Injection)을 입력하는 것을 방어하기 위해, 백엔드에서 철저한 입력값 검증(Sanitization)을 거칩니다.

---

## 8. 개발 계획 (Development Roadmap - MoSCoW 기준)

**Phase 1: 백엔드 엔진 & MVP (Must-Have)**
* Python/FastAPI 기반 비동기 데이터 파이프라인(OpenDart, Naver, yfinance 연동) 구축.
* OpenAI API를 활용한 4-Factor 스코어링 알고리즘 로직 완성.
* Supabase 데이터베이스 스키마 설계.

**Phase 2: 프론트엔드 UI & 연동 (Should-Have)**
* Next.js 프로젝트 세팅 및 Vercel 배포 연결.
* React Three Fiber를 활용한 3D 구체(Sphere) 스코어 게이지 및 인터랙티브 스파이더 차트 구현.
* 검색 커맨드 UI 및 API 연동을 통한 결과 대시보드 출력.

**Phase 3: 자동화 및 고도화 (Could-Have)**
* Redis 캐싱 및 Vercel Edge Cache 적용.
* 심야 백그라운드 스케줄러(Cron)를 활용한 상위 종목 사전 연산 기능(Today's Top Picks).
* 사용자 관심 종목 등록 및 아침 알림 기능(포트폴리오 리밸런싱).
