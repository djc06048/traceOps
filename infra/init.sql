-- 연계 캔버스 그래프 스키마 (FR-014/FR-046/FR-048)
CREATE TABLE nodes (
    id          BIGSERIAL PRIMARY KEY,
    node_type   TEXT NOT NULL CHECK (node_type IN ('ENTRY', 'PROGRAM', 'DBIO', 'EXTERNAL')),
    qualified_name TEXT NOT NULL,
    class_name  TEXT,
    method_name TEXT,
    file_path   TEXT,
    edit_state  TEXT NOT NULL DEFAULT 'AUTO' CHECK (edit_state IN ('AUTO', 'MANUAL')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (qualified_name, method_name)
);

CREATE TABLE edges (
    id              BIGSERIAL PRIMARY KEY,
    caller_node_id  BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    callee_node_id  BIGINT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    call_site_line  INTEGER,
    edit_state      TEXT NOT NULL DEFAULT 'AUTO' CHECK (edit_state IN ('AUTO', 'MANUAL')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- PMS 기능(요구사항 관리, FR-005~007) 수용 가능성 검증용 최소 예시 테이블
CREATE TABLE requirements (
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'CONFIRMED', 'REJECTED')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
