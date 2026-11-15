# 성과제출

연말 성과 제출용 발표 자료(HTML → PDF)를 만드는 폴더입니다. 제품별 폴더는 `prowin`, `traceOpsReqSync` 두 개만 둡니다.

| 위치 | 내용 |
|------|------|
| `작성가이드.md` | 공통 디자인 기준과 문체 규칙 (먼저 읽기) |
| `제안서_추진현황_요약.md` | 내용 출처 (ReqSync, ProWin, TraceOps 목표·배경·성과) |
| `assets/` | 로고, 표지·목차 배경 |
| `fonts/` | 나눔바른고딕 |
| `tools/` | 공통 생성 라이브러리(`deck_lib.py`), 스타일(`deck.css`), 점검·출력(`lint.js`, `render.js`) |
| `prowin/` | ProWin 성과 제출 (생성 스크립트, HTML, 화면 캡처, 개발자용 보완 정리) |
| `traceOpsReqSync/` | TraceOps + ReqSync 통합 성과 제출 (작성 예정) |

## 빌드

저장소 루트에서 실행합니다. HTML은 각 제품 폴더에 생성됩니다.

```bash
python3 성과제출/prowin/build_prowin.py
node 성과제출/tools/lint.js
node 성과제출/tools/render.js 성과제출/prowin/성과제출_ProWin.html out --pdf out/ProWin.pdf
```

- 파이썬은 표준 라이브러리만 사용합니다.
- `lint.js`, `render.js` 는 Playwright(Chromium)가 필요합니다.
- 결과 HTML을 브라우저로 열 때는 `성과제출/` 폴더 구조를 그대로 유지해야 로고와 글꼴이 불러와집니다.
