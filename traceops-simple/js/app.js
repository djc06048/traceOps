/* TraceOps 단순 버전 — 상세공정관리(분석/설계/개발) + 테스트관리(단위/통합)
 * 모든 데이터는 data/*.json 을 읽어서 동작한다. DB 없음.
 * 편집 내용은 브라우저 임시저장(localStorage)에 남고, 내보내기로 JSON을 받아 data/ 원본에 덮어쓸 수 있다.
 */
(function () {
  'use strict';

  var FILES = {
    master: 'data/master.json',
    asis: 'data/asis.json',
    analysis: 'data/analysis.json',
    design: 'data/design.json',
    dev: 'data/dev.json',
    unit: 'data/unit.json',
    integration: 'data/integration.json'
  };
  var DRAFT_KEY = 'traceops-simple-v2:';

  var PAGES = {
    analysis:    { kind: 'stage', tab: 'detail', file: 'analysis', typesKey: 'analysis', prefix: 'ANL', nameLabel: '분석명', title: '분석단계 조회 및 관리', desc: '분석 항목(현황업무분석)의 계획·실적·증적을 관리합니다.' },
    design:      { kind: 'stage', tab: 'detail', file: 'design', typesKey: 'design', prefix: 'SCR', nameLabel: '설계명', title: '설계단계 조회 및 관리', desc: '화면·프로그램·배치·인터페이스 설계 항목을 검색하고, 요구사항ID·물리ID를 매핑합니다.' },
    dev:         { kind: 'stage', tab: 'detail', file: 'dev', typesKey: 'dev', prefix: 'DEV', nameLabel: '프로그램명', title: '개발단계 조회 및 관리', desc: '설계 항목을 참조해 개발(프로그램) 항목을 관리합니다.' },
    unit:        { kind: 'test', tab: 'test', file: 'unit', prefix: 'TU', multi: false, title: '단위테스트 관리', desc: '개발 항목에 연결된 단위테스트 케이스와 수행 결과를 관리합니다.' },
    integration: { kind: 'test', tab: 'test', file: 'integration', prefix: 'TI', multi: true, title: '통합테스트 관리', desc: '여러 개발 항목을 묶은 통합테스트 케이스와 수행 결과를 관리합니다.' }
  };
  var TABS = {
    detail: [['analysis', '분석단계'], ['design', '설계단계'], ['dev', '개발단계']],
    test: [['unit', '단위테스트'], ['integration', '통합테스트']]
  };
  var GROUP_LABEL = {
    sys: '시스템·서브시스템', workerPlan: '작업자 계획기간', workerActual: '작업자 실적기간',
    plPlan: 'PL 계획기간', plActual: 'PL 실적기간', devMeta: '개발유형·차수', mapping: '매핑'
  };
  var STATUS_ORDER = { '지연': 0, '진행중': 1, '미착수': 2, '완료': 3 };
  var STATUS_CLS = { '지연': 'late', '진행중': 'doing', '미착수': 'todo', '완료': 'done' };
  // 단계별 하위 연결 (상위 항목을 가리키는 하위 항목의 필드)
  var CHAIN = {
    analysis: { to: 'design', key: 'analysisRef', label: '설계' },
    design: { to: 'dev', key: 'designRef', label: '개발' },
    dev: { to: 'unit', key: 'linked', label: '단위테스트' },
    unit: { to: 'integration', key: 'units', label: '통합테스트' }
  };
  var TRI = '<svg class=\"tri\" width=\"14\" height=\"13\" viewBox=\"0 0 14 13\" aria-label=\"오류\"><path d=\"M7 .8 L13.4 12.2 H.6 Z\" fill=\"#D64545\"/><rect x=\"6.15\" y=\"4.3\" width=\"1.7\" height=\"4.3\" rx=\".8\" fill=\"#fff\"/><rect x=\"6.15\" y=\"9.5\" width=\"1.7\" height=\"1.7\" rx=\".85\" fill=\"#fff\"/></svg>';
  // 값 셀 클릭 시 이동: 대상 화면과 조회 조건 키
  var NAV = { designRef: ['design', 'id'], analysisRef: ['analysis', 'id'], reqIds: ['__ext', 'requirementsUrl'], physIds: ['design', 'physId'], linked: ['dev', 'id'], units: ['unit', 'id'] };
  var PAGE_NAME = { analysis: '분석', design: '설계', dev: '개발', unit: '단위테스트', integration: '통합테스트' };
  // 실적 날짜: 오늘 이후 입력 불가
  var ACTUAL_KEYS = ['wActStart', 'wActEnd', 'pActStart', 'pActEnd', 'execDate'];
  // 매핑 팝업에서 다른 관리 화면으로 넘어가는 링크 (화면이 만들어지면 master.json 주소만 연결)
  var LINK_TARGETS = {
    reqIds: { key: 'requirementsUrl', label: '요구사항 관리에서 등록 (TODO)' },
    physIds: { key: 'physicalIdsUrl', label: 'AS-IS 목록에서 물리ID 관리' }
  };

  var S = {
    master: null, data: {}, draft: {},
    mode: 'pl', account: '', route: 'analysis',
    hidden: { sys: true }, applied: {}, pick: null, pop: null
  };

  /* ---------- 공통 유틸 ---------- */
  function $(id) { return document.getElementById(id); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function p2(n) { return String(n).padStart(2, '0'); }
  function todayISO() { var d = new Date(); return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function tag(iso) { return '[' + iso.slice(2, 4) + iso.slice(5, 7) + iso.slice(8, 10) + ']'; }
  function arr(v) { return Array.isArray(v) ? v : []; }
  function me() { return S.mode === 'pl' ? S.master.pl.name : S.account; }
  function pageOf() { return PAGES[S.route]; }
  function items(page) { return S.data[page.file].items; }
  function find(page, id) {
    return items(page).filter(function (x) { return x.id === id; })[0];
  }
  var toastTimer;
  function showToast(msg, isErr) {
    var t = $('toast');
    t.textContent = msg;
    t.classList.toggle('err', !!isErr);
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }
  function nextId(prefix, all) {
    var head = prefix + '-' + new Date().getFullYear() + '-', max = 0;
    all.forEach(function (x) {
      if (x.id.indexOf(head) === 0) {
        var n = parseInt(x.id.slice(head.length), 10);
        if (n > max) max = n;
      }
    });
    return head + String(max + 1).padStart(4, '0');
  }
  function sysNames() { return S.master.systems.map(function (s) { return s.name; }); }
  function subsOf(sys) {
    var s = S.master.systems.filter(function (x) { return x.name === sys; })[0];
    return s ? s.subs : [];
  }
  function allSubs() {
    var out = [];
    S.master.systems.forEach(function (s) {
      s.subs.forEach(function (x) { if (out.indexOf(x) < 0) out.push(x); });
    });
    return out;
  }

  /* ---------- 상태 / 검증 ---------- */
  function statusOf(it) {
    if (it.wActEnd) return '완료';
    if (it.wPlanEnd && it.wPlanEnd < todayISO()) return '지연';
    if (it.wActStart) return '진행중';
    return '미착수';
  }
  function getVal(it, f) { return f === 'status' ? statusOf(it) : it[f]; }

  function actualErrors(it, err) {
    var t = todayISO();
    var fut = ACTUAL_KEYS.filter(function (k) { return it[k] && it[k] > t; });
    if (fut.length) err.push({ t: '실적 날짜가 오늘 이후', h: '실적 날짜는 오늘(' + t + ')까지만 입력할 수 있습니다. 날짜를 수정하세요.', f: fut[0] });
    if (it.wActStart && it.wActEnd && it.wActEnd < it.wActStart) err.push({ t: '실적 종료일이 시작일보다 빠름', h: '작업자 실적 종료일을 시작일 이후로 수정하세요.', f: 'wActEnd' });
    if (it.pActStart && it.pActEnd && it.pActEnd < it.pActStart) err.push({ t: 'PL 실적 종료일이 시작일보다 빠름', h: 'PL 실적 종료일을 시작일 이후로 수정하세요.', f: 'pActEnd' });
  }
  // 반환: { err: 입력·매핑 필요 항목, info: 하위 연결 특이사항 } — 각 항목은 {t: 문제, h: 해결 방법, f: 수정할 칸, g: 이동할 화면}
  function checkItem(page, it, all) {
    var err = [], info = [], st = page.kind === 'stage', ty = page.typesKey;
    if (st) {
      if (!it.name) err.push({ t: '명 미입력', h: '명칭을 입력하세요.', f: 'name' });
      if (!it.worker) err.push({ t: '작업자 미지정', h: '작업자를 선택하세요. 선택하면 그 업무가 해당 작업자에게 할당됩니다.', f: 'worker' });
      if (!it.wPlanStart || !it.wPlanEnd) err.push({ t: '작업자 계획기간 미등록', h: '계획 시작·종료일이 없습니다. 작업자 계획기간은 PL도 수정할 수 없으므로 데이터 파일에서 입력해야 합니다.', f: null });
      if (!arr(it.reqIds).length) err.push(ty === 'analysis'
        ? { t: '요구사항 미등록', h: '요구사항ID를 선택하세요. 요구사항은 분석 단계에서 정하고 아래 단계가 물려받습니다.', f: 'reqIds' }
        : { t: '요구사항 미등록', h: '분석 항목에 요구사항이 없습니다. 분석 항목의 요구사항을 먼저 지정하세요.', f: null });
      if (ty !== 'analysis' && !arr(it.physIds).length) err.push({ t: '물리ID 미등록', h: '물리ID를 선택하세요. 목록에 없으면 AS-IS 목록에서 먼저 등록하세요.', f: 'physIds' });
      if (ty === 'design' && !arr(it.analysisRef).length) err.push({ t: '분석ID 미연결', h: '이 설계가 근거하는 분석 항목을 선택하세요.', f: 'analysisRef' });
      if (ty === 'dev' && !arr(it.designRef).length) err.push({ t: '설계ID 미연결', h: '이 개발이 구현하는 설계 항목을 선택하세요.', f: 'designRef' });
      if (all.filter(function (x) { return x.id === it.id; }).length > 1) err.push({ t: 'ID 중복', h: '같은 ID가 여러 번 등록되어 있습니다. 데이터를 확인하세요.', f: null });
      actualErrors(it, err);
    } else {
      if (!it.name) err.push({ t: '테스트명 미입력', h: '테스트명을 입력하세요.', f: 'name' });
      if (!arr(it.linked).length) err.push(page.multi
        ? { t: '연계 개발ID 미지정', h: '이 통합테스트가 묶는 개발 항목을 선택하세요.', f: 'linked' }
        : { t: '개발ID 미연결', h: '이 단위테스트가 검증하는 개발 항목을 선택하세요.', f: 'linked' });
      if (page.multi && !arr(it.units).length) err.push({ t: '묶인 단위테스트 없음', h: '통합테스트에 포함할 단위테스트를 선택하세요.', f: 'units' });
      if (!arr(it.reqIds).length) err.push({ t: '요구사항 미등록', h: '개발 항목의 요구사항에서 상속됩니다. 개발 항목을 확인하세요.', f: null });
      if (!arr(it.physIds).length) err.push({ t: '물리ID 미등록', h: '설계 항목의 물리ID에서 상속됩니다. 설계 항목을 확인하세요.', f: null });
      if (!it.worker) err.push({ t: '담당자 미지정', h: '담당자를 선택하세요.', f: 'worker' });
      if (!it.expected) err.push({ t: '기대결과 미입력', h: '검증할 기대 동작을 작성하세요.', f: 'expected' });
      if (it.result === 'FAIL' && !arr(it.evidence).length) err.push({ t: 'FAIL 증적 미첨부', h: '실패 결과는 증적을 등록해야 저장됩니다. 증적 칸에서 등록하세요.', f: 'evidence' });
      actualErrors(it, err);
    }
    var ch = CHAIN[page.file];
    if (ch && chainCount(page.file, it) === 0) {
      info.push({ t: (st ? '하위 ' : '') + ch.label + ' 미등록', h: ch.label + ' 항목을 추가하고 이 항목과 연결하세요.', g: ch.to });
    }
    if (it.recheck) {
      info.push({ t: '재검증 필요', h: '상위의 요구사항·물리ID·설계 연결이 바뀌었습니다. 결과와 실적을 확인한 뒤 "재검증 완료"를 누르세요.', f: null, rc: true });
    }
    return { err: err, info: info };
  }
  function uniq(list) { return list.filter(function (x, i) { return list.indexOf(x) === i; }); }
  function syncDown() {
    var A = {}, D = {}, V = {};
    S.data.analysis.items.forEach(function (x) { A[x.id] = x; });
    S.data.design.items.forEach(function (x) { D[x.id] = x; });
    S.data.dev.items.forEach(function (x) { V[x.id] = x; });
    S.data.design.items.forEach(function (d) {
      var a = A[arr(d.analysisRef)[0]];
      if (a) d.reqIds = arr(a.reqIds).slice();
    });
    S.data.dev.items.forEach(function (v) {
      var d = D[arr(v.designRef)[0]];
      if (!d) return;
      v.reqIds = arr(d.reqIds).slice();
      v.physIds = uniq(arr(d.physIds).concat(arr(v.physIdsAdd)));
    });
    S.data.unit.items.forEach(function (u) {
      var v = V[arr(u.linked)[0]];
      if (!v) return;
      u.reqIds = arr(v.reqIds).slice();
      u.physIds = arr(v.physIds).slice();
    });
    S.data.integration.items.forEach(function (t) {
      var rs = [], ps = [];
      arr(t.linked).forEach(function (l) {
        var v = V[l];
        if (!v) return;
        arr(v.reqIds).forEach(function (r) { if (rs.indexOf(r) < 0) rs.push(r); });
        arr(v.physIds).forEach(function (p) { if (ps.indexOf(p) < 0) ps.push(p); });
      });
      t.reqIds = rs; t.physIds = ps;
    });
  }
  function dependentsOf(file, it) {
    var ch = CHAIN[file], out = [];
    if (ch) S.data[ch.to].items.forEach(function (x) { if (arr(x[ch.key]).indexOf(it.id) >= 0) out.push(x.id); });
    if (file === 'dev') S.data.integration.items.forEach(function (x) { if (arr(x.linked).indexOf(it.id) >= 0) out.push(x.id); });
    return out;
  }
  /* ---------- 연관 영향 안내 (연결 변경·삭제 전 미리보기) ---------- */
  var IMPACT_FILES = ['analysis', 'design', 'dev', 'unit', 'integration'];
  var IMPACT_FIELDS = ['reqIds', 'physIds', 'designRef', 'analysisRef', 'linked', 'units', 'result', 'execDate', 'evidence', 'recheck'];
  var IMPACT_LABEL = { reqIds: '요구사항ID', physIds: '물리ID', designRef: '설계ID', analysisRef: '분석ID', linked: '개발ID', units: '단위테스트', result: '결과', execDate: '수행일', evidence: '증적', recheck: '재검증 필요' };
  var FILE_LABEL = { analysis: '분석', design: '설계', dev: '개발', unit: '단위테스트', integration: '통합테스트' };
  function snapData() { return JSON.parse(JSON.stringify(S.data)); }
  function restoreData(snap) { Object.keys(snap).forEach(function (k) { S.data[k] = snap[k]; }); }
  function fmt(k, v) {
    if (typeof v === 'boolean') return v ? '예' : '아니오';
    if (k === 'evidence') return arr(v).length + '건';
    if (Array.isArray(v)) return v.length ? v.join(', ') : '없음';
    return v === '' || v == null ? '없음' : String(v);
  }
  function diffData(before) {
    var out = [];
    IMPACT_FILES.forEach(function (f) {
      var prev = {}, cur = {};
      before[f].items.forEach(function (x) { prev[x.id] = x; });
      S.data[f].items.forEach(function (x) { cur[x.id] = x; });
      Object.keys(prev).forEach(function (id) {
        if (!cur[id]) { out.push({ f: f, id: id, name: prev[id].name, removed: true, changes: [] }); return; }
        var ch = [];
        IMPACT_FIELDS.forEach(function (k) {
          var a = JSON.stringify(prev[id][k] == null ? null : prev[id][k]), b = JSON.stringify(cur[id][k] == null ? null : cur[id][k]);
          if (a !== b) ch.push({ k: k, from: fmt(k, prev[id][k]), to: fmt(k, cur[id][k]) });
        });
        if (ch.length) out.push({ f: f, id: id, name: cur[id].name, removed: false, changes: ch });
      });
    });
    return out;
  }
  // mutate: 실제 변경 함수. 먼저 임시 적용해 영향을 계산한 뒤 원복하고, 확인 후 다시 적용한다.
  // 내용(요구사항·물리ID·설계·분석 연결)이 바뀐 하위 항목에 재검증 표시. 직접 바꾼 소유 항목은 제외.
  function recheckFlags(diff, source) {
    var out = [];
    diff.forEach(function (d) {
      if (d.removed) return;
      var hit = d.changes.some(function (c) {
        if (c.k === 'designRef' || c.k === 'analysisRef') return true;
        if (c.k === 'reqIds' || c.k === 'physIds') return !(source && source.id === d.id);
        return false;
      });
      if (hit) out.push({ f: d.f, id: d.id });
    });
    return out;
  }
  function applyRecheck(flags) {
    (flags || []).forEach(function (r) {
      var it = S.data[r.f].items.filter(function (x) { return x.id === r.id; })[0];
      if (it) it.recheck = true;
    });
  }
  function withImpact(title, mutate, source) {
    var before = snapData();
    mutate();
    syncDown();
    var diff = diffData(before);
    restoreData(before);
    if (!diff.length) { mutate(); syncDown(); renderTable(); return; }
    S.impact = { title: title, diff: diff, mutate: mutate, flags: recheckFlags(diff, source) };
    renderImpact();
    $('impactModal').classList.add('open');
  }
  function renderImpact() {
    var I = S.impact, del = I.diff.filter(function (d) { return d.removed; }).length;
    var rows = I.diff.map(function (d) {
      var tagc = d.note ? 'block' : (d.removed ? 'del' : 'chg');
      var head = '<div class="im-h"><span class="im-tag ' + tagc + '">' + (d.note || (d.removed ? '삭제' : '변경')) + '</span> ' +
        FILE_LABEL[d.f] + ' · <b>' + esc(d.id) + '</b> ' + esc(d.name || '') + '</div>';
      var body = d.note
        ? '<div class="im-b">먼저 정리해야 삭제할 수 있습니다</div>'
        : d.removed
        ? '<div class="im-b">연결 기준에 따라 함께 삭제됩니다</div>'
        : d.changes.map(function (c) {
            return '<div class="im-b">' + IMPACT_LABEL[c.k] + ': ' + esc(c.from) + ' → <b>' + esc(c.to) + '</b></div>';
          }).join('');
      return '<div class="im">' + head + body + '</div>';
    }).join('');
    $('impactBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + esc(I.title) + '</h3>' +
      '<p>' + (I.block ? '하위 연결 또는 실적·증적이 있어 삭제할 수 없습니다' : '연관 항목 ' + I.diff.length + '건이 함께 바뀝니다' + (del ? ' (삭제 ' + del + '건)' : '')) + '</p></div>' +
      '<button class="modal-close" data-imp-cancel="1">✕</button></div>' +
      '<div class="modal-list">' + rows + '</div>' +
      (I.block
        ? '<div class="modal-input"><div class="row"><span class="imp-note">삭제 조건: 하위 연결이 없고, 실적·증적이 없어야 합니다.</span>' +
          '<span class="pick-btns"><button class="btn sm" data-imp-cancel="1">닫기</button></span></div></div>'
        : '<div class="modal-input"><div class="row"><span class="imp-note">진행하면 저장 전까지 임시 반영됩니다. 저장 버튼으로 확정하세요.</span>' +
          '<span class="pick-btns"><button class="btn ghost sm" data-imp-cancel="1">취소</button>' +
          '<button class="btn sm" data-imp-ok="1">진행</button></span></div></div>');
  }
  function closeImpact() { S.impact = null; $('impactModal').classList.remove('open'); }
  // 연결이 바뀐 단위테스트는 수행 결과가 무효이므로 초기화
  function resetResult(it) { it.result = '미실행'; it.execDate = ''; it.evidence = []; }
  // 삭제: 하위(설계→개발→단위)는 함께 삭제, 통합테스트는 묶음에서만 제외
  // 실적·증적 기록이 있는 항목: 기록 보존을 위해 삭제 차단
  function hasRecord(file, it) {
    if (file === 'unit' || file === 'integration') {
      return (it.result && it.result !== '미실행') || !!it.execDate || arr(it.evidence).length > 0;
    }
    return !!(it.wActStart || it.wActEnd || it.pActStart || it.pActEnd || arr(it.evidence).length);
  }
  // 삭제: 하위 연결과 실적·증적이 없을 때만 가능. 그 외에는 안내만 표시.
  function deleteRow(page, id) {
    var it = find(page, id);
    if (!it) return;
    var ch = CHAIN[page.file], blockers = [];
    dependentsOf(page.file, it).forEach(function (x) {
      var child = ch && S.data[ch.to].items.filter(function (y) { return y.id === x; })[0];
      blockers.push({ f: ch.to, id: x, name: child ? child.name : '', removed: true, changes: [], note: '하위 연결 있음' });
    });
    if (hasRecord(page.file, it)) blockers.push({ f: page.file, id: id, name: it.name, removed: true, changes: [], note: '실적·증적 있음' });
    if (blockers.length) {
      S.impact = { title: '"' + id + '" 삭제 불가', diff: blockers, mutate: null, block: true };
      renderImpact();
      $('impactModal').classList.add('open');
      return;
    }
    if (!confirm('"' + id + '" 항목을 삭제할까요?')) return;
    var list = items(page);
    list.splice(list.indexOf(it), 1);
    renderTable();
    showToast('삭제했습니다. 저장 버튼으로 반영하세요');
  }
  function chainCount(file, it) {
    var ch = CHAIN[file];
    if (!ch) return 0;
    return S.data[ch.to].items.filter(function (x) { return arr(x[ch.key]).indexOf(it.id) >= 0; }).length;
  }
  /* ---------- 검증 상세 팝업 ---------- */
  function openVCheck(page, id) {
    S.vpop = { page: page, id: id };
    renderVCheck();
    $('vModal').classList.add('open');
  }
  function renderVCheck() {
    var v = S.vpop, it = find(v.page, v.id);
    if (!it) return;
    var r = checkItem(v.page, it, items(v.page));
    var card = function (x, ic, cls) {
      var act = x.rc
        ? '<button class="btn sm" data-clear-recheck="1">재검증 완료</button>'
        : x.g
        ? '<button class="btn sm" data-goto="' + x.g + '">' + PAGE_NAME[x.g] + ' 화면에서 등록 →</button>'
        : (x.f ? '<button class="btn sm" data-focus="' + x.f + '">해당 칸으로 이동</button>'
               : '<span class="vi-note">이 항목은 화면에서 직접 수정할 수 없습니다</span>');
      return '<div class="vi ' + cls + '"><div class="vi-top"><span class="vi-ic">' + ic + '</span><span class="vi-t">' + esc(x.t) + '</span></div>' +
        '<div class="vi-hint">' + esc(x.h) + '</div><div class="vi-act">' + act + '</div></div>';
    };
    var body = r.err.map(function (x) { return card(x, TRI, 'is-err'); })
      .concat(r.info.map(function (x) { return card(x, x.rc ? '🔁' : '🔗', 'is-info'); })).join('');
    $('vBox').innerHTML =
      '<div class="modal-hd"><div><h3>검증 상세</h3><p>' + esc(v.id) + ' · ' + esc(it.name || '') + '</p>' +
      '<p class="vi-legend">' + TRI + ' 입력·매핑 필요 ' + r.err.length + '건 · 🔗 하위 연결 ' + r.info.length + '건</p></div>' +
      '<button class="modal-close" data-close="1">✕</button></div>' +
      '<div class="modal-list">' + (body || '<div class="empty">정합성 문제가 없습니다.</div>') + '</div>';
  }
  function closeVCheck() { S.vpop = null; $('vModal').classList.remove('open'); }
  function focusCell(id, f) {
    var tr = $('tbody').querySelector('tr[data-id="' + id + '"]');
    if (!tr) { showToast('현재 검색 조건에서 숨겨져 있습니다. 초기화 후 다시 시도하세요', true); return; }
    var sel = f === 'worker' ? '[data-worker], [data-k="worker"]'
      : '[data-k="' + f + '"], [data-pick="' + f + '"], [data-pop="' + f + '"]';
    var el = tr.querySelector(sel);
    tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    tr.classList.add('flash');
    setTimeout(function () { tr.classList.remove('flash'); }, 1800);
    if (!el) { showToast('이 칸이 표시 컬럼에서 꺼져 있습니다. 표시 컬럼에서 켜 주세요', true); return; }
    if (el.tagName === 'BUTTON') el.click();
    else el.focus();
  }
  function needsEvidence(page, it) {
    if (page.kind === 'test') return it.result === 'FAIL' && !arr(it.evidence).length;
    return !!it.wActStart && !arr(it.evidence).length;
  }

  /* ---------- 컬럼 정의 ---------- */
  function columnsOf(page) {
    var c = [], t = page.typesKey;
    c.push({ k: 'v', label: '검증', kind: 'v' });
    if (page.kind === 'stage') {
      c.push({ k: 'system', label: '시스템', kind: 'sys', edit: 'pl', g: 'sys' });
      c.push({ k: 'subsystem', label: '서브시스템', kind: 'sub', edit: 'pl', g: 'sys' });
      c.push({ k: 'type', label: '처리유형', kind: 'typeSel', edit: t === 'analysis' ? 'none' : 'pl' });
      c.push({ k: 'id', label: 'ID', kind: 'id' });
      c.push({ k: 'name', label: page.nameLabel, kind: 'text', edit: 'pl', w: 140 });
      if (t === 'dev') c.push({ k: 'desc', label: '설명', kind: 'text', edit: 'pl', w: 160 });
      c.push({ k: 'status', label: '진행상태', kind: 'status' });
      c.push({ k: 'worker', label: '작업자', kind: 'worker', edit: 'pl' });
      c.push({ k: 'wPlanStart', label: '작업자 계획기간', sub: '시작일', kind: 'date', edit: 'none', g: 'workerPlan' });
      c.push({ k: 'wPlanEnd', label: '작업자 계획기간', sub: '종료일', kind: 'date', edit: 'none', g: 'workerPlan' });
      c.push({ k: 'wActStart', label: '작업자 실적기간', sub: '시작일', kind: 'date', edit: 'worker', g: 'workerActual' });
      c.push({ k: 'wActEnd', label: '작업자 실적기간', sub: '종료일', kind: 'date', edit: 'worker', g: 'workerActual' });
      c.push({ k: 'evidence', label: '증적', kind: 'evidence' });
      c.push({ k: 'pPlanStart', label: 'PL 계획기간', sub: '시작일', kind: 'date', edit: 'pl', g: 'plPlan', plOnly: true });
      c.push({ k: 'pPlanEnd', label: 'PL 계획기간', sub: '종료일', kind: 'date', edit: 'pl', g: 'plPlan', plOnly: true });
      c.push({ k: 'pActStart', label: 'PL 실적기간', sub: '시작일', kind: 'date', edit: 'pl', g: 'plActual', plOnly: true });
      c.push({ k: 'pActEnd', label: 'PL 실적기간', sub: '종료일', kind: 'date', edit: 'pl', g: 'plActual', plOnly: true });
      if (t !== 'analysis') {
        c.push({ k: 'devType', label: '개발유형', kind: 'select', opts: ['신규', '변경'], edit: 'pl', g: 'devMeta' });
        c.push({ k: 'devRound', label: '개발차수', kind: 'select', opts: ['1차', '2차'], edit: 'pl', g: 'devMeta' });
      }
      if (t === 'dev') {
        c.push({ k: 'difficulty', label: '난이도', kind: 'select', opts: ['상', '중', '하'], blank: true, edit: 'pl' });
        c.push({ k: 'priority', label: '우선순위', kind: 'select', opts: ['P1', 'P2', 'P3'], blank: true, edit: 'pl' });
      }
      if (t === 'design') c.push({ k: 'analysisRef', label: '분석ID', kind: 'chips', src: 'analysisIds', max: 1, edit: 'pl', g: 'mapping' });
      if (t === 'dev') c.push({ k: 'designRef', label: '설계ID', kind: 'chips', src: 'designIds', max: 1, edit: 'pl', g: 'mapping' });
      c.push({ k: 'reqIds', label: '요구사항ID', kind: 'chips', src: 'reqIds', edit: t === 'analysis' ? 'pl' : 'none', g: 'mapping' });
      if (t !== 'analysis') c.push({ k: 'physIds', label: '물리ID', kind: 'chips', src: 'physIds', edit: 'pl', g: 'mapping' });
      c.push({ k: 'remark', label: '비고', kind: 'remark' });
      c.push({ k: 'del', label: '', kind: 'del', edit: 'pl', plOnly: true });
    } else {
      c.push({ k: 'id', label: 'ID', kind: 'id' });
      c.push({ k: 'name', label: '테스트명', kind: 'text', edit: 'pl', w: 170 });
      c.push({ k: 'linked', label: '연결 개발ID', kind: 'chips', src: 'devIds', max: page.multi ? 0 : 1, edit: 'pl', g: 'mapping' });
      if (page.multi) c.push({ k: 'units', label: '묶인 단위테스트', kind: 'chips', src: 'unitIds', edit: 'pl', g: 'mapping' });
      c.push({ k: 'reqIds', label: '요구사항ID', kind: 'chips', src: 'reqIds', edit: 'none', g: 'mapping' });
      c.push({ k: 'physIds', label: '물리ID', kind: 'chips', src: 'physIds', edit: 'none', g: 'mapping' });
      c.push({ k: 'expected', label: '기대결과', kind: 'text', edit: 'pl', w: 200 });
      c.push({ k: 'round', label: '테스트 차수', kind: 'select', opts: ['1차', '2차'], edit: 'pl' });
      c.push({ k: 'worker', label: '담당자', kind: 'worker', edit: 'pl' });
      c.push({ k: 'execDate', label: '수행일', kind: 'date', edit: 'worker' });
      c.push({ k: 'result', label: '결과', kind: 'select', opts: ['미실행', 'PASS', 'FAIL'], edit: 'worker' });
      c.push({ k: 'evidence', label: '증적', kind: 'evidence' });
      c.push({ k: 'remark', label: '비고', kind: 'remark' });
      c.push({ k: 'del', label: '', kind: 'del', edit: 'pl', plOnly: true });
    }
    return c;
  }
  function visibleCols(page) {
    return columnsOf(page).filter(function (c) {
      if (c.plOnly && S.mode === 'worker') return false;
      if (c.g && S.hidden[c.g]) return false;
      return true;
    });
  }
  function groupsOf(page) {
    var g = [];
    columnsOf(page).forEach(function (c) {
      if (!c.g || (c.plOnly && S.mode === 'worker')) return;
      if (g.indexOf(c.g) < 0) g.push(c.g);
    });
    return g;
  }
  function canEdit(c) {
    if (c.edit === 'pl') return S.mode === 'pl';
    if (c.edit === 'worker') return S.mode === 'worker';
    return false;
  }
  // 편집 가능하지만 아직 입력되지 않은 칸은 음영으로 표시
  function needClass(c, it) {
    if (!canEdit(c)) return '';
    var v = it[c.k];
    var empty = c.kind === 'chips' ? !arr(v).length : !v;
    return empty ? ' need' : '';
  }

  /* ---------- 셀 렌더링 ---------- */
  function opts(list, val, blank) {
    var h = blank ? '<option value="">-</option>' : '';
    if (val && list.indexOf(val) < 0) list = [val].concat(list);
    list.forEach(function (o) {
      h += '<option value="' + esc(o) + '"' + (o === val ? ' selected' : '') + '>' + esc(o) + '</option>';
    });
    return h;
  }
  function srcOptions(src) {
    if (src === 'reqIds') return S.master.reqIds.map(function (v) { return { id: v, label: v }; });
    if (src === 'designIds') return S.data.design.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
    if (src === 'analysisIds') return S.data.analysis.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
    if (src === 'physIds') return S.data.asis.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
    if (src === 'unitIds') return S.data.unit.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
    if (src === 'devIds') return S.data.dev.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
    return [];
  }
  function badge(page, it, key) {
    if (key === 'evidence') {
      var n = arr(it.evidence).length, req = needsEvidence(page, it);
      var cls = req ? 'required' : (n ? '' : 'zero');
      return '<button class="remark-badge ' + cls + '" data-pop="evidence">' + (req ? '📎 필요' : '📎 ' + n) + '</button>';
    }
    var r = arr(it.remarks).length;
    return '<button class="remark-badge ' + (r ? '' : 'zero') + '" data-pop="remarks">💬 ' + r + '</button>';
  }
  function chipsHTML(c, it, ed) {
    var vals = arr(it[c.k]);
    if (!vals.length) return ed ? '<button class="search-btn" data-pick="' + c.k + '">🔍 검색</button>' : '<span class="mono">-</span>';
    var more = vals.length > 1 ? ' 외 ' + (vals.length - 1) + '건' : '';
    return '<button class="chip-sum" data-chips="' + c.k + '" title="값 클릭: 조회' + (vals.length > 1 ? ' 목록' : '') + '">' + esc(vals[0]) + more + '</button>' +
      (ed ? ' <button class="chip-edit" data-chips-edit="' + c.k + '" title="추가·변경·제외">✎</button>' : '');
  }
  // 값 클릭: 1건이고 수정 불가면 바로 해당 화면 조회, 그 외에는 전체 목록 모달
  function goFilter(page, key, val) {
    if (page === '__ext') { location.href = S.master[key] + '?reqId=' + encodeURIComponent(val); return; }
    var target = '#' + page + '?' + key + '=' + encodeURIComponent(val);
    if (location.hash === target) route(); else location.hash = target;
  }
  function openChips(page, id, k) {
    var it = find(page, id), c = columnsOf(page).filter(function (x) { return x.k === k; })[0];
    if (!it || !c) return;
    var ed = canEdit(c), vals = arr(it[k]), nav = NAV[k];
    var inh = (page.file === 'dev' && k === 'physIds')
      ? arr((S.data.design.items.filter(function (d) { return d.id === arr(it.designRef)[0]; })[0] || {}).physIds) : [];
    var label = {};
    srcOptions(c.src).forEach(function (o) { label[o.id] = o.label; });
    S.chips = { page: page, id: id, k: k };
    var list = vals.map(function (v) {
      return '<div class="ci">' +
        (nav ? '<button class="ci-go" data-nav-page="' + nav[0] + '" data-nav-key="' + nav[1] + '" data-nav-val="' + esc(v) + '">' +
          esc(label[v] || v) + ' <span class="ci-arrow">→ 조회</span></button>' : '<span>' + esc(label[v] || v) + '</span>') +
        (inh.indexOf(v) >= 0 ? '<em class="inh">상속</em>' : (ed ? '<button class="x-btn" data-chip-rm="' + esc(v) + '">✕ 제외</button>' : '')) + '</div>';
    }).join('');
    $('chipBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + esc(c.label) + ' (' + vals.length + '건)</h3><p>' + esc(id) + ' · 항목을 누르면 해당 화면에서 조회합니다</p></div>' +
      '<button class="modal-close" data-close="1">✕</button></div>' +
      '<div class="modal-list">' + (list || '<div class="empty">연결된 항목이 없습니다.</div>') + '</div>' +
      '<div class="modal-input"><div class="row"><span></span><span class="pick-btns">' +
      (ed ? '<button class="btn ghost sm" data-chip-add="1">🔍 추가·변경</button>' : '') +
      '<button class="btn sm" data-close="1">닫기</button></span></div></div>';
    $('chipModal').classList.add('open');
  }
  function closeChips() { S.chips = null; $('chipModal').classList.remove('open'); }
  function cell(c, it, page, msgs) {
    var ed = canEdit(c), dis = ed ? '' : ' disabled', k = c.k, v = it[k];
    switch (c.kind) {
      case 'v':
        if (!msgs.err.length && !msgs.info.length) return '<span class="check-ok">✓</span>';
        return '<button class="v-btn" data-vcheck="1" title="검증 상세 보기">' +
          (msgs.err.length ? TRI + '<span class="check-err">' + msgs.err.length + '</span>' : '') +
          (msgs.info.some(function (x) { return x.rc; }) ? '<span class="chain-mark">🔁</span>' : '') +
          (msgs.info.some(function (x) { return !x.rc; }) ? '<span class="chain-mark">🔗</span>' : '') + '</button>';
      case 'id': return '<span class="disabled-field">' + esc(it.id) + '</span>';
      case 'status': var s = statusOf(it); return '<span class="st ' + STATUS_CLS[s] + '">' + s + '</span>';
      case 'sys': return '<select class="txt-input" data-k="system"' + dis + '>' + opts(sysNames(), v) + '</select>';
      case 'sub': return '<select class="txt-input" data-k="subsystem"' + dis + '>' + opts(subsOf(it.system), v) + '</select>';
      case 'typeSel': return '<select class="txt-input" data-k="type"' + dis + '>' + opts(S.master.types[page.typesKey], v) + '</select>';
      case 'text': return '<input class="txt-input" data-k="' + k + '" value="' + esc(v) + '" style="width:' + (c.w || 120) + 'px"' + dis + '>';
      case 'date': return '<input class="txt-input" type="date" data-k="' + k + '" value="' + esc(v) + '"' +
        (ACTUAL_KEYS.indexOf(k) >= 0 ? ' max="' + todayISO() + '"' : '') + dis + '>';
      case 'select': return '<select class="txt-input" data-k="' + k + '"' + dis + '>' + opts(c.opts, v, c.blank) + '</select>';
      case 'worker':
        if (S.mode === 'pl') {
          return '<button class="worker-btn' + (v ? '' : ' empty') + '" data-worker="1">' +
            (v ? esc(v) : '+ 작업자 선택') + '</button>';
        }
        return v ? esc(v) : '<span class="mono">-</span>';
      case 'chips': return chipsHTML(c, it, ed);
      case 'del': return S.mode === 'pl' ? '<button class="btn ghost sm" data-rowdel="1">삭제</button>' : '';
      case 'evidence': return badge(page, it, 'evidence');
      case 'remark': return badge(page, it, 'remarks');
    }
    return '';
  }

  /* ---------- 헤더 / 테이블 ---------- */
  function headerHTML(cols) {
    var r1 = '', r2 = '', i = 0;
    while (i < cols.length) {
      var c = cols[i];
      if (!c.g) { r1 += '<th rowspan="2">' + esc(c.label) + '</th>'; i++; continue; }
      var j = i;
      while (j < cols.length && cols[j].g === c.g) j++;
      if (j - i === 1) {
        r1 += '<th rowspan="2" class="grp">' + esc(c.label) + '</th>';
      } else {
        r1 += '<th colspan="' + (j - i) + '" class="grp">' + esc(GROUP_LABEL[c.g] || c.g) + '</th>';
        for (var q = i; q < j; q++) r2 += '<th class="grp">' + esc(cols[q].sub || cols[q].label) + '</th>';
      }
      i = j;
    }
    return '<tr>' + r1 + '</tr><tr>' + r2 + '</tr>';
  }
  function renderTable() {
    syncDown();
    var page = pageOf(), all = items(page), cols = visibleCols(page);
    var list = all.filter(function (it) { return passes(it, S.applied); });
    if (page.kind === 'stage') {
      list.sort(function (a, b) {
        var d = STATUS_ORDER[statusOf(a)] - STATUS_ORDER[statusOf(b)];
        return d || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
      });
    }
    $('thead').innerHTML = headerHTML(cols);
    $('tbody').innerHTML = list.length
      ? list.map(function (it) {
          var msgs = checkItem(page, it, all);
          return '<tr data-id="' + esc(it.id) + '">' + cols.map(function (c) {
            return '<td class="' + (c.kind === 'date' ? 'mono' : '') + needClass(c, it) + '">' + cell(c, it, page, msgs) + '</td>';
          }).join('') + '</tr>';
        }).join('')
      : '<tr><td colspan="' + cols.length + '" class="empty">조건에 맞는 항목이 없습니다.</td></tr>';
    renderSummary(page, all, list);
    renderBanner(page, all);
  }
  function renderSummary(page, all, list) {
    var h = '<b>' + list.length + '</b>건 (전체 ' + all.length + '건)';
    if (page.kind === 'test') {
      var c = { '미실행': 0, 'PASS': 0, 'FAIL': 0 };
      all.forEach(function (x) { c[x.result] = (c[x.result] || 0) + 1; });
      h += ' · PASS ' + c.PASS + ' / FAIL ' + c.FAIL + ' / 미실행 ' + c['미실행'];
    } else {
      var s = { '지연': 0, '진행중': 0, '미착수': 0, '완료': 0 };
      all.forEach(function (x) { s[statusOf(x)]++; });
      h += ' · 지연 ' + s['지연'] + ' / 진행중 ' + s['진행중'] + ' / 미착수 ' + s['미착수'] + ' / 완료 ' + s['완료'];
    }
    $('resultCount').innerHTML = h;
  }
  function renderBanner(page, all) {
    var rows = 0, kinds = {}, ids = [];
    all.forEach(function (it) {
      var r = checkItem(page, it, all), list = r.err.concat(r.info);
      if (!list.length) return;
      rows++;
      ids.push(it.id);
      list.forEach(function (m) {
        var k = m.t;
        kinds[k] = (kinds[k] || 0) + 1;
      });
    });
    $('banner').innerHTML = rows
      ? '<div class="validation-banner">' + TRI + ' 정합성 확인 필요 ' + rows + '행 — ' +
        Object.keys(kinds).map(function (k) { return k + ' ' + kinds[k] + '건'; }).join(', ') +
        ' <span class="banner-ids">(예: ' + esc(ids.slice(0, 5).join(', ')) + (ids.length > 5 ? ' 외' : '') + ')</span></div>'
      : '';
  }
  function renderChrome() {
    var page = pageOf();
    document.body.classList.toggle('worker-mode', S.mode === 'worker');
    document.querySelectorAll('[data-go]').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-go') === page.tab);
    });
    $('subtabs').innerHTML = TABS[page.tab].map(function (t) {
      return '<button class="subtab' + (t[0] === S.route ? ' on' : '') + '" data-route="' + t[0] + '">' + t[1] + '</button>';
    }).join('');
    $('crumb').innerHTML = (page.tab === 'detail' ? '상세공정관리' : '테스트관리') + ' · <b>' + page.title + '</b>';
    $('title').textContent = page.title;
    $('desc').textContent = page.desc;
    $('btnPL').classList.toggle('active', S.mode === 'pl');
    $('btnWorker').classList.toggle('active', S.mode === 'worker');
    $('workerAccount').style.display = S.mode === 'worker' ? '' : 'none';
    $('btnSave').textContent = S.mode === 'pl' ? '저장' : '실적 저장';
    $('dataState').textContent = S.draft[page.file]
      ? '임시저장본 사용 중 (이 브라우저에만 저장됨)'
      : '원본 데이터 사용 중 (data/' + page.file + '.json)';
  }

  /* ---------- 필터 ---------- */
  function filterDefs(page) {
    var t = page.typesKey, base, adv;
    if (page.kind === 'stage') {
      base = [
        { k: 'system', label: '시스템', t: 'sel', f: 'system', src: sysNames() },
        { k: 'subsystem', label: '서브시스템', t: 'sel', f: 'subsystem', src: allSubs() },
        { k: 'id', label: 'ID', t: 'txt', f: 'id', ph: '예: UI_QPM_0001' },
        { k: 'name', label: page.nameLabel, t: 'txt', f: 'name', ph: '검색' },
        { k: 'type', label: '처리유형', t: 'sel', f: 'type', src: S.master.types[t] },
        { k: 'status', label: '진행상태', t: 'sel', f: 'status', src: ['지연', '진행중', '미착수', '완료'] },
        { k: 'worker', label: '작업자', t: 'sel', f: 'worker', src: S.master.workers }
      ];
      adv = [];
      if (t !== 'analysis') {
        adv.push({ k: 'devType', label: '개발유형', t: 'sel', f: 'devType', src: ['신규', '변경'] });
        adv.push({ k: 'devRound', label: '개발차수', t: 'sel', f: 'devRound', src: ['1차', '2차'] });
      }
      adv.push({ k: 'reqId', label: '요구사항ID', t: 'txt', f: 'reqIds', ph: 'RF_CCM' });
      if (t !== 'analysis') adv.push({ k: 'physId', label: '물리ID', t: 'txt', f: 'physIds', ph: 'LTRA' });
      if (t === 'dev') adv.push({ k: 'designRef', label: '설계ID', t: 'txt', f: 'designRef', ph: 'UI_QPM' });
      adv.push({ k: 'planFrom', label: '계획기간(시작)', t: 'from', f: 'wPlanStart' });
      adv.push({ k: 'planTo', label: '계획기간(종료)', t: 'to', f: 'wPlanEnd' });
    } else {
      base = [
        { k: 'id', label: 'ID', t: 'txt', f: 'id', ph: 'UI_QPM / IT-' },
        { k: 'name', label: '테스트명', t: 'txt', f: 'name', ph: '검색' },
        { k: 'linked', label: '연결 개발ID', t: 'txt', f: 'linked', ph: 'UI_QPM' },
        { k: 'result', label: '결과', t: 'sel', f: 'result', src: ['미실행', 'PASS', 'FAIL'] },
        { k: 'worker', label: '담당자', t: 'sel', f: 'worker', src: S.master.workers }
      ];
      adv = [
        { k: 'round', label: '테스트 차수', t: 'sel', f: 'round', src: ['1차', '2차'] },
        { k: 'reqId', label: '요구사항ID', t: 'txt', f: 'reqIds', ph: 'RF_CCM' }
      ];
    }
    return { base: base, adv: adv };
  }
  function filterCtrl(d) {
    var inner;
    if (d.t === 'sel') {
      inner = '<select class="f-select" data-fk="' + d.k + '" data-t="sel" data-f="' + d.f + '"><option value="">전체</option>' +
        d.src.map(function (o) { return '<option>' + esc(o) + '</option>'; }).join('') + '</select>';
    } else if (d.t === 'txt') {
      inner = '<input class="f-input" data-fk="' + d.k + '" data-t="txt" data-f="' + d.f + '" placeholder="' + esc(d.ph || '') + '" style="min-width:130px">';
    } else {
      inner = '<input class="f-input" type="date" data-fk="' + d.k + '" data-t="' + d.t + '" data-f="' + d.f + '" style="min-width:135px">';
    }
    return '<div class="f-field"><label>' + d.label + '</label>' + inner + '</div>';
  }
  function buildFilters(page) {
    var d = filterDefs(page);
    $('filters').innerHTML = d.base.map(filterCtrl).join('');
    $('filtersAdv').innerHTML = d.adv.map(filterCtrl).join('');
    S.applied = {};
  }
  function readFilters() {
    var out = {};
    document.querySelectorAll('#filterCard [data-fk]').forEach(function (el) {
      var v = el.value.trim();
      if (v) out[el.getAttribute('data-fk')] = { t: el.getAttribute('data-t'), f: el.getAttribute('data-f'), v: v };
    });
    return out;
  }
  function passes(it, flt) {
    for (var k in flt) {
      var c = flt[k], x = getVal(it, c.f);
      if (c.t === 'sel') {
        if (String(x == null ? '' : x) !== c.v) return false;
      } else if (c.t === 'txt') {
        var q = c.v.toLowerCase();
        var ok = Array.isArray(x)
          ? x.some(function (e) { return String(e).toLowerCase().indexOf(q) >= 0; })
          : String(x == null ? '' : x).toLowerCase().indexOf(q) >= 0;
        if (!ok) return false;
      } else if (c.t === 'from') {
        if (!x || x < c.v) return false;
      } else if (c.t === 'to') {
        if (!x || x > c.v) return false;
      }
    }
    return true;
  }
  function setWorkerFilter(v) {
    var el = document.querySelector('#filterCard [data-fk="worker"]');
    if (el) el.value = v;
  }
  function resetFilters() {
    document.querySelectorAll('#filterCard [data-fk]').forEach(function (el) { el.value = ''; });
    if (S.mode === 'worker') setWorkerFilter(S.account);
    S.applied = readFilters();
  }

  /* ---------- 피커(요구사항/물리ID/설계ID/개발ID) ---------- */
  function openPicker(page, id, k) {
    var it = find(page, id);
    var c = columnsOf(page).filter(function (x) { return x.k === k; })[0];
    var inh = (page.file === 'dev' && k === 'physIds')
      ? arr((S.data.design.items.filter(function (d) { return d.id === arr(it.designRef)[0]; })[0] || {}).physIds) : [];
    S.pick = { page: page, id: id, col: c, sel: arr(it[k]).slice(), inh: inh };
    $('pickBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + esc(c.label) + ' 선택</h3><p>' + esc(id) +
      (c.max === 1 ? ' · 1건 선택' : ' · 여러 건 선택 가능') + '</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-search"><input class="f-input" id="pickQ" placeholder="검색" style="width:100%"></div>' +
      '<div class="modal-list" id="pickList"></div>' +
      '<div class="modal-input"><div class="row">' +
      (LINK_TARGETS[c.src]
        ? '<a class="btn ghost sm" href="' + esc(S.master[LINK_TARGETS[c.src].key] || '#') + '" target="_blank" rel="noopener">' +
          esc(LINK_TARGETS[c.src].label) + ' ↗</a>'
        : '<span></span>') +
      '<span class="pick-btns"><button class="btn ghost sm" id="pickClear">선택 해제</button>' +
      '<button class="btn sm" id="pickApply">적용</button></span></div></div>';
    renderPickList('');
    $('pickModal').classList.add('open');
    $('pickQ').focus();
  }
  function renderPickList(q) {
    var p = S.pick, ql = q.toLowerCase(), single = p.col.max === 1;
    var h = srcOptions(p.col.src).filter(function (o) {
      return !ql || o.label.toLowerCase().indexOf(ql) >= 0;
    }).map(function (o) {
      var on = p.sel.indexOf(o.id) >= 0;
      var inh = p.inh.indexOf(o.id) >= 0;
      return '<label class="pick-row"><input type="' + (single ? 'radio' : 'checkbox') + '" name="pk" value="' +
        esc(o.id) + '"' + (on ? ' checked' : '') + (inh ? ' disabled' : '') + '><span>' + esc(o.label) + (inh ? ' <em class="inh">상속</em>' : '') + '</span></label>';
    }).join('');
    $('pickList').innerHTML = h || '<div class="empty">검색 결과가 없습니다.</div>';
  }
  function closePick() { S.pick = null; $('pickModal').classList.remove('open'); }

  /* ---------- 팝업(비고 / 증적) ---------- */
  function openPop(page, id, key) {
    S.pop = { page: page, id: id, key: key };
    renderPop();
    $('popModal').classList.add('open');
  }
  function renderPop() {
    var p = S.pop, it = find(p.page, p.id), list = arr(it[p.key]), isEv = p.key === 'evidence', who = me();
    var entries = list.map(function (e, i) {
      var del = e.author === who ? '<button class="del" data-del="' + i + '">삭제</button>' : '';
      return '<div class="remark-item"><div class="meta"><span class="tag">' + tag(e.date) + ' ' + esc(e.author) +
        '</span>' + del + '</div><div class="body">' + esc(e.text) + '</div>' +
        (e.file ? '<div class="file-chip">📄 ' + esc(e.file) + '</div>' : '') + '</div>';
    }).join('') || '<div class="empty">등록된 내용이 없습니다.</div>';
    $('popBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + esc(it.name || it.id) + ' — ' + (isEv ? '실적 증적' : '특이사항 / 비고') +
      '</h3><p>' + esc(it.id) + (isEv ? ' · 증적은 필수 기록' : ' · 선택 기록') + '</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-list">' + entries + '</div>' +
      '<div class="modal-input"><div class="who">오늘 등록 · ' + todayISO() + ' · ' + esc(who) + ' (권한 무관 누구나 등록 가능)</div>' +
      '<textarea id="popText" placeholder="' + (isEv ? '실적 근거를 텍스트로 남기거나 파일을 첨부하세요' : '특이사항이나 비고를 입력하세요') + '"></textarea>' +
      '<div class="row">' +
      (isEv ? '<label class="file-attach">📎 파일 첨부<input type="file" id="popFile"><span class="file-name" id="popFileName"></span></label>' : '<span></span>') +
      '<button class="btn sm" id="popAdd">등록</button></div></div>';
    $('popModal').classList.add('open');
  }
  function addEntry() {
    var p = S.pop, it = find(p.page, p.id);
    var text = $('popText').value.trim();
    var f = p.key === 'evidence' && $('popFile') ? $('popFile').files[0] : null;
    if (!text && !f) return;
    var e = { date: todayISO(), author: me(), text: text || '(첨부파일만 등록)' };
    if (f) e.file = f.name;
    it[p.key] = arr(it[p.key]);
    it[p.key].unshift(e);
    renderPop();
    renderTable();
    showToast(p.key === 'evidence' ? '실적 증적이 등록되었습니다' : '비고가 등록되었습니다');
  }
  function closePop() { S.pop = null; $('popModal').classList.remove('open'); }

  /* ---------- 작업자 선택 팝업 (PL 전용: 선택/등록/수정/삭제) ---------- */
  var ITEM_FILES = ['analysis', 'design', 'dev', 'unit', 'integration'];
  function persistFiles(names) {
    var ok = true;
    names.forEach(function (n) {
      try {
        localStorage.setItem(DRAFT_KEY + n, JSON.stringify(n === 'master' ? S.master : S.data[n]));
        S.draft[n] = true;
      } catch (e) { ok = false; }
    });
    if (!ok) showToast('브라우저 저장소에 저장하지 못했습니다. 내보내기를 이용하세요.', true);
  }
  function buildAccountSelect() {
    $('workerAccount').innerHTML = S.master.workers.map(function (w) {
      return '<option value="' + esc(w) + '"' + (w === S.account ? ' selected' : '') + '>' + esc(w) + '</option>';
    }).join('');
  }
  function workerCount(name) {
    var n = 0;
    ITEM_FILES.forEach(function (f) {
      S.data[f].items.forEach(function (it) { if (it.worker === name) n++; });
    });
    return n;
  }
  function renameWorker(i, name) {
    var old = S.master.workers[i], changed = [];
    S.master.workers[i] = name;
    ITEM_FILES.forEach(function (f) {
      var hit = false;
      S.data[f].items.forEach(function (it) { if (it.worker === old) { it.worker = name; hit = true; } });
      if (hit) changed.push(f);
    });
    if (S.account === old) S.account = name;
    return changed.concat(['master']);
  }
  function deleteWorker(i) {
    var name = S.master.workers[i], changed = [];
    S.master.workers.splice(i, 1);
    ITEM_FILES.forEach(function (f) {
      var hit = false;
      S.data[f].items.forEach(function (it) { if (it.worker === name) { it.worker = ''; hit = true; } });
      if (hit) changed.push(f);
    });
    if (S.account === name) S.account = S.master.workers[0] || '';
    return changed.concat(['master']);
  }
  function validNewName(n) {
    if (!n) { showToast('이름을 입력하세요', true); return false; }
    if (S.master.workers.indexOf(n) >= 0) { showToast('이미 등록된 작업자입니다', true); return false; }
    return true;
  }
  function openWorkerPick(page, id) {
    S.wk = { page: page, id: id, editing: null };
    renderWorkerPick();
    $('workerModal').classList.add('open');
  }
  function closeWorkerPick() { S.wk = null; $('workerModal').classList.remove('open'); }
  function renderWorkerPick() {
    var w = S.wk, it = find(w.page, w.id), cur = it.worker || '';
    var rows = S.master.workers.map(function (name, i) {
      var editing = w.editing === i;
      var nameHTML = editing
        ? '<input class="f-input" id="wkEditInput" value="' + esc(name) + '" style="min-width:140px">'
        : '<span>' + esc(name) + '</span>' + (name === cur ? ' <span class="st doing">현재 담당</span>' : '');
      var actions = editing
        ? '<button class="btn sm" data-wk-save="' + i + '">저장</button> <button class="btn ghost sm" data-wk-cancel="1">취소</button>'
        : '<button class="btn sm" data-wk-select="' + i + '">선택</button> ' +
          '<button class="btn ghost sm" data-wk-edit="' + i + '">수정</button> ' +
          '<button class="btn ghost sm" data-wk-del="' + i + '">삭제</button>';
      return '<div class="wk-row">' + nameHTML + '<div class="wk-actions">' + actions + '</div></div>';
    }).join('') || '<div class="empty">등록된 작업자가 없습니다.</div>';
    $('workerBox').innerHTML =
      '<div class="modal-hd"><div><h3>작업자 선택</h3><p>' + esc(w.id) + ' · 선택한 작업자에게 이 업무가 할당됩니다</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-list">' + rows + '</div>' +
      '<div class="modal-input"><div class="who">작업자 등록 (PL 권한)</div>' +
      '<div class="row"><input class="f-input" id="wkNew" placeholder="이름 입력" style="flex:1">' +
      '<button class="btn sm" id="wkAdd">등록</button></div>' +
      '<div class="row"><span class="pick-btns"><button class="btn ghost sm" id="wkClear">담당 해제</button>' +
      '<button class="btn ghost sm" id="wkExport">작업자 목록 내보내기</button></span></div></div>';
  }
  function exportNamed(name, data) {
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name + '.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    showToast(name + '.json 내보내기 완료');
  }

  /* ---------- 행 추가 / 저장 / 내보내기 / 원본복원 ---------- */
  function addRow() {
    var page = pageOf(), all = items(page), it;
    if (page.kind === 'stage') {
      var sys = S.master.systems[0];
      it = {
        id: nextId(page.prefix, all), system: sys.name, subsystem: sys.subs[0] || '',
        type: S.master.types[page.typesKey][0], name: '', worker: '',
        devType: '신규', devRound: '1차', reqIds: [], physIds: [], designRef: [], evidence: [], remarks: []
      };
    } else {
      it = {
        id: nextId(page.prefix, all), name: '', linked: [], reqIds: [], expected: '',
        round: '1차', worker: '', result: '미실행', evidence: [], remarks: []
      };
    }
    all.push(it);
    resetFilters();
    renderTable();
    showToast('행이 추가되었습니다');
    var tr = $('tbody').querySelector('tr[data-id="' + it.id + '"]');
    if (tr) tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function gateMessage(page) {
    if (page.kind === 'stage' && S.mode === 'worker') {
      var mine = items(page).filter(function (it) { return passes(it, S.applied); });
      var n = mine.filter(function (it) { return it.wActStart && !arr(it.evidence).length; }).length;
      if (n) return '⚠ 증적 미첨부 ' + n + '건 — 저장할 수 없습니다';
    }
    if (page.kind === 'test') {
      var f = items(page).filter(function (it) { return it.result === 'FAIL' && !arr(it.evidence).length; }).length;
      if (f) return '⚠ FAIL 결과 증적 미첨부 ' + f + '건 — 저장할 수 없습니다';
    }
    return null;
  }
  // 마지막 저장(또는 불러온) 상태와 비교한 변경 요약
  function changeSummary() {
    var mod = 0, add = 0, del = 0, files = [];
    IMPACT_FILES.forEach(function (f) {
      var base = {}, cur = {}, n = 0;
      S.baseline[f].items.forEach(function (x) { base[x.id] = JSON.stringify(x); });
      S.data[f].items.forEach(function (x) { cur[x.id] = JSON.stringify(x); });
      Object.keys(cur).forEach(function (id) {
        if (base[id] === undefined) { add++; n++; } else if (base[id] !== cur[id]) { mod++; n++; }
      });
      Object.keys(base).forEach(function (id) { if (cur[id] === undefined) { del++; n++; } });
      if (n) files.push(FILE_LABEL[f] + ' ' + n + '건');
    });
    return { add: add, mod: mod, del: del, total: add + mod + del, files: files };
  }
  function save() {
    var msg = gateMessage(pageOf());
    if (msg) { showToast(msg, true); renderTable(); return; }
    var c = changeSummary();
    if (!c.total) { showToast('변경된 내용이 없습니다'); return; }
    var ok = confirm('변경 내용을 저장할까요?\n\n' +
      '· 추가 ' + c.add + '건 · 수정 ' + c.mod + '건 · 삭제 ' + c.del + '건\n' +
      '· 대상: ' + c.files.join(', ') + '\n\n' +
      '저장은 이 브라우저에 반영됩니다. 기본 데이터 파일에 반영하려면 내보내기를 이용하세요.');
    if (!ok) return;
    try {
      IMPACT_FILES.forEach(function (f) {
        localStorage.setItem(DRAFT_KEY + f, JSON.stringify(S.data[f]));
        S.draft[f] = true;
      });
    } catch (e) {
      showToast('브라우저 저장소에 저장하지 못했습니다. 내보내기를 이용하세요.', true);
      return;
    }
    S.baseline = snapData();
    renderChrome();
    renderTable();
    showToast('저장되었습니다');
  }
  function exportFile() {
    var page = pageOf();
    var blob = new Blob([JSON.stringify(S.data[page.file], null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = page.file + '.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    showToast(page.file + '.json 내보내기 완료 · data/ 폴더에 덮어쓰면 원본이 됩니다');
  }
  async function restoreOriginal() {
    var page = pageOf();
    if (!confirm('임시저장본을 버리고 data/' + page.file + '.json 원본으로 되돌릴까요?')) return;
    try { localStorage.removeItem(DRAFT_KEY + page.file); } catch (e) { /* 저장소 접근 불가 시 무시 */ }
    S.draft[page.file] = false;
    try {
      S.data[page.file] = await fetchJSON(FILES[page.file]);
    } catch (e) {
      showToast('원본을 읽지 못했습니다: ' + e.message, true);
      return;
    }
    renderChrome();
    renderTable();
    S.baseline[page.file] = JSON.parse(JSON.stringify(S.data[page.file]));
    showToast('원본으로 복원했습니다');
  }

  /* ---------- 라우팅 / 모드 ---------- */
  function route() {
    closeChips();
    if (S.vpop) closeVCheck();
    var parts = (location.hash || '').replace('#', '').split('?');
    S.route = PAGES[parts[0]] ? parts[0] : 'analysis';
    buildFilters(pageOf());
    $('filtersAdv').classList.remove('open');
    if (parts[1]) {
      parts[1].split('&').forEach(function (kv) {
        var i = kv.indexOf('=');
        if (i < 0) return;
        var key = decodeURIComponent(kv.slice(0, i)), val = decodeURIComponent(kv.slice(i + 1));
        var el = document.querySelector('#filterCard [data-fk="' + key + '"]');
        if (!el) return;
        el.value = val;
        if (el.closest('#filtersAdv')) $('filtersAdv').classList.add('open');
      });
      S.applied = readFilters();
    }
    if (S.mode === 'worker') { setWorkerFilter(S.account); S.applied = readFilters(); }
    renderChrome();
    renderTable();
  }
  function setMode(m) {
    S.mode = m;
    if (m === 'worker') setWorkerFilter(S.account);
    else setWorkerFilter('');
    S.applied = readFilters();
    renderChrome();
    renderTable();
  }

  /* ---------- 데이터 로드 ---------- */
  async function fetchJSON(path) {
    var r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(path + ' (' + r.status + ')');
    return r.json();
  }
  async function loadFile(name) {
    try {
      var raw = localStorage.getItem(DRAFT_KEY + name);
      if (raw) return { data: JSON.parse(raw), draft: true };
    } catch (e) { /* 임시저장본이 깨졌으면 원본 사용 */ }
    return { data: await fetchJSON(FILES[name]), draft: false };
  }

  function bind() {
    document.querySelectorAll('[data-go]').forEach(function (b) {
      b.addEventListener('click', function () {
        var tab = b.getAttribute('data-go');
        location.hash = '#' + TABS[tab][0][0];
      });
    });
    $('subtabs').addEventListener('click', function (e) {
      var b = e.target.closest('[data-route]');
      if (b) location.hash = '#' + b.getAttribute('data-route');
    });
    window.addEventListener('hashchange', route);

    $('btnPL').addEventListener('click', function () { setMode('pl'); });
    $('btnWorker').addEventListener('click', function () { setMode('worker'); });
    $('workerAccount').addEventListener('change', function (e) {
      S.account = e.target.value;
      setWorkerFilter(S.account);
      S.applied = readFilters();
      renderTable();
    });

    $('btnSearch').addEventListener('click', function () { S.applied = readFilters(); renderTable(); });
    $('btnFReset').addEventListener('click', function () { resetFilters(); renderTable(); });
    $('btnMore').addEventListener('click', function () { $('filtersAdv').classList.toggle('open'); });
    $('filterCard').addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && e.target.tagName === 'INPUT') { S.applied = readFilters(); renderTable(); }
    });

    $('btnCols').addEventListener('click', function (e) {
      e.stopPropagation();
      var panel = $('colPanel');
      var open = !panel.classList.contains('open');
      panel.classList.toggle('open', open);
      if (open) {
        panel.innerHTML = '<div class="ttl">그리드에 표시할 컬럼</div>' + groupsOf(pageOf()).map(function (g) {
          return '<label><input type="checkbox" data-g="' + g + '"' + (S.hidden[g] ? '' : ' checked') + '> ' + GROUP_LABEL[g] + '</label>';
        }).join('');
      }
    });
    $('colPanel').addEventListener('change', function (e) {
      var g = e.target.getAttribute('data-g');
      if (!g) return;
      S.hidden[g] = !e.target.checked;
      renderTable();
    });
    document.addEventListener('click', function (e) {
      if (!$('colPanel').contains(e.target) && e.target.id !== 'btnCols') $('colPanel').classList.remove('open');
    });

    $('btnAdd').addEventListener('click', addRow);
    $('btnSave').addEventListener('click', save);
    $('btnExport').addEventListener('click', exportFile);
    $('btnRestore').addEventListener('click', restoreOriginal);

    $('tbody').addEventListener('change', function (e) {
      var el = e.target, k = el.getAttribute('data-k');
      if (!k) return;
      var tr = el.closest('tr');
      var it = find(pageOf(), tr.getAttribute('data-id'));
      if (!it) return;
      if (ACTUAL_KEYS.indexOf(k) >= 0 && el.value > todayISO()) {
        showToast('실적 날짜는 오늘(' + todayISO() + ')까지만 입력할 수 있습니다', true);
        renderTable();
        return;
      }
      if (k === 'system') {
        it.system = el.value;
        it.subsystem = subsOf(el.value)[0] || '';
      } else {
        it[k] = el.value;
      }
      renderTable();
    });
    $('tbody').addEventListener('click', function (e) {
      var t = e.target, tr = t.closest('tr');
      if (!tr) return;
      var page = pageOf(), id = tr.getAttribute('data-id'), x;
      if ((x = t.closest('[data-chipx]'))) {
        var it = find(page, id), k = x.getAttribute('data-chipx'), val = x.getAttribute('data-val');
        it[k] = arr(it[k]).filter(function (v) { return v !== val; });
        renderTable();
        return;
      }
      if ((x = t.closest('[data-chips-edit]'))) { openChips(page, id, x.getAttribute('data-chips-edit')); return; }
      if ((x = t.closest('[data-chips]'))) {
        var ck = x.getAttribute('data-chips'), cit = find(page, id), cc = columnsOf(page).filter(function (q) { return q.k === ck; })[0];
        var cv = arr(cit && cit[ck]);
        if (cv.length === 1 && NAV[ck]) goFilter(NAV[ck][0], NAV[ck][1], cv[0]);
        else openChips(page, id, ck);
        return;
      }
      if ((x = t.closest('[data-rowdel]'))) { deleteRow(page, id); return; }
      if ((x = t.closest('[data-vcheck]'))) { openVCheck(page, id); return; }
      if ((x = t.closest('[data-worker]'))) { openWorkerPick(page, id); return; }
      if ((x = t.closest('[data-pick]'))) { openPicker(page, id, x.getAttribute('data-pick')); return; }
      if ((x = t.closest('[data-pop]'))) { openPop(page, id, x.getAttribute('data-pop')); }
    });

    // 피커 모달
    $('pickModal').addEventListener('click', function (e) {
      if (e.target === this) { closePick(); return; }
      var id = e.target.id;
      if (e.target.hasAttribute('data-close')) closePick();
      else if (id === 'pickClear') { S.pick.sel = []; renderPickList($('pickQ').value); }
      else if (id === 'pickApply') {
        var p = S.pick;
        closePick();
        withImpact(p.col.label + ' 변경', function () {
          var pit = find(p.page, p.id);
          if (!pit) return;
          if (p.page.file === 'dev' && p.col.k === 'physIds') {
            pit.physIdsAdd = p.sel.filter(function (x) { return p.inh.indexOf(x) < 0; });
          } else {
            var prev = JSON.stringify(arr(pit[p.col.k]));
            pit[p.col.k] = p.sel.slice();
            if (p.page.file === 'unit' && p.col.k === 'linked' && prev !== JSON.stringify(pit.linked)) resetResult(pit);
          }
        }, { f: p.page.file, id: p.id });
      }
    });
    $('pickBox').addEventListener('input', function (e) {
      if (e.target.id === 'pickQ') renderPickList(e.target.value);
    });
    $('pickBox').addEventListener('change', function (e) {
      if (!S.pick || e.target.name !== 'pk') return;
      var v = e.target.value, p = S.pick;
      if (p.col.max === 1) p.sel = [v];
      else if (e.target.checked) { if (p.sel.indexOf(v) < 0) p.sel.push(v); }
      else p.sel = p.sel.filter(function (x) { return x !== v; });
    });

    // 팝업 모달
    $('popModal').addEventListener('click', function (e) {
      if (e.target === this) { closePop(); return; }
      if (e.target.hasAttribute('data-close')) { closePop(); return; }
      if (e.target.id === 'popAdd') { addEntry(); return; }
      var d = e.target.getAttribute('data-del');
      if (d !== null) {
        var p = S.pop, it = find(p.page, p.id), i = parseInt(d, 10);
        if (arr(it[p.key])[i] && it[p.key][i].author === me()) {
          it[p.key].splice(i, 1);
          renderPop();
          renderTable();
        }
      }
    });
    // 연관 영향 안내 팝업
    $('impactModal').addEventListener('click', function (e) {
      var t = e.target;
      if (t === this || t.hasAttribute('data-imp-cancel')) { closeImpact(); return; }
      if (t.hasAttribute('data-imp-ok')) {
        var I = S.impact;
        closeImpact();
        if (I && I.mutate) {
          I.mutate(); syncDown(); applyRecheck(I.flags); renderTable();
          showToast('반영했습니다. 저장 버튼으로 확정하세요');
        }
      }
    });
    // 값 모달 (여러 값 셀)
    $('chipModal').addEventListener('click', function (e) {
      var t = e.target, x;
      if (t === this || t.hasAttribute('data-close')) { closeChips(); return; }
      if ((x = t.closest('[data-nav-page]'))) {
        closeChips();
        goFilter(x.getAttribute('data-nav-page'), x.getAttribute('data-nav-key'), x.getAttribute('data-nav-val'));
        return;
      }
      if ((x = t.closest('[data-chip-rm]'))) {
        var c = S.chips; if (!c) return;
        var rmv = x.getAttribute('data-chip-rm');
        closeChips();
        withImpact(IMPACT_LABEL[c.k] + ' 제외: ' + rmv, function () {
          var it = find(c.page, c.id);
          if (!it) return;
          var prev = JSON.stringify(arr(it[c.k]));
          it[c.k] = arr(it[c.k]).filter(function (v) { return v !== rmv; });
          if (c.page.file === 'unit' && c.k === 'linked' && prev !== JSON.stringify(it.linked)) resetResult(it);
        }, { f: c.page.file, id: c.id });
        return;
      }
      if (t.hasAttribute('data-chip-add') || t.closest('[data-chip-add]')) {
        var cs = S.chips; closeChips();
        if (cs) openPicker(cs.page, cs.id, cs.k);
      }
    });
    // 검증 상세 팝업
    $('vModal').addEventListener('click', function (e) {
      var t = e.target, x;
      if (t === this) { closeVCheck(); return; }
      if (t.hasAttribute('data-close')) { closeVCheck(); return; }
      if (t.hasAttribute('data-clear-recheck')) {
        var rv = S.vpop; closeVCheck();
        if (rv) withImpact('재검증 완료 처리', function () {
          var ri = find(rv.page, rv.id); if (ri) ri.recheck = false;
        }, { f: rv.page.file, id: rv.id });
        return;
      }
      if ((x = t.closest('[data-focus]'))) {
        var v = S.vpop; closeVCheck();
        if (v) focusCell(v.id, x.getAttribute('data-focus'));
        return;
      }
      if ((x = t.closest('[data-goto]'))) {
        closeVCheck();
        location.hash = '#' + x.getAttribute('data-goto');
      }
    });
    // 작업자 팝업 (PL 전용)
    $('workerModal').addEventListener('click', function (e) {
      var t = e.target, w = S.wk, attr;
      if (t === this) { closeWorkerPick(); return; }
      if (!w) return;
      if (t.hasAttribute('data-close')) { closeWorkerPick(); return; }
      if (t.id === 'wkClear') {
        find(w.page, w.id).worker = '';
        closeWorkerPick();
        renderTable();
        showToast('담당 작업자를 해제했습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if (t.id === 'wkAdd') {
        var n = $('wkNew').value.trim();
        if (!validNewName(n)) return;
        S.master.workers.push(n);
        persistFiles(['master']);
        buildAccountSelect();
        renderWorkerPick();
        showToast('작업자가 등록되었습니다');
        return;
      }
      if (t.id === 'wkExport') { exportNamed('master', S.master); return; }
      if ((attr = t.getAttribute('data-wk-select')) !== null) {
        var picked = S.master.workers[+attr];
        find(w.page, w.id).worker = picked;
        closeWorkerPick();
        renderTable();
        showToast(picked + ' 님에게 업무가 할당되었습니다. 저장 버튼으로 반영하세요');
        return;
      }
      if ((attr = t.getAttribute('data-wk-edit')) !== null) { w.editing = +attr; renderWorkerPick(); return; }
      if (t.hasAttribute('data-wk-cancel')) { w.editing = null; renderWorkerPick(); return; }
      if ((attr = t.getAttribute('data-wk-save')) !== null) {
        var idx = +attr, nn = $('wkEditInput').value.trim();
        if (!nn) { showToast('이름을 입력하세요', true); return; }
        if (nn !== S.master.workers[idx] && S.master.workers.indexOf(nn) >= 0) {
          showToast('이미 등록된 작업자입니다', true);
          return;
        }
        persistFiles(renameWorker(idx, nn));
        w.editing = null;
        buildAccountSelect();
        renderWorkerPick();
        renderTable();
        showToast('작업자 이름을 수정했습니다');
        return;
      }
      if ((attr = t.getAttribute('data-wk-del')) !== null) {
        var di = +attr, dn = S.master.workers[di], cnt = workerCount(dn);
        if (!confirm('"' + dn + '" 작업자를 삭제할까요?' + (cnt ? '\n담당 중인 업무 ' + cnt + '건은 작업자가 비워집니다.' : ''))) return;
        persistFiles(deleteWorker(di));
        w.editing = null;
        buildAccountSelect();
        renderWorkerPick();
        renderTable();
        showToast('작업자를 삭제했습니다');
      }
    });

    $('popBox').addEventListener('change', function (e) {
      if (e.target.id === 'popFile') {
        var f = e.target.files[0];
        $('popFileName').textContent = f ? f.name : '';
      }
    });
  }

  /* ---------- 시작 ---------- */
  async function boot() {
    try {
      var names = ['master', 'asis', 'analysis', 'design', 'dev', 'unit', 'integration'];
      var res = await Promise.all(names.map(loadFile));
      names.forEach(function (n, i) {
        if (n === 'master') S.master = res[i].data; else S.data[n] = res[i].data;
        S.draft[n] = res[i].draft;
      });
    } catch (e) {
      $('thead').innerHTML = '';
      $('tbody').innerHTML = '<tr><td class="empty">데이터 파일을 읽지 못했습니다 (' + esc(e.message) +
        '). 파일을 직접 열지 말고 로컬 서버로 실행하세요: python3 -m http.server 8000</td></tr>';
      return;
    }
    S.baseline = snapData();
    S.account = S.master.workers[0];
    buildAccountSelect();
    bind();
    route();
  }

  boot();
})();
