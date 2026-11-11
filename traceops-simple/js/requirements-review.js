/* 요구사항 개정 검토 (ReqSync) — 회의록 업로드/선택 → 팝업(스플릿) 검토 → PL 확정 → 요구사항 반영 + 하이라이트
 * 데이터: 관계형 DB(traceops.db) — /api/meetings, /api/decisions, /api/reviews, /api/requirements
 * 실제 유료 AI API는 붙이지 않는다 — 업로드한 파일명을 data/meetings.json 목록과 매칭해 "이미 분석된 척" 결과를 보여주는 시뮬레이션.
 * 확정 시 요구사항 내용이 DB의 requirements에 반영되어(변경 이력에 근거 회의·결정사항 기록)
 * 요구사항관리 화면에서도 바로 확인된다(?reqId= 하이라이트도 그 화면의 기존 기능을 그대로 재사용).
 */
(function () {
  'use strict';

  var PL_NAME = '황금빛';

  var S = {
    meetings: [], decisions: [], requirements: [], review: {},
    activeMeetingFile: null, activeId: null, lastAcceptedReqId: null
  };

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var timer;
  function toast(msg, err) {
    var t = $('toast');
    t.textContent = msg; t.classList.toggle('err', !!err); t.classList.add('show');
    clearTimeout(timer); timer = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }
  async function fetchJSON(path) {
    var r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(path + ' (' + r.status + ')');
    return r.json();
  }

  function reqById(id) { return S.requirements.filter(function (x) { return x.id === id; })[0] || null; }
  function reviewOf(id) { return S.review[id] || (S.review[id] = { reviewed: false, history: [] }); }
  function decisionsOf(file) { return S.decisions.filter(function (d) { return d.meetingFile === file; }); }
  function meetingOf(file) { return S.meetings.filter(function (m) { return m.file === file; })[0] || null; }

  /* ---------- diff: 문자 단위 LCS 기반 간단 diff ---------- */
  function diffChars(a, b) {
    var n = a.length, m = b.length;
    var dp = []; for (var i = 0; i <= n; i++) dp.push(new Array(m + 1).fill(0));
    for (i = n - 1; i >= 0; i--) for (var j = m - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    i = 0; var k = 0, out = [];
    while (i < n && k < m) {
      if (a[i] === b[k]) { out.push({ t: 'eq', c: a[i] }); i++; k++; }
      else if (dp[i + 1][k] >= dp[i][k + 1]) { out.push({ t: 'del', c: a[i] }); i++; }
      else { out.push({ t: 'ins', c: b[k] }); k++; }
    }
    while (i < n) { out.push({ t: 'del', c: a[i] }); i++; }
    while (k < m) { out.push({ t: 'ins', c: b[k] }); k++; }
    var merged = [];
    out.forEach(function (seg) {
      var last = merged[merged.length - 1];
      if (last && last.t === seg.t) last.c += seg.c; else merged.push({ t: seg.t, c: seg.c });
    });
    return merged;
  }
  function renderDiff(orig, proposed) {
    return diffChars(orig, proposed).map(function (seg) {
      if (seg.t === 'eq') return esc(seg.c);
      if (seg.t === 'ins') return '<ins>' + esc(seg.c) + '</ins>';
      return '<del>' + esc(seg.c) + '</del>';
    }).join('');
  }

  var STATUS_META = { ok: { cls: 'ok', label: '확정' }, review: { cls: 'review', label: '검토 중' }, open: { cls: 'open', label: '미정·이슈' } };
  var CONF_META = { high: { cls: 'high', label: '매칭 신뢰도 높음' }, mid: { cls: 'mid', label: '매칭 신뢰도 중간' }, new: { cls: 'new', label: '매칭 실패 · 신규 후보' } };

  function proposedText(d, req) {
    if (d.replaceWith) return d.replaceWith;
    if (req) return (req.content || '') + (d.addition || '');
    return d.decision;
  }

  /* ---------- 라이브러리(회의 카드 목록) ---------- */
  function renderLibrary() {
    $('meetGrid').innerHTML = S.meetings.map(function (m) {
      var items = decisionsOf(m.file);
      var n = items.length;
      return '<div class="rv-card' + (n ? '' : ' muted') + '" data-file="' + esc(m.file) + '">' +
        '<div class="rv-top"><span class="rv-meta">' + esc(m.label) + '</span></div>' +
        '<p class="rv-decision">재생시간 ' + esc(m.duration) + '</p>' +
        '<div class="rv-match">' + (n
          ? '<span class="rv-conf high">추출 결정사항 ' + n + '건</span>'
          : '<span class="rv-conf new">사전 분석 결과 없음</span>') + '</div>' +
        '</div>';
    }).join('');
    $('meetGrid').querySelectorAll('.rv-card').forEach(function (el) {
      el.addEventListener('click', function () {
        var file = el.getAttribute('data-file');
        if (!decisionsOf(file).length) { toast('이 회의록은 추출된 결정사항이 없습니다'); return; }
        openMeetingModal(file, false);
      });
    });
  }

  /* ---------- 업로드(시뮬레이션): 파일명으로 기존 분석 결과 매칭 ---------- */
  function handleUpload(file) {
    var m = meetingOf(file.name);
    if (!m) {
      toast('등록되지 않은 회의록입니다. 회의록 관리 목록에 먼저 등록한 뒤 다시 업로드해 주세요.', true);
      return;
    }
    if (!decisionsOf(m.file).length) { toast('이 회의록에서는 추출된 결정사항이 없습니다'); return; }
    openMeetingModal(m.file, true);
  }

  /* ---------- 분석 로딩 연출: 신규 업로드는 단계별 문구로 길게, 기존 카드 재열람은 짧게 ---------- */
  var LOAD_STEPS_FRESH = ['회의록 원문을 읽는 중...', '결정사항 · 미정사항 추출 중...', '요구사항 목록과 매칭하는 중...'];
  var LOAD_STEPS_CACHED = ['분석 결과를 불러오는 중...'];
  function runLoading(steps, done) {
    $('mDecisionList').innerHTML = '<div class="rv-loading"><div class="rv-spin"></div><b id="loadLabel"></b></div>';
    $('mEditPanel').innerHTML = '';
    var i = 0;
    function tick() { var el = $('loadLabel'); if (el) el.textContent = steps[i % steps.length]; i++; }
    tick();
    var iv = setInterval(tick, 480);
    setTimeout(function () { clearInterval(iv); done(); }, steps.length * 480 + 420);
  }

  /* ---------- 모달: 좌(이 회의록 결정사항) / 우(diff + 편집 + 액션) ---------- */
  function openMeetingModal(file, justUploaded) {
    S.activeMeetingFile = file;
    var items = decisionsOf(file);
    S.activeId = items.length ? items[0].id : null;
    var m = meetingOf(file);
    $('mTitle').textContent = (m ? m.label : file);
    $('mSub').textContent = (justUploaded ? '방금 업로드 · ' : '기존 분석 결과 · ') + file + ' · ' + items.length + '건 추출';
    $('rrvModal').classList.add('open');
    runLoading(justUploaded ? LOAD_STEPS_FRESH : LOAD_STEPS_CACHED, function () {
      renderMList();
      renderMEdit();
    });
  }
  function closeModal() {
    $('rrvModal').classList.remove('open');
    if (S.lastAcceptedReqId) {
      location.href = 'requirements.html?reqId=' + encodeURIComponent(S.lastAcceptedReqId);
    }
  }

  function renderMList() {
    var list = $('mDecisionList');
    var items = decisionsOf(S.activeMeetingFile);
    $('mCount').textContent = items.length + '건';
    list.innerHTML = items.map(function (d) {
      var rv = reviewOf(d.id);
      var status = rv.status || d.finalStatus;
      var st = STATUS_META[status];
      var cf = CONF_META[d.confidence];
      var req = d.reqId ? reqById(d.reqId) : null;
      return '<div class="rv-card' + (d.id === S.activeId ? ' active' : '') + '" data-id="' + d.id + '">' +
        '<div class="rv-top"><span class="rv-meta">' + d.id + '</span>' +
        '<span class="rv-badge dot ' + st.cls + '">' + st.label + '</span></div>' +
        '<p class="rv-decision">' + esc(d.decision) + '</p>' +
        '<div class="rv-match">' + (req
          ? '<span class="rv-reqid">' + esc(d.reqId) + '</span><span>' + esc(req.name) + '</span><span class="rv-conf ' + cf.cls + '" style="margin-left:auto">' + cf.label + '</span>'
          : '<span class="rv-conf ' + cf.cls + '">' + cf.label + '</span>') + '</div>' +
        '<div class="rv-excerpt"><span class="rv-ts">' + esc(d.excerptTs) + ' 발췌</span>“' + esc(d.excerpt) + '”</div>' +
        '</div>';
    }).join('');
    list.querySelectorAll('.rv-card').forEach(function (el) {
      el.addEventListener('click', function () { S.activeId = el.getAttribute('data-id'); renderMList(); renderMEdit(); });
    });
  }

  function historyBlock(rv) {
    if (!rv.history.length) return '';
    return '<div class="rv-history"><div class="rv-block-label">개정 이력</div>' +
      rv.history.map(function (r) { return '<div class="rv-history-row"><span class="rv-hts">' + esc(r.ts) + '</span><span>' + esc(r.who) + ' — ' + esc(r.what) + '</span></div>'; }).join('') +
      '</div>';
  }

  function renderMEdit() {
    var panel = $('mEditPanel');
    var d = decisionsOf(S.activeMeetingFile).filter(function (x) { return x.id === S.activeId; })[0];
    if (!d) { panel.innerHTML = '<div class="rv-empty">왼쪽에서 항목을 선택하면 요구사항 원문과 개정안을 여기서 비교·확정할 수 있습니다.</div>'; return; }
    var rv = reviewOf(d.id);
    var status = rv.status || d.finalStatus;

    if (!d.reqId) {
      panel.innerHTML =
        '<div class="rv-status-line">매칭 실패 — 요구사항 등록부에서 대응 항목을 찾지 못했습니다. 신규 항목 등록 여부를 PL이 판단해야 합니다.</div>' +
        '<div class="rv-req-head"><span class="rv-reqid">미매칭' + (d.newReqHint ? ' · ' + esc(d.newReqHint) : '') + '</span></div>' +
        '<div class="rv-block-label">AI 추출 결정사항</div>' +
        '<div class="rv-orig-box">' + esc(d.decision) + '</div>' +
        '<div class="rv-block-label">회의록 원문 발췌 (' + esc(d.excerptTs) + ')</div>' +
        '<div class="rv-excerpt" style="margin-bottom:16px">“' + esc(d.excerpt) + '”</div>' +
        '<div class="rv-action-row">' +
        '<button class="btn sm" onclick="RRV.act(\'' + d.id + '\',\'newreq\')">신규 항목으로 등록 표시</button>' +
        '<button class="btn ghost sm" onclick="RRV.act(\'' + d.id + '\',\'hold\')">보류</button>' +
        '</div>' + historyBlock(rv);
      return;
    }

    var req = reqById(d.reqId);
    var proposed = rv.editedText != null ? rv.editedText : proposedText(d, req);
    var origText = req ? (req.content || '') : '';
    var diffHtml = renderDiff(origText, proposed);
    var st = STATUS_META[status];

    panel.innerHTML =
      '<div class="rv-req-head"><span class="rv-reqid">' + esc(d.reqId) + '</span><h3>' + esc(req ? req.name : '') + '</h3></div>' +
      '<div class="rv-status-line"><span class="rv-badge dot ' + st.cls + '">' + st.label + '</span> ' +
      esc(S.activeMeetingFile) + ' 회의 결정사항 기준 보완안 · ' + (rv.reviewed ? '확정됨 (' + esc(rv.confirmedBy) + ', ' + esc(rv.confirmedAt) + ')' : 'PL 확인 대기') + '</div>' +
      '<div class="rv-block-label">기존 요구사항내역 원문</div>' +
      '<div class="rv-orig-box">' + esc(origText) + '</div>' +
      '<div class="rv-block-label">AI 보완안 (diff — 밑줄: 추가, 취소선: 삭제)</div>' +
      '<div class="rv-diff-box">' + diffHtml + '</div>' +
      '<div class="rv-block-label">PL 편집 영역 (필요 시 직접 수정 후 확정)</div>' +
      '<textarea class="rv-edit-box" id="editArea">' + esc(proposed) + '</textarea>' +
      '<div class="rv-action-row">' +
      '<button class="btn sm" onclick="RRV.act(\'' + d.id + '\',\'accept\')"' + (rv.reviewed ? ' disabled' : '') + '>수용 · 반영 확정</button>' +
      '<button class="btn ghost sm" onclick="RRV.act(\'' + d.id + '\',\'recheck\')">재검토 요청</button>' +
      '<button class="btn ghost sm" onclick="RRV.act(\'' + d.id + '\',\'reject\')">반려</button>' +
      '</div>' +
      '<div class="rv-block-label">회의록 원문 발췌 (' + esc(d.excerptTs) + ')</div>' +
      '<div class="rv-excerpt" style="margin-bottom:16px">“' + esc(d.excerpt) + '”</div>' +
      '<div class="rv-block-label" style="margin-bottom:2px">2차 검증 메모</div>' +
      '<div class="rv-excerpt" style="margin-bottom:16px">' + esc(d.verificationNote) + '</div>' +
      historyBlock(rv);
  }

  function nowStr() { return new Date().toISOString().slice(0, 16).replace('T', ' '); }
  function persistReview(id) { return api('PUT', '/api/reviews/' + encodeURIComponent(id), S.review[id]); }
  // 변경 이력(requirement_history)은 서버가 이전 값과 비교해 자동 기록, ctx로 근거 회의/결정사항을 붙인다
  async function persistRequirements(ctx) {
    S.requirements = (await api('PUT', '/api/requirements', { items: S.requirements, who: PL_NAME, ctx: ctx })).items;
  }

  window.RRV = {
    act: async function (id, action) {
      var d = S.decisions.filter(function (x) { return x.id === id; })[0];
      var rv = reviewOf(id);
      var ta = $('editArea');
      var edited = ta ? ta.value : null;
      var now = nowStr();
      if (action === 'accept') {
        rv.reviewed = true; rv.confirmedBy = PL_NAME; rv.confirmedAt = now; rv.status = 'ok'; rv.editedText = edited;
        if (d.reqId && edited != null) {
          var req = reqById(d.reqId);
          if (req) {
            req.content = edited;
            if (req.precondition) { req.precondition = ''; req.status = '수용'; }
            try {
              await persistRequirements({
                meetingFile: S.activeMeetingFile, decisionId: d.id,
                note: '회의록(' + (meetingOf(S.activeMeetingFile) || {}).label + ') 결정사항 반영 — ' + d.decision
              });
            } catch (e) { toast('반영 실패: ' + e.message, true); return; }
          }
        }
        S.lastAcceptedReqId = d.reqId || S.lastAcceptedReqId;
        rv.history.push({ ts: now, who: PL_NAME, what: '반영 확정' + (d.reqId ? ' — ' + d.reqId + ' 요구사항내역에 반영' : '') });
        toast('반영 확정되었습니다' + (d.reqId ? ' · ' + d.reqId : ''));
      } else if (action === 'reject') {
        rv.reviewed = true; rv.confirmedBy = PL_NAME; rv.confirmedAt = now;
        rv.history.push({ ts: now, who: PL_NAME, what: '반려 — 요구사항 미반영' });
        toast('반려 처리했습니다');
      } else if (action === 'recheck') {
        rv.status = 'review';
        rv.history.push({ ts: now, who: PL_NAME, what: '재검토 요청으로 전환 (이전 이력 보존)' });
        toast('재검토 요청으로 전환했습니다');
      } else if (action === 'newreq') {
        rv.reviewed = true;
        rv.history.push({ ts: now, who: PL_NAME, what: '신규 요구사항 항목으로 등록 요청 — 요구사항관리 화면에서 "+ 추가"로 등록 필요' });
        toast('신규 등록 요청으로 표시했습니다. 요구사항관리 화면에서 추가하세요.');
      } else if (action === 'hold') {
        rv.history.push({ ts: now, who: PL_NAME, what: '보류' });
        toast('보류로 표시했습니다');
      }
      try { await persistReview(id); } catch (e) { toast('검토 저장 실패: ' + e.message, true); }
      renderMList(); renderMEdit();
    }
  };

  function exportRequirements() {
    var blob = new Blob([JSON.stringify({ kind: 'requirements', items: S.requirements }, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'requirements.json';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast('requirements.json 내보내기 완료 · data/requirements.json에 덮어쓰면 원본이 됩니다');
  }

  function bind() {
    $('btnExport').addEventListener('click', exportRequirements);
    $('mClose').addEventListener('click', closeModal);
    $('mDone').addEventListener('click', closeModal);
    $('uploadInput').addEventListener('change', function (e) {
      var f = e.target.files[0];
      e.target.value = '';
      if (f) handleUpload(f);
    });
  }

  async function boot() {
    try {
      S.requirements = (await fetchJSON('/api/requirements')).items;
      S.meetings = (await fetchJSON('/api/meetings')).items;
      S.decisions = (await fetchJSON('/api/decisions')).items;
      S.review = await fetchJSON('/api/reviews');
    } catch (e) {
      $('meetGrid').innerHTML = '<div class="rv-empty">데이터를 읽지 못했습니다 (' + esc(e.message) + '). 로컬 서버로 실행하세요: python3 server.py</div>';
      return;
    }
    $('dataState').textContent = '관계형 DB(traceops.db) 사용 중';
    bind();
    renderLibrary();
  }

  boot();
})();
