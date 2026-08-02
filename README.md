# TraceOps 개발환경

화면–프로그램–테이블–대내외 인터페이스 연계 관계를 추적하는 사내 PMS. 현재는 개발환경 스캐폴딩 단계 — 각 컴포넌트가 서로 통신 가능한지 검증하는 것이 목적이며 실제 기능은 아직 없다.

## 구성

- `infra/` — Postgres(Docker Compose), 그래프(`nodes`/`edges`)·PMS(`requirements`) 스키마, 검증용 시드 데이터
- `backend/` — Spring Boot(Java), `/api/graph`로 노드·엣지 JSON 제공
- `analyzer/` — Java 소스 AST 정적분석 (담당자 별도 구현 예정, 현재는 README만)
- `frontend/` — Vite + React + TypeScript + React Flow, 백엔드 그래프 데이터를 캔버스에 렌더링

## 로컬 실행 순서

```bash
# 1. DB
cd infra && docker compose up -d

# 2. 백엔드 (8080)
cd backend && ./mvnw spring-boot:run

# 3. 프론트엔드 (5173)
cd frontend && npm install && npm run dev
```

`analyzer/`는 담당자가 실제 파싱 로직을 작성하기 전까지 `infra/seed.sql`의 샘플 데이터로 파이프라인(Postgres → backend → frontend)을 대신 검증한다.
