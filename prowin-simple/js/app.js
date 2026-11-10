/* ProWin 단순 버전 — 데모의 기본 기능을 옮긴 프로토타입 (DB 없음)
 * 데이터: data/*.json. 편집은 브라우저 임시저장, 저장 시 변경 확인, 내보내기로 파일 교체.
 */
(function () {
  'use strict';

  var FILES = { master: 'data/master.json', schedule: 'data/schedule.json', boards: 'data/boards.json', comm: 'data/comm.json', guide: 'data/guide.json' };
  var FILE_LABEL = { master: '제안 기본정보·권한', schedule: '제안 일정', boards: '게시판·워크스페이스', comm: '커뮤니케이션', guide: '사용 가이드' };
  var KEY = 'prowin-simple-v1:';
  var ROLES = [{ v: 'writer', l: '작성자' }, { v: 'pm', l: 'PM' }, { v: 'sales', l: '영업대표' }];
  var ROLE_NAME = { writer: '작성자', pm: 'PM·사업관리', sales: '영업대표' };
  var COLORS = [{ v: 'c-wr', l: '작성 (초록)' }, { v: 'c-rv', l: '리뷰 (파랑)' }, { v: 'c-mt', l: '마일스톤 (주황)' }, { v: 'c-dl', l: '마감 (빨강)' }, { v: 'c-gy', l: '기타 (회색)' }];
  var SCHED_STATUS = ['예정', '진행중', '완료'];
  var QA_STATUS = ['답변대기', '답변완료'];
  var LEVELS = [{ v: 'none', l: '없음' }, { v: 'view', l: '조회' }, { v: 'edit', l: '편집' }];
  var INFO = {
    home: { req: '제안 개요 + 오늘 할 일(일정 연동) + 지연 항목 가시화', phase: 'Step 1 · 꼭 필요' },
    comm: { req: '제안팀 공지·공유 게시판', phase: 'Step 2 · 컨셉 강화' },
    schedule: { req: '짧은 제안 일정(2~3주)의 다일 일정 등록/수정/삭제, 색상 구분 · PM·사업관리 편집 / 그 외 조회', phase: 'Step 1 · 꼭 필요' },
    board: { req: '워크스페이스 관리에서 추가한 자유 게시판', phase: 'Step 2 · 컨셉 강화' },
    guide: { req: '사이트 사용법 통합 가이드', phase: 'Step 2 · 컨셉 강화' },
    ws: { req: '제안별 자유 게시판(폴더) 추가/수정/삭제', phase: 'Step 2 · 컨셉 강화' },
    wsperm: { req: '제안 단위 멤버·권한 관리(PM/사업관리 전용)', phase: 'Step 1 · 꼭 필요' }
  };

  var S = { role: 'writer', data: {}, base: {}, draft: {}, route: 'home', modal: null, cal: null };

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
  function addDays(iso, n) { var d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return isoOf(d); }
  function daysBetween(a, b) { return Math.round((new Date(b + 'T00:00:00') - new Date(a + 'T00:00:00')) / 86400000); }
  function snap() { return JSON.parse(JSON.stringify(S.data)); }
  function me() { return S.data.master.me[S.role]; }
  function level(k) {
    if (S.role === 'pm') return 'edit';
    var p = S.data.master.perms[k] || {};
    return p[S.role] || 'none';
  }
  function canView(k) {
    var s = scr(k);
    if (s && s.pm) return S.role === 'pm';
    return level(k) !== 'none';
  }
  function canEdit(k) {
    var s = scr(k);
    if (s && s.pm) return S.role === 'pm';
    return level(k) === 'edit';
  }
  function canEditPost(k, p) { return S.role === 'pm' || (canEdit(k) && p.by === me()); }
  function nextId(prefix, list) {
    var max = 0;
    list.forEach(function (x) { var n = parseInt(String(x.id).split('-').pop(), 10); if (n > max) max = n; });
    return prefix + '-' + String(max + 1).padStart(3, '0');
  }
  var timer;
  function toast(msg, err) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.toggle('err', !!err);
    t.classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(function () { t.classList.remove('show'); }, 2400);
  }

  /* ---------- 화면 목록 (게시판은 워크스페이스 관리에 따라 동적) ---------- */
  function screens() {
    var list = [
      { k: 'home', label: '제안서 홈', grp: 'ws' },
      { k: 'comm', label: '커뮤니케이션', grp: 'ws' },
      { k: 'schedule', label: '제안 일정', grp: 'ws' }
    ];
    S.data.boards.boards.forEach(function (b) { list.push({ k: 'board-' + b.id, label: b.name, grp: 'ws', board: b.id }); });
    list.push({ k: 'guide', label: '사용 가이드', grp: 'etc' });
    list.push({ k: 'ws', label: '워크스페이스 관리', grp: 'adm', pm: true });
    list.push({ k: 'wsperm', label: '제안 권한관리', grp: 'adm', pm: true });
    return list;
  }
  function scr(k) { return screens().filter(function (x) { return x.k === k; })[0]; }
  function boardOf(k) {
    var id = parseInt(String(k).replace('board-', ''), 10);
    return S.data.boards.boards.filter(function (b) { return b.id === id; })[0];
  }

  /* ---------- 모달 ---------- */
  function openForm(title, fields, vals, onSave, onDelete, validate) {
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
    h += '</div><div class="modal-input"><div class="row"><span>' +
      (onDelete ? '<button class="btn ghost sm" data-del="1">삭제</button>' : '') +
      '</span><span class="pick-btns"><button class="btn ghost sm" data-x="1">취소</button><button class="btn sm" data-save="1">저장</button></span></div></div>';
    $('modalBox').innerHTML = h;
    S.modal = { fields: fields, onSave: onSave, onDelete: onDelete, validate: validate };
    $('modal').classList.add('open');
    var first = $('modalBox').querySelector('[data-f]');
    if (first) first.focus();
  }
  function openView(title, rows) {
    var h = '<div class="modal-hd"><div><h3>' + esc(title) + '</h3></div><button class="modal-close" data-x="1">✕</button></div><div class="modal-list">' +
      rows.map(function (r) { return '<div class="fld"><span>' + esc(r[0]) + '</span><div style="font-size:14px;white-space:pre-wrap">' + esc(r[1]) + '</div></div>'; }).join('') +
      '</div><div class="modal-input"><div class="row"><span></span><span class="pick-btns"><button class="btn sm" data-x="1">닫기</button></span></div></div>';
    $('modalBox').innerHTML = h;
    S.modal = null;
    $('modal').classList.add('open');
  }
  function closeModal() { S.modal = null; $('modal').classList.remove('open'); }
  function openInfo() {
    var k = S.route, s = scr(k), key = s && s.board ? 'board' : k, info = INFO[key] || { req: '정보 없음', phase: '' };
    openView('화면 정보 · ' + (s ? s.label : ''), [['요구사항', info.req], ['단계', info.phase]]);
  }

  /* ---------- 화면: 제안서 홈 ---------- */
  function progress() {
    var items = S.data.schedule.items, t = todayISO();
    var done = items.filter(function (x) { return x.status === '완료'; }).length;
    var late = items.filter(function (x) { return x.end < t && x.status !== '완료'; }).length;
    var doing = items.filter(function (x) { return x.status === '진행중'; }).length;
    var todo = items.length - done - doing;
    return { total: items.length, done: done, doing: doing, todo: todo, late: late, pct: items.length ? Math.round(done / items.length * 100) : 0 };
  }
  function activity() {
    var a = [];
    S.data.schedule.items.forEach(function (x) { a.push({ d: x.start, t: '일정 · ' + x.title + ' (' + x.status + ')', by: x.owner }); });
    S.data.comm.posts.forEach(function (p) { a.push({ d: p.date, t: '커뮤니케이션 · ' + p.title, by: p.by }); });
    S.data.boards.boards.forEach(function (b) {
      b.posts.forEach(function (p) { a.push({ d: p.date, t: b.name + ' · ' + p.title, by: p.by }); });
    });
    return a.sort(function (x, y) { return x.d < y.d ? 1 : -1; }).slice(0, 6);
  }
  function listSched(list, empty) {
    if (!list.length) return '<div class="empty">' + empty + '</div>';
    return '<table><tbody>' + list.map(function (x) {
      var late = x.end < todayISO() && x.status !== '완료';
      return '<tr class="' + (late ? 'late' : '') + '"><td>' + esc(x.title) + '</td><td class="muted">' + esc(x.start) + ' ~ ' + esc(x.end) +
        '</td><td class="muted">' + esc(x.owner) + '</td><td><span class="st ' + (late ? 'late' : x.status === '진행중' ? 'doing' : 'todo') + '">' +
        (late ? '지연' : esc(x.status)) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
  }
  function viewHome() {
    var m = S.data.master, p = m.project, t = todayISO(), pg = progress();
    var dday = daysBetween(t, p.deadline);
    var today = S.data.schedule.items.filter(function (x) { return x.start <= t && t <= x.end && x.status !== '완료'; });
    var late = S.data.schedule.items.filter(function (x) { return x.end < t && x.status !== '완료'; });
    var h = '<div class="grid2"><div>';
    h += '<div class="card"><h3>' + esc(p.name) + (canEdit('home') ? '<button class="btn ghost sm" data-proj-edit="1">수정</button>' : '') + '</h3>' +
      '<div class="kv"><div class="k">발주처</div><div>' + esc(p.client) + '</div>' +
      '<div class="k">제안 기간</div><div>' + esc(p.start) + ' ~ ' + esc(p.deadline) + ' · ' + (dday >= 0 ? '마감 D-' + dday : '마감 지남') + '</div>' +
      '<div class="k">PM</div><div>' + esc(p.team.pm) + '</div>' +
      '<div class="k">사업관리</div><div>' + esc(p.team.biz) + '</div>' +
      '<div class="k">영업대표</div><div>' + esc(p.team.sales) + '</div>' +
      '<div class="k">진척</div><div><span class="pbar"><span style="width:' + pg.pct + '%"></span></span> ' + pg.pct + '% (완료 ' + pg.done + ' · 진행 ' + pg.doing + ' · 예정 ' + pg.todo + ' · 지연 ' + pg.late + ')</div>' +
      '<div class="k">개요</div><div>' + esc(p.summary) + '</div></div></div>';
    h += '<div class="card"><h3>최근 업데이트</h3>' + activity().map(function (a) {
      return '<div class="act"><span>' + esc(a.t) + '</span><span class="d">' + esc(a.by) + ' · ' + esc(a.d) + '</span></div>';
    }).join('') + '</div>';
    h += '</div><div>';
    h += '<div class="card"><h3>오늘 할 일 <span class="muted">' + esc(t) + '</span></h3>' + listSched(today, '오늘 할 일이 없습니다.') + '</div>';
    h += '<div class="card"><h3>⚠ 지연 항목 <span class="muted">마감 지남 · 미완료</span></h3>' + listSched(late, '지연 항목이 없습니다.') + '</div>';
    h += '</div></div>';
    return h;
  }
  function projectFields() {
    var mem = S.data.master.members.map(function (x) { return x.name; });
    return [
      { k: 'name', label: '사업명', req: true }, { k: 'client', label: '발주처', req: true },
      { k: 'summary', label: '개요', type: 'textarea' },
      { k: 'start', label: '제안 시작', type: 'date' }, { k: 'deadline', label: '제안 마감', type: 'date' },
      { k: 'presentation', label: '제안 발표', type: 'date' },
      { k: 'pm', label: 'PM', type: 'select', opts: mem }, { k: 'biz', label: '사업관리', type: 'select', opts: mem },
      { k: 'sales', label: '영업대표', type: 'select', opts: mem }
    ];
  }

  /* ---------- 화면: 커뮤니케이션 / 게시판 (공통 글 목록) ---------- */
  function postsOf(k) { return k === 'comm' ? S.data.comm.posts : boardOf(k).posts; }
  function postFields(k) {
    var f = [{ k: 'title', label: '제목', req: true }, { k: 'body', label: '내용', type: 'textarea' }];
    if (k === 'comm') f.push({ k: 'att', label: '첨부 파일명' });
    if (k !== 'comm' && boardOf(k) && boardOf(k).kind === 'qna') {
      f.push({ k: 'status', label: '상태', type: 'select', opts: QA_STATUS });
      f.push({ k: 'answer', label: '답변', type: 'textarea' });
    }
    if (k !== 'comm' && boardOf(k) && boardOf(k).kind === 'ref') f.push({ k: 'link', label: '자료 위치 (파일명·경로)' });
    return f;
  }
  function viewPosts(k, title) {
    var list = postsOf(k).slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
    var b = k === 'comm' ? null : boardOf(k);
    var h = canEdit(k) ? '<div style="margin-bottom:12px"><button class="btn sm" data-post-add="' + k + '">＋ 새 글</button></div>' : '';
    if (!list.length) h += '<div class="card"><div class="empty">글이 없습니다.</div></div>';
    h += '<div class="card">';
    list.forEach(function (p) {
      var can = canEditPost(k, p);
      h += '<div class="post"><div class="pt">' + esc(p.title) + '</div><div class="pm">' + esc(p.by) + ' · ' + esc(p.date) + '</div>' +
        '<div class="pb">' + esc(p.body) + '</div>';
      if (p.att) h += '<span class="att">PPT ' + esc(p.att) + '</span>';
      if (b && b.kind === 'qna') {
        h += '<div style="margin-top:8px"><span class="st ' + (p.status === '답변완료' ? 'done' : 'wait') + '">' + esc(p.status || '답변대기') + '</span>' +
          (p.answer ? '<div class="pb" style="margin-top:6px">↳ 답변: ' + esc(p.answer) + '</div>' : '') + '</div>';
      }
      if (b && b.kind === 'ref' && p.link) h += '<span class="att">📎 ' + esc(p.link) + '</span>';
      if (can) {
        h += '<div style="margin-top:8px"><button class="btn ghost sm" data-post-edit="' + k + '|' + esc(p.id) + '">수정</button> ' +
          '<button class="btn ghost sm" data-post-del="' + k + '|' + esc(p.id) + '">삭제</button></div>';
      }
      h += '</div>';
    });
    return h + '</div>';
  }

  /* ---------- 화면: 제안 일정 (달력 + 목록) ---------- */
  function monthCells(y, m) {
    var first = new Date(y, m, 1), off = first.getDay(), days = new Date(y, m + 1, 0).getDate();
    var total = Math.ceil((off + days) / 7) * 7, cells = [];
    for (var i = 0; i < total; i++) {
      var d = new Date(y, m, 1 - off + i);
      cells.push({ iso: isoOf(d), inMonth: d.getMonth() === m, num: d.getDate() });
    }
    return cells;
  }
  function calHTML() {
    var c = S.cal, cells = monthCells(c.y, c.m), t = todayISO(), items = S.data.schedule.items, h = '';
    var weeks = cells.length / 7;
    for (var w = 0; w < weeks; w++) {
      var wk = cells.slice(w * 7, w * 7 + 7), ws = wk[0].iso, we = wk[6].iso;
      var segs = items.filter(function (x) { return x.end >= ws && x.start <= we; }).map(function (x) {
        var s = x.start > ws ? x.start : ws, e = x.end < we ? x.end : we;
        var c1 = wk.findIndex(function (q) { return q.iso === s; }), c2 = wk.findIndex(function (q) { return q.iso === e; });
        return { it: x, c1: c1, c2: c2 };
      }).sort(function (a, b) { return a.c1 - b.c1 || b.c2 - a.c2; });
      var lanes = [];
      segs.forEach(function (sg) {
        var ln = 0;
        while (lanes[ln] !== undefined && lanes[ln] >= sg.c1) ln++;
        lanes[ln] = sg.c2; sg.lane = ln;
      });
      var minH = 30 + lanes.length * 22 + 6;
      h += '<div class="week" style="min-height:' + minH + 'px">' +
        wk.map(function (q) {
          return '<div class="day' + (q.inMonth ? '' : ' out') + '"' + (q.iso === t ? ' style="background:var(--accent-bg)"' : '') + '><span class="n' + (q.iso === t ? '' : '') + '">' + q.num + '</span></div>';
        }).join('') +
        segs.map(function (sg) {
          return '<div class="bar ' + esc(sg.it.color) + '" data-ev="' + esc(sg.it.id) + '" title="' + esc(sg.it.title) + ' (' + esc(sg.it.start) + ' ~ ' + esc(sg.it.end) + ')" ' +
            'style="left:calc(' + (sg.c1 / 7 * 100) + '% + 3px);width:calc(' + ((sg.c2 - sg.c1 + 1) / 7 * 100) + '% - 6px);top:' + (28 + sg.lane * 22) + 'px">' + esc(sg.it.title) + '</div>';
        }).join('') + '</div>';
    }
    var head = '<div class="cal-head">' + ['일', '월', '화', '수', '목', '금', '토'].map(function (d) { return '<div>' + d + '</div>'; }).join('') + '</div>';
    return '<div class="cal-bar"><button class="btn ghost sm" data-cal="prev">‹</button><span class="ttl">' + c.y + '년 ' + (c.m + 1) + '월</span>' +
      '<button class="btn ghost sm" data-cal="next">›</button><button class="btn ghost sm" data-cal="today">오늘</button></div>' +
      head + h +
      '<div class="legend"><span class="c-wr">작성</span><span class="c-rv">리뷰</span><span class="c-mt">마일스톤</span><span class="c-dl">마감</span><span class="c-gy">기타</span></div>';
  }
  function schedFields() {
    var mem = S.data.master.members.map(function (x) { return x.name; });
    return [
      { k: 'title', label: '제목', req: true },
      { k: 'start', label: '시작일', type: 'date', req: true },
      { k: 'end', label: '종료일', type: 'date', req: true },
      { k: 'color', label: '색상', type: 'select', opts: COLORS },
      { k: 'owner', label: '담당', type: 'select', opts: mem },
      { k: 'status', label: '상태', type: 'select', opts: SCHED_STATUS }
    ];
  }
  function schedValidate(v) { return v.end < v.start ? '종료일이 시작일보다 빠릅니다' : null; }
  function openSched(id) {
    var it = S.data.schedule.items.filter(function (x) { return x.id === id; })[0];
    if (!it) return;
    if (!canEdit('schedule')) {
      openView('일정 조회', [['제목', it.title], ['기간', it.start + ' ~ ' + it.end], ['담당', it.owner], ['상태', it.status]]);
      return;
    }
    openForm('일정 수정', schedFields(), it, function (v) { Object.assign(it, v); }, function () {
      S.data.schedule.items = S.data.schedule.items.filter(function (x) { return x.id !== id; });
    }, schedValidate);
  }
  function viewSchedule() {
    var c = S.cal || (S.cal = { y: new Date().getFullYear(), m: new Date().getMonth() });
    var can = canEdit('schedule');
    var h = '<div class="card" style="padding:16px">' + (can ? '<div style="margin-bottom:12px"><button class="btn sm" data-sc-add="1">＋ 일정 추가</button> <span class="muted">일정 막대를 누르면 수정할 수 있습니다</span></div>' : '<div class="muted" style="margin-bottom:10px">조회 전용 · 일정 편집은 PM·사업관리만 가능합니다</div>') + calHTML() + '</div>';
    var items = S.data.schedule.items.slice().sort(function (a, b) { return a.start < b.start ? -1 : 1; }), t = todayISO();
    h += '<div class="card"><h3>일정 목록</h3><table><thead><tr><th>제목</th><th>시작</th><th>종료</th><th>색상</th><th>담당</th><th>상태</th>' + (can ? '<th></th>' : '') + '</tr></thead><tbody>';
    if (!items.length) h += '<tr><td colspan="7" class="empty">등록된 일정이 없습니다.</td></tr>';
    items.forEach(function (x) {
      var late = x.end < t && x.status !== '완료';
      h += '<tr class="' + (late ? 'late' : '') + '"><td>' + esc(x.title) + '</td><td>' + esc(x.start) + '</td><td>' + esc(x.end) + '</td>' +
        '<td><span class="' + esc(x.color) + '" style="display:inline-block;width:12px;height:12px;border-radius:3px"></span></td>' +
        '<td>' + esc(x.owner) + '</td><td><span class="st ' + (late ? 'late' : x.status === '완료' ? 'done' : x.status === '진행중' ? 'doing' : 'todo') + '">' + (late ? '지연' : esc(x.status)) + '</span></td>' +
        (can ? '<td><button class="btn ghost sm" data-sc-edit="' + esc(x.id) + '">수정</button> <button class="btn ghost sm" data-sc-del="' + esc(x.id) + '">삭제</button></td>' : '') + '</tr>';
    });
    return h + '</tbody></table></div>';
  }

  /* ---------- 화면: 워크스페이스 관리 (게시판 추가·수정·삭제, PM 전용) ---------- */
  function viewWs() {
    var h = '<div style="margin-bottom:12px"><button class="btn sm" data-ws-add="1">＋ 게시판 추가</button></div>';
    h += '<table><thead><tr><th>게시판</th><th>설명</th><th>글 수</th><th>유형</th><th></th></tr></thead><tbody>';
    S.data.boards.boards.forEach(function (b) {
      var kindLabel = b.kind === 'qna' ? 'Q&A (상태)' : b.kind === 'ref' ? '자료 (링크)' : '자유 글';
      h += '<tr><td>' + esc(b.name) + '</td><td class="muted">' + esc(b.desc) + '</td><td>' + b.posts.length + '</td><td class="muted">' + kindLabel + '</td>' +
        '<td><button class="btn ghost sm" data-ws-edit="' + b.id + '">수정</button> <button class="btn ghost sm" data-ws-del="' + b.id + '">삭제</button></td></tr>';
    });
    return h + '</tbody></table><p class="muted" style="margin-top:10px">게시판을 추가하면 좌측 메뉴 "제안 워크스페이스"에 바로 나타납니다. 새 게시판은 작성자가 글을 쓸 수 있고 영업대표는 조회만 합니다.</p>';
  }

  /* ---------- 화면: 사용 가이드 ---------- */
  function viewGuide() {
    var g = S.data.guide, h = '<div style="max-width:760px"><div class="rule">📌 <b>핵심 규칙</b> — ' + esc(g.rule) + '</div>';
    g.sections.forEach(function (s, i) {
      h += '<div class="guide-sec"><h4><span class="gnum">' + (i + 1) + '</span>' + esc(s.t) + '</h4><p>' + esc(s.b) + '</p></div>';
    });
    return h + '</div>';
  }

  /* ---------- 화면: 제안 권한관리 (PM 전용) ---------- */
  function viewWsperm() {
    var m = S.data.master;
    var h = '<div style="display:grid;grid-template-columns:320px 1fr;gap:16px">';
    h += '<div class="card"><h3>멤버 <button class="btn sm" data-mem-add="1">＋ 추가</button></h3>';
    h += '<table><tbody>';
    m.members.forEach(function (x, i) {
      h += '<tr><td><b>' + esc(x.name) + '</b><div class="muted">' + esc(x.title) + '</div></td><td>' +
        '<select class="perm-sel" data-mem-role="' + i + '">' + ROLES.map(function (r) {
          return '<option value="' + r.v + '"' + (x.role === r.v ? ' selected' : '') + '>' + r.l + '</option>';
        }).join('') + '</select></td><td>' +
        (x.name === S.data.master.me.writer || x.name === S.data.master.me.pm ? '' : '<button class="btn ghost sm" data-mem-del="' + i + '">제외</button>') + '</td></tr>';
    });
    h += '</tbody></table></div>';
    var rows = [{ k: 'home', l: '제안서 홈' }, { k: 'comm', l: '커뮤니케이션' }, { k: 'schedule', l: '제안 일정' }];
    S.data.boards.boards.forEach(function (b) { rows.push({ k: 'board-' + b.id, l: b.name }); });
    rows.push({ k: 'guide', l: '사용 가이드' });
    h += '<div class="card"><h3>화면별 접근 권한</h3><p class="muted" style="margin-bottom:10px">PM·사업관리는 모든 화면을 편집합니다. 작성자와 영업대표는 아래에서 정합니다.</p>';
    h += '<table><thead><tr><th>화면</th><th>PM·사업관리</th><th>작성자</th><th>영업대표</th></tr></thead><tbody>';
    rows.forEach(function (r) {
      var p = m.perms[r.k] || {};
      h += '<tr><td>' + esc(r.l) + '</td><td><span class="dot yes">●</span></td>' +
        '<td><select class="perm-sel" data-perm="' + r.k + '|writer">' + LEVELS.map(function (o) {
          return '<option value="' + o.v + '"' + ((p.writer || 'none') === o.v ? ' selected' : '') + '>' + o.l + '</option>';
        }).join('') + '</select></td>' +
        '<td><select class="perm-sel" data-perm="' + r.k + '|sales">' + LEVELS.map(function (o) {
          return '<option value="' + o.v + '"' + ((p.sales || 'none') === o.v ? ' selected' : '') + '>' + o.l + '</option>';
        }).join('') + '</select></td></tr>';
    });
    h += '</tbody></table></div></div>';
    return h;
  }
  function denyView() {
    return '<div class="deny"><div style="font-size:30px">⛔</div><h3>접근 권한이 없습니다</h3><p>이 화면은 현재 권한(' + esc(ROLE_NAME[S.role]) + ')으로 볼 수 없습니다.<br>상단에서 권한을 바꿔 보세요.</p></div>';
  }

  /* ---------- 렌더 ---------- */
  function renderNav() {
    var h = '', groups = [{ g: 'ws', t: '제안 워크스페이스' }, { g: 'etc', t: '기타' }, { g: 'adm', t: 'ProWin 관리' }];
    groups.forEach(function (gr) {
      var items = screens().filter(function (s) { return s.grp === gr.g && (s.pm ? S.role === 'pm' : canView(s.k)); });
      if (!items.length) return;
      h += '<div class="sec">' + gr.t + '</div>';
      items.forEach(function (s) {
        h += '<button class="nav' + (S.route === s.k ? ' on' : '') + '" data-go="' + s.k + '">' + esc(s.label) + '</button>';
      });
    });
    $('side').innerHTML = h;
  }
  function renderHeader() {
    var s = scr(S.route) || scr('home');
    $('projName').textContent = S.data.master.project.name;
    $('roleTag').textContent = '지금 보는 권한: ' + ROLE_NAME[S.role] + ' (' + me() + ')';
    ROLES.forEach(function (r) { $('btn' + (r.v === 'writer' ? 'Writer' : r.v === 'pm' ? 'PM' : 'Sales')).classList.toggle('active', S.role === r.v); });
    $('crumb').innerHTML = '제안 워크스페이스 · <b>' + esc(s.label) + '</b>';
    $('title').textContent = s.label;
    $('desc').textContent = (INFO[s.board ? 'board' : s.k] || {}).req || '';
    var ch = changedFiles().length;
    $('dataState').textContent = (ch ? '저장 전 변경 있음 · ' : '') + (anyDraft() ? '임시저장본 사용 중 (이 브라우저에만 저장됨)' : '원본 데이터 사용 중');
  }
  function renderContent() {
    var k = S.route, h;
    if (!scr(k)) k = S.route = 'home';
    var s = scr(k);
    if (s.pm && S.role !== 'pm') h = denyView();
    else if (!canView(k)) h = denyView();
    else if (k === 'home') h = viewHome();
    else if (k === 'comm') h = viewPosts('comm');
    else if (k === 'schedule') h = viewSchedule();
    else if (k === 'guide') h = viewGuide();
    else if (k === 'ws') h = viewWs();
    else if (k === 'wsperm') h = viewWsperm();
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
    var ok = confirm('변경 내용을 저장할까요?\n\n대상: ' + ch.map(function (k) { return FILE_LABEL[k]; }).join(', ') +
      '\n\n이 브라우저에 반영됩니다. 기본 데이터 파일에 반영하려면 내보내기를 이용하세요.');
    if (!ok) return;
    try {
      ch.forEach(function (k) { localStorage.setItem(KEY + k, JSON.stringify(S.data[k])); S.draft[k] = true; });
    } catch (e) { toast('브라우저 저장소에 저장하지 못했습니다. 내보내기를 이용하세요.', true); return; }
    S.base = snap();
    renderAll();
    toast('저장되었습니다');
  }
  function fileForRoute() {
    var k = S.route;
    if (k === 'home' || k === 'wsperm') return 'master';
    if (k === 'comm') return 'comm';
    if (k === 'schedule') return 'schedule';
    if (k === 'guide') return 'guide';
    return 'boards';
  }
  function exportCurrent() {
    var k = fileForRoute();
    var blob = new Blob([JSON.stringify(S.data[k], null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = k + '.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast(k + '.json 내보내기 완료 · data 폴더에 덮어쓰면 기본 데이터가 바뀝니다');
  }
  function restoreOriginal() {
    if (!confirm('임시저장본을 모두 버리고 data 폴더의 원본으로 되돌릴까요?')) return;
    Object.keys(FILES).forEach(function (k) {
      try { localStorage.removeItem(KEY + k); } catch (e) { /* 무시 */ }
      S.draft[k] = false;
    });
    loadAll(true).then(renderAll);
    toast('원본으로 복원했습니다');
  }

  /* ---------- 데이터 로드 ---------- */
  function fetchJSON(path) {
    return fetch(path, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error(path + ' (' + r.status + ')');
      return r.json();
    });
  }
  function loadOne(k, forceOriginal) {
    if (!forceOriginal) {
      try {
        var raw = localStorage.getItem(KEY + k);
        if (raw) { S.draft[k] = true; return Promise.resolve(JSON.parse(raw)); }
      } catch (e) { /* 임시저장 불가 시 원본 */ }
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

  /* ---------- 이벤트 ---------- */
  function route() {
    var h = (location.hash || '').replace('#', '');
    S.route = scr(h) ? h : 'home';
    renderAll();
  }
  function setRole(r) { S.role = r; renderAll(); }

  function bind() {
    $('side').addEventListener('click', function (e) {
      var b = e.target.closest('[data-go]');
      if (b) location.hash = '#' + b.getAttribute('data-go');
    });
    ROLES.forEach(function (r) {
      var id = 'btn' + (r.v === 'writer' ? 'Writer' : r.v === 'pm' ? 'PM' : 'Sales');
      $(id).addEventListener('click', function () { setRole(r.v); });
    });
    $('btnSave').addEventListener('click', save);
    $('btnExport').addEventListener('click', exportCurrent);
    $('btnRestore').addEventListener('click', restoreOriginal);
    $('btnInfo').addEventListener('click', openInfo);
    window.addEventListener('hashchange', route);

    $('content').addEventListener('click', function (e) {
      var t = e.target, x, id, p;
      if (t.closest('[data-cal]')) {
        var cb = t.closest('[data-cal]').getAttribute('data-cal'), c = S.cal;
        if (cb === 'prev') { c.m--; if (c.m < 0) { c.m = 11; c.y--; } }
        if (cb === 'next') { c.m++; if (c.m > 11) { c.m = 0; c.y++; } }
        if (cb === 'today') { var n = new Date(); c.y = n.getFullYear(); c.m = n.getMonth(); }
        renderContent();
        return;
      }
      if ((x = t.closest('[data-ev]'))) { openSched(x.getAttribute('data-ev')); return; }
      if (t.closest('[data-proj-edit]')) {
        openForm('제안 기본정보 수정', projectFields(), Object.assign({}, S.data.master.project, {
          pm: S.data.master.project.team.pm, biz: S.data.master.project.team.biz, sales: S.data.master.project.team.sales
        }), function (v) {
          var pr = S.data.master.project;
          pr.name = v.name; pr.client = v.client; pr.summary = v.summary; pr.start = v.start; pr.deadline = v.deadline; pr.presentation = v.presentation;
          pr.team = { pm: v.pm, biz: v.biz, sales: v.sales };
        });
        return;
      }
      if (t.closest('[data-sc-add]')) {
        var today = todayISO();
        openForm('일정 추가', schedFields(), { start: today, end: today, color: 'c-wr', owner: me(), status: '예정' }, function (v) {
          S.data.schedule.items.push(Object.assign({ id: nextId('SC', S.data.schedule.items) }, v));
        }, null, schedValidate);
        return;
      }
      if ((x = t.closest('[data-sc-edit]'))) { openSched(x.getAttribute('data-sc-edit')); return; }
      if ((x = t.closest('[data-sc-del]'))) {
        id = x.getAttribute('data-sc-del');
        if (!confirm('이 일정을 삭제할까요?')) return;
        S.data.schedule.items = S.data.schedule.items.filter(function (y) { return y.id !== id; });
        renderAll();
        toast('삭제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if ((x = t.closest('[data-post-add]'))) {
        var kk = x.getAttribute('data-post-add');
        openForm('새 글', postFields(kk), kk === 'qna' || (boardOf(kk) && boardOf(kk).kind === 'qna') ? { status: '답변대기' } : {}, function (v) {
          var list = postsOf(kk);
          var pref = kk === 'comm' ? 'CM' : kk === 'board-1' ? 'QA' : 'RF';
          var np = Object.assign({ id: nextId(pref, list), by: me(), date: todayISO() }, v);
          list.push(np);
        });
        return;
      }
      if ((x = t.closest('[data-post-edit]'))) {
        p = x.getAttribute('data-post-edit').split('|');
        openPostEdit(p[0], p[1]);
        return;
      }
      if ((x = t.closest('[data-post-del]'))) {
        p = x.getAttribute('data-post-del').split('|');
        var list2 = postsOf(p[0]), target = list2.filter(function (y) { return y.id === p[1]; })[0];
        if (!target || !canEditPost(p[0], target)) { toast('이 글은 삭제할 수 없습니다', true); return; }
        if (!confirm('이 글을 삭제할까요?')) return;
        var remain = list2.filter(function (y) { return y.id !== p[1]; });
        if (p[0] === 'comm') S.data.comm.posts = remain; else boardOf(p[0]).posts = remain;
        renderAll();
        toast('삭제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if ((x = t.closest('[data-ws-add]'))) {
        openForm('게시판 추가', [
          { k: 'name', label: '게시판명', req: true }, { k: 'desc', label: '설명' },
          { k: 'kind', label: '유형', type: 'select', opts: [{ v: 'free', l: '자유 글' }, { v: 'qna', l: 'Q&A (답변 상태)' }, { v: 'ref', l: '자료 (링크)' }] }
        ], { kind: 'free' }, function (v) {
          var bid = S.data.boards.nextId++;
          S.data.boards.boards.push({ id: bid, name: v.name, desc: v.desc, kind: v.kind, posts: [] });
          S.data.master.perms['board-' + bid] = { writer: 'edit', sales: 'view' };
        });
        return;
      }
      if ((x = t.closest('[data-ws-edit]'))) {
        var bid2 = parseInt(x.getAttribute('data-ws-edit'), 10), bd = boardOf('board-' + bid2);
        openForm('게시판 수정', [{ k: 'name', label: '게시판명', req: true }, { k: 'desc', label: '설명' }], bd, function (v) {
          bd.name = v.name; bd.desc = v.desc;
        });
        return;
      }
      if ((x = t.closest('[data-ws-del]'))) {
        var did = parseInt(x.getAttribute('data-ws-del'), 10), dbd = boardOf('board-' + did);
        if (!confirm('"' + dbd.name + '" 게시판과 글 ' + dbd.posts.length + '건을 삭제할까요?')) return;
        S.data.boards.boards = S.data.boards.boards.filter(function (b) { return b.id !== did; });
        delete S.data.master.perms['board-' + did];
        if (S.route === 'board-' + did) location.hash = '#home';
        renderAll();
        toast('삭제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if (t.closest('[data-mem-add]')) {
        openForm('멤버 추가', [
          { k: 'name', label: '이름', req: true }, { k: 'title', label: '직함' },
          { k: 'role', label: '권한', type: 'select', opts: ROLES }
        ], { role: 'writer' }, function (v) { S.data.master.members.push(v); });
        return;
      }
      if ((x = t.closest('[data-mem-del]'))) {
        var di = parseInt(x.getAttribute('data-mem-del'), 10);
        if (!confirm('이 멤버를 목록에서 제외할까요?')) return;
        S.data.master.members.splice(di, 1);
        renderAll();
        toast('제외했습니다. 저장 버튼으로 반영하세요');
        return;
      }
    });
    $('content').addEventListener('change', function (e) {
      var t = e.target;
      if (t.hasAttribute('data-mem-role')) {
        S.data.master.members[parseInt(t.getAttribute('data-mem-role'), 10)].role = t.value;
        renderAll();
      } else if (t.hasAttribute('data-perm')) {
        var pp = t.getAttribute('data-perm').split('|');
        var entry = S.data.master.perms[pp[0]] || (S.data.master.perms[pp[0]] = {});
        entry[pp[1]] = t.value;
        renderAll();
      }
    });
    $('modal').addEventListener('click', function (e) {
      var t = e.target, M = S.modal;
      if (t === this || t.hasAttribute('data-x')) { closeModal(); return; }
      if (!M) return;
      if (t.hasAttribute('data-del')) {
        if (!confirm('삭제할까요?')) return;
        if (M.onDelete) M.onDelete();
        closeModal();
        renderAll();
        toast('삭제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if (t.hasAttribute('data-save')) {
        var v = {}, ok = true;
        M.fields.forEach(function (f) {
          var el = $('modalBox').querySelector('[data-f="' + f.k + '"]');
          v[f.k] = el ? el.value.trim() : '';
          if (f.req && !v[f.k]) ok = false;
        });
        if (!ok) { toast('필수 항목을 입력하세요', true); return; }
        if (M.validate) {
          var msg = M.validate(v);
          if (msg) { toast(msg, true); return; }
        }
        M.onSave(v);
        closeModal();
        renderAll();
        toast('반영했습니다. 저장 버튼으로 확정하세요');
      }
    });
  }
  function openPostEdit(k, pid) {
    var list = postsOf(k), p = list.filter(function (y) { return y.id === pid; })[0];
    if (!p) return;
    if (!canEditPost(k, p)) { toast('이 글은 수정할 수 없습니다', true); return; }
    openForm('글 수정', postFields(k), p, function (v) { Object.assign(p, v); });
  }

  function boot() {
    loadAll(false).then(function () {
      var n = new Date();
      S.cal = { y: n.getFullYear(), m: n.getMonth() };
      bind();
      route();
    }).catch(function (err) {
      $('content').innerHTML = '<div class="empty">데이터를 읽지 못했습니다 (' + esc(err.message) +
        '). 파일을 직접 열지 말고 로컬 서버로 실행하세요: python3 -m http.server 8000</div>';
    });
  }
  boot();
})();
