/* 연계관리(연계 캔버스) — AS-IS/TO-BE 프로세스 목록 + 캔버스(노드·연결선) + AS-IS 콜트리 매핑
 * 기존 추적 체인(분석/설계/개발/테스트)과는 독립. 데이터: /api/linkage/* (관계형 DB)
 */
(function () {
  'use strict';

  var NW = 168, NH_FALLBACK = 70;
  var STATUSES = ['미착수', '진행중', '완료', '확정'];

  var S = { mode: 'pl', processes: [], transactions: [], pid: null, detail: null, selId: null, drag: null, edgeDrag: null, newProc: null,
    collapsed: { asis: true, tobe: false }, listFilter: { q: '', domain: '' } };

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

  /* ---------- 목록 화면 ---------- */
  function statusChip(s) { return '<span class="lk-status on-' + esc(s) + '">' + esc(s) + '</span>'; }
  function progressOf(p) {
    if (p.nodeSource === 'dev' && p.devTotal) return '<b>' + p.devDone + '</b> / ' + p.devTotal + ' 개발완료';
    if (!p.leafTotal) return '-';
    return '<b>' + p.leafMapped + '</b> / ' + p.leafTotal + ' 매핑';
  }
  function matchesFilter(p) {
    var f = S.listFilter;
    if (f.domain && p.domain !== f.domain) return false;
    if (f.q && (p.id + ' ' + p.name + ' ' + (p.owner || '')).toLowerCase().indexOf(f.q) < 0) return false;
    return true;
  }
  function rowHTML(p, child) {
    return '<div class="lk-row" data-pid="' + esc(p.id) + '">' +
      (child ? '<span class="indent" style="width:22px"></span>' : '') +
      '<span class="nm">' + esc(p.name || '(이름 없음)') +
      (p.domain ? ' <span class="lk-domain">' + esc(p.domain) + '</span>' : '') +
      (p.nodeSource === 'dev' ? ' <span class="lk-model tobe">개발 항목 기반</span>' : '') + '</span>' +
      '<span class="tx">' + esc(p.txCode || '') + '</span>' +
      '<span class="own">' + esc(p.owner || '') + '</span>' +
      '<span class="prog">' + progressOf(p) + '</span>' +
      (p.missingToBe ? '<span class="chip-missing">TO-BE 없음</span>' : '') +
      statusChip(p.status) +
      '<span class="sp"></span>' +
      '<span class="actions pl-only">' +
      (p.model === 'asis' ? '<button class="btn ghost sm" data-copy-tobe="' + esc(p.id) + '">TO-BE로 복사</button>' : '') +
      '<button class="btn ghost sm" data-del-proc="' + esc(p.id) + '">삭제</button>' +
      '</span></div>';
  }
  function groupHTML(label, model) {
    var top = S.processes.filter(function (p) { return p.model === model && !p.parentId; });
    var active = !!(S.listFilter.q || S.listFilter.domain);
    var collapsed = S.collapsed[model];
    var rows = [], shown = 0;
    top.forEach(function (p) {
      var children = S.processes.filter(function (c) { return c.parentId === p.id; });
      var visibleChildren = active ? children.filter(matchesFilter) : children;
      if (active && !matchesFilter(p) && !visibleChildren.length) return;
      shown += 1 + visibleChildren.length;
      rows.push(rowHTML(p, false));
      visibleChildren.forEach(function (c) { rows.push(rowHTML(c, true)); });
    });
    var body = collapsed ? '' : (rows.length ? rows.join('')
      : '<div class="empty" style="padding:24px">' + (active ? '조건에 맞는 프로세스가 없습니다.' : '등록된 프로세스가 없습니다.') + '</div>');
    return '<div class="card">' +
      '<div class="lk-group-hd" data-group-toggle="' + model + '"><span class="lk-group-chevron">' + (collapsed ? '▸' : '▾') + '</span>' +
      '<h2>' + label + '</h2><span class="cnt">' + shown + '건</span></div>' + body + '</div>';
  }
  function renderList() {
    $('lkGroups').innerHTML = groupHTML('AS-IS 프로세스', 'asis') + groupHTML('TO-BE 프로세스', 'tobe');
  }
  async function reloadProcesses() {
    S.processes = (await fetchJSON('/api/linkage/processes')).items;
    renderList();
  }
  async function deleteProcess(pid) {
    if (!confirm('"' + pid + '" 프로세스를 삭제할까요? 캔버스·매핑도 함께 삭제됩니다.')) return;
    try {
      await api('DELETE', '/api/linkage/processes/' + encodeURIComponent(pid));
      await reloadProcesses();
      toast('삭제했습니다');
    } catch (e) { toast('삭제 실패: ' + e.message, true); }
  }

  var NODE_SOURCE_LABEL = { free: '자유 입력 (추상 단계)', dev: '개발 항목 기반' };
  var LK_PROCESS_DOMAINS = ['AI', '인수지침', '인수심사', '가입설계', '대응개발'];

  /* ---------- TO-BE 프로세스 생성 모달 (최상위 생성 / 노드의 "하위 캔버스 만들기" 공용) ---------- */
  /* AS-IS는 미리 준비된 데이터로 취급 — 화면에서 새로 만들지 않는다 */
  function openNewProc(opts) {
    opts = opts || {};
    S.newProc = { model: 'tobe', fromNode: opts.fromNode || null };
    var isSub = !!opts.fromNode;
    var sameModel = S.processes.filter(function (p) { return p.model === 'tobe'; });
    var asisList = S.processes.filter(function (p) { return p.model === 'asis'; });
    $('newProcBox').innerHTML =
      '<div class="modal-hd"><div><h3>' + (isSub ? '하위 캔버스 만들기' : 'TO-BE 프로세스 생성') + '</h3>' +
      '<p>' + (isSub ? '이 캔버스의 노드를 자유롭게 쓸지, 개발 항목으로 채울지 고르세요.' : '이름만으로 새로 만들거나, AS-IS 프로세스를 복사해 시작합니다.') + '</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-list">' +
      (isSub ? '' : '<div class="f-field"><label>AS-IS에서 복사 (선택)</label><select class="f-select" id="npCopyFrom" style="width:100%"><option value="">-- 선택 안 함 --</option>' +
        asisList.map(function (p) { return '<option value="' + esc(p.id) + '">' + esc(p.name) + (p.txCode ? ' (' + esc(p.txCode) + ')' : '') + '</option>'; }).join('') + '</select></div>') +
      '<div class="f-field"><label>이름</label><input class="f-input" id="npName" style="width:100%" value="' + esc(isSub ? opts.fromNode.name + ' 상세' : '') + '" placeholder="선택한 항목이 있으면 자동으로 채워집니다"></div>' +
      '<div class="f-field"><label>담당자</label><input class="f-input" id="npOwner" style="width:100%"></div>' +
      '<div class="f-field"><label>상태</label><select class="f-select" id="npStatus" style="width:100%">' +
      STATUSES.map(function (s) { return '<option' + (s === '진행중' ? ' selected' : '') + '>' + s + '</option>'; }).join('') + '</select></div>' +
      '<div class="f-field"><label>노드 구성</label><select class="f-select" id="npNodeSource" style="width:100%">' +
      Object.keys(NODE_SOURCE_LABEL).map(function (k) { return '<option value="' + k + '">' + NODE_SOURCE_LABEL[k] + '</option>'; }).join('') + '</select></div>' +
      '<div class="f-field"><label>카테고리 (선택)</label><select class="f-select" id="npDomain" style="width:100%"><option value="">-- 없음 --</option>' +
      LK_PROCESS_DOMAINS.map(function (d) { return '<option value="' + d + '">' + d + '</option>'; }).join('') + '</select></div>' +
      (isSub ? '' : '<div class="f-field"><label>상위 그룹 (선택)</label><select class="f-select" id="npParent" style="width:100%"><option value="">-- 없음 --</option>' +
        sameModel.map(function (p) { return '<option value="' + esc(p.id) + '">' + esc(p.name) + '</option>'; }).join('') + '</select></div>') +
      '</div>' +
      '<div class="modal-input"><div class="row"><span></span><span class="pick-btns">' +
      '<button class="btn ghost sm" data-close>취소</button><button class="btn sm" id="npCreate">생성</button></span></div></div>';
    $('newProcModal').classList.add('open');
  }
  function closeNewProc() { S.newProc = null; $('newProcModal').classList.remove('open'); }
  async function submitNewProc() {
    var np = S.newProc, body = {
      model: 'tobe', name: ($('npName').value || '').trim(), owner: ($('npOwner').value || '').trim(),
      status: $('npStatus').value, parentId: $('npParent') ? ($('npParent').value || null) : null,
      nodeSource: $('npNodeSource').value, domain: $('npDomain').value
    };
    if ($('npCopyFrom') && $('npCopyFrom').value) body.copyFromProcessId = $('npCopyFrom').value;
    if (!body.name && !body.copyFromProcessId) { toast('이름을 입력하거나 선택 항목을 고르세요', true); return; }
    try {
      var detail = await api('POST', '/api/linkage/processes', body);
      closeNewProc();
      if (np.fromNode) {
        np.fromNode.subProcessId = detail.process.id;
        await saveCanvas();
      }
      toast('생성되었습니다');
      location.hash = '#' + detail.process.id;
    } catch (e) { toast('생성 실패: ' + e.message, true); }
  }

  /* ---------- 프로세스 수정 모달 (이름·담당자·상태·거래코드·상위 그룹) ---------- */
  function openEditProc() {
    var p = S.detail.process;
    S.newProc = { model: p.model, editPid: p.id };
    var sameModel = S.processes.filter(function (x) { return x.model === p.model && x.id !== p.id; });
    $('newProcBox').innerHTML =
      '<div class="modal-hd"><div><h3>프로세스 수정</h3><p>' + esc(p.id) + ' · 캔버스·매핑은 바뀌지 않습니다</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-list">' +
      '<div class="f-field"><label>이름</label><input class="f-input" id="npName" style="width:100%" value="' + esc(p.name) + '"></div>' +
      '<div class="f-field"><label>담당자</label><input class="f-input" id="npOwner" style="width:100%" value="' + esc(p.owner) + '"></div>' +
      '<div class="f-field"><label>상태</label><select class="f-select" id="npStatus" style="width:100%">' +
      STATUSES.map(function (s) { return '<option' + (s === p.status ? ' selected' : '') + '>' + s + '</option>'; }).join('') + '</select></div>' +
      '<div class="f-field"><label>거래코드(txCode)</label><input class="f-input" id="npTx" style="width:100%" value="' + esc(p.txCode) + '" placeholder="예: TX_QPM_UDCHK1 (비우면 AS-IS 콜트리 패널이 사라집니다)"></div>' +
      '<div class="f-field"><label>카테고리 (선택)</label><select class="f-select" id="npDomain" style="width:100%"><option value="">-- 없음 --</option>' +
      LK_PROCESS_DOMAINS.map(function (d) { return '<option value="' + d + '"' + (d === p.domain ? ' selected' : '') + '>' + d + '</option>'; }).join('') + '</select></div>' +
      '<div class="f-field"><label>상위 그룹 (선택)</label><select class="f-select" id="npParent" style="width:100%"><option value="">-- 없음 --</option>' +
      sameModel.map(function (x) { return '<option value="' + esc(x.id) + '"' + (x.id === p.parentId ? ' selected' : '') + '>' + esc(x.name) + '</option>'; }).join('') + '</select></div>' +
      '</div>' +
      '<div class="modal-input"><div class="row"><span></span><span class="pick-btns">' +
      '<button class="btn ghost sm" data-close>취소</button><button class="btn sm" id="npCreate">저장</button></span></div></div>';
    $('newProcModal').classList.add('open');
  }
  async function submitEditProc() {
    var pid = S.newProc.editPid, body = {
      name: ($('npName').value || '').trim(), owner: ($('npOwner').value || '').trim(),
      status: $('npStatus').value, txCode: ($('npTx').value || '').trim(), parentId: $('npParent').value || null,
      domain: $('npDomain').value
    };
    try {
      S.detail = await api('PUT', '/api/linkage/processes/' + encodeURIComponent(pid), body);
      closeNewProc();
      renderCanvas();
      toast('수정되었습니다');
    } catch (e) { toast('수정 실패: ' + e.message, true); }
  }

  /* ---------- 캔버스 화면 ---------- */
  function nodeEl(id) { return $('lkCanvas').querySelector('[data-node="' + id + '"]'); }
  function findNode(id) { return (S.detail.nodes || []).filter(function (n) { return n.id === id; })[0]; }
  function nextLocalId(prefix) { return prefix + '-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5); }
  // AS-IS는 조회 전용(캔버스·매핑 모두 수정 불가) — TO-BE만 PL 모드에서 편집 가능
  function canEditCanvas() { return S.mode === 'pl' && S.detail.process.model !== 'asis'; }

  function txOf() {
    var p = S.detail.process;
    if (!p.txCode) return null;
    return S.transactions.filter(function (t) { return t.id === p.txCode; })[0] || null;
  }
  function treeHTML(tx) {
    var byParent = {};
    tx.nodes.forEach(function (n) { (byParent[n.parentId || ''] = byParent[n.parentId || ''] || []).push(n); });
    function render(parentId) {
      return (byParent[parentId || ''] || []).map(function (n) {
        var kids = byParent[n.id] || [];
        var label = n.method.indexOf('#') >= 0 ? n.method.split('#').pop() : n.method;
        if (!kids.length) {
          var dest = n.mappedTo, here = dest && dest.processId === S.pid;
          var destHTML = !dest ? '' : here
            ? ' <span class="src-id">→ ' + esc(dest.nodeName) + '</span>'
            : ' <span class="src-id"><a href="#' + esc(dest.processId) + '" data-nav-process="1">→ ' + esc(dest.processName) + ' · ' + esc(dest.nodeName) + '</a></span>';
          return '<div class="lk-tree-leaf' + (n.mapped ? ' mapped' : '') + '" draggable="' + canEditCanvas() + '" data-cn="' + esc(n.id) + '" title="' + esc(n.method) + '">' +
            (n.mapped ? '<span class="ck">✓</span>' : '○') + ' ' + esc(label) + destHTML + '</div>';
        }
        return '<div class="lk-tree-node"><div class="lk-tree-branch">' + esc(label) + '</div>' + render(n.id) + '</div>';
      }).join('');
    }
    return render(null) || '<div class="empty">콜트리가 없습니다.</div>';
  }
  function renderSide() {
    var tx = txOf();
    if (!tx) { $('lkSide').style.display = 'none'; return; }
    $('lkSide').style.display = '';
    $('lkTree').innerHTML = treeHTML(tx);
  }

  var NODE_CATEGORY_LABEL = { service: '서비스', if_external: '인터페이스(대외계 연결)', if_channel: '인터페이스(채널계 연결)' };
  function nodeHTML(n) {
    var pl = canEditCanvas(), free = !n.refId;
    var mapped = (n.mapped || []).map(function (m) {
      var label = m.method.indexOf('#') >= 0 ? m.method.split('#').pop() : m.method;
      return '<span class="map-chip">' + esc(label) + (pl ? '<span class="x" data-unmap="' + esc(m.callNodeId) + '">✕</span>' : '') + '</span>';
    }).join('');
    var nameHTML = free
      ? (pl ? '<div class="nd-name" data-nd-name="1" title="더블클릭: 이름 수정">' + esc(n.name || '(이름 없음)') + '</div>'
            : '<div class="nd-name">' + esc(n.name || '(이름 없음)') + '</div>')
      : '<div class="nd-name">' + esc(n.name || '(이름 없음)') + (n.refMissing ? ' <span class="chip-missing">삭제됨</span>' : '') +
          (n.devDone ? ' <span class="nd-done">✓ 완료</span>' : '') + '</div>' +
        '<div class="src-id">' + esc(n.refId) + (n.refMissing ? '' :
          ' · <a href="index.html#' + S.detail.process.nodeSource + '?id=' + encodeURIComponent(n.refId) + '" target="_blank" rel="noopener">열기 →</a>') + '</div>';
    return '<div class="lk-node cat-' + (n.category || 'service') + (n.id === S.selId ? ' sel' : '') + '" data-node="' + esc(n.id) + '" style="left:' + n.x + 'px;top:' + n.y + 'px">' +
      '<div class="nd-row"><span></span><button class="nd-del pl-only" data-nd-del="1" title="삭제">✕</button></div>' +
      nameHTML +
      '<input class="txt-input nd-note" data-nd-note="1" value="' + esc(n.note || '') + '" placeholder="설명 추가"' + (pl ? '' : ' disabled') + '>' +
      '<select class="nd-cat ' + (n.category || 'service') + '" data-nd-cat="1"' + (pl ? '' : ' disabled') + '>' +
      Object.keys(NODE_CATEGORY_LABEL).map(function (k) { return '<option value="' + k + '"' + (k === n.category ? ' selected' : '') + '>' + NODE_CATEGORY_LABEL[k] + '</option>'; }).join('') + '</select>' +
      (n.subProcessId ? '<button class="nd-sub" data-nd-sub="' + esc(n.subProcessId) + '">하위 캔버스 열기 →</button>'
        : (pl ? '<button class="nd-sub pl-only" data-nd-sub-new="1">+ 하위 캔버스 만들기</button>' : '')) +
      (mapped ? '<div class="nd-map">' + mapped + '</div>' : '') +
      (pl ? '<div class="anchor pl-only" data-nd-anchor="1" title="드래그: 연결선 만들기"></div>' : '') +
      '</div>';
  }
  function nodeRect(n) {
    var el = nodeEl(n.id);
    var h = el ? el.offsetHeight : NH_FALLBACK;
    return { x: n.x, y: n.y, w: NW, h: h };
  }
  // 중심에서 상대 노드 방향으로 쏜 선이 사각형 경계와 만나는 점(각도에 따라 연속적으로 변함 — 같은 노드에서 나가는
  // 여러 연결선이 한 점에 뭉치지 않고 가장자리를 따라 자연스럽게 퍼지도록).
  function sidePoint(r, towardX, towardY) {
    var cx = r.x + r.w / 2, cy = r.y + r.h / 2, dx = towardX - cx, dy = towardY - cy;
    if (!dx && !dy) return { x: cx, y: cy };
    var hw = r.w / 2, hh = r.h / 2;
    var scale = Math.min(dx ? hw / Math.abs(dx) : Infinity, dy ? hh / Math.abs(dy) : Infinity);
    return { x: cx + dx * scale, y: cy + dy * scale };
  }
  function redrawEdges() {
    var svg = $('lkEdgeSvg'), defs = svg.querySelector('defs');
    var lines = (S.detail.edges || []).map(function (e, i) {
      var a = findNode(e.from), b = findNode(e.to);
      if (!a || !b) return '';
      var ra = nodeRect(a), rb = nodeRect(b);
      var ca = { x: ra.x + ra.w / 2, y: ra.y + ra.h / 2 }, cb = { x: rb.x + rb.w / 2, y: rb.y + rb.h / 2 };
      var p1 = sidePoint(ra, cb.x, cb.y), p2 = sidePoint(rb, ca.x, ca.y);
      return '<g data-edge="' + i + '"><line class="lk-edge-hit" x1="' + p1.x + '" y1="' + p1.y + '" x2="' + p2.x + '" y2="' + p2.y + '"></line>' +
        '<line class="' + (e.async ? 'async' : '') + '" x1="' + p1.x + '" y1="' + p1.y + '" x2="' + p2.x + '" y2="' + p2.y + '"></line>' +
        (e.async ? '<text class="edge-label" x="' + (p1.x + p2.x) / 2 + '" y="' + ((p1.y + p2.y) / 2 - 4) + '" text-anchor="middle">비동기</text>' : '') +
        '</g>';
    }).join('');
    svg.innerHTML = defs.outerHTML + lines + (S.tempLine || '');
  }
  function renderCanvas() {
    var p = S.detail.process;
    document.body.classList.toggle('asis-locked', p.model === 'asis');
    $('lkPName').textContent = p.name;
    $('lkCrumbName').textContent = p.name;
    $('lkPMeta').textContent = (p.model === 'asis' ? 'AS-IS' : 'TO-BE') + (p.txCode ? ' · ' + p.txCode : '') + (p.owner ? ' · ' + p.owner : '') + ' · ' + p.status;
    var svg = $('lkEdgeSvg');
    $('lkCanvas').innerHTML = '';
    $('lkCanvas').appendChild(svg);
    (S.detail.nodes || []).forEach(function (n) { $('lkCanvas').insertAdjacentHTML('beforeend', nodeHTML(n)); });
    redrawEdges();
    renderSide();
    renderRefSide();
    $('btnDelNode').disabled = !S.selId;
  }
  function refSideKind() { return 'dev'; }
  async function loadCanvas(pid) {
    S.detail = await fetchJSON('/api/linkage/processes/' + encodeURIComponent(pid));
    S.selId = null;
    S.refItems = S.detail.process.model === 'tobe' ? (await fetchJSON('/api/' + refSideKind())).items : null;
    renderCanvas();
  }
  function renderRefSide() {
    if (!S.refItems) { $('lkRefSide').style.display = 'none'; return; }
    $('lkRefSide').style.display = '';
    $('lkRefTitle').textContent = '개발 목록';
    renderRefList($('lkRefQ').value || '');
  }
  function renderRefList(q) {
    var ql = q.toLowerCase();
    var used = {};
    if (S.detail.process.nodeSource !== 'free') {
      (S.detail.nodes || []).forEach(function (n) { if (n.refId) used[n.refId] = true; });
    }
    var rows = S.refItems.filter(function (x) { return !used[x.id] && (!ql || (x.id + ' ' + x.name).toLowerCase().indexOf(ql) >= 0); })
      .map(function (x) { return '<div class="lk-tree-leaf" draggable="' + canEditCanvas() + '" data-ref-drag="' + esc(x.id) + '" data-ref-name="' + esc(x.name) + '" title="' + esc(x.id) + '">' + esc(x.id) + ' · ' + esc(x.name) + '</div>'; }).join('');
    $('lkRefList').innerHTML = rows || '<div class="empty">추가할 수 있는 항목이 없습니다.</div>';
  }

  /* ---------- 노드 드래그 / 연결선 드래그 ---------- */
  function cardScrollPoint(e) {
    var r = $('lkCanvas').getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }
  function startNodeDrag(e, n) {
    e.preventDefault();
    var startX = e.clientX, startY = e.clientY, ox = n.x, oy = n.y;
    S.drag = { n: n };
    function onMove(ev) {
      n.x = Math.max(0, ox + (ev.clientX - startX));
      n.y = Math.max(0, oy + (ev.clientY - startY));
      var el = nodeEl(n.id);
      el.style.left = n.x + 'px'; el.style.top = n.y + 'px';
      redrawEdges();
    }
    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      S.drag = null;
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }
  function startEdgeDrag(e, n) {
    e.preventDefault();
    e.stopPropagation();
    var r = nodeRect(n);
    var from = { x: r.x + r.w, y: r.y + r.h / 2 };
    function onMove(ev) {
      var pt = cardScrollPoint(ev);
      S.tempLine = '<line x1="' + from.x + '" y1="' + from.y + '" x2="' + pt.x + '" y2="' + pt.y + '" stroke-dasharray="4,3" stroke="#FB7520"></line>';
      redrawEdges();
    }
    function onUp(ev) {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      S.tempLine = null;
      var el = document.elementFromPoint(ev.clientX, ev.clientY);
      var target = el && el.closest('[data-node]');
      if (target) {
        var toId = target.getAttribute('data-node');
        if (toId !== n.id) {
          var dup = (S.detail.edges || []).some(function (x) { return x.from === n.id && x.to === toId; });
          if (!dup) S.detail.edges.push({ from: n.id, to: toId });
        }
      }
      redrawEdges();
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  function addNode() {
    if (S.detail.process.nodeSource !== 'free') { openRefPicker(); return; }
    var n = { id: nextLocalId('ND'), kind: 'step', name: '새 노드', x: 40, y: 40, status: 'ok', subProcessId: null, mapped: [], note: '', category: 'service' };
    S.detail.nodes.push(n);
    renderCanvas();
    toast('노드를 추가했습니다. 저장 버튼으로 반영하세요');
  }

  /* ---------- 개발 항목 피커 (노드 구성이 free가 아닐 때 "+ 노드 추가" — 드래그 대안 경로) ---------- */
  function openRefPicker() {
    var used = {};
    (S.detail.nodes || []).forEach(function (n) { if (n.refId) used[n.refId] = true; });
    S.refPick = { items: S.refItems.filter(function (x) { return !used[x.id]; }) };
    $('refPickBox').innerHTML =
      '<div class="modal-hd"><div><h3>개발 항목 선택</h3><p>이미 이 캔버스에 있는 항목은 목록에서 빠집니다</p></div>' +
      '<button class="modal-close" data-close>✕</button></div>' +
      '<div class="modal-search"><input class="f-input" id="refPickQ" placeholder="검색" style="width:100%"></div>' +
      '<div class="modal-list" id="refPickList"></div>' +
      '<div class="modal-input"><div class="row"><span></span><span class="pick-btns"><button class="btn sm" data-close>닫기</button></span></div></div>';
    renderRefPickList('');
    $('refPickModal').classList.add('open');
    $('refPickQ').focus();
  }
  function renderRefPickList(q) {
    var ql = q.toLowerCase();
    var rows = S.refPick.items.filter(function (x) { return !ql || (x.id + ' ' + x.name).toLowerCase().indexOf(ql) >= 0; })
      .map(function (x) { return '<div class="ci"><button class="ci-go" data-ref-pick="' + esc(x.id) + '">' + esc(x.id) + ' · ' + esc(x.name) + '</button></div>'; }).join('');
    $('refPickList').innerHTML = rows || '<div class="empty">추가할 수 있는 항목이 없습니다.</div>';
  }
  function closeRefPick() { S.refPick = null; $('refPickModal').classList.remove('open'); }
  function newNodeAt(x, y, refId, name) {
    var ref = S.detail.process.nodeSource !== 'free';
    return { id: nextLocalId('ND'), kind: 'step', name: name, x: Math.max(0, x), y: Math.max(0, y), status: 'ok',
      subProcessId: null, mapped: [], note: '', category: 'service', refId: ref ? refId : null, refMissing: false };
  }
  function addRefNode(refId) {
    var item = S.refPick.items.filter(function (x) { return x.id === refId; })[0];
    closeRefPick();
    S.detail.nodes.push(newNodeAt(40, 40, refId, item ? item.name : refId));
    renderCanvas();
    toast('노드를 추가했습니다. 저장 버튼으로 반영하세요');
  }
  function createNodeFromDrag(refId, name, pt) {
    S.detail.nodes.push(newNodeAt(pt.x - NW / 2, pt.y - 20, refId, name));
    renderCanvas();
    toast('노드를 추가했습니다. 저장 버튼으로 반영하세요');
  }
  function deleteSelectedNode() {
    if (!S.selId) return;
    var id = S.selId;
    S.detail.nodes = S.detail.nodes.filter(function (n) { return n.id !== id; });
    S.detail.edges = S.detail.edges.filter(function (e) { return e.from !== id && e.to !== id; });
    S.selId = null;
    renderCanvas();
    toast('노드를 삭제했습니다. 저장 버튼으로 반영하세요');
  }
  async function saveCanvas() {
    try {
      S.detail = await api('PUT', '/api/linkage/processes/' + encodeURIComponent(S.pid) + '/canvas',
        { nodes: S.detail.nodes, edges: S.detail.edges });
      S.selId = null;
      renderCanvas();
      toast('저장되었습니다');
    } catch (e) { toast('저장 실패: ' + e.message, true); }
  }
  function makeSubCanvas(n) {
    openNewProc({ fromNode: n });
  }
  async function mapCallNode(callNodeId, nodeId) {
    try {
      await api('POST', '/api/linkage/map', { callNodeId: callNodeId, nodeId: nodeId });
      await loadCanvas(S.pid);
      toast('매핑되었습니다');
    } catch (e) { toast('매핑 실패: ' + e.message, true); }
  }
  async function unmapCallNode(callNodeId) {
    try {
      await api('DELETE', '/api/linkage/map/' + encodeURIComponent(callNodeId));
      await loadCanvas(S.pid);
      toast('매핑을 해제했습니다');
    } catch (e) { toast('해제 실패: ' + e.message, true); }
  }

  /* ---------- 권한 미리보기(PL/작업자) ---------- */
  function setMode(m) {
    S.mode = m;
    document.body.classList.toggle('worker-mode', m === 'worker');
    $('btnPL').classList.toggle('active', m === 'pl');
    $('btnWorker').classList.toggle('active', m === 'worker');
    if (S.pid) renderCanvas(); else renderList();
  }

  /* ---------- 라우팅 ---------- */
  async function route() {
    var pid = (location.hash || '').replace('#', '').trim();
    if (!pid) {
      S.pid = null;
      document.body.classList.remove('asis-locked');
      $('lkList').style.display = '';
      $('lkCanvasView').style.display = 'none';
      await reloadProcesses();
      return;
    }
    S.pid = pid;
    $('lkList').style.display = 'none';
    $('lkCanvasView').style.display = '';
    try {
      await loadCanvas(pid);
    } catch (e) {
      toast('불러오지 못했습니다: ' + e.message, true);
      location.hash = '';
    }
  }

  /* ---------- 이벤트 바인딩 ---------- */
  function bind() {
    window.addEventListener('hashchange', route);
    $('lkBack').addEventListener('click', function (e) { e.preventDefault(); location.hash = ''; });
    LK_PROCESS_DOMAINS.forEach(function (d) { $('lkDomainFilter').insertAdjacentHTML('beforeend', '<option value="' + d + '">' + d + '</option>'); });

    $('btnPL').addEventListener('click', function () { setMode('pl'); });
    $('btnWorker').addEventListener('click', function () { setMode('worker'); });

    $('btnNewTobe').addEventListener('click', function () { openNewProc(); });
    $('btnEditProcess').addEventListener('click', openEditProc);
    $('newProcModal').addEventListener('click', function (e) {
      if (e.target === this || e.target.hasAttribute('data-close')) { closeNewProc(); return; }
      if (e.target.id === 'npCreate') { if (S.newProc.editPid) submitEditProc(); else submitNewProc(); }
    });
    $('newProcBox').addEventListener('change', function (e) {
      if (e.target.id === 'npCopyFrom' && e.target.value && !$('npName').value) {
        var p = S.processes.filter(function (x) { return x.id === e.target.value; })[0];
        if (p) $('npName').value = p.name + ' (복사본)';
      }
    });

    $('lkGroups').addEventListener('click', function (e) {
      var t = e.target, x;
      if ((x = t.closest('[data-group-toggle]'))) {
        var k = x.getAttribute('data-group-toggle');
        S.collapsed[k] = !S.collapsed[k];
        renderList();
        return;
      }
      if ((x = t.closest('[data-del-proc]'))) { e.stopPropagation(); deleteProcess(x.getAttribute('data-del-proc')); return; }
      if ((x = t.closest('[data-copy-tobe]'))) {
        e.stopPropagation();
        openNewProc();
        setTimeout(function () { $('npCopyFrom').value = x.getAttribute('data-copy-tobe'); $('npCopyFrom').dispatchEvent(new Event('change')); }, 0);
        return;
      }
      var row = t.closest('[data-pid]');
      if (row) location.hash = '#' + row.getAttribute('data-pid');
    });
    $('lkSearchQ').addEventListener('input', function (e) { S.listFilter.q = e.target.value.trim().toLowerCase(); renderList(); });
    $('lkDomainFilter').addEventListener('change', function (e) { S.listFilter.domain = e.target.value; renderList(); });

    $('btnAddNode').addEventListener('click', addNode);
    $('btnDelNode').addEventListener('click', deleteSelectedNode);
    $('btnSaveCanvas').addEventListener('click', saveCanvas);
    $('btnDelProcess').addEventListener('click', async function () {
      if (!confirm('"' + S.pid + '" 프로세스를 삭제할까요? 캔버스·매핑도 함께 삭제됩니다.')) return;
      try {
        await api('DELETE', '/api/linkage/processes/' + encodeURIComponent(S.pid));
        toast('삭제했습니다');
        location.hash = '';
      } catch (e) { toast('삭제 실패: ' + e.message, true); }
    });

    $('lkCanvas').addEventListener('mousedown', function (e) {
      var nodeDiv = e.target.closest('[data-node]');
      if (!nodeDiv) return;
      var n = findNode(nodeDiv.getAttribute('data-node'));
      if (!n) return;
      if (e.target.closest('[data-nd-anchor]')) { startEdgeDrag(e, n); return; }
      if (e.target.closest('[data-nd-del],[data-nd-sub],[data-nd-sub-new],[data-unmap],[data-nd-note],[data-nd-cat]')) return;
      if (canEditCanvas()) startNodeDrag(e, n);
    });
    $('lkCanvas').addEventListener('click', function (e) {
      var t = e.target, x;
      if ((x = t.closest('[data-unmap]'))) { unmapCallNode(x.getAttribute('data-unmap')); return; }
      if ((x = t.closest('[data-nd-del]'))) {
        var nid = x.closest('[data-node]').getAttribute('data-node');
        S.selId = nid;
        deleteSelectedNode();
        return;
      }
      if ((x = t.closest('[data-nd-sub]'))) { location.hash = '#' + x.getAttribute('data-nd-sub'); return; }
      if ((x = t.closest('[data-nd-sub-new]'))) {
        var n2 = findNode(x.closest('[data-node]').getAttribute('data-node'));
        makeSubCanvas(n2);
        return;
      }
      if ((x = t.closest('[data-edge]'))) {
        if (!canEditCanvas()) return;
        var i = +x.getAttribute('data-edge');
        if (e.shiftKey) {
          if (confirm('연결선을 삭제할까요?')) { S.detail.edges.splice(i, 1); redrawEdges(); }
        } else {
          S.detail.edges[i].async = !S.detail.edges[i].async;
          redrawEdges();
        }
        return;
      }
      if ((x = t.closest('[data-node]'))) {
        S.selId = S.selId === x.getAttribute('data-node') ? null : x.getAttribute('data-node');
        renderCanvas();
      }
    });
    $('lkCanvas').addEventListener('change', function (e) {
      var nodeDiv = e.target.closest('[data-node]');
      if (!nodeDiv) return;
      var n = findNode(nodeDiv.getAttribute('data-node'));
      if (!n) return;
      if (e.target.matches('[data-nd-note]')) n.note = e.target.value.trim();
      else if (e.target.matches('[data-nd-cat]')) { n.category = e.target.value; renderCanvas(); }
    });

    // 콜트리 → 캔버스 노드 드래그 매핑
    $('lkTree').addEventListener('dragstart', function (e) {
      var leaf = e.target.closest('[data-cn]');
      if (!leaf) return;
      e.dataTransfer.setData('text/plain', leaf.getAttribute('data-cn'));
    });
    // 개발 목록 → 캔버스 드래그로 노드 생성
    $('lkRefList').addEventListener('dragstart', function (e) {
      var leaf = e.target.closest('[data-ref-drag]');
      if (!leaf) return;
      e.dataTransfer.setData('text/plain', 'REF:' + JSON.stringify({ id: leaf.getAttribute('data-ref-drag'), name: leaf.getAttribute('data-ref-name') }));
    });
    $('lkRefQ').addEventListener('input', function (e) { renderRefList(e.target.value); });
    $('lkCanvas').addEventListener('dragover', function (e) {
      e.preventDefault();
      var nodeDiv = e.target.closest('[data-node]');
      if (nodeDiv) nodeDiv.classList.add('drop-ok');
    });
    $('lkCanvas').addEventListener('dragleave', function (e) {
      var nodeDiv = e.target.closest('[data-node]');
      if (nodeDiv) nodeDiv.classList.remove('drop-ok');
    });
    $('lkCanvas').addEventListener('drop', function (e) {
      e.preventDefault();
      var nodeDiv = e.target.closest('[data-node]');
      if (nodeDiv) nodeDiv.classList.remove('drop-ok');
      var raw = e.dataTransfer.getData('text/plain');
      if (!raw) return;
      if (raw.indexOf('REF:') === 0) {
        var info = JSON.parse(raw.slice(4));
        createNodeFromDrag(info.id, info.name, cardScrollPoint(e));
        return;
      }
      if (nodeDiv) mapCallNode(raw, nodeDiv.getAttribute('data-node'));
    });

    // 자유 입력 노드 이름 수정 (더블클릭 → 입력창)
    $('lkCanvas').addEventListener('dblclick', function (e) {
      if (!canEditCanvas()) return;
      var x = e.target.closest('[data-nd-name]');
      if (!x) return;
      x.outerHTML = '<input class="txt-input" data-nd-name-input="1" value="' + esc(x.textContent.trim()) + '" style="width:100%">';
      var inp = x.closest('[data-node]').querySelector('[data-nd-name-input]');
      inp.focus();
      inp.select();
    });
    $('lkCanvas').addEventListener('keydown', function (e) {
      if (e.target.matches('[data-nd-name-input]') && e.key === 'Enter') e.target.blur();
    });
    $('lkCanvas').addEventListener('blur', function (e) {
      if (!e.target.matches || !e.target.matches('[data-nd-name-input]')) return;
      var n = findNode(e.target.closest('[data-node]').getAttribute('data-node'));
      if (n) n.name = e.target.value.trim() || n.name;
      renderCanvas();
    }, true);

    // 개발 항목 피커 모달
    $('refPickModal').addEventListener('click', function (e) {
      var t = e.target, x;
      if (t === this || t.hasAttribute('data-close')) { closeRefPick(); return; }
      if ((x = t.closest('[data-ref-pick]'))) addRefNode(x.getAttribute('data-ref-pick'));
    });
    $('refPickBox').addEventListener('input', function (e) {
      if (e.target.id === 'refPickQ') renderRefPickList(e.target.value);
    });
  }

  async function boot() {
    try {
      var res = await Promise.all([fetchJSON('/api/linkage/processes'), fetchJSON('/api/linkage/transactions')]);
      S.processes = res[0].items;
      S.transactions = res[1].items;
    } catch (e) {
      $('lkGroups').innerHTML = '<div class="empty">데이터를 읽지 못했습니다 (' + esc(e.message) + '). 로컬 서버로 실행하세요: python3 server.py</div>';
      return;
    }
    bind();
    route();
  }

  boot();
})();
