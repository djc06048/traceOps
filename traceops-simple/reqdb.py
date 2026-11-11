"""요구사항 관리 관계형 스키마(SQLite) + 시드 + 조회/동기화.

requirements ─< req_stakeholders
     │  (requirement_history: 삭제 후에도 남도록 FK 없음)
     └─< decisions >─ meetings
              └─ decision_reviews ─< review_history
"""
import json, os, sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DBFILE = os.environ.get('TRACEOPS_DB', os.path.join(ROOT, 'traceops.db'))

SCHEMA = """
CREATE TABLE IF NOT EXISTS store (key TEXT PRIMARY KEY, json TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS requirements (
  id           TEXT PRIMARY KEY,
  major        TEXT NOT NULL DEFAULT '',
  middle       TEXT NOT NULL DEFAULT '',
  minor        TEXT NOT NULL DEFAULT '',
  name         TEXT NOT NULL DEFAULT '',
  content      TEXT NOT NULL DEFAULT '',
  stage        TEXT NOT NULL CHECK (stage  IN ('분석','설계')),
  status       TEXT NOT NULL CHECK (status IN ('수용','조건부수용','부분수용','미수용')),
  kind         TEXT NOT NULL CHECK (kind   IN ('기능','비기능')),
  precondition TEXT NOT NULL DEFAULT '',
  source       TEXT NOT NULL DEFAULT '',
  created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime')),
  updated_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS req_stakeholders (
  req_id TEXT NOT NULL REFERENCES requirements(id) ON DELETE CASCADE ON UPDATE CASCADE,
  role   TEXT NOT NULL CHECK (role IN ('vendor','cust_it','cust_biz')),
  owner  TEXT NOT NULL DEFAULT '',
  team   TEXT NOT NULL DEFAULT '',
  PRIMARY KEY (req_id, role)
);

CREATE TABLE IF NOT EXISTS requirement_history (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  req_id       TEXT NOT NULL,
  ts           TEXT NOT NULL,
  who          TEXT NOT NULL,
  action       TEXT NOT NULL CHECK (action IN ('create','update','delete')),
  field        TEXT,
  old_value    TEXT,
  new_value    TEXT,
  meeting_file TEXT,
  decision_id  TEXT,
  note         TEXT
);
CREATE INDEX IF NOT EXISTS ix_reqhist_req ON requirement_history(req_id);

CREATE TABLE IF NOT EXISTS meetings (
  file     TEXT PRIMARY KEY,
  label    TEXT NOT NULL,
  duration TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS decisions (
  id                TEXT PRIMARY KEY,
  meeting_file      TEXT NOT NULL REFERENCES meetings(file),
  req_id            TEXT REFERENCES requirements(id) ON UPDATE CASCADE,
  meeting_text      TEXT NOT NULL DEFAULT '',
  excerpt_ts        TEXT NOT NULL DEFAULT '',
  excerpt           TEXT NOT NULL DEFAULT '',
  decision          TEXT NOT NULL,
  raw_status        TEXT NOT NULL DEFAULT '',
  final_status      TEXT NOT NULL CHECK (final_status IN ('ok','review','open')),
  verification_note TEXT NOT NULL DEFAULT '',
  confidence        TEXT NOT NULL DEFAULT '',
  addition          TEXT,
  replace_with      TEXT,
  new_req_hint      TEXT
);
CREATE INDEX IF NOT EXISTS ix_dec_meeting ON decisions(meeting_file);
CREATE INDEX IF NOT EXISTS ix_dec_req ON decisions(req_id);

CREATE TABLE IF NOT EXISTS decision_reviews (
  decision_id  TEXT PRIMARY KEY REFERENCES decisions(id) ON DELETE CASCADE,
  reviewed     INTEGER NOT NULL DEFAULT 0,
  status       TEXT,
  confirmed_by TEXT,
  confirmed_at TEXT,
  edited_text  TEXT
);

CREATE TABLE IF NOT EXISTS review_history (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  decision_id TEXT NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,
  ts          TEXT NOT NULL,
  who         TEXT NOT NULL,
  what        TEXT NOT NULL
);
-- ===== 분석 / 설계 / 개발 (단계별 독립 테이블) + 연결 테이블 =====
-- evidence/remarks/extra는 JSON 텍스트 (ponytail: 증적·비고는 별도 엔티티가 생기면 테이블로 분리)
CREATE TABLE IF NOT EXISTS analysis_items (
  id TEXT PRIMARY KEY, src_id TEXT NOT NULL DEFAULT '',
  system TEXT NOT NULL DEFAULT '', subsystem TEXT NOT NULL DEFAULT '', type TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL DEFAULT '', worker TEXT NOT NULL DEFAULT '',
  w_plan_start TEXT NOT NULL DEFAULT '', w_plan_end TEXT NOT NULL DEFAULT '',
  w_act_start TEXT NOT NULL DEFAULT '', w_act_end TEXT NOT NULL DEFAULT '',
  p_plan_start TEXT NOT NULL DEFAULT '', p_plan_end TEXT NOT NULL DEFAULT '',
  p_act_start TEXT NOT NULL DEFAULT '', p_act_end TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '[]', remarks TEXT NOT NULL DEFAULT '[]', extra TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS design_items (
  id TEXT PRIMARY KEY, src_id TEXT NOT NULL DEFAULT '',
  system TEXT NOT NULL DEFAULT '', subsystem TEXT NOT NULL DEFAULT '', type TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL DEFAULT '', worker TEXT NOT NULL DEFAULT '',
  w_plan_start TEXT NOT NULL DEFAULT '', w_plan_end TEXT NOT NULL DEFAULT '',
  w_act_start TEXT NOT NULL DEFAULT '', w_act_end TEXT NOT NULL DEFAULT '',
  p_plan_start TEXT NOT NULL DEFAULT '', p_plan_end TEXT NOT NULL DEFAULT '',
  p_act_start TEXT NOT NULL DEFAULT '', p_act_end TEXT NOT NULL DEFAULT '',
  dev_type TEXT NOT NULL DEFAULT '', dev_round TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '[]', remarks TEXT NOT NULL DEFAULT '[]', extra TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS dev_items (
  id TEXT PRIMARY KEY, src_id TEXT NOT NULL DEFAULT '', src_name TEXT NOT NULL DEFAULT '',
  system TEXT NOT NULL DEFAULT '', subsystem TEXT NOT NULL DEFAULT '', type TEXT NOT NULL DEFAULT '',
  name TEXT NOT NULL DEFAULT '', worker TEXT NOT NULL DEFAULT '',
  w_plan_start TEXT NOT NULL DEFAULT '', w_plan_end TEXT NOT NULL DEFAULT '',
  w_act_start TEXT NOT NULL DEFAULT '', w_act_end TEXT NOT NULL DEFAULT '',
  p_plan_start TEXT NOT NULL DEFAULT '', p_plan_end TEXT NOT NULL DEFAULT '',
  p_act_start TEXT NOT NULL DEFAULT '', p_act_end TEXT NOT NULL DEFAULT '',
  dev_type TEXT NOT NULL DEFAULT '', dev_round TEXT NOT NULL DEFAULT '',
  difficulty TEXT NOT NULL DEFAULT '', priority TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '', link_basis TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '[]', remarks TEXT NOT NULL DEFAULT '[]', extra TEXT NOT NULL DEFAULT '{}'
);

-- 분석 ↔ 요구사항 (요구사항은 분석 단계에서 정하고 아래 단계가 물려받음)
CREATE TABLE IF NOT EXISTS analysis_requirements (
  analysis_id TEXT NOT NULL REFERENCES analysis_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  req_id      TEXT NOT NULL REFERENCES requirements(id) ON UPDATE CASCADE,
  PRIMARY KEY (analysis_id, req_id)
);
-- 설계 ↔ 분석
CREATE TABLE IF NOT EXISTS design_analysis (
  design_id   TEXT NOT NULL REFERENCES design_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  analysis_id TEXT NOT NULL REFERENCES analysis_items(id) ON UPDATE CASCADE,
  PRIMARY KEY (design_id, analysis_id)
);
-- 개발 ↔ 설계
CREATE TABLE IF NOT EXISTS dev_design (
  dev_id    TEXT NOT NULL REFERENCES dev_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  design_id TEXT NOT NULL REFERENCES design_items(id) ON UPDATE CASCADE,
  PRIMARY KEY (dev_id, design_id)
);
-- 설계·개발의 요구사항은 분석에서 상속되므로 저장하지 않고 뷰로 계산 (불일치 방지)
CREATE VIEW IF NOT EXISTS design_requirements AS
  SELECT DISTINCT da.design_id, ar.req_id
  FROM design_analysis da JOIN analysis_requirements ar ON ar.analysis_id = da.analysis_id;
CREATE VIEW IF NOT EXISTS dev_requirements AS
  SELECT DISTINCT dd.dev_id, dr.req_id
  FROM dev_design dd JOIN design_requirements dr ON dr.design_id = dd.design_id;

-- ===== 물리ID 마스터 + 설계/개발 연결 =====
CREATE TABLE IF NOT EXISTS physical_ids (
  id TEXT PRIMARY KEY, type TEXT NOT NULL DEFAULT '', name TEXT NOT NULL DEFAULT '',
  group_name TEXT NOT NULL DEFAULT '', related_screen TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT '', remark TEXT NOT NULL DEFAULT ''
);
-- 설계 ↔ 물리ID
CREATE TABLE IF NOT EXISTS design_physical (
  design_id TEXT NOT NULL REFERENCES design_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  phys_id   TEXT NOT NULL REFERENCES physical_ids(id) ON UPDATE CASCADE,
  PRIMARY KEY (design_id, phys_id)
);
-- 개발이 설계의 물리ID 외에 추가로 갖는 물리ID (개발의 물리ID = 설계 것 + 추가분)
CREATE TABLE IF NOT EXISTS dev_physical_add (
  dev_id  TEXT NOT NULL REFERENCES dev_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  phys_id TEXT NOT NULL REFERENCES physical_ids(id) ON UPDATE CASCADE,
  PRIMARY KEY (dev_id, phys_id)
);
CREATE VIEW IF NOT EXISTS dev_physical AS
  SELECT dd.dev_id, dp.phys_id FROM dev_design dd JOIN design_physical dp ON dp.design_id = dd.design_id
  UNION
  SELECT dev_id, phys_id FROM dev_physical_add;

-- ===== 단위테스트 / 통합테스트 =====
CREATE TABLE IF NOT EXISTS unit_items (
  id TEXT PRIMARY KEY, src_id TEXT NOT NULL DEFAULT '', name TEXT NOT NULL DEFAULT '',
  expected TEXT NOT NULL DEFAULT '', round TEXT NOT NULL DEFAULT '', worker TEXT NOT NULL DEFAULT '',
  exec_date TEXT NOT NULL DEFAULT '', result TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '[]', remarks TEXT NOT NULL DEFAULT '[]', extra TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS integration_items (
  id TEXT PRIMARY KEY, src_id TEXT NOT NULL DEFAULT '', name TEXT NOT NULL DEFAULT '',
  expected TEXT NOT NULL DEFAULT '', round TEXT NOT NULL DEFAULT '', worker TEXT NOT NULL DEFAULT '',
  exec_date TEXT NOT NULL DEFAULT '', result TEXT NOT NULL DEFAULT '',
  evidence TEXT NOT NULL DEFAULT '[]', remarks TEXT NOT NULL DEFAULT '[]', extra TEXT NOT NULL DEFAULT '{}'
);
-- 단위테스트 ↔ 개발
CREATE TABLE IF NOT EXISTS unit_dev (
  unit_id TEXT NOT NULL REFERENCES unit_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  dev_id  TEXT NOT NULL REFERENCES dev_items(id) ON UPDATE CASCADE,
  PRIMARY KEY (unit_id, dev_id)
);
-- 통합테스트 ↔ 묶인 단위테스트 (통합의 개발ID·요구사항ID·물리ID는 모두 여기서 계산)
CREATE TABLE IF NOT EXISTS integration_units (
  integration_id TEXT NOT NULL REFERENCES integration_items(id) ON DELETE CASCADE ON UPDATE CASCADE,
  unit_id        TEXT NOT NULL REFERENCES unit_items(id) ON UPDATE CASCADE,
  PRIMARY KEY (integration_id, unit_id)
);
CREATE VIEW IF NOT EXISTS unit_requirements AS
  SELECT DISTINCT ud.unit_id, dr.req_id FROM unit_dev ud JOIN dev_requirements dr ON dr.dev_id = ud.dev_id;
CREATE VIEW IF NOT EXISTS unit_physical AS
  SELECT DISTINCT ud.unit_id, dp.phys_id FROM unit_dev ud JOIN dev_physical dp ON dp.dev_id = ud.dev_id;
CREATE VIEW IF NOT EXISTS integration_dev AS
  SELECT DISTINCT iu.integration_id, ud.dev_id FROM integration_units iu JOIN unit_dev ud ON ud.unit_id = iu.unit_id;
CREATE VIEW IF NOT EXISTS integration_requirements AS
  SELECT DISTINCT iu.integration_id, ur.req_id FROM integration_units iu JOIN unit_requirements ur ON ur.unit_id = iu.unit_id;
CREATE VIEW IF NOT EXISTS integration_physical AS
  SELECT DISTINCT iu.integration_id, up.phys_id FROM integration_units iu JOIN unit_physical up ON up.unit_id = iu.unit_id;
"""

COLS = ['major', 'middle', 'minor', 'name', 'content', 'stage', 'status', 'precondition', 'kind', 'source']
PEOPLE = ['vendorOwner', 'custITOwner', 'custITTeam', 'custBizOwner', 'custBizTeam']
LABEL = {'major': '대분류', 'middle': '중분류', 'minor': '소분류', 'name': '요구사항명', 'content': '요구사항내역',
         'stage': '단계', 'status': '수용여부', 'precondition': '선행조건', 'kind': '구분', 'source': '출처',
         'vendorOwner': '업체담당', 'custITOwner': '고객IT담당자', 'custITTeam': '고객IT담당팀',
         'custBizOwner': '고객업무담당자', 'custBizTeam': '고객업무담당팀'}
ROLES = [('vendor', 'vendorOwner', None), ('cust_it', 'custITOwner', 'custITTeam'), ('cust_biz', 'custBizOwner', 'custBizTeam')]


def connect():
    c = sqlite3.connect(DBFILE)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys = ON')
    return c


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _seed_file(name):
    p = os.path.join(ROOT, 'data', name + '.json')
    return json.load(open(p, encoding='utf-8'))['items'] if os.path.exists(p) else []


def init():
    c = connect()
    c.executescript(SCHEMA)
    with c:
        if not c.execute('SELECT 1 FROM requirements').fetchone():
            _write_reqs(c, _seed_file('requirements'), {})
        if not c.execute('SELECT 1 FROM meetings').fetchone():
            for m in _seed_file('meetings'):
                c.execute('INSERT INTO meetings VALUES (?,?,?)', (m['file'], m['label'], m.get('duration', '')))
            for d in _seed_file('decisions'):
                c.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                    d['id'], d['meetingFile'], d.get('reqId'), d.get('meeting', ''), d.get('excerptTs', ''),
                    d.get('excerpt', ''), d['decision'], d.get('rawStatus', ''), d['finalStatus'],
                    d.get('verificationNote', ''), d.get('confidence', ''), d.get('addition'),
                    d.get('replaceWith'), d.get('newReqHint')))
        if not c.execute('SELECT 1 FROM physical_ids').fetchone():
            _write_phys(c, _seed_file('asis'))
        _migrate_phys_columns(c)
        # 단계별로 비어 있는 것만 시드 (이미 쓰던 DB에 새 단계가 추가된 경우도 처리)
        empty = [k for k in KINDS if not c.execute('SELECT 1 FROM %s' % SPEC[k]['table']).fetchone()]
        if empty:
            _write_trace(c, {k: _seed_file(k) for k in empty})
    c.close()


# ---------- 요구사항 ----------
def flatten(x):
    f = {k: x.get(k) or '' for k in COLS}
    f['vendorOwner'] = x.get('vendorOwner') or ''
    for key, pre in (('custIT', 'custIT'), ('custBiz', 'custBiz')):
        o = x.get(key) or {}
        f[pre + 'Owner'] = o.get('owner') or ''
        f[pre + 'Team'] = o.get('team') or ''
    return f


def _snip(o, n, w=30):
    """긴 문장은 처음 달라진 위치 주변만 보여준다."""
    o, n = o or '', n or ''
    if max(len(o), len(n)) <= 2 * w:
        return o or '(없음)', n or '(없음)'
    i = 0
    while i < min(len(o), len(n)) and o[i] == n[i]:
        i += 1
    lo = max(0, i - 10)
    cut = lambda t: ('…' if lo else '') + t[lo:lo + w] + ('…' if len(t) > lo + w else '')
    return cut(o) or '(없음)', cut(n) or '(없음)'


def _revisions(rows):
    groups, out = {}, []
    for h in rows:
        k = (h['ts'], h['who'], h['meeting_file'], h['decision_id'], h['note'])
        if k not in groups:
            groups[k] = {'ts': h['ts'][:16], 'who': h['who'], 'meetingFile': h['meeting_file'],
                         'decisionId': h['decision_id'], 'parts': [], 'note': h['note']}
            out.append(groups[k])
        g = groups[k]
        if h['action'] == 'create':
            g['parts'].append('신규 등록')
        else:
            o, n = _snip(h['old_value'], h['new_value'])
            g['parts'].append('%s: %s → %s' % (LABEL.get(h['field'], h['field']), o, n))
    return [{'ts': g['ts'], 'who': g['who'], 'meetingFile': g['meetingFile'], 'decisionId': g['decisionId'],
             'note': (g['note'] + ' · ' if g['note'] else '') + ' / '.join(g['parts'])} for g in out]


def req_items(c):
    st = {}
    for r in c.execute('SELECT * FROM req_stakeholders'):
        st.setdefault(r['req_id'], {})[r['role']] = r
    hist = {}
    for h in c.execute('SELECT * FROM requirement_history ORDER BY id'):
        hist.setdefault(h['req_id'], []).append(h)
    items = []
    for r in c.execute('SELECT * FROM requirements ORDER BY id'):
        s = st.get(r['id'], {})
        g = lambda role, f: (s[role][f] if role in s else '')
        x = {'id': r['id']}
        for k in COLS:
            x[k] = r[k]
        x['vendorOwner'] = g('vendor', 'owner')
        x['custIT'] = {'owner': g('cust_it', 'owner'), 'team': g('cust_it', 'team')}
        x['custBiz'] = {'owner': g('cust_biz', 'owner'), 'team': g('cust_biz', 'team')}
        x['revisions'] = _revisions(hist.get(r['id'], []))
        items.append(x)
    return items


def _write_reqs(c, items, ctx, who=None):
    """items 전체를 DB와 맞춘다(추가/수정/삭제). who가 있으면 변경 이력 기록."""
    old = {x['id']: flatten(x) for x in req_items(c)}
    new = {}
    for x in items:
        if not x.get('id'):
            raise ValueError('요구사항ID 미입력')
        if x['id'] in new:
            raise ValueError('중복 요구사항ID: ' + x['id'])
        new[x['id']] = flatten(x)
    ts = now()

    def hist(rid, action, field=None, o=None, n=None):
        if who is None:
            return
        c.execute('INSERT INTO requirement_history (req_id,ts,who,action,field,old_value,new_value,meeting_file,decision_id,note)'
                  ' VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (rid, ts, who, action, field, o, n, ctx.get('meetingFile'), ctx.get('decisionId'), ctx.get('note')))

    for rid in old.keys() - new.keys():
        c.execute('DELETE FROM requirements WHERE id = ?', (rid,))  # 결정사항이 참조 중이면 FK 오류
        hist(rid, 'delete', 'name', old[rid]['name'], None)
    for rid, f in new.items():
        if rid not in old:
            c.execute('INSERT INTO requirements (id,%s) VALUES (?,%s)' % (','.join(COLS), ','.join('?' * len(COLS))),
                      [rid] + [f[k] for k in COLS])
            hist(rid, 'create')
        else:
            diff = [k for k in COLS + PEOPLE if f[k] != old[rid][k]]
            if not diff:
                continue
            c.execute('UPDATE requirements SET %s, updated_at = ? WHERE id = ?' % ','.join(k + ' = ?' for k in COLS),
                      [f[k] for k in COLS] + [ts, rid])
            for k in diff:
                hist(rid, 'update', k, old[rid][k], f[k])
        for role, ok, tk in ROLES:
            c.execute('INSERT INTO req_stakeholders VALUES (?,?,?,?) ON CONFLICT(req_id, role) DO UPDATE '
                      'SET owner = excluded.owner, team = excluded.team', (rid, role, f[ok], f[tk] if tk else ''))


def save_reqs(items, who, ctx):
    c = connect()
    try:
        with c:
            _write_reqs(c, items, ctx or {}, who or '시스템')
        return req_items(c)
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if 'FOREIGN KEY' in msg:
            raise ValueError('결정사항·분석 단계가 참조 중인 요구사항ID는 삭제·변경할 수 없습니다')
        raise ValueError('입력값 오류: ' + msg)
    finally:
        c.close()


# ---------- 회의 / 결정사항 / 검토 ----------
def meetings(c):
    return [dict(r) for r in c.execute('SELECT file,label,duration FROM meetings ORDER BY rowid')]


def decisions(c):
    out = []
    for r in c.execute('SELECT * FROM decisions ORDER BY rowid'):
        d = {'id': r['id'], 'meetingFile': r['meeting_file'], 'meeting': r['meeting_text'], 'excerptTs': r['excerpt_ts'],
             'excerpt': r['excerpt'], 'decision': r['decision'], 'rawStatus': r['raw_status'], 'finalStatus': r['final_status'],
             'verificationNote': r['verification_note'], 'reqId': r['req_id'], 'confidence': r['confidence'],
             'addition': r['addition'], 'replaceWith': r['replace_with']}
        if r['new_req_hint']:
            d['newReqHint'] = r['new_req_hint']
        out.append(d)
    return out


def reviews(c):
    out = {}
    for r in c.execute('SELECT * FROM decision_reviews'):
        v = {'reviewed': bool(r['reviewed']), 'history': []}
        for k, col in (('status', 'status'), ('confirmedBy', 'confirmed_by'), ('confirmedAt', 'confirmed_at'), ('editedText', 'edited_text')):
            if r[col] is not None:
                v[k] = r[col]
        out[r['decision_id']] = v
    for h in c.execute('SELECT * FROM review_history ORDER BY id'):
        out.setdefault(h['decision_id'], {'reviewed': False, 'history': []})['history'].append(
            {'ts': h['ts'], 'who': h['who'], 'what': h['what']})
    return out


def save_review(did, rv):
    c = connect()
    try:
        with c:
            c.execute('INSERT INTO decision_reviews VALUES (?,?,?,?,?,?) ON CONFLICT(decision_id) DO UPDATE SET '
                      'reviewed=excluded.reviewed, status=excluded.status, confirmed_by=excluded.confirmed_by, '
                      'confirmed_at=excluded.confirmed_at, edited_text=excluded.edited_text',
                      (did, 1 if rv.get('reviewed') else 0, rv.get('status'), rv.get('confirmedBy'),
                       rv.get('confirmedAt'), rv.get('editedText')))
            c.execute('DELETE FROM review_history WHERE decision_id = ?', (did,))
            for h in rv.get('history', []):
                c.execute('INSERT INTO review_history (decision_id,ts,who,what) VALUES (?,?,?,?)',
                          (did, h['ts'], h['who'], h['what']))
    except sqlite3.IntegrityError:
        raise ValueError('존재하지 않는 결정사항입니다: ' + did)
    finally:
        c.close()


# ---------- 분석 / 설계 / 개발 / 단위 / 통합 + 물리ID ----------
import re

_COMMON = ['srcId', 'system', 'subsystem', 'type', 'name', 'worker', 'wPlanStart', 'wPlanEnd', 'wActStart', 'wActEnd',
           'pPlanStart', 'pPlanEnd', 'pActStart', 'pActEnd']
_TEST = ['srcId', 'name', 'expected', 'round', 'worker', 'execDate', 'result']
KINDS = ['analysis', 'design', 'dev', 'unit', 'integration']
# links: (연결 테이블, 내 FK, 상대 FK, 화면 필드) — 저장되는 연결.  derived: 상위에서 계산되는 필드(저장 안 함)
SPEC = {
    'analysis': dict(table='analysis_items', cols=_COMMON, j=['evidence', 'remarks'], derived=[],
                     links=[('analysis_requirements', 'analysis_id', 'req_id', 'reqIds')]),
    'design': dict(table='design_items', cols=_COMMON + ['devType', 'devRound'], j=['evidence', 'remarks'], derived=['reqIds'],
                   links=[('design_analysis', 'design_id', 'analysis_id', 'analysisRef'),
                          ('design_physical', 'design_id', 'phys_id', 'physIds')]),
    'dev': dict(table='dev_items', cols=_COMMON + ['srcName', 'devType', 'devRound', 'difficulty', 'priority', 'desc', 'linkBasis'],
                j=['evidence', 'remarks'], derived=['reqIds', 'physIds'],
                links=[('dev_design', 'dev_id', 'design_id', 'designRef'),
                       ('dev_physical_add', 'dev_id', 'phys_id', 'physIdsAdd')]),
    'unit': dict(table='unit_items', cols=_TEST, j=['evidence', 'remarks'], derived=['reqIds', 'physIds'],
                 links=[('unit_dev', 'unit_id', 'dev_id', 'linked')]),
    'integration': dict(table='integration_items', cols=_TEST, j=['evidence', 'remarks'], derived=['linked', 'reqIds', 'physIds'],
                        links=[('integration_units', 'integration_id', 'unit_id', 'units')]),
}


def _col(k):
    return 'description' if k == 'desc' else re.sub(r'([A-Z])', lambda m: '_' + m.group(1).lower(), k)


def _union(*lists):
    out = []
    for l in lists:
        for v in l:
            if v not in out:
                out.append(v)
    return out


def _derive(d):
    """상위 단계에서 상속·집계되는 값 계산. 화면 app.js의 syncDown과 같은 규칙(여러 건 연결도 합집합으로 처리)."""
    A = {x['id']: x for x in d['analysis']}
    for x in d['design']:
        x['reqIds'] = _union(*[A[a]['reqIds'] for a in x['analysisRef'] if a in A])
    D = {x['id']: x for x in d['design']}
    for x in d['dev']:
        ds = [D[i] for i in x['designRef'] if i in D]
        x['reqIds'] = _union(*[p['reqIds'] for p in ds])
        x['physIds'] = _union(*[p['physIds'] for p in ds], x['physIdsAdd'])
    V = {x['id']: x for x in d['dev']}
    for x in d['unit']:
        vs = [V[i] for i in x['linked'] if i in V]
        x['reqIds'] = _union(*[v['reqIds'] for v in vs])
        x['physIds'] = _union(*[v['physIds'] for v in vs])
    U = {x['id']: x for x in d['unit']}
    for x in d['integration']:
        us = [U[i] for i in x['units'] if i in U]
        x['linked'] = _union(*[u['linked'] for u in us])
        x['reqIds'] = _union(*[u['reqIds'] for u in us])
        x['physIds'] = _union(*[u['physIds'] for u in us])


def trace_all(c):
    d = {}
    for kind, sp in SPEC.items():
        links = {}
        for ltab, mine, other, field in sp['links']:
            for r in c.execute('SELECT %s, %s FROM %s ORDER BY rowid' % (mine, other, ltab)):
                links.setdefault((field, r[0]), []).append(r[1])
        items = []
        for r in c.execute('SELECT * FROM %s ORDER BY rowid' % sp['table']):
            x = {'id': r['id']}
            for k in sp['cols']:
                x[k] = r[_col(k)]
            for k in sp['j']:
                x[k] = json.loads(r[_col(k)])
            x.update(json.loads(r['extra']))
            for _, _, _, field in sp['links']:
                x[field] = links.get((field, r['id']), [])
            items.append(x)
        d[kind] = items
    _derive(d)
    return d


def _write_trace(c, data):
    """data에 들어 있는 단계만 한 트랜잭션에서 DB와 맞춘다. 순서: 항목 upsert(상위→하위) → 연결 재작성 → 삭제(하위→상위)."""
    kinds = [k for k in KINDS if k in data]
    ids = {}
    for kind in kinds:
        sp = SPEC[kind]
        ids[kind] = []
        for x in data[kind] or []:
            if not x.get('id'):
                raise ValueError('ID 미입력')
            if x['id'] in ids[kind]:
                raise ValueError('중복 ID: ' + x['id'])
            ids[kind].append(x['id'])
            known = set(sp['cols']) | set(sp['j']) | set(sp['derived']) | {'id'} | {l[3] for l in sp['links']}
            extra = {k: v for k, v in x.items() if k not in known and not k.startswith('_')}
            names = ['id'] + [_col(k) for k in sp['cols'] + sp['j']] + ['extra']
            vals = [x['id']] + [x.get(k) or '' for k in sp['cols']] + \
                   [json.dumps(x.get(k) or [], ensure_ascii=False) for k in sp['j']] + [json.dumps(extra, ensure_ascii=False)]
            c.execute('INSERT INTO %s (%s) VALUES (%s) ON CONFLICT(id) DO UPDATE SET %s' % (
                sp['table'], ','.join(names), ','.join('?' * len(names)), ','.join('%s = excluded.%s' % (n, n) for n in names[1:])), vals)
    for kind in kinds:
        for x in data[kind] or []:
            for ltab, mine, other, field in SPEC[kind]['links']:
                c.execute('DELETE FROM %s WHERE %s = ?' % (ltab, mine), (x['id'],))
                for t in dict.fromkeys(x.get(field) or []):
                    c.execute('INSERT INTO %s (%s, %s) VALUES (?, ?)' % (ltab, mine, other), (x['id'], t))
    for kind in reversed(kinds):
        table = SPEC[kind]['table']
        for (rid,) in c.execute('SELECT id FROM %s' % table).fetchall():
            if rid not in ids[kind]:
                c.execute('DELETE FROM %s WHERE id = ?' % table, (rid,))   # 하위가 참조 중이면 FK 오류


def _fk_error(e):
    if 'FOREIGN KEY' in str(e):
        return ValueError('연결된 항목이 없거나, 다른 항목이 참조 중인 항목은 삭제·변경할 수 없습니다')
    return ValueError('입력값 오류: ' + str(e))


def save_trace(data):
    c = connect()
    try:
        with c:
            _write_trace(c, data)
        return trace_all(c)
    except sqlite3.IntegrityError as e:
        raise _fk_error(e)
    finally:
        c.close()


# ---------- 물리ID ----------
def phys_items(c):
    return [{'id': r['id'], 'type': r['type'], 'name': r['name'], 'group': r['group_name'],
             'relatedScreen': r['related_screen'], 'status': r['status'], 'remark': r['remark']}
            for r in c.execute('SELECT * FROM physical_ids ORDER BY rowid')]


def _write_phys(c, items):
    seen = []
    for x in items:
        if not x.get('id'):
            raise ValueError('물리ID 미입력')
        if x['id'] in seen:
            raise ValueError('중복 물리ID: ' + x['id'])
        seen.append(x['id'])
        v = [x['id'], x.get('type') or '', x.get('name') or '', x.get('group') or '',
             x.get('relatedScreen') or '', x.get('status') or '', x.get('remark') or '']
        c.execute('INSERT INTO physical_ids VALUES (?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET type=excluded.type, '
                  'name=excluded.name, group_name=excluded.group_name, related_screen=excluded.related_screen, '
                  'status=excluded.status, remark=excluded.remark', v)
    for (rid,) in c.execute('SELECT id FROM physical_ids').fetchall():
        if rid not in seen:
            c.execute('DELETE FROM physical_ids WHERE id = ?', (rid,))   # 설계·개발이 사용 중이면 FK 오류


def save_phys(items):
    c = connect()
    try:
        with c:
            _write_phys(c, items)
        return phys_items(c)
    except sqlite3.IntegrityError as e:
        raise ValueError('사용 중인 물리ID는 삭제·변경할 수 없습니다' if 'FOREIGN KEY' in str(e) else '입력값 오류: ' + str(e))
    finally:
        c.close()


def _migrate_phys_columns(c):
    """이전 버전(design_items/dev_items.phys_ids JSON 컬럼)을 연결 테이블로 옮기고 컬럼을 제거한다."""
    for table, ltab, fk in (('design_items', 'design_physical', 'design_id'), ('dev_items', 'dev_physical_add', 'dev_id')):
        if 'phys_ids' not in [r[1] for r in c.execute('PRAGMA table_info(%s)' % table)]:
            continue
        for rid, js in c.execute('SELECT id, phys_ids FROM %s' % table).fetchall():
            own = json.loads(js)
            if table == 'dev_items':   # 개발은 설계에서 물리ID를 상속하므로 설계에 없는 것만 추가분으로
                inherited = {p for (p,) in c.execute('SELECT dp.phys_id FROM dev_design dd JOIN design_physical dp '
                                                      'ON dp.design_id = dd.design_id WHERE dd.dev_id = ?', (rid,))}
                own = [p for p in own if p not in inherited]
            for p in own:
                c.execute('INSERT OR IGNORE INTO %s (%s, phys_id) VALUES (?, ?)' % (ltab, fk), (rid, p))
        c.execute('ALTER TABLE %s DROP COLUMN phys_ids' % table)
