# analyzer

Java 소스 정적분석(AST 기반 caller→callee 추출) 담당: 홍건 프로. 이 폴더는 개발환경 스캐폴딩 단계에서 자리만 잡아둔 상태이며, 실제 파싱 로직은 아직 없다.

## 적재 대상 DB 스키마

`infra/init.sql` 참고. 분석기는 아래 두 테이블에 upsert하면 된다.

- `nodes(id, node_type, qualified_name, class_name, method_name, file_path, edit_state, created_at)`
  - `node_type`: `ENTRY` | `PROGRAM` | `DBIO` | `EXTERNAL`
  - `edit_state`: 분석기가 자동 생성한 로우는 항상 `AUTO`. 개발자가 캔버스에서 직접 수정한 로우만 `MANUAL`로 바뀐다 — 분석기는 `MANUAL` 로우를 덮어쓰면 안 됨.
- `edges(id, caller_node_id, callee_node_id, call_site_line, edit_state, created_at)`

## 접속 정보 (로컬 개발)

```
host=localhost port=5432 db=traceops user=traceops password=traceops
```

`infra/docker-compose.yml`로 기동. `infra/seed.sql`에 파이프라인 검증용 샘플 데이터가 있으니, 실제 파싱 로직 작성 전 참고용으로 볼 것.
