/* ProWin 단순 버전 — 로그인(데모), 역할별 권한, 변경 이력, 소프트 삭제, 데모 화면 이식 (DB 없음)
 * 데이터: data/*.json. 편집은 브라우저 임시저장, 저장 시 변경 확인, 내보내기로 파일 교체.
 */
(function () {
  'use strict';

  var FILES = {
    master: 'data/master.json', proposals: 'data/proposals.json', schedule: 'data/schedule.json', comm: 'data/comm.json',
    boards: 'data/boards.json', matrix: 'data/matrix.json', expense: 'data/expense.json', effort: 'data/effort.json',
    assets: 'data/assets.json', guide: 'data/guide.json', history: 'data/history.json'
  };
  /* RFP·목차·제안서 검토·제안서 관리는 더 이상 정적 파일이 아니라 Java 백엔드(SQLite)가 보관 — js/store.js의 api()로 호출 */
  var PROJECT_ID = 'P-001';
  var KEY = 'prowin-simple-v2:';
  var SESSION = 'prowin-simple-session';
  var LEVEL_LABEL = { none: '없음', view: '조회', edit: '편집' };
  var SCHED_STATUS = ['예정', '진행중', '완료'];
  var QA_STATUS = ['답변대기', '답변완료'];
  var COLORS = [{ v: 'c-wr', l: '작성 (초록)' }, { v: 'c-rv', l: '리뷰 (파랑)' }, { v: 'c-mt', l: '마일스톤 (주황)' }, { v: 'c-dl', l: '마감 (빨강)' }, { v: 'c-gy', l: '기타 (회색)' }];
  var KIND_COLOR = { c_wr: 'c-wr' };
  var INFO = {
    proposals: { req: '기간별 제안 진행 현황을 목록으로 파악', phase: 'Step 1 · 꼭 필요' },
    home: { req: '제안 개요 + 오늘 할 일(일정 연동) + 지연 항목 가시화', phase: 'Step 1 · 꼭 필요' },
    comm: { req: '제안팀 공지·공유 게시판', phase: 'Step 2 · 컨셉 강화' },
    schedule: { req: '짧은 제안 일정(2~3주)의 다일 일정 등록/수정/삭제, 색상 구분 · PM·사업관리 편집 / 그 외 조회', phase: 'Step 1 · 꼭 필요' },
    rfp: { req: 'RFP 업로드/다운로드 및 요구사항 정리 한눈 · 유사 사례 추천', phase: 'Step 1 · 꼭 필요 (자동추출·유사사례는 Step 2)' },
    toc: { req: '제안서 전체 목차 = 진척 마스터(담당·상태·예상장수), 엑셀 다운로드', phase: 'Step 1 · 꼭 필요' },
    review: { req: '슬라이드 보기 · 설명회 지정 · 리뷰 코멘트(회의록 대체)', phase: 'Step 1 · 꼭 필요' },
    versions: { req: '업로드=커밋 · 합본=불변 스냅샷(PM/사업관리 권한)', phase: 'Step 1 · 꼭 필요' },
    matrix: { req: '최종 취합본 기준 요구사항↔목차/페이지 매핑', phase: 'Step 1 · 꼭 필요' },
    board: { req: '워크스페이스 관리에서 추가한 자유 게시판', phase: 'Step 2 · 컨셉 강화' },
    workspace: { req: '제안별 자유 게시판(폴더) 추가/수정/삭제', phase: 'Step 2 · 컨셉 강화' },
    wsperm: { req: '제안 단위 멤버·권한 관리(PM/사업관리 전용)', phase: 'Step 1 · 꼭 필요' },
    expense: { req: '자사/외주 인건비·디자인·인쇄비 통합 관리, 그리드 편집 (PM·사업관리)', phase: 'Step 2 · 컨셉 강화' },
    effort: { req: '투입 M/M·직급별 공수 관리, 그리드 편집 (PM·사업관리)', phase: 'Step 2 · 컨셉 강화' },
    assets: { req: '과거 제안서 페이지 단위 적재(Step 1) + 의미 기반 검색(Step 2)', phase: 'Step 2 · 컨셉 강화' },
    sysperm: { req: '프로젝트에 종속되지 않는 시스템 마스터 권한 관리', phase: 'Step 2 · 컨셉 강화' },
    guide: { req: '사이트 사용법 통합 가이드', phase: 'Step 2 · 컨셉 강화' },
    history: { req: '추가·수정·삭제 이력 (감사 대응)', phase: '공통 기능' }
  };

  var S = { user: null, data: {}, base: {}, draft: {}, route: 'home', modal: null, cal: null, rv: null, commit: null, rfpReq: null, versionSection: '', expTab: 'staff' };

  /* ---------- 공통 유틸 ---------- */
  function $(id) { return document.getElementById(id); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function p2(n) { return String(n).padStart(2, '0'); }
  function isoOf(d) { return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function todayISO() { return isoOf(new Date()); }
  function nowText() { var d = new Date(); return isoOf(d) + ' ' + p2(d.getHours()) + ':' + p2(d.getMinutes()); }
  function addDays(iso, n) { var d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return isoOf(d); }
  function daysBetween(a, b) { return Math.round((new Date(b + 'T00:00:00') - new Date(a + 'T00:00:00')) / 86400000); }
  function snap() { return JSON.parse(JSON.stringify(S.data)); }
  function alive(list) { return list.filter(function (x) { return !x.deleted; }); }
  function nextNum(prefix, list) {
    var max = 0;
    list.forEach(function (x) { var n = parseInt(String(x.id).split('-').pop(), 10); if (n > max) max = n; });
    return prefix + '-' + String(max + 1).padStart(3, '0');
  }
  function roleName(r) { return S.data.master.roles[r] || r; }
  var timer;
  function toast(msg, err) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.toggle('err', !!err);
    t.classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(function () { t.classList.remove('show'); }, 2400);
  }
  function logH(action, target, detail) {
    var h = S.data.history;
    h.nextId = (h.nextId || 1);
    h.items.unshift({ id: 'H-' + String(h.nextId).padStart(4, '0'), at: nowText(), who: S.user ? S.user.name : '-', action: action, target: target, detail: detail || '' });
    h.nextId++;
  }

  /* ---------- 권한 ---------- */
  function role() { return S.user ? S.user.role : 'writer'; }
  function level(k) {
    var p = S.data.master.perms[k] || {};
    return p[role()] || 'none';
  }
  function canView(k) { return level(k) !== 'none'; }
  function canEdit(k) { return level(k) === 'edit'; }
  function canEditPost(k, p) { return canEdit(k) && (role() === 'pm' || p.by === S.user.name); }

  /* ---------- 화면 목록 ---------- */
  function boardOf(k) {
    var id = parseInt(String(k).replace('board-', ''), 10);
    return S.data.boards.boards.filter(function (b) { return b.id === id; })[0];
  }
  function screens() {
    var list = [
      { k: 'proposals', label: '제안 현황', grp: 'global' },
      { k: 'assets', label: '자산 라이브러리', grp: 'global' },
      { k: 'home', label: '제안서 홈', grp: 'ws' },
      { k: 'comm', label: '커뮤니케이션', grp: 'ws' },
      { k: 'schedule', label: '제안 일정', grp: 'ws' },
      { k: 'rfp', label: 'RFP / 요구사항', grp: 'ws' }
    ];
    alive(S.data.boards.boards).forEach(function (b) { list.push({ k: 'board-' + b.id, label: b.name, grp: 'ws', board: true }); });
    list.push({ k: 'toc', label: '목차', grp: 'ws' }, { k: 'review', label: '제안서 검토', grp: 'ws' }, { k: 'versions', label: '제안서 관리', grp: 'ws' },
      { k: 'matrix', label: '조견표', grp: 'ws' }, { k: 'workspace', label: '워크스페이스 관리', grp: 'ws' }, { k: 'wsperm', label: '제안 권한관리', grp: 'ws' },
      { k: 'expense', label: '제안 경비 관리', grp: 'ws' }, { k: 'effort', label: '수행 공수 관리', grp: 'ws' });
    list.push({ k: 'sysperm', label: '시스템 접근 권한관리', grp: 'adm' }, { k: 'guide', label: '사용 가이드', grp: 'adm' }, { k: 'history', label: '변경 이력', grp: 'adm' });
    return list;
  }
  function scr(k) { return screens().filter(function (x) { return x.k === k; })[0]; }

  /* ---------- 모달 ---------- */
  function openForm(title, fields, vals, onSave, onDelete, validate, savedMsg) {
    var h = '<div class="modal-hd"><div><h3>' + esc(title) + '</h3></div><button class="modal-close" data-x="1">✕</button></div><div class="modal-list">';
    fields.forEach(function (f) {
      var v = vals[f.k] == null ? '' : vals[f.k];
      h += '<label class="fld"><span>' + esc(f.label) + (f.req ? ' *' : '') + '</span>';
      if (f.type === 'textarea') h += '<textarea data-f="' + f.k + '">' + esc(v) + '</textarea>';
      else if (f.type === 'select') h += '<select data-f="' + f.k + '">' + f.opts.map(function (o) {
        var val = o.v == null ? o : o.v, lab = o.l == null ? o : o.l;
        return '<option value="' + esc(val) + '"' + (val === v ? ' selected' : '') + '>' + esc(lab) + '</option>';
      }).join('') + '</select>';
      else h += '<input type="' + (f.type || 'text') + '" data-f="' + f.k + '" value="' + esc(v) + '">';
      h += '</label>';
    });
    h += '</div><div class="modal-input"><div class="row"><span>' + (onDelete ? '<button class="btn ghost sm" data-del="1">삭제</button>' : '') +
      '</span><span class="pick-btns"><button class="btn ghost sm" data-x="1">취소</button><button class="btn sm" data-save="1">저장</button></span></div></div>';
    $('modalBox').innerHTML = h;
    S.modal = { fields: fields, onSave: onSave, onDelete: onDelete, validate: validate, savedMsg: savedMsg };
    $('modal').classList.add('open');
    var first = $('modalBox').querySelector('[data-f]');
    if (first) first.focus();
  }
  function openView(title, rows) {
    $('modalBox').innerHTML = '<div class="modal-hd"><div><h3>' + esc(title) + '</h3></div><button class="modal-close" data-x="1">✕</button></div><div class="modal-list">' +
      rows.map(function (r) { return '<div class="fld"><span>' + esc(r[0]) + '</span><div style="font-size:14px;white-space:pre-wrap">' + esc(r[1]) + '</div></div>'; }).join('') +
      '</div><div class="modal-input"><div class="row"><span></span><span class="pick-btns"><button class="btn sm" data-x="1">닫기</button></span></div></div>';
    S.modal = null;
    $('modal').classList.add('open');
  }
  function closeModal() { S.modal = null; $('modal').classList.remove('open'); }
  // 삭제: 사유 필수, 실제로는 지우지 않고 '삭제됨'으로 표시 + 이력
  function askDelete(label, target, onOk, savedMsg) {
    openForm('삭제 · ' + label, [{ k: 'reason', label: '삭제 사유', type: 'textarea', req: true }], {}, function (v) {
      S.lastReason = v.reason;
      logH('삭제', target, v.reason);
      return onOk(v.reason);
    }, null, null, savedMsg);
    $('modalBox').querySelector('[data-save]').textContent = '삭제 확인';
  }
  function markDeleted(item, reason) { item.deleted = { at: nowText(), by: S.user.name, reason: reason }; }
  function openInfo() {
    var k = S.route, s = scr(k), key = s && s.board ? 'board' : k, info = INFO[key] || { req: '정보 없음', phase: '' };
    openView('화면 정보 · ' + (s ? s.label : ''), [['요구사항', info.req], ['단계', info.phase]]);
  }

  /* ---------- 화면: 제안 현황 ---------- */
  function progress() {
    var items = alive(S.data.schedule.items), t = todayISO();
    var done = items.filter(function (x) { return x.status === '완료'; }).length;
    var doing = items.filter(function (x) { return x.status === '진행중'; }).length;
    var late = items.filter(function (x) { return x.end < t && x.status !== '완료'; }).length;
    return { total: items.length, done: done, doing: doing, todo: items.length - done - doing, late: late, pct: items.length ? Math.round(done / items.length * 100) : 0 };
  }
  function viewProposals() {
    var rows = alive(S.data.proposals.items), pg = progress();
    var h = canEdit('proposals') ? '<div style="margin-bottom:12px"><button class="btn sm" data-prop-add="1">＋ 새 제안</button></div>' : '';
    h += '<div class="card" style="padding:0"><table><thead><tr><th>상태</th><th>제안명</th><th>구성</th><th>제안 기간</th><th>PM</th><th>사업관리</th><th>영업대표</th><th>진척</th>' + (canEdit('proposals') ? '<th></th>' : '') + '</tr></thead><tbody>';
    rows.forEach(function (r) {
      var pct = r.id === 'P-001' ? pg.pct : r.pct;
      h += '<tr class="prow" data-go-home="1"><td><span class="st ' + esc(r.cls) + '">' + esc(r.status) + '</span></td><td style="font-weight:700">' + esc(r.name) + '</td>' +
        '<td style="color:var(--ink3)">' + esc(r.scope) + '</td><td>' + esc(r.start) + ' ~ ' + esc(r.end) + '</td><td>' + esc(r.pm) + '</td><td>' + esc(r.biz) + '</td><td>' + esc(r.sales) + '</td>' +
        '<td><span class="pbar"><span style="width:' + pct + '%"></span></span> ' + pct + '%</td>' +
        (canEdit('proposals') ? '<td><button class="btn ghost sm" data-prop-del="' + esc(r.id) + '">삭제</button></td>' : '') + '</tr>';
    });
    h += '</tbody></table></div><p class="muted" style="margin:12px 4px">행을 누르면 제안서 홈으로 이동합니다. 추가와 삭제는 이 화면에서만 합니다.</p>';
    return h;
  }

  /* ---------- 화면: 제안서 홈 ---------- */
  function activity() {
    var a = [];
    alive(S.data.schedule.items).forEach(function (x) { a.push({ d: x.start, t: '일정 · ' + x.title + ' (' + x.status + ')', by: x.owner }); });
    alive(S.data.comm.posts).forEach(function (p) { a.push({ d: p.date, t: '커뮤니케이션 · ' + p.title, by: p.by }); });
    S.data.boards.boards.forEach(function (b) { alive(b.posts).forEach(function (p) { a.push({ d: p.date, t: b.name + ' · ' + p.title, by: p.by }); }); });
    return a.sort(function (x, y) { return x.d < y.d ? 1 : -1; }).slice(0, 6);
  }
  function listSched(list, empty) {
    if (!list.length) return '<div class="empty">' + empty + '</div>';
    var t = todayISO();
    return '<table><tbody>' + list.map(function (x) {
      var late = x.end < t && x.status !== '완료';
      return '<tr class="' + (late ? 'late' : '') + '"><td>' + esc(x.title) + '</td><td class="muted">' + esc(x.start) + ' ~ ' + esc(x.end) +
        '</td><td class="muted">' + esc(x.owner) + '</td><td><span class="st ' + (late ? 'late' : x.status === '진행중' ? 'doing' : 'todo') + '">' + (late ? '지연' : esc(x.status)) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
  }
  function viewHome() {
    var p = S.data.master.project, t = todayISO(), pg = progress(), dday = daysBetween(t, p.deadline);
    var today = alive(S.data.schedule.items).filter(function (x) { return x.start <= t && t <= x.end && x.status !== '완료'; });
    var late = alive(S.data.schedule.items).filter(function (x) { return x.end < t && x.status !== '완료'; });
    var tm = S.data.master.members;
    var h = '<div class="grid2"><div>';
    h += '<div class="card"><h3>' + esc(p.name) + (canEdit('home') ? '<button class="btn ghost sm" data-proj-edit="1">수정</button>' : '') + '</h3>' +
      '<div class="kv"><div class="k">발주처</div><div>' + esc(p.client) + '</div>' +
      '<div class="k">제안 기간</div><div>' + esc(p.start) + ' ~ ' + esc(p.deadline) + ' · ' + (dday >= 0 ? '마감 D-' + dday : '마감 지남') + '</div>' +
      '<div class="k">PM</div><div>' + esc(p.team.pm) + '</div><div class="k">사업관리</div><div>' + esc(p.team.biz) + '</div>' +
      '<div class="k">영업대표</div><div>' + esc(p.team.sales) + '</div>' +
      '<div class="k">진척</div><div><span class="pbar"><span style="width:' + pg.pct + '%"></span></span> ' + pg.pct + '% (완료 ' + pg.done + ' · 진행 ' + pg.doing + ' · 예정 ' + pg.todo + ' · 지연 ' + pg.late + ')</div>' +
      '<div class="k">개요</div><div>' + esc(p.summary) + '</div></div></div>';
    h += '<div class="card"><h3>최근 업데이트</h3>' + activity().map(function (a) {
      return '<div class="act"><span>' + esc(a.t) + '</span><span class="d">' + esc(a.by) + ' · ' + esc(a.d) + '</span></div>';
    }).join('') + '</div></div><div>';
    h += '<div class="card"><h3>오늘 할 일 <span class="muted">' + esc(t) + '</span></h3>' + listSched(today, '오늘 할 일이 없습니다.') + '</div>';
    h += '<div class="card"><h3>⚠ 지연 항목 <span class="muted">마감 지남 · 미완료</span></h3>' + listSched(late, '지연 항목이 없습니다.') + '</div>';
    h += '<div class="card"><h3>팀 <span class="muted">' + tm.length + '명</span></h3><table><tbody>' + tm.map(function (x) {
      return '<tr><td><b>' + esc(x.name) + '</b></td><td class="muted">' + esc(x.title) + '</td><td><span class="tag">' + esc(roleName(x.role)) + '</span></td></tr>';
    }).join('') + '</tbody></table></div>';
    return h + '</div></div>';
  }
  function projectFields() {
    var mem = alive(S.data.master.members).map(function (x) { return x.name; });
    return [
      { k: 'name', label: '사업명', req: true }, { k: 'client', label: '발주처', req: true }, { k: 'summary', label: '개요', type: 'textarea' },
      { k: 'start', label: '제안 시작', type: 'date' }, { k: 'deadline', label: '제안 마감', type: 'date' }, { k: 'presentation', label: '제안 발표', type: 'date' },
      { k: 'pm', label: 'PM', type: 'select', opts: mem }, { k: 'biz', label: '사업관리', type: 'select', opts: mem }, { k: 'sales', label: '영업대표', type: 'select', opts: mem }
    ];
  }

  /* ---------- 화면: 커뮤니케이션 / 게시판 ---------- */
  function postsOf(k) { return k === 'comm' ? S.data.comm.posts : boardOf(k).posts; }
  function postFields(k) {
    var f = [{ k: 'title', label: '제목', req: true }, { k: 'body', label: '내용', type: 'textarea' }];
    if (k === 'comm') f.push({ k: 'att', label: '첨부 파일명' });
    var b = k === 'comm' ? null : boardOf(k);
    if (b && b.kind === 'qna') { f.push({ k: 'status', label: '상태', type: 'select', opts: QA_STATUS }); f.push({ k: 'answer', label: '답변', type: 'textarea' }); }
    if (b && b.kind === 'ref') f.push({ k: 'link', label: '자료 위치 (파일명·경로)' });
    return f;
  }
  function viewPosts(k) {
    var list = alive(postsOf(k)).slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
    var b = k === 'comm' ? null : boardOf(k);
    var h = canEdit(k) ? '<div style="margin-bottom:12px"><button class="btn sm" data-post-add="' + k + '">＋ 새 글</button></div>' : '';
    if (!list.length) h += '<div class="card"><div class="empty">글이 없습니다.</div></div>';
    h += '<div class="card">';
    list.forEach(function (p) {
      h += '<div class="post"><div class="pt">' + esc(p.title) + '</div><div class="pm">' + esc(p.by) + ' · ' + esc(p.date) + '</div><div class="pb">' + esc(p.body) + '</div>';
      if (p.att) h += '<span class="att">PPT ' + esc(p.att) + '</span>';
      if (b && b.kind === 'qna') h += '<div style="margin-top:8px"><span class="st ' + (p.status === '답변완료' ? 'done' : 'wait') + '">' + esc(p.status || '답변대기') + '</span>' +
        (p.answer ? '<div class="pb" style="margin-top:6px">↳ 답변: ' + esc(p.answer) + '</div>' : '') + '</div>';
      if (b && b.kind === 'ref' && p.link) h += '<span class="att">📎 ' + esc(p.link) + '</span>';
      if (canEditPost(k, p)) h += '<div style="margin-top:8px"><button class="btn ghost sm" data-post-edit="' + k + '|' + esc(p.id) + '">수정</button> <button class="btn ghost sm" data-post-del="' + k + '|' + esc(p.id) + '">삭제</button></div>';
      h += '</div>';
    });
    return h + '</div>';
  }

  /* ---------- 화면: 제안 일정 (달력 + 목록) ---------- */
  function monthCells(y, m) {
    var off = new Date(y, m, 1).getDay(), days = new Date(y, m + 1, 0).getDate(), total = Math.ceil((off + days) / 7) * 7, cells = [];
    for (var i = 0; i < total; i++) { var d = new Date(y, m, 1 - off + i); cells.push({ iso: isoOf(d), inMonth: d.getMonth() === m, num: d.getDate() }); }
    return cells;
  }
  function calHTML() {
    var c = S.cal, cells = monthCells(c.y, c.m), t = todayISO(), items = alive(S.data.schedule.items), h = '';
    for (var w = 0; w < cells.length / 7; w++) {
      var wk = cells.slice(w * 7, w * 7 + 7), ws = wk[0].iso, we = wk[6].iso;
      var segs = items.filter(function (x) { return x.end >= ws && x.start <= we; }).map(function (x) {
        var s = x.start > ws ? x.start : ws, e = x.end < we ? x.end : we;
        return { it: x, c1: wk.findIndex(function (q) { return q.iso === s; }), c2: wk.findIndex(function (q) { return q.iso === e; }) };
      }).sort(function (a, b) { return a.c1 - b.c1 || b.c2 - a.c2; });
      var lanes = [];
      segs.forEach(function (sg) { var ln = 0; while (lanes[ln] !== undefined && lanes[ln] >= sg.c1) ln++; lanes[ln] = sg.c2; sg.lane = ln; });
      h += '<div class="week" style="min-height:' + (30 + lanes.length * 22 + 6) + 'px">' + wk.map(function (q) {
        return '<div class="day' + (q.inMonth ? '' : ' out') + '"' + (q.iso === t ? ' style="background:var(--accent-bg)"' : '') + '><span class="n">' + q.num + '</span></div>';
      }).join('') + segs.map(function (sg) {
        return '<div class="bar ' + esc(sg.it.color) + '" data-ev="' + esc(sg.it.id) + '" title="' + esc(sg.it.title) + ' (' + esc(sg.it.start) + ' ~ ' + esc(sg.it.end) + ')" ' +
          'style="left:calc(' + (sg.c1 / 7 * 100) + '% + 3px);width:calc(' + ((sg.c2 - sg.c1 + 1) / 7 * 100) + '% - 6px);top:' + (28 + sg.lane * 22) + 'px">' + esc(sg.it.title) + '</div>';
      }).join('') + '</div>';
    }
    return '<div class="cal-bar"><button class="btn ghost sm" data-cal="prev">‹</button><span class="ttl">' + c.y + '년 ' + (c.m + 1) + '월</span>' +
      '<button class="btn ghost sm" data-cal="next">›</button><button class="btn ghost sm" data-cal="today">오늘</button></div>' +
      '<div class="cal-head">' + ['일', '월', '화', '수', '목', '금', '토'].map(function (d) { return '<div>' + d + '</div>'; }).join('') + '</div>' + h +
      '<div class="legend"><span class="c-wr">작성</span><span class="c-rv">리뷰</span><span class="c-mt">마일스톤</span><span class="c-dl">마감</span><span class="c-gy">기타</span></div>';
  }
  function schedFields() {
    return [
      { k: 'title', label: '제목', req: true }, { k: 'start', label: '시작일', type: 'date', req: true }, { k: 'end', label: '종료일', type: 'date', req: true },
      { k: 'color', label: '색상', type: 'select', opts: COLORS },
      { k: 'owner', label: '담당', type: 'select', opts: alive(S.data.master.members).map(function (x) { return x.name; }) },
      { k: 'status', label: '상태', type: 'select', opts: SCHED_STATUS }
    ];
  }
  function schedValidate(v) { return v.end < v.start ? '종료일이 시작일보다 빠릅니다' : null; }
  function openSched(id) {
    var it = S.data.schedule.items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (!canEdit('schedule')) { openView('일정 조회', [['제목', it.title], ['기간', it.start + ' ~ ' + it.end], ['담당', it.owner], ['상태', it.status]]); return; }
    openForm('일정 수정', schedFields(), it, function (v) { Object.assign(it, v); logH('수정', '일정 ' + id, v.title); }, function () {
      askDelete('일정 ' + it.title, '일정 ' + id, function () { markDeleted(it, S.lastReason); });
    }, schedValidate);
  }
  function viewSchedule() {
    var c = S.cal, can = canEdit('schedule'), t = todayISO();
    var h = '<div class="card" style="padding:16px">' + (can ? '<div style="margin-bottom:12px"><button class="btn sm" data-sc-add="1">＋ 일정 추가</button> <span class="muted">막대를 누르면 수정할 수 있습니다</span></div>' : '<div class="muted" style="margin-bottom:10px">조회 전용 · 일정 편집은 편집 권한이 있는 역할만 가능합니다</div>') + calHTML() + '</div>';
    var items = alive(S.data.schedule.items).slice().sort(function (a, b) { return a.start < b.start ? -1 : 1; });
    h += '<div class="card"><h3>일정 목록</h3><table><thead><tr><th>제목</th><th>시작</th><th>종료</th><th>색상</th><th>담당</th><th>상태</th>' + (can ? '<th></th>' : '') + '</tr></thead><tbody>';
    if (!items.length) h += '<tr><td colspan="7" class="empty">등록된 일정이 없습니다.</td></tr>';
    items.forEach(function (x) {
      var late = x.end < t && x.status !== '완료';
      h += '<tr class="' + (late ? 'late' : '') + '"><td>' + esc(x.title) + '</td><td>' + esc(x.start) + '</td><td>' + esc(x.end) + '</td>' +
        '<td><span class="' + esc(x.color) + '" style="display:inline-block;width:12px;height:12px;border-radius:3px"></span></td><td>' + esc(x.owner) + '</td>' +
        '<td><span class="st ' + (late ? 'late' : x.status === '완료' ? 'done' : x.status === '진행중' ? 'doing' : 'todo') + '">' + (late ? '지연' : esc(x.status)) + '</span></td>' +
        (can ? '<td><button class="btn ghost sm" data-sc-edit="' + esc(x.id) + '">수정</button> <button class="btn ghost sm" data-sc-del="' + esc(x.id) + '">삭제</button></td>' : '') + '</tr>';
    });
    return h + '</tbody></table></div>';
  }

  /* ---------- 화면: RFP / 요구사항 (Java 백엔드 · SQLite) ---------- */
  function viewRfp() {
    var data = S.data.rfp || { document: null, requirements: [] };
    var doc = data.document, reqs = data.requirements || [];
    if (!reqs.some(function (q) { return q.id === S.rfpReq; })) S.rfpReq = reqs.length ? reqs[0].id : null;
    var sel = S.rfpReq;
    var h = doc
      ? '<div class="card" style="display:flex;align-items:center;gap:14px"><span class="tag" style="background:#000;color:#fff;border-color:#000">PDF</span><div><div style="font-weight:700">' + esc(doc.fileName) + '</div><div class="muted">' + esc(doc.pageCount) + ' · ' + esc(doc.receivedDate) + '</div></div></div>'
      : '<div class="card"><div class="empty">등록된 RFP 원문이 없습니다.</div></div>';
    h += '<div class="grid2"><div><div class="card"><h3>요구사항 정리' + (canEdit('rfp') ? ' <button class="btn sm" data-req-add="1">＋ 추가</button>' : '') + '</h3><table><tbody>';
    if (!reqs.length) h += '<tr><td class="empty" colspan="3">등록된 요구사항이 없습니다.</td></tr>';
    reqs.forEach(function (q) {
      h += '<tr class="prow" data-req="' + esc(q.id) + '" style="' + (q.id === sel ? 'background:var(--accent-bg)' : '') + '"><td style="font-weight:700;width:60px">' + esc(q.id) + '</td><td><b>' + esc(q.title) + '</b><div class="muted">' + esc(q.description || '') + '</div></td>' +
        (canEdit('rfp') ? '<td><button class="btn ghost sm" data-req-del="' + esc(q.id) + '">삭제</button></td>' : '') + '</tr>';
    });
    h += '</tbody></table></div></div><div><div class="card"><h3>유사 사례 추천 <span class="chip">Step 2</span></h3><div class="empty">추천 사례 기능은 Step 2에서 제공됩니다.</div></div></div></div>';
    return h;
  }
  function reqFields() { return [{ k: 'code', label: 'ID (예: R-07)', req: true }, { k: 'title', label: '요구사항', req: true }, { k: 'description', label: '설명', type: 'textarea' }]; }

  /* ---------- 화면: 목차 (Java 백엔드 · SQLite) ---------- */
  function viewToc() {
    var data = S.data.toc || { rows: [], statusLabel: {} };
    var st = data.statusLabel || {}, rows = data.rows || [], can = canEdit('toc');
    var h = (can ? '<div style="margin-bottom:12px"><button class="btn sm" data-toc-add="1">＋ 목차 추가</button></div>' : '');
    h += '<div class="card" style="overflow:auto;padding:0"><table><thead><tr><th style="width:40%">목차</th><th>담당</th><th>예상 장수</th><th>상태</th>' + (can ? '<th></th>' : '') + '</tr></thead><tbody>';
    if (!rows.length) h += '<tr><td class="empty" colspan="' + (can ? 5 : 4) + '">등록된 목차가 없습니다.</td></tr>';
    rows.forEach(function (r) {
      if (r.level === 1) h += '<tr><td colspan="' + (can ? 5 : 4) + '" style="font-weight:700;background:#FAFAFA">' + esc(r.title) + (can ? ' <button class="btn ghost sm" data-toc-edit="' + esc(r.id) + '">수정</button> <button class="btn ghost sm" data-toc-del="' + esc(r.id) + '">삭제</button>' : '') + '</td></tr>';
      else h += '<tr><td style="padding-left:20px">' + esc(r.title) + '</td><td>' + esc(r.owner || '') + '</td><td>' + esc(r.pages || '') + '</td><td><span class="chip ' + esc(r.status) + '">' + esc(st[r.status] || r.status || '') + '</span></td>' +
        (can ? '<td><button class="btn ghost sm" data-toc-edit="' + esc(r.id) + '">수정</button> <button class="btn ghost sm" data-toc-del="' + esc(r.id) + '">삭제</button></td>' : '') + '</tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin:10px 4px">전체 목차 = 진척 마스터(담당·상태·장수). 여러 장은 (1/2)(2/2)처럼 하위로 나눕니다.</p>';
  }
  function tocFields() {
    return [{ k: 'title', label: '제목', req: true }, { k: 'level', label: '단계', type: 'select', opts: [{ v: '1', l: '대분류' }, { v: '2', l: '세부' }] },
      { k: 'owner', label: '담당', type: 'select', opts: alive(S.data.master.members).map(function (x) { return x.name; }) },
      { k: 'pages', label: '예상 장수' }, { k: 'status', label: '상태', type: 'select', opts: [{ v: 'todo', l: '미착수' }, { v: 'doing', l: '진행중' }, { v: 'fix', l: '보완' }, { v: 'done', l: '완료' }] }];
  }

  /* ---------- 화면: 제안서 검토 (Java 백엔드 · SQLite) ---------- */
  function splitLines(s) { return String(s || '').split('\n').map(function (x) { return x.trim(); }).filter(Boolean); }
  function joinLines(arr) { return (arr || []).join('\n'); }
  function reviewNodeOf(id) { return (S.data.review || []).filter(function (n) { return n.tocRowId === id; })[0]; }
  function latestUploadFor(tocRowId) {
    var commits = (S.data.versions && S.data.versions.commits) || [];
    return commits.filter(function (c) { return c.tocRowId === tocRowId && c.fileName && c.slideCount > 0; })[0];
  }
  function reviewFields() {
    return [{ k: 'memo', label: '메모 (담당·예상 장수 등)' }, { k: 'titleDetail', label: '세부 제목' },
      { k: 'flowSteps', label: '흐름 단계 (줄바꿈으로 구분)', type: 'textarea' }, { k: 'bullets', label: '핵심 내용 (줄바꿈으로 구분)', type: 'textarea' }];
  }
  function viewReview() {
    var rows = (S.data.toc && S.data.toc.rows) || [];
    var level2 = rows.filter(function (r) { return r.level === 2; });
    if (!level2.some(function (r) { return r.id === S.rv; })) S.rv = level2.length ? level2[0].id : null;
    var curId = S.rv, can = canEdit('review');
    var h = '<div class="grid2" style="grid-template-columns:300px 1fr"><div class="tree"><div style="padding:8px 10px;font-size:12px;font-weight:700;color:var(--ink2)">목차 (읽기 · 리뷰)</div>';
    rows.forEach(function (r) {
      if (r.level === 1) h += '<div class="tnode g"><span class="dot2"></span>' + esc(r.title) + '</div>';
      else h += '<div class="tnode c2' + (r.id === curId ? ' sel' : '') + '" data-node="' + esc(r.id) + '"><span class="dot2 ' + esc(r.status) + '"></span>' + esc(r.title) + (r.owner ? ' <span class="muted">' + esc(r.owner) + '</span>' : '') + '</div>';
    });
    h += '</div>';
    if (!curId) return h + '<div class="card"><div class="empty">검토할 목차가 없습니다. 목차 화면에서 먼저 등록하세요.</div></div></div>';
    var n = reviewNodeOf(curId) || { tocRowId: curId, memo: '', titleDetail: '', flowSteps: [], bullets: [], presentationAssigned: false, comments: [] };
    var tr = rows.filter(function (r) { return r.id === curId; })[0] || {};
    var st = (S.data.toc && S.data.toc.statusLabel) || {};
    h += '<div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><div><span class="chip ' + esc(tr.status) + '">' + esc(st[tr.status] || tr.status || '') + '</span> <b style="font-size:17px;margin-left:6px">' + esc(tr.title) + '</b></div>' +
      (can ? '<button class="btn ghost sm" data-review-edit="' + esc(curId) + '">내용 수정</button>' : '') + '</div>';
    h += '<div class="muted" style="margin:8px 0 14px">' + esc(n.memo || '') + '</div>';
    if (n.titleDetail) h += '<div style="font-size:13px;font-weight:700;margin-bottom:6px">' + esc(n.titleDetail) + '</div>';
    if ((n.flowSteps || []).length) h += '<div class="pipe" style="margin-bottom:14px">' + n.flowSteps.map(function (f, i) { return '<span class="tag">' + esc(f) + '</span>' + (i < n.flowSteps.length - 1 ? '<span class="muted">→</span>' : ''); }).join('') + '</div>';
    if ((n.bullets || []).length) h += '<ul style="padding-left:18px;font-size:14px;line-height:1.9">' + n.bullets.map(function (b) { return '<li>' + esc(b) + '</li>'; }).join('') + '</ul>';
    var upload = latestUploadFor(curId);
    if (upload) {
      h += '<div style="margin:14px 0"><div style="font-size:13px;font-weight:700;margin-bottom:6px">슬라이드 미리보기 <span class="muted">' + esc(upload.fileName) + ' · ' + upload.slideCount + '장</span></div><div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:4px">';
      for (var si = 0; si < upload.slideCount; si++) {
        var imgUrl = apiPath('/versions/commits/' + encodeURIComponent(upload.commitHash) + '/slides/' + si);
        h += '<a href="' + imgUrl + '" target="_blank"><img src="' + imgUrl + '" alt="슬라이드 ' + (si + 1) + '" style="height:140px;border:1px solid var(--line2);border-radius:6px;flex:none"></a>';
      }
      h += '</div></div>';
    }
    h += '<div style="margin:14px 0"><button class="btn ' + (n.presentationAssigned ? 'acc' : 'ghost') + ' sm" ' + (can ? 'data-review-present="' + esc(curId) + '"' : 'disabled') + '>' + (n.presentationAssigned ? '✓ 설명회 지정됨' : '설명회 지정') + '</button></div>';
    h += '<h3 style="margin-bottom:8px">리뷰 코멘트' + (can ? ' <button class="btn sm" data-review-comment="' + esc(curId) + '">＋ 코멘트</button>' : '') + '</h3>';
    var comments = n.comments || [];
    h += comments.length ? comments.map(function (c) {
      return '<div class="post"><div class="pm">' + esc(c.author) + ' · ' + esc(c.createdAt) + '</div><div class="pb">' + esc(c.body) + '</div></div>';
    }).join('') : '<div class="empty">코멘트가 없습니다.</div>';
    return h + '</div></div>';
  }

  /* ---------- 화면: 제안서 관리 (버전 이력 · 합본, Java 백엔드 · SQLite) ---------- */
  function tocLevel2Rows() { return ((S.data.toc && S.data.toc.rows) || []).filter(function (r) { return r.level === 2; }); }
  function tocTitleOf(id) { var r = tocLevel2Rows().filter(function (r) { return r.id === id; })[0]; return r ? r.title : id; }
  function viewVersions() {
    var v = S.data.versions || { branches: ['main'], commits: [] };
    var level2 = tocLevel2Rows();
    var filtered = S.versionSection ? v.commits.filter(function (c) { return c.tocRowId === S.versionSection; }) : v.commits;
    if (!filtered.some(function (c) { return c.commitHash === S.commit; })) S.commit = filtered.length ? filtered[0].commitHash : null;
    var sel = filtered.filter(function (c) { return c.commitHash === S.commit; })[0], can = canEdit('versions');
    var h = '<div style="margin-bottom:12px">' + (can ? '<button class="btn sm" data-upload="1">업로드(커밋)</button> <button class="btn acc sm" data-merge="1">합본(스냅샷 생성)</button>' : '<button class="btn sm" disabled>업로드 — 편집 권한 필요</button>') + '<input type="file" id="versionFile" style="display:none"></div>';
    h += '<div style="margin-bottom:12px"><label class="fld" style="max-width:300px"><span>목차 섹션별 버전관리</span><select id="versionSectionFilter"><option value="">전체 섹션</option>' +
      level2.map(function (r) { return '<option value="' + esc(r.id) + '"' + (r.id === S.versionSection ? ' selected' : '') + '>' + esc(r.title) + '</option>'; }).join('') + '</select></label></div>';
    h += '<div class="grid2" style="grid-template-columns:360px 1fr"><div class="card" style="padding:6px 4px"><div class="tabs" style="margin:8px">' + v.branches.map(function (b, i) { return '<button class="' + (i === 0 ? 'on' : '') + '">⑂ ' + esc(b) + '</button>'; }).join('') + '</div>';
    if (!filtered.length) h += '<div class="empty" style="padding:14px">커밋 내역이 없습니다.</div>';
    filtered.forEach(function (c) {
      h += '<div class="commit' + (sel && c.commitHash === sel.commitHash ? ' sel' : '') + '" data-commit="' + esc(c.commitHash) + '"><div class="h">' + esc(c.commitHash) + ' · ' + esc(c.uploadedAt) + '</div><div style="font-weight:600">' + esc(c.message) + (c.fileName ? ' <span class="muted">(' + esc(c.fileName) + ')</span>' : '') + '</div><div class="muted">' + esc(c.uploadedBy) + (c.tag ? ' · <span class="tag">' + esc(c.tag) + '</span>' : '') + (c.tocRowId ? ' · <span class="tag">' + esc(tocTitleOf(c.tocRowId)) + '</span>' : '') +
        (c.fileName ? ' · <a href="' + apiPath('/versions/commits/' + encodeURIComponent(c.commitHash) + '/download') + '" download>⬇ 다운로드</a>' : '') + '</div></div>';
    });
    h += '</div><div class="card"><h3>변경 내용 <span class="muted">' + esc(sel ? sel.commitHash : '') + '</span></h3>';
    if (!sel) h += '<div class="empty">선택된 커밋이 없습니다.</div>';
    else if (!sel.diff.length) h += '<div class="empty">변경 내용 기록이 없습니다.</div>';
    else sel.diff.forEach(function (d) {
      h += '<div class="act"><span class="' + (d.kind === 'add' ? 'diff-add' : 'diff-mod') + '" style="font-weight:700;min-width:90px">' + esc(d.label) + '</span><span>' + esc(d.detail) + '</span></div>';
    });
    return h + '</div></div>';
  }

  /* ---------- 화면: 조견표 ---------- */
  function viewMatrix() {
    var m = S.data.matrix, can = canEdit('matrix'), tocs = ((S.data.toc && S.data.toc.rows) || []).filter(function (r) { return r.level === 2; }).map(function (r) { return r.title; });
    var h = '<div class="card" style="overflow:auto;padding:0"><table><thead><tr><th>RFP 쪽</th><th>대분류</th><th>중분류</th><th>소분류</th><th>세부사항 1</th><th>수용여부</th><th>해당 목차</th><th>page</th></tr></thead><tbody>';
    m.rows.forEach(function (r, i) {
      h += '<tr><td>' + esc(r.rfp) + '</td><td class="muted">' + esc(r.big) + '</td><td class="muted">' + esc(r.mid) + '</td><td class="muted">' + esc(r.small) + '</td><td>' + esc(r.d1) + '</td>' +
        '<td><select class="cellin" data-mx="' + i + '|ok"' + (can ? '' : ' disabled') + '>' + m.okOptions.map(function (o) { return '<option' + (o === r.ok ? ' selected' : '') + '>' + o + '</option>'; }).join('') + '</select></td>' +
        '<td><select class="cellin" data-mx="' + i + '|toc"' + (can ? '' : ' disabled') + '>' + tocs.map(function (o) { return '<option' + (o === r.toc ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') + '</select></td>' +
        '<td style="width:80px"><input class="cellin" data-mx="' + i + '|page" value="' + esc(r.page) + '"' + (can ? '' : ' disabled') + '></td></tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin:10px 4px">최종 취합본(스냅샷) 기준 · RFP 발췌 칸은 읽기 전용, 수용여부·해당 목차·page는 사람이 매핑합니다.</p>';
  }

  /* ---------- 화면: 워크스페이스 관리 ---------- */
  function viewWorkspace() {
    var h = '<div style="margin-bottom:12px"><button class="btn sm" data-ws-add="1">＋ 게시판 추가</button></div><div class="card" style="padding:0"><table><thead><tr><th>게시판</th><th>설명</th><th>글 수</th><th>유형</th><th></th></tr></thead><tbody>';
    alive(S.data.boards.boards).forEach(function (b) {
      var kind = b.kind === 'qna' ? 'Q&A (답변 상태)' : b.kind === 'ref' ? '자료 (링크)' : '자유 글';
      h += '<tr><td>' + esc(b.name) + '</td><td class="muted">' + esc(b.desc) + '</td><td>' + alive(b.posts).length + '</td><td class="muted">' + kind + '</td>' +
        '<td><button class="btn ghost sm" data-ws-edit="' + b.id + '">수정</button> <button class="btn ghost sm" data-ws-del="' + b.id + '">삭제</button></td></tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin-top:10px">게시판을 추가하면 좌측 메뉴 "제안 워크스페이스"에 바로 나타납니다. 새 게시판은 작성자가 글을 쓰고 영업대표는 조회만 합니다.</p>';
  }

  /* ---------- 화면: 제안 권한관리 ---------- */
  function viewWsperm() {
    var m = S.data.master, mem = alive(m.members);
    var h = '<div style="display:grid;grid-template-columns:340px 1fr;gap:16px"><div class="card"><h3>멤버 <button class="btn sm" data-mem-add="1">＋ 추가</button></h3><table><tbody>';
    mem.forEach(function (x) {
      var i = m.members.indexOf(x);
      h += '<tr><td><b>' + esc(x.name) + '</b><div class="muted">' + esc(x.title) + ' · ' + esc(x.id) + '</div></td><td>' +
        '<select class="cellin" data-mem-role="' + i + '">' + Object.keys(m.roles).map(function (r) { return '<option value="' + r + '"' + (x.role === r ? ' selected' : '') + '>' + esc(m.roles[r]) + '</option>'; }).join('') + '</select></td>' +
        '<td>' + (x.id === S.user.id ? '' : '<button class="btn ghost sm" data-mem-del="' + i + '">제외</button>') + '</td></tr>';
    });
    h += '</tbody></table></div><div class="card"><h3>화면별 권한 <span class="muted">역할 단위</span></h3><table><thead><tr><th>화면</th>' +
      Object.keys(m.roles).map(function (r) { return '<th>' + esc(m.roles[r]) + '</th>'; }).join('') + '</tr></thead><tbody>';
    screens().forEach(function (s) {
      h += '<tr><td>' + esc(s.label) + '</td>' + Object.keys(m.roles).map(function (r) {
        var lv = (m.perms[s.k] || {})[r] || 'none';
        return '<td><select class="cellin" data-perm="' + s.k + '|' + r + '">' + Object.keys(LEVEL_LABEL).map(function (o) { return '<option value="' + o + '"' + (lv === o ? ' selected' : '') + '>' + LEVEL_LABEL[o] + '</option>'; }).join('') + '</select></td>';
      }).join('') + '</tr>';
    });
    return h + '</tbody></table></div></div>';
  }

  /* ---------- 화면: 제안 경비 / 수행 공수 (편집 그리드) ---------- */
  function viewExpense() {
    var e = S.data.expense, can = canEdit('expense'), t = S.expTab, d = e.tabs[t];
    var h = '<div class="sumrow">' + e.summary.map(function (s, i) { return '<div class="s' + (i === 4 ? ' hl' : '') + '"><div class="l">' + esc(s[0]) + '</div><div class="v">' + esc(s[1]) + ' <span class="muted" style="font-size:11px">원</span></div></div>'; }).join('') + '</div>';
    h += '<div class="tabs">' + Object.keys(e.tabs).map(function (k) { return '<button class="' + (k === t ? 'on' : '') + '" data-exp-tab="' + k + '">' + esc(e.tabs[k].label) + '</button>'; }).join('') + '</div>';
    h += '<div class="card" style="overflow:auto;padding:0"><table><thead><tr>' + d.cols.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('') + '</tr></thead><tbody>';
    d.rows.forEach(function (r, ri) {
      h += '<tr>' + r.map(function (c, ci) { return '<td><input class="cellin" data-exp="' + t + '|' + ri + '|' + ci + '" value="' + esc(c) + '"' + (can ? '' : ' disabled') + '></td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin:10px 4px">' + (can ? '값을 고치면 저장 버튼으로 반영됩니다. 합계는 입력값을 그대로 보여 줍니다(자동 합계는 준비 중).' : '조회 전용 · 편집 권한이 있는 역할만 수정할 수 있습니다.') + '</p>';
  }
  function viewEffort() {
    var e = S.data.effort, can = canEdit('effort');
    var h = '<div class="card" style="overflow:auto;padding:0"><table><thead><tr>' + e.cols.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('') + '</tr></thead><tbody>';
    e.rows.forEach(function (r, ri) {
      h += '<tr>' + r.map(function (c, ci) { return '<td><input class="cellin" data-eff="' + ri + '|' + ci + '" value="' + esc(c) + '"' + (can ? '' : ' disabled') + '></td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin:10px 4px">투입 M/M·직급별 입력 그리드입니다. 경비 관리와 별도 화면입니다.</p>';
  }

  /* ---------- 화면: 자산 라이브러리 ---------- */
  function viewAssets() {
    var h = '<div style="display:grid;grid-template-columns:200px 1fr;gap:16px"><div class="card" style="padding:14px"><div style="font-size:12px;font-weight:700;margin-bottom:10px">필터</div>' +
      '<div style="font-size:12.5px;color:var(--ink2);line-height:2.2">발주처 ▾<br>문서 유형 ▾<br>연도 ▾</div>' +
      '<div style="margin-top:14px;font-size:12px;color:#B85315;background:var(--accent-bg);padding:8px;border-radius:8px">의미(시맨틱) 검색과 요구사항 기준 페이지 추천은 <b>Step 2</b>입니다.</div></div><div class="cards">';
    S.data.assets.cards.forEach(function (c) {
      h += '<div class="acard"><div class="ti">' + esc(c.t) + '</div><div class="m">' + esc(c.m) + ' · ' + esc(c.s) + '</div><div class="p">' + esc(c.p) + '</div></div>';
    });
    return h + '</div></div><p class="muted" style="margin:12px 4px">과거 제안서 페이지 단위 적재(Step 1) · 키워드·메타 검색(Step 1) · 시맨틱 추천(Step 2)</p>';
  }

  /* ---------- 화면: 시스템 접근 권한관리 ---------- */
  function viewSysperm() {
    var can = canEdit('sysperm'), u = S.data.master.sysUsers;
    var h = '<p class="muted" style="margin-bottom:12px">프로젝트 단위(제안 권한관리)가 아닌, <b>시스템 전체</b>에 대한 마스터 권한을 관리합니다.</p><div class="card" style="padding:0"><table><thead><tr><th>사용자</th><th>비고</th><th>전체 프로젝트 접근</th></tr></thead><tbody>';
    u.forEach(function (x, i) {
      h += '<tr><td><b>' + esc(x.name) + '</b></td><td class="muted">' + esc(x.note) + '</td><td><span class="sw' + (x.on ? ' on' : '') + '" ' + (can ? 'data-sw="' + i + '" style="cursor:pointer"' : 'style="opacity:.5"') + '></span></td></tr>';
    });
    return h + '</tbody></table></div>';
  }

  /* ---------- 화면: 사용 가이드 ---------- */
  function viewGuide() {
    var g = S.data.guide, h = '<div style="max-width:760px"><div class="rule">📌 <b>핵심 규칙</b> — ' + esc(g.rule) + '</div>';
    g.sections.forEach(function (s, i) { h += '<div class="guide-sec"><h4><span class="gnum">' + (i + 1) + '</span>' + esc(s.t) + '</h4><p>' + esc(s.b) + '</p></div>'; });
    h += '<div class="guide-sec"><h4>준비 중 (아직 동작하지 않는 기능)</h4><ul style="padding-left:18px;font-size:14px;color:var(--ink2);line-height:1.9">' + g.pending.map(function (p) { return '<li>' + esc(p) + '</li>'; }).join('') + '</ul></div>';
    return h + '</div>';
  }

  /* ---------- 화면: 변경 이력 ---------- */
  function viewHistory() {
    var list = S.data.history.items;
    var h = '<div class="card" style="padding:0"><table><thead><tr><th>시각</th><th>사용자</th><th>작업</th><th>대상</th><th>내용 (삭제 사유 포함)</th></tr></thead><tbody>';
    if (!list.length) h += '<tr><td colspan="5" class="empty">기록이 없습니다.</td></tr>';
    list.slice(0, 200).forEach(function (x) {
      h += '<tr><td class="muted">' + esc(x.at) + '</td><td>' + esc(x.who) + '</td><td><span class="tag">' + esc(x.action) + '</span></td><td>' + esc(x.target) + '</td><td>' + esc(x.detail) + '</td></tr>';
    });
    return h + '</tbody></table></div><p class="muted" style="margin:10px 4px">이력은 저장 버튼을 누르면 파일에 함께 저장됩니다.</p>';
  }

  /* ---------- 렌더 ---------- */
  function renderNav() {
    var h = '', groups = [{ g: 'global', t: '전역' }, { g: 'ws', t: '제안 워크스페이스' }, { g: 'adm', t: 'ProWin 관리' }];
    groups.forEach(function (gr) {
      var items = screens().filter(function (s) { return s.grp === gr.g && canView(s.k); });
      if (!items.length) return;
      h += '<div class="sec">' + gr.t + '</div>';
      items.forEach(function (s) { h += '<button class="nav' + (S.route === s.k ? ' on' : '') + '" data-go="' + s.k + '">' + esc(s.label) + '</button>'; });
    });
    $('side').innerHTML = h;
  }
  function renderHeader() {
    var s = scr(S.route) || scr('home');
    $('projName').textContent = S.data.master.project.name;
    $('meTag').textContent = S.user.name + ' · ' + roleName(role());
    $('crumb').innerHTML = (s.grp === 'global' ? '전역' : s.grp === 'ws' ? '제안 워크스페이스' : 'ProWin 관리') + ' · <b>' + esc(s.label) + '</b>';
    $('title').textContent = s.label;
    var inf = INFO[s.board ? 'board' : s.k] || {};
    $('desc').textContent = inf.req || '';
    var ch = changedFiles().length;
    $('dataState').textContent = (ch ? '저장 전 변경 ' + ch + '개 파일 · ' : '') + (anyDraft() ? '임시저장본 사용 중' : '원본 데이터 사용 중');
  }
  function renderContent() {
    var k = S.route;
    if (!scr(k)) { k = S.route = 'home'; }
    var s = scr(k), h;
    if (!canView(k)) h = '<div class="deny"><div style="font-size:30px">⛔</div><h3>접근 권한이 없습니다</h3><p>현재 역할(' + esc(roleName(role())) + ')은 이 화면을 볼 수 없습니다.</p></div>';
    else if (k === 'proposals') h = viewProposals();
    else if (k === 'home') h = viewHome();
    else if (k === 'comm') h = viewPosts('comm');
    else if (k === 'schedule') h = viewSchedule();
    else if (k === 'rfp') h = viewRfp();
    else if (k === 'toc') h = viewToc();
    else if (k === 'review') h = viewReview();
    else if (k === 'versions') h = viewVersions();
    else if (k === 'matrix') h = viewMatrix();
    else if (k === 'workspace') h = viewWorkspace();
    else if (k === 'wsperm') h = viewWsperm();
    else if (k === 'expense') h = viewExpense();
    else if (k === 'effort') h = viewEffort();
    else if (k === 'assets') h = viewAssets();
    else if (k === 'sysperm') h = viewSysperm();
    else if (k === 'guide') h = viewGuide();
    else if (k === 'history') h = viewHistory();
    else if (s.board) h = viewPosts(k);
    $('content').innerHTML = h;
  }
  function renderAll() { renderNav(); renderHeader(); renderContent(); }

  /* ---------- 저장 / 내보내기 / 원본 복원 ---------- */
  function changedFiles() {
    return Object.keys(FILES).filter(function (k) { return JSON.stringify(S.data[k]) !== JSON.stringify(S.base[k]); });
  }
  function anyDraft() { return Object.keys(S.draft).some(function (k) { return S.draft[k]; }); }
  function save() {
    var ch = changedFiles();
    if (!ch.length) { toast('변경된 내용이 없습니다'); return; }
    var ok = confirm('변경 내용을 저장할까요?\n\n대상 파일: ' + ch.join(', ') + '\n\n이 브라우저에 반영됩니다. 기본 데이터 파일에 반영하려면 내보내기를 이용하세요.');
    if (!ok) return;
    try {
      ch.forEach(function (k) { localStorage.setItem(KEY + k, JSON.stringify(S.data[k])); S.draft[k] = true; });
    } catch (e) { toast('브라우저 저장소에 저장하지 못했습니다. 내보내기를 이용하세요.', true); return; }
    S.base = snap();
    renderAll();
    toast('저장되었습니다');
  }
  function exportAll() {
    var list = changedFiles().length ? changedFiles() : Object.keys(FILES);
    list.forEach(function (k, i) {
      setTimeout(function () {
        var blob = new Blob([JSON.stringify(S.data[k], null, 2)], { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = k + '.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      }, i * 400);
    });
    toast(list.length + '개 파일을 내보냅니다 · data 폴더에 덮어쓰면 기본 데이터가 바뀝니다');
  }
  function restoreOriginal() {
    if (!confirm('임시저장본을 모두 버리고 data 폴더의 원본으로 되돌릴까요?')) return;
    Object.keys(FILES).forEach(function (k) { try { localStorage.removeItem(KEY + k); } catch (e) { /* 무시 */ } S.draft[k] = false; });
    loadAll(true).then(function () { renderAll(); toast('원본으로 복원했습니다'); });
  }

  /* ---------- 데이터 로드 / 로그인 ---------- */
  function fetchJSON(path) {
    return fetch(path, { cache: 'no-store' }).then(function (r) { if (!r.ok) throw new Error(path + ' (' + r.status + ')'); return r.json(); });
  }
  function loadOne(k, forceOriginal) {
    if (!forceOriginal) {
      try { var raw = localStorage.getItem(KEY + k); if (raw) { S.draft[k] = true; return Promise.resolve(JSON.parse(raw)); } } catch (e) { /* 원본 사용 */ }
    }
    S.draft[k] = false;
    return fetchJSON(FILES[k]);
  }
  function loadAll(forceOriginal) {
    var keys = Object.keys(FILES);
    return Promise.all(keys.map(function (k) { return loadOne(k, forceOriginal); })).then(function (res) {
      keys.forEach(function (k, i) { S.data[k] = res[i]; });
      S.base = snap();
    });
  }
  function apiPath(p) { return '/api/projects/' + PROJECT_ID + p; }
  function loadRfp() { return api('GET', apiPath('/rfp')).then(function (d) { S.data.rfp = d; }); }
  function loadToc() { return api('GET', apiPath('/toc')).then(function (d) { S.data.toc = d; }); }
  function loadReview() { return api('GET', apiPath('/review')).then(function (d) { S.data.review = d; }); }
  function loadVersions() { return api('GET', apiPath('/versions')).then(function (d) { S.data.versions = d; }); }
  function loadBackend() { return Promise.all([loadRfp(), loadToc(), loadReview(), loadVersions()]); }
  function memberById(id) { return S.data.master.members.filter(function (m) { return m.id === id && !m.deleted; })[0]; }
  function showLogin() {
    $('login').style.display = 'flex';
    $('app').style.display = 'none';
    $('loginProj').textContent = S.data.master.project.name;
  }
  function showApp() {
    $('login').style.display = 'none';
    $('app').style.display = 'block';
    route();
  }
  function doLogin() {
    var id = $('loginId').value.trim(), pw = $('loginPw').value;
    var m = S.data.master.members.filter(function (x) { return x.id === id && x.pw === pw && !x.deleted; })[0];
    if (!m) { toast('아이디 또는 비밀번호가 맞지 않습니다', true); return; }
    S.user = m;
    sessionStorage.setItem(SESSION, m.id);
    logH('로그인', '로그인', m.name + ' · ' + roleName(m.role));
    $('loginPw').value = '';
    showApp();
  }
  function logout() {
    sessionStorage.removeItem(SESSION);
    S.user = null;
    showLogin();
  }
  var QUICK_ROLE = { writer: 'writer', pm: 'pm', sales: 'sales', admin: 'admin' };
  function quickFill(r) {
    var m = S.data.master.members.filter(function (x) { return x.role === QUICK_ROLE[r] && !x.deleted; })[0];
    if (!m) return;
    $('loginId').value = m.id;
    $('loginPw').value = m.pw;
    $('btnLogin').focus();
  }

  /* ---------- 이벤트 ---------- */
  function route() {
    if (!S.user) return;
    var h = (location.hash || '').replace('#', '');
    S.route = scr(h) ? h : 'home';
    renderAll();
  }

  function bind() {
    $('btnLogin').addEventListener('click', doLogin);
    $('loginPw').addEventListener('keydown', function (e) { if (e.key === 'Enter') doLogin(); });
    document.querySelectorAll('[data-quick]').forEach(function (b) {
      b.addEventListener('click', function () { quickFill(b.getAttribute('data-quick')); });
    });
    $('btnLogout').addEventListener('click', logout);
    $('btnSave').addEventListener('click', save);
    $('btnExport').addEventListener('click', exportAll);
    $('btnRestore').addEventListener('click', restoreOriginal);
    $('btnInfo').addEventListener('click', openInfo);
    window.addEventListener('hashchange', route);

    $('side').addEventListener('click', function (e) {
      var b = e.target.closest('[data-go]');
      if (b) location.hash = '#' + b.getAttribute('data-go');
    });

    $('content').addEventListener('click', function (e) {
      var t = e.target, x, id, p;
      if ((x = t.closest('[data-go-home]')) && !t.closest('button')) { location.hash = '#home'; return; }
      if ((x = t.closest('[data-req]'))) { S.rfpReq = x.getAttribute('data-req'); renderContent(); return; }
      if ((x = t.closest('[data-node]'))) { S.rv = x.getAttribute('data-node'); renderContent(); return; }
      if ((x = t.closest('[data-commit]'))) { S.commit = x.getAttribute('data-commit'); renderContent(); return; }
      if ((x = t.closest('[data-exp-tab]'))) { S.expTab = x.getAttribute('data-exp-tab'); renderContent(); return; }
      if ((x = t.closest('[data-cal]'))) {
        var cb = x.getAttribute('data-cal'), c = S.cal;
        if (cb === 'prev') { c.m--; if (c.m < 0) { c.m = 11; c.y--; } }
        if (cb === 'next') { c.m++; if (c.m > 11) { c.m = 0; c.y++; } }
        if (cb === 'today') { var n = new Date(); c.y = n.getFullYear(); c.m = n.getMonth(); }
        renderContent();
        return;
      }
      if ((x = t.closest('[data-ev]'))) { openSched(x.getAttribute('data-ev')); return; }
      if (t.closest('[data-proj-edit]')) {
        var pr = S.data.master.project;
        openForm('제안 기본정보 수정', projectFields(), Object.assign({}, pr, { pm: pr.team.pm, biz: pr.team.biz, sales: pr.team.sales }), function (v) {
          Object.assign(pr, { name: v.name, client: v.client, summary: v.summary, start: v.start, deadline: v.deadline, presentation: v.presentation, team: { pm: v.pm, biz: v.biz, sales: v.sales } });
          logH('수정', '제안 기본정보', v.name);
        });
        return;
      }
      if (t.closest('[data-prop-add]')) {
        openForm('새 제안', [{ k: 'name', label: '제안명', req: true }, { k: 'scope', label: '구성' }, { k: 'start', label: '시작일', type: 'date' }, { k: 'end', label: '마감일', type: 'date' }],
          {}, function (v) {
            var list = S.data.proposals.items;
            list.push({ id: nextNum('P', list), status: '준비중', cls: 'prep', name: v.name, scope: v.scope, start: v.start, end: v.end, pm: '', biz: '', sales: '—', pct: 0 });
            logH('추가', '제안 ' + v.name, '');
          });
        return;
      }
      if ((x = t.closest('[data-prop-del]'))) {
        id = x.getAttribute('data-prop-del');
        var pitem = S.data.proposals.items.filter(function (y) { return y.id === id; })[0];
        askDelete('제안 ' + pitem.name, '제안 ' + id, function () { markDeleted(pitem, S.lastReason); });
        return;
      }
      if (t.closest('[data-sc-add]')) {
        var today = todayISO();
        openForm('일정 추가', schedFields(), { start: today, end: today, color: 'c-wr', owner: S.user.name, status: '예정' }, function (v) {
          S.data.schedule.items.push(Object.assign({ id: nextNum('SC', S.data.schedule.items) }, v));
          logH('추가', '일정', v.title);
        }, null, schedValidate);
        return;
      }
      if ((x = t.closest('[data-sc-edit]'))) { openSched(x.getAttribute('data-sc-edit')); return; }
      if ((x = t.closest('[data-sc-del]'))) {
        id = x.getAttribute('data-sc-del');
        var sit = S.data.schedule.items.filter(function (y) { return y.id === id; })[0];
        askDelete('일정 ' + sit.title, '일정 ' + id, function () { markDeleted(sit, S.lastReason); });
        return;
      }
      if ((x = t.closest('[data-post-add]'))) {
        var kk = x.getAttribute('data-post-add');
        openForm('새 글', postFields(kk), boardOf(kk) && boardOf(kk).kind === 'qna' ? { status: '답변대기' } : {}, function (v) {
          var list = postsOf(kk), pref = kk === 'comm' ? 'CM' : boardOf(kk) && boardOf(kk).kind === 'qna' ? 'QA' : 'RF';
          list.push(Object.assign({ id: nextNum(pref, list), by: S.user.name, date: todayISO() }, v));
          logH('추가', kk === 'comm' ? '커뮤니케이션' : boardOf(kk).name, v.title);
        });
        return;
      }
      if ((x = t.closest('[data-post-edit]'))) {
        p = x.getAttribute('data-post-edit').split('|');
        var pp = postsOf(p[0]).filter(function (y) { return y.id === p[1]; })[0];
        if (!pp || !canEditPost(p[0], pp)) { toast('이 글은 수정할 수 없습니다', true); return; }
        openForm('글 수정', postFields(p[0]), pp, function (v) { Object.assign(pp, v); logH('수정', p[0] === 'comm' ? '커뮤니케이션' : boardOf(p[0]).name, v.title); },
          function () { askDelete('글 ' + pp.title, p[1], function () { markDeleted(pp, S.lastReason); }); });
        return;
      }
      if ((x = t.closest('[data-post-del]'))) {
        p = x.getAttribute('data-post-del').split('|');
        var dp = postsOf(p[0]).filter(function (y) { return y.id === p[1]; })[0];
        if (!dp || !canEditPost(p[0], dp)) { toast('이 글은 삭제할 수 없습니다', true); return; }
        askDelete('글 ' + dp.title, p[1], function () { markDeleted(dp, S.lastReason); });
        return;
      }
      if (t.closest('[data-req-add]')) {
        openForm('요구사항 추가', reqFields(), {}, function (v) {
          return api('POST', apiPath('/rfp/requirements'), { code: v.code, title: v.title, description: v.description, who: S.user.name }).then(function () {
            logH('추가', '요구사항 ' + v.code, v.title);
            return loadRfp();
          });
        }, null, null, '추가했습니다');
        return;
      }
      if ((x = t.closest('[data-req-del]'))) {
        id = x.getAttribute('data-req-del');
        var rq = (S.data.rfp.requirements || []).filter(function (y) { return y.id === id; })[0];
        askDelete('요구사항 ' + rq.title, '요구사항 ' + id, function (reason) {
          return api('DELETE', apiPath('/rfp/requirements/' + encodeURIComponent(id)), { who: S.user.name, reason: reason }).then(loadRfp);
        }, '삭제했습니다');
        return;
      }
      if (t.closest('[data-toc-add]')) {
        openForm('목차 추가', tocFields(), { level: '2', status: 'todo' }, function (v) {
          return api('POST', apiPath('/toc/rows'), { level: parseInt(v.level, 10), title: v.title, owner: v.owner || '', pages: v.pages || '', status: v.status || 'todo', who: S.user.name }).then(function () {
            logH('추가', '목차', v.title);
            return Promise.all([loadToc(), loadReview()]);
          });
        }, null, null, '추가했습니다');
        return;
      }
      if ((x = t.closest('[data-toc-edit]'))) {
        id = x.getAttribute('data-toc-edit');
        var tr = S.data.toc.rows.filter(function (y) { return y.id === id; })[0];
        openForm('목차 수정', tocFields(), Object.assign({}, tr, { level: String(tr.level) }), function (v) {
          return api('PUT', apiPath('/toc/rows/' + encodeURIComponent(id)), { level: parseInt(v.level, 10), title: v.title, owner: v.owner, pages: v.pages, status: v.status, who: S.user.name }).then(function () {
            logH('수정', '목차 ' + id, v.title);
            return Promise.all([loadToc(), loadReview()]);
          });
        }, null, null, '수정했습니다');
        return;
      }
      if ((x = t.closest('[data-toc-del]'))) {
        id = x.getAttribute('data-toc-del');
        var tr2 = S.data.toc.rows.filter(function (y) { return y.id === id; })[0];
        askDelete('목차 ' + tr2.title, '목차 ' + id, function (reason) {
          return api('DELETE', apiPath('/toc/rows/' + encodeURIComponent(id)), { who: S.user.name, reason: reason }).then(function () {
            return Promise.all([loadToc(), loadReview()]);
          });
        }, '삭제했습니다');
        return;
      }
      if ((x = t.closest('[data-review-edit]'))) {
        id = x.getAttribute('data-review-edit');
        var rn = reviewNodeOf(id) || {};
        openForm('검토 내용 수정', reviewFields(), { memo: rn.memo, titleDetail: rn.titleDetail, flowSteps: joinLines(rn.flowSteps), bullets: joinLines(rn.bullets) }, function (v) {
          return api('PUT', apiPath('/review/nodes/' + encodeURIComponent(id)), {
            memo: v.memo, titleDetail: v.titleDetail, flowSteps: splitLines(v.flowSteps), bullets: splitLines(v.bullets), who: S.user.name
          }).then(function () {
            logH('수정', '제안서 검토 ' + id, v.titleDetail || v.memo);
            return loadReview();
          });
        }, null, null, '수정했습니다');
        return;
      }
      if ((x = t.closest('[data-review-present]'))) {
        id = x.getAttribute('data-review-present');
        var curNode = reviewNodeOf(id) || {};
        api('PUT', apiPath('/review/nodes/' + encodeURIComponent(id) + '/presentation'), { assigned: !curNode.presentationAssigned, who: S.user.name }).then(function () {
          logH('수정', '설명회 지정 ' + id, !curNode.presentationAssigned ? '지정' : '해제');
          return loadReview();
        }).then(renderAll).catch(function (err) { toast(err.message || '처리하지 못했습니다', true); });
        return;
      }
      if ((x = t.closest('[data-review-comment]'))) {
        id = x.getAttribute('data-review-comment');
        openForm('코멘트 추가', [{ k: 'body', label: '내용', type: 'textarea', req: true }], {}, function (v) {
          return api('POST', apiPath('/review/nodes/' + encodeURIComponent(id) + '/comments'), { author: S.user.name, body: v.body }).then(function () {
            logH('추가', '리뷰 코멘트 ' + id, v.body);
            return loadReview();
          });
        }, null, null, '코멘트를 등록했습니다');
        return;
      }
      if (t.closest('[data-upload]')) {
        $('versionFile').click();
        return;
      }
      if (t.closest('[data-merge]')) {
        openForm('합본(스냅샷 생성)', [{ k: 'message', label: '커밋 메시지', req: true }], { message: '합본 스냅샷 생성' }, function (v) {
          return api('POST', apiPath('/versions/snapshot'), { branch: 'main', message: v.message, who: S.user.name }).then(function (c) {
            logH('추가', '합본', c.tag || c.commitHash);
            S.modal.savedMsg = '합본 스냅샷을 만들었습니다 (슬라이드 ' + c.slideCount + '장 병합)';
            return loadVersions();
          });
        }, null, null, '합본 스냅샷을 만들었습니다');
        return;
      }
      if (t.closest('[data-ws-add]')) {
        openForm('게시판 추가', [{ k: 'name', label: '게시판명', req: true }, { k: 'desc', label: '설명' },
          { k: 'kind', label: '유형', type: 'select', opts: [{ v: 'free', l: '자유 글' }, { v: 'qna', l: 'Q&A (답변 상태)' }, { v: 'ref', l: '자료 (링크)' }] }],
          { kind: 'free' }, function (v) {
            var bid = S.data.boards.nextId++;
            S.data.boards.boards.push({ id: bid, name: v.name, desc: v.desc, kind: v.kind, posts: [] });
            S.data.master.perms['board-' + bid] = { writer: 'edit', pm: 'edit', sales: 'view' };
            logH('추가', '게시판 ' + v.name, '');
          });
        return;
      }
      if ((x = t.closest('[data-ws-edit]'))) {
        var bid2 = parseInt(x.getAttribute('data-ws-edit'), 10), bd = boardOf('board-' + bid2);
        openForm('게시판 수정', [{ k: 'name', label: '게시판명', req: true }, { k: 'desc', label: '설명' }], bd, function (v) {
          bd.name = v.name; bd.desc = v.desc; logH('수정', '게시판 ' + v.name, '');
        });
        return;
      }
      if ((x = t.closest('[data-ws-del]'))) {
        var did = parseInt(x.getAttribute('data-ws-del'), 10), dbd = boardOf('board-' + did);
        askDelete('게시판 ' + dbd.name, '게시판 ' + dbd.name, function () { markDeleted(dbd, S.lastReason); });
        return;
      }
      if (t.closest('[data-mem-add]')) {
        openForm('멤버 추가', [{ k: 'name', label: '이름', req: true }, { k: 'id', label: '아이디', req: true }, { k: 'pw', label: '비밀번호', req: true },
          { k: 'title', label: '직함' }, { k: 'role', label: '역할', type: 'select', opts: Object.keys(S.data.master.roles).map(function (r) { return { v: r, l: S.data.master.roles[r] }; }) }],
          { role: 'writer' }, function (v) {
            if (S.data.master.members.some(function (m) { return m.id === v.id; })) { toast('이미 있는 아이디입니다', true); return; }
            S.data.master.members.push(v); logH('추가', '멤버 ' + v.name, roleName(v.role));
          });
        return;
      }
      if ((x = t.closest('[data-mem-del]'))) {
        var mi = parseInt(x.getAttribute('data-mem-del'), 10), mm = S.data.master.members[mi];
        askDelete('멤버 ' + mm.name, '멤버 ' + mm.name, function () { markDeleted(mm, S.lastReason); });
        return;
      }
      if ((x = t.closest('[data-sw]'))) {
        var si = parseInt(x.getAttribute('data-sw'), 10), su = S.data.master.sysUsers[si];
        su.on = !su.on; logH('수정', '시스템 권한 ' + su.name, su.on ? '전체 접근 허용' : '전체 접근 해제');
        renderAll();
        return;
      }
      if ((x = t.closest('[data-del]'))) { return; }
    });

    $('content').addEventListener('change', function (e) {
      var t = e.target;
      if (t.id === 'versionFile') {
        var file = t.files && t.files[0];
        if (!file) return;
        var level2Rows = tocLevel2Rows();
        openForm('업로드(커밋)', [
          { k: 'tocRowId', label: '대상 목차', type: 'select', req: true, opts: level2Rows.map(function (r) { return { v: r.id, l: r.title }; }) },
          { k: 'message', label: '커밋 메시지', req: true }
        ], { tocRowId: S.versionSection || (level2Rows[0] && level2Rows[0].id), message: file.name }, function (v) {
          var fd = new FormData();
          fd.append('file', file);
          fd.append('message', v.message);
          fd.append('who', S.user.name);
          fd.append('branch', 'main');
          fd.append('tocRowId', v.tocRowId);
          return apiUpload(apiPath('/versions/commits'), fd).then(function () {
            logH('추가', '커밋', v.message + ' (' + tocTitleOf(v.tocRowId) + ')');
            return Promise.all([loadVersions(), loadToc(), loadReview()]);
          });
        }, null, null, '업로드했습니다. 목차·검토 내용에 자동 반영됐습니다');
        t.value = '';
        return;
      }
      if (t.id === 'versionSectionFilter') {
        S.versionSection = t.value;
        S.commit = null;
        renderContent();
        return;
      }
      if (t.hasAttribute('data-mem-role')) {
        var mem = S.data.master.members[parseInt(t.getAttribute('data-mem-role'), 10)];
        logH('수정', '멤버 ' + mem.name, '역할: ' + roleName(mem.role) + ' → ' + roleName(t.value));
        mem.role = t.value;
        renderAll();
      } else if (t.hasAttribute('data-perm')) {
        var pp = t.getAttribute('data-perm').split('|');
        var entry = S.data.master.perms[pp[0]] || (S.data.master.perms[pp[0]] = {});
        logH('수정', '화면 권한 ' + pp[0], roleName(pp[1]) + ' → ' + LEVEL_LABEL[t.value]);
        entry[pp[1]] = t.value;
        renderAll();
      } else if (t.hasAttribute('data-mx')) {
        var mx = t.getAttribute('data-mx').split('|'), row = S.data.matrix.rows[parseInt(mx[0], 10)];
        row[mx[1]] = t.value;
        logH('수정', '조견표', (row.mid || '') + ' · ' + mx[1] + ' → ' + t.value);
      } else if (t.hasAttribute('data-exp')) {
        var ex = t.getAttribute('data-exp').split('|');
        S.data.expense.tabs[ex[0]].rows[parseInt(ex[1], 10)][parseInt(ex[2], 10)] = t.value;
        logH('수정', '경비 ' + S.data.expense.tabs[ex[0]].label, t.value);
      } else if (t.hasAttribute('data-eff')) {
        var ef = t.getAttribute('data-eff').split('|');
        S.data.effort.rows[parseInt(ef[0], 10)][parseInt(ef[1], 10)] = t.value;
        logH('수정', '수행 공수', t.value);
      }
    });

    $('modal').addEventListener('click', function (e) {
      var t = e.target, M = S.modal;
      if (t === this || t.hasAttribute('data-x')) { closeModal(); return; }
      if (!M) return;
      if (t.hasAttribute('data-del')) { var dfn = M.onDelete; closeModal(); if (dfn) dfn(); renderAll(); return; }
      if (t.hasAttribute('data-save')) {
        var v = {}, ok = true;
        M.fields.forEach(function (f) {
          var el = $('modalBox').querySelector('[data-f="' + f.k + '"]');
          v[f.k] = el ? el.value.trim() : '';
          if (f.req && !v[f.k]) ok = false;
        });
        if (!ok) { toast('필수 항목을 입력하세요', true); return; }
        if (M.validate) { var msg = M.validate(v); if (msg) { toast(msg, true); return; } }
        Promise.resolve().then(function () { return M.onSave(v); }).then(function () {
          closeModal();
          renderAll();
          toast(M.savedMsg || '반영했습니다. 저장 버튼으로 확정하세요');
        }).catch(function (err) { toast(err.message || '처리하지 못했습니다', true); });
      }
    });
  }

  function boot() {
    Promise.all([loadAll(false), loadBackend()]).then(function () {
      var n = new Date();
      S.cal = { y: n.getFullYear(), m: n.getMonth() };
      bind();
      var saved = sessionStorage.getItem(SESSION);
      var m = saved ? memberById(saved) : null;
      if (m) { S.user = m; showApp(); } else { showLogin(); }
    }).catch(function (err) {
      document.body.innerHTML = '<div class="empty" style="padding:40px">데이터를 읽지 못했습니다 (' + esc(err.message) +
        '). 파일을 직접 열지 말고 로컬 서버로 실행하세요: python3 -m http.server 8000 또는 Java 백엔드(8080)를 기동하세요</div>';
    });
  }
  boot();
})();
