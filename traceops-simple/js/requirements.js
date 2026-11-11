/* 요구사항 관리 — 조회 / 추가 / 수정 / 삭제
 * 데이터: 관계형 DB(traceops.db) — GET/PUT /api/requirements. 저장 시 서버가 변경 이력을 기록
 * 사용 중인 요구사항ID는 삭제·ID 변경 불가 (분석·설계·개발·테스트 매핑 무결성)
 */
(function () {
  'use strict';

  var KEY = 'traceops-simple:';
  var PREFIX = 'RQ_QPM_';
  var STAGES = ['분석', '설계'];
  var STATUSES = ['수용', '조건부수용', '부분수용', '미수용'];
  var KINDS = ['기능', '비기능'];
  var SOURCES = { analysis: '/api/analysis', design: '/api/design', dev: '/api/dev', unit: '/api/unit', integration: '/api/integration' };
  var S = { items: [], src: {}, draft: false, filter: { minor: '', status: '', q: '' } };

  function $(id) { return document.getElementById(id); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  var timer;
  function toast(msg, err) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.toggle('err', !!err);
    t.classList.add('show');
    clearTimeout(timer);
    timer = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }
  async function fetchJSON(path) {
    var r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(path + ' (' + r.status + ')');
    return r.json();
  }
  async function load(name, path) {
    if (path.charAt(0) === '/') return { data: await fetchJSON(path), draft: false }; // 관계형 DB(API)
    try {
      var raw = DB.getItem(KEY + name);
      if (raw) return { data: JSON.parse(raw), draft: true };
    } catch (e) { /* 임시저장 불가 시 원본 사용 */ }
    return { data: await fetchJSON(path), draft: false };
  }

  var WHO = '황금빛'; // ponytail: 로그인이 없어 PL 고정. 인증이 생기면 사용자명으로 교체

  /* 사용처 집계: 분석/설계/개발/단위/통합 어디에 몇 건 매핑되어 있는지 */
  function usageOf(id) {
    var u = { 분석: 0, 설계: 0, 개발: 0, 단위: 0, 통합: 0, total: 0 };
    var map = { analysis: '분석', design: '설계', dev: '개발', unit: '단위', integration: '통합' };
    Object.keys(map).forEach(function (k) {
      (S.src[k] || []).forEach(function (x) {
        if ((x.reqIds || []).indexOf(id) >= 0) { u[map[k]]++; u.total++; }
      });
    });
    return u;
  }
  function isUsed(id) { return id && usageOf(id).total > 0; }

  function minors() {
    var seen = {}, out = [];
    S.items.forEach(function (x) { if (x.minor && !seen[x.minor]) { seen[x.minor] = true; out.push(x.minor); } });
    return out;
  }
  function syncMinorOptions() {
    var cur = $('fMinor').value;
    $('fMinor').innerHTML = '<option value="">전체</option>' + minors().map(function (m) {
      return '<option' + (m === cur ? ' selected' : '') + '>' + esc(m) + '</option>';
    }).join('');
  }

  function visibleIdx() {
    var q = S.filter.q.toLowerCase();
    var out = [];
    S.items.forEach(function (x, i) {
      if (S.filter.minor && x.minor !== S.filter.minor) return;
      if (S.filter.status && x.status !== S.filter.status) return;
      if (q && [x.id, x.name, x.content].join(' ').toLowerCase().indexOf(q) < 0) return;
      out.push(i);
    });
    return out;
  }
  function opts(list, val) {
    return list.map(function (o) {
      return '<option' + (o === val ? ' selected' : '') + '>' + esc(o) + '</option>';
    }).join('');
  }
  function nextId() {
    var max = 0;
    S.items.forEach(function (x) {
      var m = /^RQ_QPM_(\d+)$/.exec(x.id || '');
      if (m) max = Math.max(max, +m[1]);
    });
    return PREFIX + String(max + 1).padStart(4, '0');
  }
  function rowHTML(x, i) {
    var u = usageOf(x.id), used = u.total > 0;
    var idCell = used
      ? '<span class="disabled-field">' + esc(x.id) + '</span>'
      : '<input class="txt-input" data-f="id" value="' + esc(x.id) + '" placeholder="RQ_QPM_0000" style="width:140px">';
    return '<tr data-i="' + i + '"' + (x._flash ? ' class="flash"' : '') + '>' +
      '<td class="mono">' + idCell + '</td>' +
      '<td><input class="txt-input" data-f="minor" value="' + esc(x.minor) + '" style="width:120px"></td>' +
      '<td><input class="txt-input" data-f="name" value="' + esc(x.name) + '" style="width:170px"></td>' +
      '<td><textarea class="txt-input" data-f="content" rows="2" style="width:260px;resize:vertical">' + esc(x.content) + '</textarea></td>' +
      '<td><select class="txt-input" data-f="stage">' + opts(STAGES, x.stage) + '</select></td>' +
      '<td><select class="txt-input" data-f="status">' + opts(STATUSES, x.status) + '</select></td>' +
      '<td><input class="txt-input" data-f="precondition" value="' + esc(x.precondition) + '" style="width:180px"></td>' +
      '<td><input class="txt-input" data-f="vendorOwner" value="' + esc(x.vendorOwner) + '" style="width:90px"></td>' +
      '<td><input class="txt-input" data-f="custITOwner" value="' + esc((x.custIT || {}).owner) + '" style="width:110px" placeholder="담당자"><input class="txt-input" data-f="custITTeam" value="' + esc((x.custIT || {}).team) + '" style="width:110px;margin-top:4px" placeholder="담당팀"></td>' +
      '<td><input class="txt-input" data-f="custBizOwner" value="' + esc((x.custBiz || {}).owner) + '" style="width:110px" placeholder="담당자"><input class="txt-input" data-f="custBizTeam" value="' + esc((x.custBiz || {}).team) + '" style="width:110px;margin-top:4px" placeholder="담당팀"></td>' +
      '<td><select class="txt-input" data-f="kind">' + opts(KINDS, x.kind) + '</select></td>' +
      '<td><input class="txt-input" data-f="source" value="' + esc(x.source) + '" style="width:110px"></td>' +
      '<td><button class="remark-badge' + ((x.revisions || []).length ? '' : ' zero') + '" data-hist="1">🕘 ' + (x.revisions || []).length + '</button></td>' +
      '<td class="mono">분석 ' + u.분석 + ' · 설계 ' + u.설계 + ' · 개발 ' + u.개발 + ' · 단위 ' + u.단위 + ' · 통합 ' + u.통합 + '</td>' +
      '<td><button class="btn ghost sm" data-del="1"' + (used ? ' disabled title="사용 중인 요구사항ID는 삭제할 수 없습니다"' : '') + '>삭제</button></td>' +
      '</tr>';
  }
  function validateAll() {
    var seen = {}, errs = 0, msgs = [];
    S.items.forEach(function (x) {
      if (!x.id) { errs++; msgs.push('요구사항ID 미입력'); return; }
      if (seen[x.id]) { errs++; msgs.push('중복 요구사항ID: ' + x.id); }
      seen[x.id] = true;
    });
    return { errs: errs, msgs: msgs };
  }
  function render() {
    syncMinorOptions();
    var idx = visibleIdx();
    $('tbody').innerHTML = idx.length
      ? idx.map(function (i) { return rowHTML(S.items[i], i); }).join('')
      : '<tr><td colspan="15" class="empty">조건에 맞는 항목이 없습니다.</td></tr>';
    $('count').innerHTML = '<b>' + idx.length + '</b>건 (전체 ' + S.items.length + '건)';
    var v = validateAll();
    $('banner').innerHTML = v.errs
      ? '<div class="validation-banner">⚠ ' + esc(v.msgs.join(' / ')) + '</div>'
      : '';
    $('dataState').textContent = '관계형 DB(traceops.db) 사용 중 · 변경 이력 자동 기록';
    var flash = $('tbody').querySelector('tr.flash');
    if (flash) flash.scrollIntoView({ block: 'center' });
  }

  function cleanItems() {
    return S.items.map(function (x) {
      var o = {};
      Object.keys(x).forEach(function (k) { if (k.charAt(0) !== '_') o[k] = x[k]; });
      return o;
    });
  }
  async function save() {
    var v = validateAll();
    if (v.errs) { toast('저장 불가: ' + v.msgs[0], true); render(); return; }
    try {
      S.items = (await api('PUT', '/api/requirements', { items: cleanItems(), who: WHO })).items;
      toast('저장되었습니다');
    } catch (e) { toast('저장 실패: ' + e.message, true); }
    render();
  }
  function exportFile() {
    var blob = new Blob([JSON.stringify({ kind: 'requirements', items: cleanItems() }, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'requirements.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast('requirements.json 내보내기 완료 · data/requirements.json에 덮어쓰면 원본이 됩니다');
  }
  async function restore() {
    if (!confirm('현재 요구사항을 data/requirements.json 초기 데이터로 되돌릴까요?\n(되돌린 변경도 변경 이력에 기록됩니다)')) return;
    try {
      var d = await fetchJSON('data/requirements.json');
      S.items = (await api('PUT', '/api/requirements', { items: d.items, who: WHO })).items;
      render();
      toast('초기 데이터로 복원했습니다');
    } catch (e) { toast('복원 실패: ' + e.message, true); }
  }

  function bind() {
    $('fMinor').addEventListener('change', function (e) { S.filter.minor = e.target.value; render(); });
    $('fStatus').addEventListener('change', function (e) { S.filter.status = e.target.value; render(); });
    $('fQ').addEventListener('input', function (e) { S.filter.q = e.target.value.trim(); render(); });
    $('btnAdd').addEventListener('click', function () {
      S.items.unshift({
        id: nextId(), major: '가입설계시스템', middle: '가입설계/청약', minor: '', name: '', content: '',
        stage: '분석', status: '수용', precondition: '', vendorOwner: '', custIT: { owner: '', team: '' },
        custBiz: { owner: '', team: '' }, kind: '기능', source: '', _new: true
      });
      S.filter = { minor: '', status: '', q: '' };
      $('fMinor').value = ''; $('fStatus').value = ''; $('fQ').value = '';
      render();
      var first = $('tbody').querySelector('input[data-f="id"]');
      if (first) first.focus();
    });
    $('btnSave').addEventListener('click', save);
    $('btnExport').addEventListener('click', exportFile);
    $('btnRestore').addEventListener('click', restore);

    $('tbody').addEventListener('change', function (e) {
      var el = e.target, f = el.getAttribute('data-f');
      if (!f) return;
      var tr = el.closest('tr'), x = S.items[+tr.getAttribute('data-i')];
      if (f === 'id') {
        var nid = el.value.trim();
        if (!nid) { toast('요구사항ID를 입력하세요', true); render(); return; }
        if (S.items.some(function (o) { return o !== x && o.id === nid; })) {
          toast('이미 등록된 요구사항ID입니다: ' + nid, true); render(); return;
        }
        x.id = nid;
      } else if (f === 'custITOwner') { x.custIT = x.custIT || {}; x.custIT.owner = el.value; }
      else if (f === 'custITTeam') { x.custIT = x.custIT || {}; x.custIT.team = el.value; }
      else if (f === 'custBizOwner') { x.custBiz = x.custBiz || {}; x.custBiz.owner = el.value; }
      else if (f === 'custBizTeam') { x.custBiz = x.custBiz || {}; x.custBiz.team = el.value; }
      else { x[f] = el.value; }
      render();
    });
    $('histModal').addEventListener('click', function (e) {
      if (e.target === this || e.target.hasAttribute('data-close')) closeHist();
    });
    $('tbody').addEventListener('click', function (e) {
      var h = e.target.closest('[data-hist]');
      if (h) { openHist(+h.closest('tr').getAttribute('data-i')); return; }
      var b = e.target.closest('[data-del]');
      if (!b || b.disabled) return;
      var tr = b.closest('tr'), i = +tr.getAttribute('data-i'), x = S.items[i];
      if (x.id && isUsed(x.id)) { toast('사용 중인 요구사항ID는 삭제할 수 없습니다', true); return; }
      if (!confirm('"' + (x.id || '(신규)') + '" 항목을 삭제할까요?')) return;
      S.items.splice(i, 1);
      render();
      toast('삭제했습니다. 저장 버튼으로 반영하세요');
    });
  }

  /* 개정이력 팝업 — 회의록 검토 화면에서 반영된 변경 기록(근거 회의, 확정자·일시) 조회 */
  function openHist(i) {
    S.histIdx = i;
    renderHist();
    $('histModal').classList.add('open');
  }
  function renderHist() {
    var x = S.items[S.histIdx];
    var revs = (x.revisions || []).slice().reverse();
    var entries = revs.map(function (r) {
      return '<div class="remark-item"><div class="meta"><span class="tag">' + esc(r.ts) + ' · ' + esc(r.who) + '</span></div>' +
        '<div class="body">' + esc(r.note || '요구사항내역 변경') + '</div>' +
        (r.meetingFile ? '<div class="file-chip">🗂 ' + esc(r.meetingFile) + (r.decisionId ? ' · ' + esc(r.decisionId) : '') + '</div>' : '') +
        '</div>';
    }).join('') || '<div class="empty">회의록을 근거로 반영된 개정 이력이 없습니다.</div>';
    $('histBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + esc(x.name || x.id) + ' — 개정이력</h3>' +
      '<p>' + esc(x.id) + ' · 회의록 검토(AI 회의록 검토)에서 확정 반영 시 자동 기록</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-list">' + entries + '</div>';
  }
  function closeHist() { $('histModal').classList.remove('open'); }

  function applyReqIdParam() {
    var m = /[?&]reqId=([^&]+)/.exec(location.search);
    if (!m) return;
    var id = decodeURIComponent(m[1]);
    var hit = S.items.filter(function (x) { return x.id === id; });
    if (!hit.length) { toast('요구사항ID를 찾을 수 없습니다: ' + id, true); return; }
    hit[0]._flash = true;
    S.filter.q = id;
    $('fQ').value = id;
  }

  async function boot() {
    try {
      S.items = (await fetchJSON('/api/requirements')).items;
      var keys = Object.keys(SOURCES);
      var res = await Promise.all(keys.map(function (k) { return load(k, SOURCES[k]); }));
      keys.forEach(function (k, i) { S.src[k] = res[i].data.items; });
    } catch (e) {
      $('tbody').innerHTML = '<tr><td colspan="15" class="empty">데이터를 읽지 못했습니다 (' + esc(e.message) +
        '). 로컬 서버로 실행하세요: python3 server.py</td></tr>';
      return;
    }
    applyReqIdParam();
    bind();
    render();
  }

  boot();
})();
