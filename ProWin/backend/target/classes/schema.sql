CREATE TABLE IF NOT EXISTS rfp_document (
  project_id TEXT PRIMARY KEY,
  file_name TEXT NOT NULL,
  page_count TEXT,
  received_date TEXT
);

CREATE TABLE IF NOT EXISTS rfp_requirement (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  code TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT,
  deleted_by TEXT,
  deleted_reason TEXT
);

CREATE TABLE IF NOT EXISTS toc_row (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  level INTEGER NOT NULL,
  title TEXT NOT NULL,
  owner TEXT,
  pages TEXT,
  status TEXT,
  order_index INTEGER NOT NULL,
  presentation_assigned INTEGER NOT NULL DEFAULT 0,
  deleted_at TEXT,
  deleted_by TEXT,
  deleted_reason TEXT
);

CREATE TABLE IF NOT EXISTS review_node (
  toc_row_id TEXT PRIMARY KEY REFERENCES toc_row(id),
  memo TEXT,
  title_detail TEXT,
  flow_steps TEXT,
  bullets TEXT
);

CREATE TABLE IF NOT EXISTS review_comment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  toc_row_id TEXT NOT NULL REFERENCES toc_row(id),
  author TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proposal_commit (
  commit_hash TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  branch TEXT NOT NULL,
  message TEXT NOT NULL,
  tag TEXT,
  uploaded_by TEXT NOT NULL,
  uploaded_at TEXT NOT NULL,
  file_name TEXT,
  file_path TEXT,
  is_snapshot INTEGER NOT NULL DEFAULT 0,
  diff_json TEXT,
  toc_row_id TEXT REFERENCES toc_row(id),
  slide_count INTEGER NOT NULL DEFAULT 0
);
