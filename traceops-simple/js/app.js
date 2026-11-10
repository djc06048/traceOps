/* TraceOps 단순 버전 — 상세공정관리(분석/설계/개발) + 테스트관리(단위/통합)
 * 모든 데이터는 data/*.json 을 읽어서 동작한다. DB 없음.
 * 편집 내용은 브라우저 임시저장(localStorage)에 남고, 내보내기로 JSON을 받아 data/ 원본에 덮어쓸 수 있다.
 */
(function () {
  'use strict';

  var FILES = {
    master: 'data/master.json',
    analysis: 'data/analysis.json',
    design: 'data/design.json',
    dev: 'data/dev.json',
    unit: 'data/unit.json',
    integration: 'data/integration.json'
  };
  var DRAFT_KEY = 'traceops-simple:';

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
    workerPlan: '작업자 계획기간', workerActual: '작업자 실적기간',
    plPlan: 'PL 계획기간', plActual: 'PL 실적기간', devMeta: '개발유형·차수', mapping: '매핑'
  };
  var STATUS_ORDER = { '지연': 0, '진행중': 1, '미착수': 2, '완료': 3 };
  var STATUS_CLS = { '지연': 'late', '진행중': 'doing', '미착수': 'todo', '완료': 'done' };
  // 매핑 팝업에서 다른 관리 화면으로 넘어가는 링크 (화면이 만들어지면 master.json 주소만 연결)
  var LINK_TARGETS = {
    reqIds: { key: 'requirementsUrl', label: '요구사항 관리에서 등록 (TODO)' },
    physIds: { key: 'physicalIdsUrl', label: '물리ID 관리에서 등록 (TODO)' }
  };

  var S = {
    master: null, data: {}, draft: {},
    mode: 'pl', account: '', route: 'analysis',
    hidden: {}, applied: {}, pick: null, pop: null
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

  function validate(page, it, all) {
    var m = [];
    if (page.kind === 'stage') {
      if (page.typesKey === 'design' && !arr(it.physIds).length) m.push('물리ID 미매핑');
      if (page.typesKey === 'dev' && !arr(it.designRef).length) m.push('설계ID 미연결');
      if (all.filter(function (x) { return x.id === it.id; }).length > 1) m.push('ID 중복');
    } else {
      if (!arr(it.linked).length) m.push(page.multi ? '연계 개발ID 미지정' : '개발ID 미연결');
      if (it.result === 'FAIL' && !arr(it.evidence).length) m.push('FAIL 증적 필요');
      if (page.multi && !arr(it.units).length) m.push('묶인 단위테스트 없음');
    }
    return m;
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
      c.push({ k: 'system', label: '시스템', kind: 'sys', edit: 'pl' });
      c.push({ k: 'subsystem', label: '서브시스템', kind: 'sub', edit: 'pl' });
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
      if (t === 'dev') c.push({ k: 'designRef', label: '설계ID', kind: 'chips', src: 'designIds', max: 1, edit: 'pl', g: 'mapping' });
      c.push({ k: 'reqIds', label: '요구사항ID', kind: 'chips', src: 'reqIds', edit: 'pl', g: 'mapping' });
      if (t === 'design') c.push({ k: 'physIds', label: '물리ID', kind: 'chips', src: 'physIds', edit: 'pl', g: 'mapping' });
      c.push({ k: 'remark', label: '비고', kind: 'remark' });
    } else {
      c.push({ k: 'id', label: 'ID', kind: 'id' });
      c.push({ k: 'name', label: '테스트명', kind: 'text', edit: 'pl', w: 170 });
      c.push({ k: 'linked', label: '연결 개발ID', kind: 'chips', src: 'devIds', max: page.multi ? 0 : 1, edit: 'pl', g: 'mapping' });
      if (page.multi) c.push({ k: 'units', label: '묶인 단위테스트', kind: 'chips', src: 'unitIds', edit: 'pl', g: 'mapping' });
      c.push({ k: 'reqIds', label: '요구사항ID', kind: 'chips', src: 'reqIds', edit: 'pl', g: 'mapping' });
      c.push({ k: 'expected', label: '기대결과', kind: 'text', edit: 'pl', w: 200 });
      c.push({ k: 'round', label: '테스트 차수', kind: 'select', opts: ['1차', '2차'], edit: 'pl' });
      c.push({ k: 'worker', label: '담당자', kind: 'worker', edit: 'pl' });
      c.push({ k: 'execDate', label: '수행일', kind: 'date', edit: 'worker' });
      c.push({ k: 'result', label: '결과', kind: 'select', opts: ['미실행', 'PASS', 'FAIL'], edit: 'worker' });
      c.push({ k: 'evidence', label: '증적', kind: 'evidence' });
      c.push({ k: 'remark', label: '비고', kind: 'remark' });
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
    if (src === 'physIds') return S.master.physIds.map(function (v) { return { id: v, label: v }; });
    if (src === 'designIds') return S.data.design.items.map(function (x) { return { id: x.id, label: x.id + ' · ' + x.name }; });
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
    var h = vals.map(function (v) {
      return '<span class="chip">' + esc(v) +
        (ed ? ' <span class="x" data-chipx="' + c.k + '" data-val="' + esc(v) + '">✕</span>' : '') + '</span>';
    }).join('');
    if (ed && !(c.max === 1 && vals.length)) {
      h += ' <button class="search-btn" data-pick="' + c.k + '">🔍 검색</button>';
    }
    return h || (ed ? '' : '<span class="mono">-</span>');
  }
  function cell(c, it, page, msgs) {
    var ed = canEdit(c), dis = ed ? '' : ' disabled', k = c.k, v = it[k];
    switch (c.kind) {
      case 'v':
        return msgs.length
          ? '<span class="check-err" title="' + esc(msgs.join(' / ')) + '">⚠</span>'
          : '<span class="check-ok">✓</span>';
      case 'id': return '<span class="disabled-field">' + esc(it.id) + '</span>';
      case 'status': var s = statusOf(it); return '<span class="st ' + STATUS_CLS[s] + '">' + s + '</span>';
      case 'sys': return '<select class="txt-input" data-k="system"' + dis + '>' + opts(sysNames(), v) + '</select>';
      case 'sub': return '<select class="txt-input" data-k="subsystem"' + dis + '>' + opts(subsOf(it.system), v) + '</select>';
      case 'typeSel': return '<select class="txt-input" data-k="type"' + dis + '>' + opts(S.master.types[page.typesKey], v) + '</select>';
      case 'text': return '<input class="txt-input" data-k="' + k + '" value="' + esc(v) + '" style="width:' + (c.w || 120) + 'px"' + dis + '>';
      case 'date': return '<input class="txt-input" type="date" data-k="' + k + '" value="' + esc(v) + '"' + dis + '>';
      case 'select': return '<select class="txt-input" data-k="' + k + '"' + dis + '>' + opts(c.opts, v, c.blank) + '</select>';
      case 'worker':
        if (S.mode === 'pl') {
          return '<button class="worker-btn' + (v ? '' : ' empty') + '" data-worker="1">' +
            (v ? esc(v) : '+ 작업자 선택') + '</button>';
        }
        return v ? esc(v) : '<span class="mono">-</span>';
      case 'chips': return chipsHTML(c, it, ed);
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
          var msgs = validate(page, it, all);
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
    if (S.mode !== 'pl') { $('banner').innerHTML = ''; return; }
    var rows = 0, kinds = {};
    all.forEach(function (it) {
      var m = validate(page, it, all);
      if (m.length) {
        rows++;
        m.forEach(function (x) { kinds[x] = (kinds[x] || 0) + 1; });
      }
    });
    $('banner').innerHTML = rows
      ? '<div class="validation-banner">⚠ 검증 오류 ' + rows + '행 — ' +
        Object.keys(kinds).map(function (k) { return k + ' ' + kinds[k] + '건'; }).join(', ') +
        '. 저장 전 확인이 필요합니다.</div>'
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
        { k: 'id', label: 'ID', t: 'txt', f: 'id', ph: '예: SCR-2026' },
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
      if (t === 'design') adv.push({ k: 'physId', label: '물리ID', t: 'txt', f: 'physIds', ph: 'CCM' });
      if (t === 'dev') adv.push({ k: 'designRef', label: '설계ID', t: 'txt', f: 'designRef', ph: 'SCR' });
      adv.push({ k: 'planFrom', label: '계획기간(시작)', t: 'from', f: 'wPlanStart' });
      adv.push({ k: 'planTo', label: '계획기간(종료)', t: 'to', f: 'wPlanEnd' });
    } else {
      base = [
        { k: 'name', label: '테스트명', t: 'txt', f: 'name', ph: '검색' },
        { k: 'linked', label: '연결 개발ID', t: 'txt', f: 'linked', ph: 'DEV' },
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
    S.pick = { page: page, id: id, col: c, sel: arr(it[k]).slice() };
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
      return '<label class="pick-row"><input type="' + (single ? 'radio' : 'checkbox') + '" name="pk" value="' +
        esc(o.id) + '"' + (on ? ' checked' : '') + '><span>' + esc(o.label) + '</span></label>';
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
  function save() {
    var page = pageOf(), all = items(page), msg = null;
    if (page.kind === 'stage' && S.mode === 'worker') {
      // 작업자는 현재 조회된(본인) 행만 대상으로 증적 게이트를 적용한다
      var mine = all.filter(function (it) { return passes(it, S.applied); });
      var n = mine.filter(function (it) { return it.wActStart && !arr(it.evidence).length; }).length;
      if (n) msg = '⚠ 증적 미첨부 ' + n + '건 — 저장할 수 없습니다';
    }
    if (!msg && page.kind === 'test') {
      var f = all.filter(function (it) { return it.result === 'FAIL' && !arr(it.evidence).length; }).length;
      if (f) msg = '⚠ FAIL 결과 증적 미첨부 ' + f + '건 — 저장할 수 없습니다';
    }
    if (msg) { showToast(msg, true); renderTable(); return; }
    try {
      localStorage.setItem(DRAFT_KEY + page.file, JSON.stringify(S.data[page.file]));
      S.draft[page.file] = true;
    } catch (e) {
      showToast('브라우저 저장소에 저장하지 못했습니다. 내보내기를 이용하세요.', true);
      return;
    }
    renderChrome();
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
    showToast('원본으로 복원했습니다');
  }

  /* ---------- 라우팅 / 모드 ---------- */
  function route() {
    var h = (location.hash || '').replace('#', '');
    S.route = PAGES[h] ? h : 'analysis';
    buildFilters(pageOf());
    $('filtersAdv').classList.remove('open');
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
        find(p.page, p.id)[p.col.k] = p.sel.slice();
        closePick();
        renderTable();
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
      var names = ['master', 'analysis', 'design', 'dev', 'unit', 'integration'];
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
    S.account = S.master.workers[0];
    buildAccountSelect();
    bind();
    route();
  }

  boot();
})();
