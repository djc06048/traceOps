# TraceOps 샘플 (traceops-simple)

요구사항부터 분석 · 설계 · 개발 · 단위테스트 · 통합테스트까지 **추적 관계를 관리**하는 프로토타입입니다.
Python 서버 하나와 SQLite 파일 하나로 동작하며, 별도 설치가 필요 없습니다.

- 요구사항 관리, 회의록 기반 요구사항 개정 검토, 변경 이력
- 분석 / 설계 / 개발 단계 관리와 단위 / 통합 테스트 관리
- 물리ID(AS-IS 목록) 관리
- 위 단계 사이의 연결(요구사항 ← 분석 ← 설계 ← 개발 ← 단위 ← 통합)을 DB 제약으로 보장

> 관계 구조는 [docs/ERD.md](docs/ERD.md) 를 참고하세요.

## 실행

```bash
cd traceops-simple
python3 server.py              # http://localhost:8000
PORT=8011 python3 server.py    # 포트 변경
```

Python 3.9 이상 표준 라이브러리만 사용합니다. 파일을 더블클릭해서 열면 API가 없어 동작하지 않으니 반드시 서버로 실행하세요.

## 회의록 AI 분석 (로컬 LLM, 무료)

`requirements-review.html`에서 새 회의록(클로바노트 .txt)을 업로드하면, 서버가 **로컬 LLM**으로 결정사항을 뽑고 요구사항에 매칭합니다.
회의록은 외부로 나가지 않습니다. 결과는 뽑히는 대로 화면에 표시되며, PL이 확정해야 요구사항에 반영됩니다.

**로컬 LLM이 떠 있지 않으면** 예전처럼 시연 모드로 동작합니다. 업로드한 파일명을 회의 목록과 맞춰, 저장된 분석 결과를 분석 연출과 함께 보여줍니다. 업로드할 때마다 연결 상태를 다시 확인하므로, 나중에 Ollama를 띄우면 새로고침 없이 실제 분석으로 바뀝니다.

| 구성 | 사용 | 라이선스 |
|---|---|---|
| LLM 서버 | [Ollama](https://ollama.com) | MIT (무료) |
| 모델 | Qwen3 | Apache 2.0 (상업 사용 무료) |

EXAONE, Qwen2.5-3B/72B 등 비상업 라이선스 모델은 쓰지 마세요.

### 설치 (최초 1회)

```bash
# 1) Ollama 설치 (Windows 설치 파일 또는 Linux: curl -fsSL https://ollama.com/install.sh | sh)
#    설치 파일이 막힌 PC(VDI 등)는 GitHub 릴리스의 ollama-windows-amd64.zip을 풀어 ollama.exe serve 로 실행
# 2) 문맥 길이를 8K로 (요구사항 목록 + 회의록 조각이 들어가야 함). 설정 후 Ollama 재시작
setx OLLAMA_CONTEXT_LENGTH 8192          # Linux: export OLLAMA_CONTEXT_LENGTH=8192
# 3) 모델 받기
ollama pull qwen3:4b
```

### 설정 (환경변수, 모두 선택)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI 호환 주소. 별도 GPU 서버로 옮기면 이 값만 바꿉니다 (vLLM 등도 가능) |
| `LLM_MODEL` | `qwen3:4b` | 사용할 모델 |
| `LLM_API_KEY` | 없음 | 인증이 필요한 서버만 |
| `LLM_TIMEOUT` | `600` | 요청당 초 |
| `LLM_NO_THINK` | `1` | 사고 과정 출력 끄기(`reasoning_effort: none`). 지원하지 않는 서버면 `0` |

하드웨어별 권장 모델:
- GPU 없음 (시험용): `qwen3:4b`. 실측(i7-1360P, RAM 16GB): 결정사항 추출은 조각당 약 25~60초, 매핑은 건당 약 1분. 결정사항 10건짜리 1시간 회의면 약 15분
- GPU 16GB: `qwen3:14b`
- GPU 24GB 이상: `qwen3:32b` (운영 권장)

동작 확인: `http://localhost:8000/api/llm/status`. 화면 상단에도 연결 상태가 표시됩니다.
시험용 회의록: `samples/sample_meeting.txt`

### 처리 방식 (`minutes.py`)
1. 클로바노트 형식(`참석자 N 00:00` + 발언)을 읽고, 약 12분(최대 6,000자) 단위 조각으로 자릅니다.
2. 조각마다 결정사항을 뽑습니다(발췌·시각·상태·검증 메모). 회의록에 없는 발췌문이면 검증 메모에 표시합니다.
3. **AI 2차 검증**: 결정사항마다 근거 발언과 앞뒤 대화(앞 1개, 뒤 3개 발언)를 LLM에 다시 보내 판단합니다. 결정사항이 아니면 제외하고, 상태(확정·검토 중·미정)가 틀리면 고칩니다. 검증 메모에 `1차: … / 2차 검증: … (상태 보정: 확정 → 미정)` 형태로 남습니다. `MINUTES_VERIFY=0`이면 끕니다.
4. 결정사항마다 글자가 많이 겹치는 요구사항 15건을 후보로 골라 LLM에 넘기고 매칭합니다. 목록 전체(77건)를 넣으면 CPU에서 건당 5분 이상 걸립니다. 목록에 없는 ID가 오면 신규 후보(`new`)로 처리합니다.
5. 같은 회의록을 다시 분석하면, 검토 기록이 없는 AI 결정사항(`AI-*`)만 지우고 새로 만듭니다.

## 화면

| 주소 | 화면 |
|---|---|
| `/index.html#analysis` `#design` `#dev` | 분석 / 설계 / 개발 단계 조회·관리 |
| `/index.html#unit` `#integration` | 단위 / 통합 테스트 관리 |
| `/requirements.html` | 요구사항 관리 (등록·수정·삭제, 🕘 변경 이력) |
| `/requirements-review.html` | 회의록 결정사항을 검토해 요구사항에 반영 |
| `/asis.html` | 물리ID(AS-IS 목록) 관리 |

요구사항ID 칩을 누르면 요구사항 관리 화면으로 이동하고 해당 행이 하이라이트됩니다(`requirements.html?reqId=...`).

## 구조

```
브라우저 ──(정적 파일 + REST API)── server.py ── reqdb.py ── traceops.db (SQLite)
```

```
traceops-simple/
├─ server.py          정적 파일 서버 + API (표준 라이브러리 http.server)
├─ reqdb.py           스키마, 시드, 조회·저장·파생값 계산, 마이그레이션
├─ test_reqdb.py      DB 자체 점검 (python3 test_reqdb.py)
├─ llm.py             로컬 LLM 호출 (OpenAI 호환 API, 표준 라이브러리)
├─ minutes.py         회의록 파싱 → 결정사항 추출 → 요구사항 매핑
├─ test_minutes.py    분석 파이프라인 점검 (가짜 LLM, Ollama 불필요)
├─ samples/           시험용 회의록
├─ traceops.db        SQLite 파일 (자동 생성, git 제외)
├─ docs/ERD.md        ERD (Mermaid)
├─ index.html / requirements.html / requirements-review.html / asis.html
├─ css/style.css
├─ js/
│  ├─ app.js                  분석·설계·개발·단위·통합 공통 화면 엔진
│  ├─ requirements.js         요구사항 관리
│  ├─ requirements-review.js  요구사항 개정 검토
│  ├─ asis.js                 물리ID 관리
│  └─ store.js                API 호출 헬퍼(api)와 문서 저장(DB)
└─ data/              최초 실행 시 DB를 채우는 시드 JSON
```

### 데이터 흐름

- 최초 실행 시 테이블이 비어 있으면 `data/*.json`으로 채웁니다. **이후에는 DB가 원본**이며 JSON을 고쳐도 반영되지 않습니다.
- 화면에서 `저장`을 누르면 목록 전체를 서버로 보내고, 서버가 DB와 비교해 추가·수정·삭제를 한 트랜잭션으로 반영합니다.
- 요구사항은 저장할 때 이전 값과 비교해 **변경 이력**(`requirement_history`)을 자동 기록합니다.
- 분석·설계·개발·단위·통합은 `PUT /api/trace`로 **한 번에** 저장합니다. 연결이 끊기거나 하위가 참조 중이면 DB가 막고 화면에 오류가 표시됩니다.
- `master.json`(담당자 등)만 아직 JSON 문서로 저장합니다(`store` 테이블).

## 데이터 모델 요약

```
requirements ← analysis_items ← design_items ← dev_items ← unit_items ← integration_items
              (analysis_requirements) (design_analysis) (dev_design) (unit_dev) (integration_units)
```

- 단계마다 독립 테이블이 있고, 단계 사이는 연결 테이블로 잇습니다.
- **상속되는 값은 저장하지 않고 계산**합니다. 설계·개발·단위의 요구사항ID와 물리ID, 통합테스트의 개발ID·요구사항ID·물리ID는 위 단계에서 자동으로 따라옵니다. 요구사항은 분석 단계에서만 지정합니다.
- 통합테스트는 단위테스트 일부를 골라 묶는 것이며, 연관 요구사항·물리ID·개발ID는 묶인 단위들의 합집합입니다.
- 요구사항 개정 검토는 `meetings` → `decisions` → `decision_reviews` 로 이어지고, 확정하면 요구사항 내용이 바뀌며 근거 회의가 변경 이력에 남습니다.

전체 테이블과 관계는 [docs/ERD.md](docs/ERD.md) 에 있습니다.

## API

| 메서드 | 주소 | 설명 |
|---|---|---|
| GET / PUT | `/api/requirements` | 요구사항 목록 / 전체 저장 (`{items, who, ctx}`) |
| GET | `/api/meetings` `/api/decisions` | 회의 / 회의 결정사항 |
| GET | `/api/reviews` | 결정사항별 검토 결과·이력 |
| PUT | `/api/reviews/<결정사항ID>` | 검토 결과 저장 |
| GET | `/api/analysis` `design` `dev` `unit` `integration` | 단계별 목록(상속 값 포함) |
| PUT | `/api/trace` | 5단계 한 번에 저장 |
| GET / PUT | `/api/asis` | 물리ID 목록 / 저장 |
| GET / PUT / DELETE | `/api/store[/<key>]` | 문서 저장 (`master` 등) |

오류는 `400 {"error": "메시지"}` 로 내려가며 화면 토스트에 그대로 표시됩니다.

## 동작 규칙

| 항목 | 규칙 |
|---|---|
| 권한 | `PL` / `작업자` 토글로 미리보기. 작업자는 계획·PL 컬럼이 숨겨지고 실적 입력만 가능 |
| 작업자 계획기간 | 누구도 화면에서 수정 불가 |
| 작업자 선택 | PL만 셀을 눌러 팝업에서 선택·등록·수정·삭제 |
| 요구사항 지정 | 분석 단계에서만 지정. 설계·개발·테스트는 상속(읽기 전용) |
| 통합테스트 | 묶인 단위테스트만 선택. 연결 개발ID는 읽기 전용(계산값) |
| 삭제 제한 | 하위 단계가 참조 중인 항목, 사용 중인 요구사항ID·물리ID는 삭제 불가 |
| 진행상태 | 완료=작업자 실적 종료일 입력, 지연=계획 종료일 경과 후 미완료, 진행중=실적 시작일만 입력, 미착수=그 외 |
| 증적 | 실적 시작일이 있는데 증적이 없으면 저장 차단. 테스트는 FAIL인데 증적이 없으면 저장 차단 |
| ID 채번 | `+ 행 추가` 시 `접두어-연도-순번` 자동 부여 (ANL, SCR, DEV, TU, TI) |
| 매핑 | 요구사항ID·물리ID·설계ID·개발ID는 검색 팝업에서 선택 (직접 타이핑 없음) |

## 운영 메모

| 작업 | 방법 |
|---|---|
| DB 내용 보기 | `sqlite3 -header -column traceops.db` → `.tables`, `.schema requirements` |
| 초기화 | 서버를 끄고 `traceops.db` 삭제 후 재실행 (시드 JSON으로 다시 채움) |
| 백업 | 서버를 끄고 `traceops.db` 파일 복사 (또는 `sqlite3 traceops.db ".backup 백업.db"`) |
| 점검 | `python3 test_reqdb.py` (임시 DB 사용, 운영 DB는 건드리지 않음) |
| 다른 DB 파일 | `TRACEOPS_DB=/경로/x.db python3 server.py` |

구버전 DB(설계·개발의 `phys_ids` JSON 컬럼)는 서버 시작 시 연결 테이블로 자동 이전됩니다.

## 알려진 한계

- **인증이 없습니다.** 접속한 모든 사람이 같은 데이터를 보고 수정합니다. 변경 이력 작성자는 `황금빛`(PL) 고정입니다.
- **동시 편집 시 마지막 저장이 이깁니다.** 목록 전체를 덮어쓰는 방식이라 충돌 감지가 없습니다.
- 증적·비고는 JSON 컬럼입니다. 파일 업로드는 없고 파일명만 기록합니다.
- 시작 시 문서 저장소(`/api/store`)를 동기 방식으로 읽습니다. 데이터가 커지면 비동기로 바꿔야 합니다.
- 엑셀 붙여넣기, 페이지네이션, 결함관리, 커버리지, 연계 캔버스는 범위 밖입니다.
- 폰트(Pretendard)는 CDN에서 받으며, 연결이 안 되면 시스템 글꼴로 표시됩니다.
- 상위 폴더의 `backend/`(Spring Boot) · `frontend/`(React) · `infra/`(Postgres)는 본 제품 스캐폴딩이며 이 샘플과는 독립적입니다.
