/* AS-IS 목록(물리ID 관리) — 조회 / 추가 / 수정 / 삭제
 * 데이터: data/asis.json (저장은 DB, 내보내기로 파일에 반영)
 * 사용 중인 물리ID는 삭제·ID 변경 불가 (설계·분석·개발·테스트 매핑 무결성)
 */
(function () {
  'use strict';

  var KEY = 'traceops-simple:';
  var TYPES = ['화면', '프로그램', '배치', '인터페이스', '기타'];
  var STATUS = ['사용확정', '사용중지'];
  var SOURCES = { design: '/api/design', dev: '/api/dev', analysis: '/api/analysis', unit: '/api/unit', integration: '/api/integration' };
  var S = { items: [], src: {}, draft: false, filter: { type: '', q: '' } };

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

  /* 사용처 집계: 분석/설계/개발/단위/통합 어디에 몇 건 매핑되어 있는지 */
  function usageOf(id) {
    var u = { 설계: 0, 분석: 0, 개발: 0, 단위: 0, 통합: 0, total: 0 };
    var map = { design: '설계', analysis: '분석', dev: '개발', unit: '단위', integration: '통합' };
    Object.keys(map).forEach(function (k) {
      (S.src[k] || []).forEach(function (x) {
        if ((x.physIds || []).indexOf(id) >= 0) { u[map[k]]++; u.total++; }
      });
    });
    return u;
  }
  function isUsed(id) { return id && usageOf(id).total > 0; }

  function visibleIdx() {
    var q = S.filter.q.toLowerCase();
    var out = [];
    S.items.forEach(function (x, i) {
      if (S.filter.type && x.type !== S.filter.type) return;
      if (q && [x.id, x.name, x.group, x.relatedScreen].join(' ').toLowerCase().indexOf(q) < 0) return;
      out.push(i);
    });
    return out;
  }
  function opts(list, val) {
    return list.map(function (o) {
      return '<option' + (o === val ? ' selected' : '') + '>' + esc(o) + '</option>';
    }).join('');
  }
  function rowHTML(x, i) {
    var u = usageOf(x.id), used = u.total > 0;
    var idCell = used
      ? '<span class="disabled-field">' + esc(x.id) + '</span>'
      : '<input class="txt-input" data-f="id" value="' + esc(x.id) + '" placeholder="물리ID" style="width:170px">';
    return '<tr data-i="' + i + '">' +
      '<td><select class="txt-input" data-f="type">' + opts(TYPES, x.type) + '</select></td>' +
      '<td>' + idCell + '</td>' +
      '<td><input class="txt-input" data-f="name" value="' + esc(x.name) + '" style="width:200px"></td>' +
      '<td><input class="txt-input" data-f="group" value="' + esc(x.group) + '" style="width:130px"></td>' +
      '<td><input class="txt-input" data-f="relatedScreen" value="' + esc(x.relatedScreen) + '" style="width:130px"></td>' +
      '<td><select class="txt-input" data-f="status">' + opts(STATUS, x.status) + '</select></td>' +
      '<td class="mono">설계 ' + u.설계 + ' · 분석 ' + u.분석 + ' · 개발 ' + u.개발 + ' · 단위 ' + u.단위 + ' · 통합 ' + u.통합 + '</td>' +
      '<td><input class="txt-input" data-f="remark" value="' + esc(x.remark) + '" style="width:160px"></td>' +
      '<td><button class="btn ghost sm" data-del="1"' + (used ? ' disabled title="사용 중인 물리ID는 삭제할 수 없습니다"' : '') + '>삭제</button></td>' +
      '</tr>';
  }
  function validateAll() {
    var seen = {}, errs = 0, msgs = [];
    S.items.forEach(function (x) {
      if (!x.id) { errs++; msgs.push('물리ID 미입력'); return; }
      if (seen[x.id]) { errs++; msgs.push('중복 물리ID: ' + x.id); }
      seen[x.id] = true;
    });
    return { errs: errs, msgs: msgs };
  }
  function render() {
    var idx = visibleIdx();
    $('tbody').innerHTML = idx.length
      ? idx.map(function (i) { return rowHTML(S.items[i], i); }).join('')
      : '<tr><td colspan="9" class="empty">조건에 맞는 항목이 없습니다.</td></tr>';
    $('count').innerHTML = '<b>' + idx.length + '</b>건 (전체 ' + S.items.length + '건)';
    var v = validateAll();
    $('banner').innerHTML = v.errs
      ? '<div class="validation-banner">⚠ ' + esc(v.msgs.join(' / ')) + '</div>'
      : '';
    $('dataState').textContent = '관계형 DB(traceops.db) 사용 중 · 설계·개발에서 사용 중인 물리ID는 삭제할 수 없음';
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
      S.items = (await api('PUT', '/api/asis', { items: cleanItems() })).items;
      toast('저장되었습니다');
    } catch (e) { toast('저장 실패: ' + e.message, true); }
    render();
  }
  function exportFile() {
    var blob = new Blob([JSON.stringify({ kind: 'asis', items: cleanItems() }, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'asis.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast('asis.json 내보내기 완료 · data/asis.json에 덮어쓰면 원본이 됩니다');
  }
  async function restore() {
    if (!confirm('저장하지 않은 변경을 버리고 DB에 저장된 내용으로 되돌릴까요?')) return;
    try {
      S.items = (await fetchJSON('/api/asis')).items;
      render();
      toast('DB 저장본으로 되돌렸습니다');
    } catch (e) { toast('읽지 못했습니다: ' + e.message, true); }
  }

  function bind() {
    $('fType').addEventListener('change', function (e) { S.filter.type = e.target.value; render(); });
    $('fQ').addEventListener('input', function (e) { S.filter.q = e.target.value.trim(); render(); });
    $('btnAdd').addEventListener('click', function () {
      S.items.unshift({ id: '', type: '화면', name: '', group: '가입설계/청약', relatedScreen: '', status: '사용확정', remark: '', _new: true });
      S.filter = { type: '', q: '' };
      $('fType').value = ''; $('fQ').value = '';
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
        if (!nid) { toast('물리ID를 입력하세요', true); render(); return; }
        if (S.items.some(function (o) { return o !== x && o.id === nid; })) {
          toast('이미 등록된 물리ID입니다: ' + nid, true); render(); return;
        }
        x.id = nid;
      } else {
        x[f] = el.value;
      }
      render();
    });
    $('tbody').addEventListener('click', function (e) {
      var b = e.target.closest('[data-del]');
      if (!b || b.disabled) return;
      var tr = b.closest('tr'), i = +tr.getAttribute('data-i'), x = S.items[i];
      if (x.id && isUsed(x.id)) { toast('사용 중인 물리ID는 삭제할 수 없습니다', true); return; }
      if (!confirm('"' + (x.id || '(신규)') + '" 항목을 삭제할까요?')) return;
      S.items.splice(i, 1);
      render();
      toast('삭제했습니다. 저장 버튼으로 반영하세요');
    });
  }

  async function boot() {
    try {
      S.items = (await fetchJSON('/api/asis')).items;
      var keys = Object.keys(SOURCES);
      var res = await Promise.all(keys.map(function (k) { return load(k, SOURCES[k]); }));
      keys.forEach(function (k, i) { S.src[k] = res[i].data.items; });
    } catch (e) {
      $('tbody').innerHTML = '<tr><td colspan="9" class="empty">데이터를 읽지 못했습니다 (' + esc(e.message) +
        '). 로컬 서버로 실행하세요: python3 -m http.server 8000</td></tr>';
      return;
    }
    bind();
    render();
  }

  boot();
})();
