# traceOpsReqSync

TraceOps와 ReqSync를 하나로 묶은 성과 제출 자료 폴더입니다. 구조는 `../prowin/` 과 같습니다.
**ReqSync는 TraceOps 안의 요구사항 개정 검토 모듈**입니다(같은 서버·DB, 요구사항 관리 화면의 `ReqSync` 버튼으로 진입).

```
traceOpsReqSync/
├─ README.md                       이 문서 (작성 방침, 장 구성)
├─ build_traceopsreqsync.py        장 구성과 문구 → HTML 생성
├─ 성과제출_TraceOps_ReqSync.html   결과물 (22장)
├─ shots/                          화면 캡처 12장 (1440×900 @2x, 실제 데이터)
├─ capture_traceops.py / capture.js 빈 임시 DB로 서버를 띄워 화면 촬영 (원본 DB 미수정)
└─ TraceOps_보완사항.md             개발자 전달용 (로컬 LLM 추출, 호출구조 통합 등)
```

공통 디자인 기준은 `../작성가이드.md`, 공통 부품은 `../tools/deck_lib.py`, 내용 출처는 `../제안서_추진현황_요약.md` 의 1장(ReqSync)과 3장(TraceOps)입니다.

## 작성 방침 (확정)

| 항목 | 결정 |
|------|------|
| 연계관리 | **포함**. ProWin 증적에 있던 연계관리(연계 캔버스) 자료를 TraceOps 장에 포함 |
| 일정 | 연말 평가 자료이므로 **일정 표현은 쓰지 않음** (요약 문서 3-5 제외) |
| 실명 | **마스킹하지 않음**(이미 변조된 자료). 클래스·메서드명, 회의 발췌문도 그대로 사용 |
| 회의록 결정사항 추출 | **로컬 LLM(Ollama, Qwen3) 연동 구현 완료**로 기재(`traceops-simple/llm.py`, `minutes.py`). LLM 미기동 시 저장 결과로 시연 |
| 호출구조 정적분석 POC | **연계관리 기능으로 표기**(POC 표현 제거). 연계관리 화면에서 분석을 실행해 AS-IS 콜트리를 반영하는 것으로 기재하며, 해당 버튼의 구현이 전제 |
| 와이어프레임, PRD 정리 과정 | 와이어프레임 없이 바로 개발했으므로 **장표에서 제외** (요약 문서 3-3의 "통합 PRD v1.0", "와이어프레임 7종" 문구 사용 안 함) |
| 개발자 전달 문서 | `TraceOps_보완사항.md` 작성 완료 (로컬 LLM 추출, 호출구조 POC 통합 포함, 구현 방안은 담당 개발자가 작성) |
| AI 부각 | AI 활용 KPI 자료이므로 제목 옆 `AI 활용` 표시, 별도 장 `AI 활용 구조`(AI가 하는 일 / 사람이 하는 일 / 현재 상태와 보완), 흐름·카드의 `AI` 태그로 강조 |

## 장 구성 (22장)

| # | 패턴 | 제목 | 비고 |
|---|------|------|------|
| 1 | 표지 | TraceOps · ReqSync AI 활용 성과 보고 | |
| 2 | 목차 | | |
| 3 | 성과 요약 | 성과 요약 | AI, 6단계, 연계관리, 정합성 4카드 |
| 4 | P1 | TraceOps · ReqSync 소개 | ReqSync 카드 강조 |
| 5 | 수행주기 | 프로젝트 수행주기와 적용 지점 | ReqSync·연계관리 적용 구간, 단계별 변경 통제 |
| 6 | P2 | 추진 배경 | ReqSync, 연계관리, 정합성 |
| 7 | P3 | 목표 | 자산화, AI 활용 자동화, 정합성 있는 추적성 |
| 8 | P4 | 기대효과 | |
| 9 | P5 | 업무 흐름 | ReqSync 도입 시 업무 방식, 단계별 AI·사람 역할 표시 |
| 10 | AI | ReqSync 구성과 동작 | ReqSync 정의, 동작 흐름(추출, 2차 검증, 매칭, 확정), 로컬 LLM 스펙(Ollama, Qwen3) |
| 11 | AI | ReqSync AI 역할 설계 | 역할 지시문 3종(`1117_박혜림/local_llm_slides.py` 내용 반영) |
| 12~15 | P6 | 주요 기능 1~4/5 | ReqSync, 요구사항 관리, 상세공정, 테스트 |
| 16 | 연계 1/3 | 연계관리 개요 | 메서드 누락 방지, 연계 테스트케이스(E2E), 기간계 외 연계 |
| 17 | 연계 2/3 | 연계관리 예시 | 기간계, 채널, AI Agent |
| 18 | 연계 3/3 | 연계관리 화면 | 핵심 기능 5/5 |
| 19 | P7 | 단계별 화면 | 6개 화면 타일 |
| 20 | P8 | 기술 구성 | 로컬 LLM 서버, 호출구조 정적분석, 상용화 보완 방향 |
| 21 | P9 | 고도화 계획 | ReqSync·AI 확대, 연계관리 확대, 수행관리 자동화 |
| 22 | 엔딩 | | |

## 촬영 방법

저장소 루트에서 실행합니다. Python과 Node(Playwright)가 필요합니다.

```bash
python3 성과제출/traceOpsReqSync/capture_traceops.py      # 화면 촬영
python3 성과제출/traceOpsReqSync/build_traceopsreqsync.py  # HTML 생성
node 성과제출/tools/lint.js 성과제출/traceOpsReqSync/성과제출_TraceOps_ReqSync.html
```

- 원본 `traceops-simple/` 과 시드 데이터는 수정하지 않고, 빈 임시 DB로 서버를 띄워 촬영합니다.
