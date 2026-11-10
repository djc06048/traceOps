/* ProWin 단순 버전 — 좌측 메뉴의 제안 워크스페이스 화면 + 제안 권한관리
 * 데이터: data/*.json (DB 없음). 편집은 브라우저 임시저장, 저장 시 변경 확인, 내보내기로 파일 교체.
 */
(function () {
  'use strict';

  var FILES = { master: 'data/master.json', schedule: 'data/schedule.json', boards: 'data/boards.json', guide: 'data/guide.json' };
  var FILE_LABEL = { master: '제안 기본정보·권한', schedule: '제안 일정', boards: '게시판(커뮤니케이션·RFP Q&A·참고 자료)', guide: '사용 가이드' };
  var KEY = 'prowin-simple-v1:';
  var SCREENS = [
    { k: 'home', label: '제안서 홈', group: 'ws', file: 'master', desc: '제안 개요, 오늘 할 일, 지연 항목을 한눈에 봅니다.' },
    { k: 'comm', label: '커뮤니케이션', group: 'ws', file: 'boards', board: true, desc: '제안팀 공지와 공유 글입니다.' },
    { k: 'schedule', label: '제안 일정', group: 'ws', file: 'schedule', desc: '제안 일정을 등록하고 진행 상태를 관리합니다.' },
    { k: 'qna', label: 'RFP Q&A', group: 'ws', file: 'boards', board: true, desc: '발주처 질의와 답변을 기록합니다.' },
    { k: 'refs', label: '참고 자료', group: 'ws', file: 'boards', board: true, desc: '유사 제안과 기술 자료를 모아 둡니다.' },
    { k: 'guide', label: '사용 가이드', group: 'etc', file: 'guide', desc: '사이트 사용법입니다.' },
    { k: 'wsperm', label: '제안 권한관리', group: 'adm', file: 'master', pmOnly: true, desc: '멤버와 화면별 편집 권한을 관리합니다. PM만 볼 수 있습니다.' }
  ];
  var SCREEN_LABEL = { home: '제안서 홈', comm: '커뮤니케이션', schedule: '제안 일정', qna: 'RFP Q&A', refs: '참고 자료', guide: '사용 가이드' };
  var KIND = { review: '리뷰', write: '작성', meeting: '회의', deadline: '마감' };
  var SCHED_STATUS = ['예정', '진행중', '완료'];
  var QA_STATUS = ['답변대기', '답변완료'];
  var PREFIX = { comm: 'CM', qna: 'QA', refs: 'RF', schedule: 'SC' };

  var S = { role: 'writer', data: {}, base: {}, draft: {}, route: 'home', modal: null };

  /* ---------- 공통 유틸 ---------- */
  function $(id) { return document.getElementById(id); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function p2(n) { return String(n).padStart(2, '0'); }
  function todayISO() { var d = new Date(); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function addDays(iso, n) { var d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function snap() { return JSON.parse(JSON.stringify(S.data)); }
  function me() { return S.role === 'pm' ? S.data.master.pm : S.data.master.me; }
  function canManage() { return S.role === 'pm'; }
  function canEdit(k) { return canManage() || S.data.master.perms[k] === 'writer'; }
  function canEditPost(k, p) { return canManage() || (canEdit(k) && p.by === me()); }
  function nextId(prefix, list) {
    var max = 0;
    list.forEach(function (x) { var n = parseInt(String(x.id).split('-')[1], 10); if (n > max) max = n; });
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
  function memberName(n) { return esc(n); }
  function screenOf(k) { return SCREENS.filter(function (x) { return x.k === k; })[0]; }

  /* ---------- 일정 상태 ---------- */
  function schedClass(it) {
    var t = todayISO();
    if (it.end < t && it.status !== '완료') return 'late';
    if (it.start <= t && t <= it.end) return 'today';
    return '';
  }
  function schedLabel(it) {
    var c = schedClass(it);
    return c === 'late' ? '지연' : it.status;
  }

  /* ---------- 모달 ---------- */
  function openForm(title, fields, vals, onSave, onDelete) {
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
    S.modal = { fields: fields, onSave: onSave, onDelete: onDelete };
    $('modal').classList.add('open');
    var first = $('modalBox').querySelector('[data-f]');
    if (first) first.focus();
  }
  function closeModal() { S.modal = null; $('modal').classList.remove('open'); }

  /* ---------- 화면: 제안서 홈 ---------- */
  function viewHome() {
    var m = S.data.master, p = m.project, t = todayISO(), soon = addDays(t, 3);
    var sched = S.data.schedule.items;
    var todo = sched.filter(function (x) { return x.start <= soon && x.end >= t && x.status !== '완료'; });
    var late = sched.filter(function (x) { return x.end < t && x.status !== '완료'; });
    var notice = S.data.boards.comm.posts.slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; }).slice(0, 3);
    var h = '<div class="card"><h3>제안 개요' +
      (canEdit('home') ? '<button class="btn ghost sm" data-proj-edit="1">수정</button>' : '') + '</h3>' +
      '<div class="kv"><div class="k">사업명</div><div>' + esc(p.name) + '</div>' +
      '<div class="k">발주처</div><div>' + esc(p.client) + '</div>' +
      '<div class="k">개요</div><div>' + esc(p.summary) + '</div>' +
      '<div class="k">제안 마감</div><div>' + esc(p.deadline) + '</div>' +
      '<div class="k">제안 발표</div><div>' + esc(p.presentation) + '</div></div></div>';
    h += '<div class="grid2">';
    h += '<div class="card"><h3>오늘 할 일 <span class="muted">3일 이내 · 미완료</span></h3>' + listSched(todo, '오늘 할 일이 없습니다.') + '</div>';
    h += '<div class="card"><h3>지연 항목 <span class="muted">마감 지남 · 미완료</span></h3>' + listSched(late, '지연 항목이 없습니다.') + '</div>';
    h += '</div>';
    h += '<div class="card"><h3>최근 공지</h3>' + (notice.length ? '<table><tbody>' + notice.map(function (n) {
      return '<tr><td>' + esc(n.title) + '</td><td class="muted">' + esc(n.by) + '</td><td class="muted">' + esc(n.date) + '</td></tr>';
    }).join('') + '</tbody></table>' : '<div class="empty">공지가 없습니다.</div>') + '</div>';
    return h;
  }
  function listSched(list, empty) {
    if (!list.length) return '<div class="empty">' + empty + '</div>';
    return '<table><tbody>' + list.map(function (x) {
      return '<tr class="' + schedClass(x) + '"><td>' + esc(x.title) + '</td><td class="muted">' + esc(x.start) + ' ~ ' + esc(x.end) +
        '</td><td class="muted">' + esc(x.owner) + '</td><td><span class="st ' + (schedClass(x) === 'late' ? 'late' : 'todo') + '">' + esc(schedLabel(x)) + '</span></td></tr>';
    }).join('') + '</tbody></table>';
  }

  /* ---------- 화면: 제안 일정 ---------- */
  function viewSchedule() {
    var items = S.data.schedule.items.slice().sort(function (a, b) { return a.start < b.start ? -1 : 1; });
    var can = canEdit('schedule');
    var h = (can ? '<div style="margin-bottom:12px"><button class="btn sm" data-sc-add="1">＋ 일정 추가</button></div>' : '') +
      '<table><thead><tr><th>제목</th><th>시작</th><th>종료</th><th>구분</th><th>담당</th><th>상태</th>' + (can ? '<th></th>' : '') + '</tr></thead><tbody>';
    if (!items.length) h += '<tr><td colspan="7" class="empty">등록된 일정이 없습니다.</td></tr>';
    items.forEach(function (x) {
      var c = schedClass(x);
      h += '<tr class="' + c + '"><td>' + (can ? '<button class="title-link" data-sc-edit="' + esc(x.id) + '">' + esc(x.title) + '</button>' : esc(x.title)) + '</td>' +
        '<td>' + esc(x.start) + '</td><td>' + esc(x.end) + '</td><td><span class="tag">' + esc(KIND[x.kind] || x.kind) + '</span></td>' +
        '<td>' + esc(x.owner) + '</td><td><span class="st ' + (c === 'late' ? 'late' : x.status === '완료' ? 'done' : x.status === '진행중' ? 'doing' : 'todo') + '">' + esc(schedLabel(x)) + '</span></td>' +
        (can ? '<td><button class="btn ghost sm" data-sc-edit="' + esc(x.id) + '">수정</button></td>' : '') + '</tr>';
    });
    return h + '</tbody></table>';
  }
  function schedForm(it) {
    var mem = S.data.master.members.map(function (m) { return m.name; });
    return [
      { k: 'title', label: '제목', req: true },
      { k: 'start', label: '시작일', type: 'date', req: true },
      { k: 'end', label: '종료일', type: 'date', req: true },
      { k: 'kind', label: '구분', type: 'select', opts: Object.keys(KIND).map(function (k) { return { v: k, l: KIND[k] }; }) },
      { k: 'owner', label: '담당', type: 'select', opts: mem },
      { k: 'status', label: '상태', type: 'select', opts: SCHED_STATUS }
    ];
  }

  /* ---------- 화면: 게시판 (커뮤니케이션 · RFP Q&A · 참고 자료) ---------- */
  function viewBoard(k) {
    var b = S.data.boards[k], posts = b.posts.slice().sort(function (a, b2) { return a.date < b2.date ? 1 : -1; });
    var h = canEdit(k) ? '<div style="margin-bottom:12px"><button class="btn sm" data-post-add="' + k + '">＋ 새 글</button></div>' : '';
    var extra = k === 'qna' ? '상태' : k === 'refs' ? '자료' : '';
    h += '<table><thead><tr><th>제목</th><th>작성자</th><th>날짜</th>' + (extra ? '<th>' + extra + '</th>' : '') + '<th></th></tr></thead><tbody>';
    if (!posts.length) h += '<tr><td colspan="5" class="empty">글이 없습니다.</td></tr>';
    posts.forEach(function (p) {
      var can = canEditPost(k, p);
      h += '<tr><td><button class="title-link" data-post-open="' + k + '|' + esc(p.id) + '">' + esc(p.title) + '</button></td>' +
        '<td>' + esc(p.by) + '</td><td class="muted">' + esc(p.date) + '</td>';
      if (k === 'qna') h += '<td><span class="st ' + (p.status === '답변완료' ? 'done' : 'wait') + '">' + esc(p.status) + '</span></td>';
      if (k === 'refs') h += '<td class="muted">' + esc(p.link || '') + '</td>';
      h += '<td>' + (can ? '<button class="btn ghost sm" data-post-open="' + k + '|' + esc(p.id) + '">수정</button>' : '') + '</td></tr>';
    });
    return h + '</tbody></table>';
  }
  function postForm(k) {
    var f = [{ k: 'title', label: '제목', req: true }, { k: 'body', label: '내용', type: 'textarea' }];
    if (k === 'qna') {
      f.push({ k: 'status', label: '상태', type: 'select', opts: QA_STATUS });
      f.push({ k: 'answer', label: '답변', type: 'textarea' });
    }
    if (k === 'refs') f.push({ k: 'link', label: '자료 위치 (파일명·경로)' });
    return f;
  }

  /* ---------- 화면: 사용 가이드 ---------- */
  function viewGuide() {
    return S.data.guide.sections.map(function (s) {
      return '<div class="guide-sec"><h4>' + esc(s.t) + '</h4><p>' + esc(s.b) + '</p></div>';
    }).join('');
  }

  /* ---------- 화면: 제안 권한관리 (PM 전용) ---------- */
  function viewWsperm() {
    if (!canManage()) return '<div class="deny"><div style="font-size:30px">⛔</div><h3>접근 권한이 없습니다</h3><p>제안 권한관리는 PM만 접근할 수 있습니다.<br>상단에서 "PM"으로 바꾸면 확인할 수 있습니다.</p></div>';
    var m = S.data.master;
    var h = '<div class="card"><h3>멤버 <button class="btn sm" data-mem-add="1">＋ 멤버 추가</button></h3><table><thead><tr><th>이름</th><th>직함</th><th>권한</th><th></th></tr></thead><tbody>';
    m.members.forEach(function (x, i) {
      var locked = x.name === m.pm;
      h += '<tr><td>' + esc(x.name) + '</td><td class="muted">' + esc(x.title) + '</td><td>' +
        '<select class="cell" data-mem-role="' + i + '"' + (locked ? ' disabled' : '') + '>' +
        '<option value="writer"' + (x.role === 'writer' ? ' selected' : '') + '>작성자</option>' +
        '<option value="pm"' + (x.role === 'pm' ? ' selected' : '') + '>PM</option></select></td>' +
        '<td>' + (locked ? '' : '<button class="btn ghost sm" data-mem-del="' + i + '">삭제</button>') + '</td></tr>';
    });
    h += '</tbody></table></div>';
    h += '<div class="card"><h3>화면별 편집 권한</h3><p class="muted" style="margin-bottom:10px">"작성자"로 설정하면 작성자와 PM이 편집할 수 있고, "PM만"이면 PM만 편집합니다. 조회는 모두 가능합니다.</p><table><thead><tr><th>화면</th><th>편집 권한</th></tr></thead><tbody>';
    Object.keys(SCREEN_LABEL).forEach(function (k) {
      h += '<tr><td>' + esc(SCREEN_LABEL[k]) + '</td><td><select class="cell" data-perm="' + k + '">' +
        '<option value="writer"' + (m.perms[k] === 'writer' ? ' selected' : '') + '>작성자 포함</option>' +
        '<option value="pm"' + (m.perms[k] === 'pm' ? ' selected' : '') + '>PM만</option></select></td></tr>';
    });
    return h + '</tbody></table></div>';
  }

  /* ---------- 렌더 ---------- */
  var GROUPS = [{ g: 'ws', t: '제안 워크스페이스' }, { g: 'etc', t: '기타' }, { g: 'adm', t: 'ProWin 관리' }];
  function renderNav() {
    var h = '';
    GROUPS.forEach(function (gr) {
      h += '<div class="sec">' + gr.t + '</div>';
      SCREENS.filter(function (s) { return s.group === gr.g; }).forEach(function (s) {
        if (s.pmOnly && !canManage()) return;
        h += '<button class="nav' + (S.route === s.k ? ' on' : '') + '" data-go="' + s.k + '">' + esc(s.label) +
          (s.pmOnly ? '<span class="lock">PM</span>' : '') + '</button>';
      });
    });
    $('side').innerHTML = h;
  }
  function renderHeader() {
    var s = screenOf(S.route), p = S.data.master.project;
    $('projName').textContent = p.name;
    $('roleTag').textContent = '지금 보는 권한: ' + (canManage() ? 'PM (' + S.data.master.pm + ')' : '작성자 (' + S.data.master.me + ')');
    $('btnWriter').classList.toggle('active', !canManage());
    $('btnPM').classList.toggle('active', canManage());
    $('crumb').innerHTML = '제안 워크스페이스 · <b>' + esc(s.label) + '</b>';
    $('title').textContent = s.label;
    $('desc').textContent = s.desc;
    var changed = changedFiles().length;
    $('dataState').textContent = (changed ? '저장 전 변경 있음 · ' : '') +
      (anyDraft() ? '임시저장본 사용 중 (이 브라우저에만 저장됨)' : '원본 데이터 사용 중');
  }
  function renderContent() {
    var k = S.route, h = '';
    if (k === 'home') h = viewHome();
    else if (k === 'schedule') h = viewSchedule();
    else if (k === 'comm' || k === 'qna' || k === 'refs') h = viewBoard(k);
    else if (k === 'guide') h = viewGuide();
    else if (k === 'wsperm') h = viewWsperm();
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
  function exportCurrent() {
    var s = screenOf(S.route), k = s.file;
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
    S.route = screenOf(h) ? h : 'home';
    renderAll();
  }
  function setRole(r) {
    S.role = r;
    renderAll();
  }
  function bind() {
    $('side').addEventListener('click', function (e) {
      var b = e.target.closest('[data-go]');
      if (b) location.hash = '#' + b.getAttribute('data-go');
    });
    $('btnWriter').addEventListener('click', function () { setRole('writer'); });
    $('btnPM').addEventListener('click', function () { setRole('pm'); });
    $('btnSave').addEventListener('click', save);
    $('btnExport').addEventListener('click', exportCurrent);
    $('btnRestore').addEventListener('click', restoreOriginal);
    window.addEventListener('hashchange', route);

    $('content').addEventListener('click', function (e) {
      var t = e.target, x;
      if ((x = t.closest('[data-proj-edit]'))) {
        var p = S.data.master.project;
        openForm('제안 기본정보 수정', [
          { k: 'name', label: '사업명', req: true }, { k: 'client', label: '발주처', req: true },
          { k: 'summary', label: '개요', type: 'textarea' }, { k: 'deadline', label: '제안 마감', type: 'date' },
          { k: 'presentation', label: '제안 발표', type: 'date' }
        ], p, function (v) { Object.assign(S.data.master.project, v); });
        return;
      }
      if ((x = t.closest('[data-sc-add]'))) {
        openForm('일정 추가', schedForm(), { status: '예정', kind: 'write', owner: me() }, function (v) {
          S.data.schedule.items.push(Object.assign({ id: nextId(PREFIX.schedule, S.data.schedule.items) }, v));
        });
        return;
      }
      if ((x = t.closest('[data-sc-edit]'))) {
        var id = x.getAttribute('data-sc-edit');
        var it = S.data.schedule.items.filter(function (y) { return y.id === id; })[0];
        if (!it) return;
        openForm('일정 수정', schedForm(it), it, function (v) { Object.assign(it, v); }, function () {
          S.data.schedule.items = S.data.schedule.items.filter(function (y) { return y.id !== id; });
        });
        return;
      }
      if ((x = t.closest('[data-post-add]'))) {
        var kk = x.getAttribute('data-post-add');
        openForm('새 글 (' + S.data.boards[kk].name + ')', postForm(kk), { status: '답변대기' }, function (v) {
          S.data.boards[kk].posts.push(Object.assign({ id: nextId(PREFIX[kk], S.data.boards[kk].posts), by: me(), date: todayISO() }, v));
        });
        return;
      }
      if ((x = t.closest('[data-post-open]'))) {
        var parts = x.getAttribute('data-post-open').split('|'), bk = parts[0], pid = parts[1];
        var post = S.data.boards[bk].posts.filter(function (y) { return y.id === pid; })[0];
        if (!post) return;
        if (!canEditPost(bk, post)) { toast('이 글은 수정할 수 없습니다', true); return; }
        openForm('글 수정 · ' + post.title, postForm(bk), post, function (v) { Object.assign(post, v); }, function () {
          S.data.boards[bk].posts = S.data.boards[bk].posts.filter(function (y) { return y.id !== pid; });
        });
        return;
      }
      if ((x = t.closest('[data-mem-add]'))) {
        openForm('멤버 추가', [
          { k: 'name', label: '이름', req: true }, { k: 'title', label: '직함' },
          { k: 'role', label: '권한', type: 'select', opts: [{ v: 'writer', l: '작성자' }, { v: 'pm', l: 'PM' }] }
        ], { role: 'writer' }, function (v) { S.data.master.members.push(v); });
        return;
      }
      if ((x = t.closest('[data-mem-del]'))) {
        var di = parseInt(x.getAttribute('data-mem-del'), 10);
        if (!confirm('이 멤버를 목록에서 삭제할까요?')) return;
        S.data.master.members.splice(di, 1);
        renderAll();
        toast('삭제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
    });
    $('content').addEventListener('change', function (e) {
      var t = e.target;
      if (t.hasAttribute('data-mem-role')) {
        S.data.master.members[parseInt(t.getAttribute('data-mem-role'), 10)].role = t.value;
        renderAll();
      } else if (t.hasAttribute('data-perm')) {
        S.data.master.perms[t.getAttribute('data-perm')] = t.value;
        renderAll();
      }
    });
    $('modal').addEventListener('click', function (e) {
      var t = e.target, M = S.modal;
      if (t === this || t.hasAttribute('data-x')) { closeModal(); return; }
      if (!M) return;
      if (t.hasAttribute('data-del')) {
        if (!confirm('삭제할까요?')) return;
        M.onDelete && M.onDelete();
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
        M.onSave(v);
        closeModal();
        renderAll();
        toast('반영했습니다. 저장 버튼으로 확정하세요');
      }
    });
  }

  function boot() {
    loadAll(false).then(function () {
      bind();
      route();
    }).catch(function (err) {
      $('content').innerHTML = '<div class="empty">데이터를 읽지 못했습니다 (' + esc(err.message) +
        '). 파일을 직접 열지 말고 로컬 서버로 실행하세요: python3 -m http.server 8000</div>';
    });
  }

  boot();
})();
