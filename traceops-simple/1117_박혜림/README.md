# 로컬 LLM 회의록 분석 장표 (1117_박혜림)

성과제출 자료(`성과제출/traceOpsReqSync/성과제출_TraceOps_ReqSync.html`)에 붙여넣을 **로컬 LLM 회의록 분석** 장표 6장입니다.
디자인은 `성과제출/작성가이드.md` 기준이고, 공통 부품 `성과제출/tools/deck_lib.py`로 생성합니다. `lint.js` 점검을 통과했습니다.

## 파일

| 파일 | 용도 |
|---|---|
| `로컬LLM_장표_미리보기.html` | 이 폴더에서 바로 열어 보는 미리보기 (6장) |
| `로컬LLM_장표_붙여넣기용.html` | 성과제출 HTML에 그대로 넣을 `<section>` 6개 (로고 경로 `../assets/` 기준) |
| `local_llm_slides.py` | 장표 생성 스크립트. 문구를 고친 뒤 `python local_llm_slides.py`로 두 HTML을 다시 생성 |
| `png/` | 장표 이미지 6장 (PPT나 메신저 공유용) |

## 장 구성

| # | 제목 | 패턴 | 내용 |
|---|---|---|---|
| 1 | 로컬 LLM 구성 | P8 구조도 | 브라우저, TraceOps 서버, Ollama, Qwen3 / 사내 PC 내부 동작 / 무료 라이선스 / 설정만으로 교체 |
| 2 | 로컬 LLM 분석 흐름 | P5 5단계 | 기동, 업로드·분할, 추출·2차 검증(AI), 요구사항 매칭(AI), PL 검토·확정 |
| 3 | AI 역할 설계 | 역할 카드 3열 | 회의록 분석가(추출), 2차 검토자(검증), 요구사항 매핑 분석가(매칭)의 입력·출력·핵심 규칙 / 고도화: 오판 사례 예시, 용어집, 지시문 버전 관리 |
| 4 | 백엔드 모델 호출 구조 | 번호 행 + 코드 | 분석 요청, 백그라운드 작업, 한 건씩 저장, 진행 조회 / 실제 호출 요청 예시 / 형식 강제, AI 2차 검증, 결과 보정 |
| 5 | 처리 시간 단축과 대기 대응 | P4 전후 비교 | 사고 과정 끄기, 후보 15건 선별, 추출 즉시 표시, LLM 중단 시 시연 모드 / 실측 환경 |
| 6 | 로컬 LLM 고도화 방향 | P9 로드맵 | 현재 구현 5가지 / GPU 서버 이전, 묶음 매칭, 실회의록 검증 |

## 성과제출 자료에 넣는 방법

**방법 A. HTML에 직접 붙여넣기 (빠름)**
1. `로컬LLM_장표_붙여넣기용.html`을 열어 내용 전체를 복사합니다.
2. `성과제출/traceOpsReqSync/성과제출_TraceOps_ReqSync.html`에서 넣을 위치의 `</section>` 뒤에 붙여넣습니다. 권장 위치는 9장 `AI 활용 구조` 다음입니다.
3. 쪽번호(`class="a pgno"`)는 10~15로 생성되어 있으니, 넣은 위치에 맞게 고칩니다.

> 주의: `build_traceopsreqsync.py`를 다시 실행하면 HTML이 새로 만들어져 붙여넣은 내용이 사라집니다. 계속 빌드할 예정이면 방법 B를 쓰세요.

**방법 B. 빌드 스크립트에 연동 (권장)**

`build_traceopsreqsync.py`의 9장(AI 활용 구조) `slides.append(...)` 바로 다음에 아래를 추가합니다.

```python
sys.path.insert(0, os.path.join(HERE, '..', '..', 'traceops-simple', '1117_박혜림'))
import local_llm_slides
slides += local_llm_slides.slides()   # 쪽번호는 deck_lib.PAGE 기준으로 이어짐
```

## 기존 장표에서 함께 고칠 문구

로컬 LLM 실행 연동이 구현되었으므로, 기존 자료에서 "보완 필요"로 적힌 부분을 바꿔야 합니다.

| 위치 (`build_traceopsreqsync.py`) | 현재 | 변경 제안 |
|---|---|---|
| 3장 성과 요약, 하단 바 | 로컬 LLM 기반 결정사항 추출 연동과 … 보완하여 | 호출구조 분석의 TraceOps 통합을 보완하여 |
| 9장 AI 활용 구조, `현재 상태와 보완` | 로컬 LLM 실행 연동 {{보완 필요}} | 로컬 LLM(Ollama, Qwen3) 실행 연동 구현 |
| 9장 AI 활용 구조, 흐름 상자 | 1차 생성 후 2차 검증 | 그대로 사용 가능 (2차 검증 단계 구현 완료) |
| 11장 ReqSync 상세, 핵심 포인트 | 실행 연동은 구현 방안 작성 후 적용 {{보완 필요}} | 회의록 업로드 시 로컬 LLM이 추출·매칭 |
| README `작성 방침` | 사전에 분석된 결과를 API로 조회 | 로컬 LLM 분석 구현, LLM 미기동 시 저장 결과로 시연 |

## 장표 내용의 근거 (구현 위치)

| 내용 | 근거 |
|---|---|
| LLM 호출(OpenAI 호환, JSON 스키마, `reasoning_effort: none`, 1회 재요청) | `traceops-simple/llm.py` |
| 클로바노트 파싱, 12분·6,000자 조각, 3단계(추출·2차 검증·매칭), 후보 15건 선별, 결과 보정 | `traceops-simple/minutes.py` |
| AI 역할 지시문 3종: `EXTRACT_SYSTEM`(회의록 분석가), `VERIFY_SYSTEM`(2차 검토자), `MAP_SYSTEM`(요구사항 매핑 분석가) | `minutes.py` 상단 상수 |
| AI 2차 검증: 근거 발언 앞 1개·뒤 3개 발언과 대조, 예/아니오 3문항으로 판단, 결정사항이 아니면 제외, `확정`은 남은 확인·승인이 있으면 `검토 중`·`미정`으로 낮춤 | `minutes.py` `verify()` |
| 매칭 보정: 모델이 신규라고 해도 유사도 1위가 뚜렷하면(12점 이상, 2위의 1.3배) 신뢰도 중간으로 제안 | `minutes.py` `fallback_candidate()` |
| `POST /api/meetings/analyze`, 백그라운드 스레드(동시 1건), `GET /api/jobs/{id}`, `GET /api/llm/status` | `traceops-simple/server.py` |
| 결정사항 한 건씩 저장(ID `AI-n`), 재분석 시 검토된 건 유지 | `traceops-simple/reqdb.py` |
| 1.5초 진행 조회, 추출 즉시 표시, LLM 미기동 시 시연 모드 | `traceops-simple/js/requirements-review.js` |
| 실측: 추출 조각당 약 5분 → 25~60초, 매칭 건당 약 5분 → 1분 이내, 2차 검증 건당 15~35초, 샘플(25분 분량) 전체 3분 41초 | 2026-11-16~17 CPU 노트북(i7-1360P, RAM 16GB), Qwen3 4B, `samples/sample_meeting.txt` |

## 로컬 LLM 기동 방법 (시연 전 확인)

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve     # LLM 서버 기동
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" ps        # 모델 적재 상태 확인
python server.py                                             # traceops-simple 폴더에서 실행
```

- 브라우저에서 `http://localhost:11434`를 열어 `Ollama is running`이 보이면 LLM 서버가 정상입니다.
- `requirements-review.html` 상단에 "로컬 LLM 연결됨 (qwen3:4b)"이 보이면 실제 분석이 동작합니다. LLM 서버가 꺼져 있으면 저장된 결과로 시연합니다.
