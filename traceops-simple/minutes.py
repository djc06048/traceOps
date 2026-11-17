"""회의록(클로바노트 .txt) → 결정사항 추출 → 요구사항 매핑 파이프라인.

1단계 추출: 회의록을 약 12분 단위 조각으로 잘라 조각마다 결정사항을 뽑는다.
2단계 검증: 결정사항마다 앞뒤 발언과 대조해 AI가 다시 판단한다(합의가 아니면 제외, 상태가 틀리면 보정).
3단계 매칭: 검증을 통과한 결정사항을 요구사항 목록과 매핑한다(하나 끝날 때마다 on_decision 콜백 → 화면에 바로 표시).
LLM 호출 함수(chat)는 주입 가능 — 기본은 llm.chat_json, 테스트는 가짜 함수.
"""
import os, re

CHUNK_SECONDS = 12 * 60
CHUNK_CHARS = 6000
STATUSES = {'확정': 'ok', '검토 중': 'review', '미정': 'open'}
CONFIDENCES = ('high', 'mid', 'new')

_TS = r'\d{1,2}:\d{2}(?::\d{2})?'
_SPEAKER = re.compile(r'^(\S.{0,40}?)\s+(' + _TS + r')\s*$')
_LABEL = re.compile(r'(\d{4}\.\d{2}\.\d{2}\s+\S\s+(?:오전|오후)\s+\d{1,2}:\d{2})')
_DURATION = re.compile(r'((?:\d+시간\s*)?\d+분(?:\s*\d+초)?)')


def ts_seconds(ts):
    s = 0
    for p in (ts or '').split(':'):
        s = s * 60 + int(p)
    return s


def parse_clova(text):
    """→ {'label', 'duration', 'utterances': [{speaker, ts, text}]}. 화자·시각 줄이 없으면 utterances는 문단 단위(ts='')."""
    text = text.replace('\r\n', '\n').lstrip('﻿')
    lines = text.split('\n')
    head = '\n'.join(lines[:5])
    label = _LABEL.search(head)
    dur = _DURATION.search(head[label.end():] if label else head)
    utts, cur = [], None
    for line in lines:
        m = _SPEAKER.match(line.strip())
        if m:
            cur = {'speaker': m.group(1), 'ts': m.group(2), 'text': ''}
            utts.append(cur)
        elif cur is not None and line.strip():
            cur['text'] = (cur['text'] + ' ' + line.strip()).strip()
    utts = [u for u in utts if u['text']]
    if not utts:  # 형식이 다르면 빈 줄 기준 문단
        utts = [{'speaker': '', 'ts': '', 'text': p.strip()} for p in re.split(r'\n\s*\n', text) if p.strip()]
    return {'label': label.group(1) if label else '', 'duration': dur.group(1) if dur else '', 'utterances': utts}


def _line(u):
    return ('[%s] ' % u['ts'] if u['ts'] else '') + (u['speaker'] + ': ' if u['speaker'] else '') + u['text']


def chunks(utts):
    """발언 시각 기준 약 12분, 최대 6,000자 단위로 묶는다."""
    out, cur, start, size = [], [], None, 0
    for u in utts:
        sec = ts_seconds(u['ts']) if u['ts'] else None
        n = len(_line(u))
        if cur and (size + n > CHUNK_CHARS or (sec is not None and start is not None and sec - start >= CHUNK_SECONDS)):
            out.append(cur)
            cur, start, size = [], None, 0
        if start is None:
            start = sec
        cur.append(u)
        size += n
    if cur:
        out.append(cur)
    return out


# ---------- 1단계: 결정사항 추출 ----------
EXTRACT_SYSTEM = """너는 보험사 차세대 시스템 구축 프로젝트의 회의록 분석가다.
회의록 조각에서 요구사항에 영향을 주는 '결정사항'만 뽑는다. 잡담, 일정 조율, 단순 질의응답은 제외한다.
각 항목:
- excerptTs: 근거 발언의 시각(회의록의 [mm:ss] 값 그대로)
- excerpt: 근거 발언 원문을 그대로 복사(1~3문장, 고쳐 쓰지 말 것)
- decision: 무엇을 어떻게 하기로 했는지 한 문장으로, 시스템 요구사항 문체로 작성
- rawStatus: 확정(합의됨) | 검토 중(추가 확인 필요) | 미정(이슈로 남음)
- verificationNote: 그 상태로 판단한 근거(발언 표현, 반대 의견 유무)
결정사항이 없으면 items를 빈 배열로 돌려준다. 회의록에 없는 내용을 지어내지 않는다."""

EXTRACT_SCHEMA = {
    'type': 'object',
    'properties': {'items': {'type': 'array', 'items': {
        'type': 'object',
        'properties': {
            'excerptTs': {'type': 'string'}, 'excerpt': {'type': 'string'}, 'decision': {'type': 'string'},
            'rawStatus': {'type': 'string', 'enum': list(STATUSES)}, 'verificationNote': {'type': 'string'}},
        'required': ['excerptTs', 'excerpt', 'decision', 'rawStatus', 'verificationNote']}}},
    'required': ['items'],
}


def _check_extract(out):
    if not isinstance(out.get('items'), list):
        raise ValueError('items가 배열이 아님')
    for it in out['items']:
        if not isinstance(it, dict) or not str(it.get('decision') or '').strip():
            raise ValueError('decision 누락')
        if it.get('rawStatus') not in STATUSES:
            raise ValueError('rawStatus 값 오류: %r' % it.get('rawStatus'))


def _norm(s):
    return re.sub(r'\s+', '', s or '')


def extract(chunk, chat):
    body = '\n'.join(_line(u) for u in chunk)
    out = chat(EXTRACT_SYSTEM, '회의록 조각:\n' + body, EXTRACT_SCHEMA, _check_extract)
    tss = [u['ts'] for u in chunk if u['ts']]
    res = []
    for it in out['items']:
        ts = str(it.get('excerptTs') or '').strip().strip('[]')
        if not re.fullmatch(_TS, ts) or (tss and ts not in tss):
            ts = tss[0] if tss else ''
        note = str(it.get('verificationNote') or '').strip()
        excerpt = re.sub(r'^(?:\[[\d:]+\]\s*)?(?:참석자\s*\d+|[^:\s]{1,10})\s*:\s*', '', str(it.get('excerpt') or '').strip())
        if excerpt and _norm(excerpt) not in _norm(body):
            note += ' (발췌문이 회의록 원문과 정확히 일치하지 않음 — 원문 확인 필요)'
        res.append({'excerptTs': ts, 'excerpt': excerpt, 'decision': it['decision'].strip(),
                    'rawStatus': it['rawStatus'], 'finalStatus': STATUSES[it['rawStatus']],
                    'verificationNote': note.strip()})
    return res


# ---------- 2단계: AI 2차 검증 ----------
VERIFY = os.environ.get('MINUTES_VERIFY', '1') != '0'
# 작은 모델은 상태를 통째로 다시 고르는 일에 약해(실측: 오판을 고치지 못하고 문장까지 망가뜨림),
# 예/아니오 질문 세 개로 묻고 상태는 코드가 정한다. 확정 오판이 가장 위험하므로 '확정'을 낮추는 방향으로만 보정한다.
VERIFY_SYSTEM = """너는 회의록 분석 결과를 검증하는 2차 검토자다.
1차로 추출된 결정사항을 근거 발언과 그 앞뒤 대화에 비추어 아래 질문에 true/false로 답한다.
- isDecision: 회의에서 실제로 결정·합의·검토 요청된 업무 사항인가? 잡담, 단순 의견, 질문이면 false
- pendingCheck: 근거 발언이나 그 뒤 대화에 "확인 받아 보고", "승인 받아서", "다음 주에 다시", "검토 후"처럼 아직 남은 확인·승인·재협의가 있는가?
- scopeOpen: 무엇을 할지는 말했더라도 범위·방법·일정이 아직 정해지지 않았는가?
- note: 판단 근거가 된 발언을 짧게 인용한 한 문장
대화에 없는 내용을 덧붙이지 않는다."""

VERIFY_SCHEMA = {
    'type': 'object',
    'properties': {
        'isDecision': {'type': 'boolean'}, 'pendingCheck': {'type': 'boolean'},
        'scopeOpen': {'type': 'boolean'}, 'note': {'type': 'string'}},
    'required': ['isDecision', 'pendingCheck', 'scopeOpen', 'note'],
}


def _check_verify(out):
    for k in ('isDecision', 'pendingCheck', 'scopeOpen'):
        if not isinstance(out.get(k), bool):
            raise ValueError('%s가 true/false가 아님' % k)


def context(d, chunk, before=1, after=3, limit=1500):
    """근거 발언(발언 시각 기준)과 앞 1개, 뒤 3개 발언. 시각을 못 찾으면 조각 앞부분."""
    idx = next((i for i, u in enumerate(chunk) if u['ts'] and u['ts'] == d['excerptTs']), None)
    if idx is None:
        idx = next((i for i, u in enumerate(chunk) if d['excerpt'] and _norm(d['excerpt'])[:20] in _norm(u['text'])), 0)
    lines = [_line(u) for u in chunk[max(0, idx - before): idx + after + 1]]
    return '\n'.join(lines)[:limit]


def verify(d, chunk, chat):
    """→ 검증을 통과한 결정사항(상태 보정, 검증 메모 추가) 또는 None(결정사항 아님 → 제외). 결정사항 문장은 고치지 않는다."""
    out = chat(VERIFY_SYSTEM, '1차 결정사항: %s\n근거 발언: %s\n\n앞뒤 대화:\n%s'
               % (d['decision'], d['excerpt'], context(d, chunk)), VERIFY_SCHEMA, _check_verify)
    if not out['isDecision']:
        return None
    v = dict(d)
    note = '1차: %s / 2차 검증: %s' % (d['verificationNote'], str(out.get('note') or '').strip())
    new = d['rawStatus']
    if d['rawStatus'] == '확정' and (out['pendingCheck'] or out['scopeOpen']):
        new = '미정' if out['scopeOpen'] else '검토 중'  # 범위가 안 정해졌으면 미정, 확인만 남았으면 검토 중
    if new != d['rawStatus']:
        note += ' (상태 보정: %s → %s)' % (d['rawStatus'], new)
        v['rawStatus'], v['finalStatus'] = new, STATUSES[new]
    v['verificationNote'] = note
    return v


# ---------- 3단계: 요구사항 매핑 ----------
MAP_SYSTEM = """너는 회의 결정사항을 요구사항 등록부에 매핑하는 분석가다.
아래 요구사항 목록에서 결정사항이 보완·변경하는 요구사항 하나를 고른다.
결정사항이 보류·재협의·검토 요청이어도, 다루는 기능이 목록에 있으면 그 ID를 고른다(이때 addition은 빈 문자열). new는 목록 어디에도 해당 기능이 없을 때만 쓴다.
- reqId: 목록에 있는 ID 그대로. 맞는 항목이 없으면 빈 문자열
- confidence: high(명확히 해당) | mid(관련 있으나 불확실) | new(맞는 항목 없음 → 신규 요구사항 후보)
- addition: 기존 요구사항내역 뒤에 이어 붙일 보완 문장(공백으로 시작, 요구사항 문체). 바꿀 필요 없으면 빈 문자열
- replaceWith: 결정사항이 기존 내용과 상충해 전체를 고쳐 써야 할 때만 새 요구사항내역 전체. 아니면 빈 문자열
- newReqHint: confidence가 new일 때 신규 요구사항의 짧은 이름. 아니면 빈 문자열

요구사항 목록(ID | 분류 | 이름 | 요구사항내역):
"""

MAP_SCHEMA = {
    'type': 'object',
    'properties': {
        'reqId': {'type': 'string'}, 'confidence': {'type': 'string', 'enum': list(CONFIDENCES)},
        'addition': {'type': 'string'}, 'replaceWith': {'type': 'string'}, 'newReqHint': {'type': 'string'}},
    'required': ['reqId', 'confidence', 'addition', 'replaceWith', 'newReqHint'],
}


def _check_map(out):
    if out.get('confidence') not in CONFIDENCES:
        raise ValueError('confidence 값 오류: %r' % out.get('confidence'))


SHORTLIST = 15  # 매핑 후보 수. 전체 목록(77건 ≈ 7천 토큰)을 넣으면 CPU에서 매핑 1건에 수 분이 걸린다


def _req_text(r):
    return ' '.join(str(r.get(k) or '') for k in ('major', 'middle', 'minor', 'name', 'content'))


def _bigrams(s):
    s = re.sub(r'\s+', '', s or '')
    return {s[i:i + 2] for i in range(len(s) - 1)}


def _scored(d, reqs):
    q = _bigrams(d['decision'] + ' ' + d.get('excerpt', ''))
    return sorted(((len(q & _bigrams(_req_text(r))), r) for r in reqs), key=lambda x: -x[0])


def shortlist(d, reqs, k=SHORTLIST):
    """결정사항과 글자 2-gram이 많이 겹치는 요구사항 상위 k건(LLM에 넘길 후보)."""
    return [r for _, r in _scored(d, reqs)[:k]]


# 모델이 '신규'라고 해도 유사도 1위가 뚜렷하면 그 후보를 mid로 제안한다(작은 모델의 매칭 누락 보완, PL이 최종 확인).
FALLBACK_MIN, FALLBACK_LEAD = 12, 1.3


def fallback_candidate(d, reqs):
    sc = _scored(d, reqs)
    if sc and sc[0][0] >= FALLBACK_MIN and (len(sc) < 2 or sc[0][0] >= FALLBACK_LEAD * max(sc[1][0], 1)):
        return sc[0][1]
    return None


def req_catalog(reqs):
    return '\n'.join('%s | %s | %s | %s' % (r['id'], '/'.join(x for x in (r.get('major'), r.get('middle'), r.get('minor')) if x),
                                            r.get('name', ''), (r.get('content') or '').replace('\n', ' ')[:200])
                     for r in reqs)


def map_decision(d, reqs, chat):
    cands = shortlist(d, reqs)
    out = chat(MAP_SYSTEM + req_catalog(cands), '결정사항: %s\n근거 발언: %s' % (d['decision'], d['excerpt']), MAP_SCHEMA, _check_map)
    ids = {r['id'] for r in reqs}
    rid = str(out.get('reqId') or '').strip()
    conf = out['confidence']
    fixed = False
    if rid not in ids or conf == 'new':
        rid, conf = None, 'new'
        fb = fallback_candidate(d, reqs)
        if fb:
            rid, conf, fixed = fb['id'], 'mid', True
    m = dict(d, reqId=rid, confidence=conf,
             addition=(out.get('addition') or None) if rid else None,
             replaceWith=((out.get('replaceWith') or '').strip() or None) if rid else None)
    if m['addition'] and not m['addition'].startswith(' '):
        m['addition'] = ' ' + m['addition']
    if fixed:
        m['verificationNote'] = (d.get('verificationNote', '') + ' (매칭 보정: 모델은 신규로 판단했으나 유사도 1순위 후보 제안)').strip()
    if not rid:
        hint = (out.get('newReqHint') or '').strip()
        m['newReqHint'] = hint if hint and not re.match(r'^[A-Z]{2,}_', hint) else d['decision'][:30]  # ID 모양이면 버림
    return m


def run(text, reqs, chat, on_progress=lambda p: None, on_decision=lambda d: None, verify_on=None):
    """전체 파이프라인. 결정사항이 하나 매핑될 때마다 on_decision(d) 호출. 매핑된 결정사항 목록을 돌려준다.
    verify_on=None이면 환경변수 MINUTES_VERIFY(기본 켜짐)를 따른다."""
    verify_on = VERIFY if verify_on is None else verify_on
    parsed = parse_clova(text)
    parts = chunks(parsed['utterances'])
    out = []
    for i, part in enumerate(parts):
        tag = '조각 %d/%d · ' % (i + 1, len(parts))
        on_progress({'step': tag + '결정사항 추출 중', 'done': i, 'total': len(parts)})
        found = extract(part, chat)
        for j, d in enumerate(found):
            n = '(%d/%d)' % (j + 1, len(found))
            if verify_on:
                on_progress({'step': tag + 'AI 2차 검증 중 ' + n, 'done': i, 'total': len(parts)})
                d = verify(d, part, chat)
                if d is None:  # 결정사항이 아니라고 판단 → 매칭하지 않고 제외
                    continue
            on_progress({'step': tag + '요구사항 매칭 중 ' + n, 'done': i, 'total': len(parts)})
            m = map_decision(d, reqs, chat)
            on_decision(m)
            out.append(m)
    on_progress({'step': '완료', 'done': len(parts), 'total': len(parts)})
    return out
