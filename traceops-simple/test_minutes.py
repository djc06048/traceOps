"""minutes.py / LLM 분석 저장 점검 — 가짜 LLM 사용(Ollama 불필요). 실행: python3 test_minutes.py"""
import json, os, tempfile

os.environ['TRACEOPS_DB'] = os.path.join(tempfile.mkdtemp(), 'test.db')
import llm
import minutes
import reqdb

ROOT = os.path.dirname(os.path.abspath(__file__))
TEXT = open(os.path.join(ROOT, 'samples', 'sample_meeting.txt'), encoding='utf-8').read()

# 1) 클로바노트 파싱
p = minutes.parse_clova(TEXT)
assert p['label'] == '2026.11.16 월 오후 2:00', p['label']
assert p['duration'] == '25분 10초', p['duration']
assert len(p['utterances']) == 8 and p['utterances'][1]['ts'] == '00:40'
assert '6단계' in p['utterances'][1]['text']
assert minutes.ts_seconds('1:02:03') == 3723

# 2) 조각: 12분 단위 → 00:05~05:45 / 13:30~20:00
parts = minutes.chunks(p['utterances'])
assert [len(x) for x in parts] == [5, 3], [len(x) for x in parts]
# 형식이 다른 글은 문단 단위로
assert len(minutes.parse_clova('첫 문단\n\n둘째 문단')['utterances']) == 2

# 3) 파이프라인: 가짜 LLM — 추출은 첫 호출에 깨진 JSON을 돌려 재요청을 확인
calls = {'extract': 0}


def fake(system, user, schema, validate):
    if schema is minutes.EXTRACT_SCHEMA:
        calls['extract'] += 1
        if '6단계' in user:
            items = [{'excerptTs': '01:20', 'excerpt': '6단계로 확정하겠습니다.', 'decision': '가입설계 프로세스를 6단계로 구성한다.',
                      'rawStatus': '확정', 'verificationNote': '반대 없음'},
                     {'excerptTs': '99:99', 'excerpt': '지어낸 문장', 'decision': '고객 검색 기간을 6개월로 늘린다.',
                      'rawStatus': '검토 중', 'verificationNote': 'DBA 확인 필요'}]
        else:  # PDF는 1차에서 '확정'으로 잘못 뽑히고, 점심 잡담도 결정사항으로 잘못 뽑힌 상황
            items = [{'excerptTs': '14:05', 'excerpt': '그건 신규로 올리고', 'decision': '설계서 PDF 출력 기능을 신규 요구사항으로 등록한다.',
                      'rawStatus': '확정', 'verificationNote': '신규로 올리기로 함'},
                     {'excerptTs': '20:00', 'excerpt': '점심 메뉴는 뭐로 할까요.', 'decision': '점심 메뉴를 정한다.',
                      'rawStatus': '확정', 'verificationNote': '발언 있음'}]
        out = {'items': items}
    elif schema is minutes.VERIFY_SCHEMA:
        calls['verify'] = calls.get('verify', 0) + 1
        assert '앞뒤 대화' in user
        if '1차 결정사항: 점심' in user:  # 문맥에는 점심 발언이 섞일 수 있으니 결정사항 문장으로 판단
            out = {'isDecision': False, 'pendingCheck': False, 'scopeOpen': False, 'note': '잡담'}
        elif 'PDF' in user:
            assert 'PM 승인' in user  # 뒤 발언까지 문맥으로 전달되는지
            out = {'isDecision': True, 'pendingCheck': True, 'scopeOpen': True, 'note': 'PM 승인 후 범위 결정'}
        elif '1차 결정사항: 가입설계' in user:
            out = {'isDecision': True, 'pendingCheck': False, 'scopeOpen': False, 'note': '반대 없음'}
        else:  # 6개월: 1차가 이미 검토 중이면 확인이 남아 있어도 그대로(올리거나 바꾸지 않음)
            out = {'isDecision': True, 'pendingCheck': True, 'scopeOpen': False, 'note': 'DBA 확인'}
    else:
        if '6단계' in user:
            out = {'reqId': 'RQ_QPM_0002', 'confidence': 'high', 'addition': '고지사항 확인 단계를 추가한다.', 'replaceWith': '', 'newReqHint': ''}
        elif '6개월' in user:
            out = {'reqId': 'RQ_XXX_9999', 'confidence': 'high', 'addition': 'x', 'replaceWith': '', 'newReqHint': ''}  # 없는 ID
        else:
            out = {'reqId': '', 'confidence': 'new', 'addition': '', 'replaceWith': '', 'newReqHint': '설계서 PDF 출력' if 'PDF' in user else 'RQ_QPM_0073'}
    validate(out)
    return out


def flaky(system, user, schema, validate):  # chat_json의 재요청 동작 흉내: 첫 응답은 검증 실패
    if schema is minutes.EXTRACT_SCHEMA and calls['extract'] == 0:
        calls['extract'] += 1
        try:
            validate({'items': [{'decision': '', 'rawStatus': '확정'}]})
        except ValueError:
            pass
        else:
            raise AssertionError('검증이 빈 decision을 막지 못함')
    return fake(system, user, schema, validate)


reqdb.init()
c = reqdb.connect()
reqs = reqdb.req_items(c)
c.close()
seen, prog = [], []
out = minutes.run(TEXT, reqs, flaky, prog.append, seen.append)
assert len(out) == 3 and seen == out
a, b, n = out
assert a['reqId'] == 'RQ_QPM_0002' and a['confidence'] == 'high' and a['finalStatus'] == 'ok'
assert a['addition'] == ' 고지사항 확인 단계를 추가한다.'  # 앞 공백 보정
assert b['reqId'] is None and b['confidence'] == 'new' and b['finalStatus'] == 'review'  # 없는 ID → 신규 후보
assert b['excerptTs'] == '00:05'  # 조각에 없는 시각 → 조각 첫 시각
assert '일치하지 않음' in b['verificationNote']  # 지어낸 발췌 표시
assert n['reqId'] is None and n['newReqHint'] == '설계서 PDF 출력' and n['finalStatus'] == 'open'
assert n['rawStatus'] == '미정' and '상태 보정: 확정 → 미정' in n['verificationNote']  # 2차 검증이 상태를 고침
assert n['verificationNote'].startswith('1차: 신규로 올리기로 함 / 2차 검증: PM 승인 후 범위 결정')
assert a['decision'] == '가입설계 프로세스를 6단계로 구성한다.' and a['finalStatus'] == 'ok'  # 문장은 고치지 않음
assert '상태 보정' not in b['verificationNote'] and b['rawStatus'] == '검토 중'
assert minutes.map_decision({'decision': '점심 메뉴를 정한다', 'excerpt': ''}, reqs, fake)['newReqHint'] == '점심 메뉴를 정한다'  # ID 모양 이름은 버림
# 모델이 신규라고 해도 유사도 1위가 뚜렷하면 mid로 제안 (실측 사례: 6단계 결정사항)
six = {'decision': '가입설계 프로세스 단계를 기존 5단계에서 심사요청 단계 전에 고지사항 확인 단계를 추가하여 6단계로 변경합니다.',
       'excerpt': '프로세스는 기존 5단계에서 심사요청 앞에 고지사항 확인 단계를 하나 더 넣어서 6단계로 가는 걸로 하죠.', 'verificationNote': 'v'}
newer = lambda *a: {'reqId': '', 'confidence': 'new', 'addition': '', 'replaceWith': '', 'newReqHint': 'x'}
m6 = minutes.map_decision(six, reqs, newer)
assert m6['reqId'] == 'RQ_QPM_0002' and m6['confidence'] == 'mid' and '매칭 보정' in m6['verificationNote']
pdf = {'decision': '설계서 PDF 출력 기능을 신규 요구사항으로 추가해야 한다.', 'excerpt': '그건 신규로 올리고', 'verificationNote': 'v'}
assert minutes.map_decision(pdf, reqs, newer)['reqId'] is None  # 유사도가 낮으면 신규 유지
assert calls['verify'] == 4  # 4건 검증, 점심 잡담은 제외되어 3건만 매칭
assert any('AI 2차 검증 중' in x['step'] for x in prog) and prog[-1]['step'] == '완료'
# 검증을 끄면 잡담까지 4건이 그대로 매칭됨
assert len(minutes.run(TEXT, reqs, fake, verify_on=False)) == 4
# 문맥: 근거 발언 시각 기준 앞 1개, 뒤 3개 발언
ctx = minutes.context({'excerptTs': '13:30', 'excerpt': ''}, parts[1])
assert ctx.startswith('[13:30]') and '[14:05]' in ctx and '[20:00]' in ctx

# 4) LLM 응답 파싱: 사고 과정·코드블록 제거
assert llm._parse_json('<think>음</think>```json\n{"a": 1}\n```') == {'a': 1}

# 5) DB 저장 / 재분석 시 검토된 건 유지
reqdb.upsert_meeting('sample_meeting.txt', p['label'], p['duration'])
ids = [reqdb.insert_decision('sample_meeting.txt', d) for d in out]
c = reqdb.connect()
start = int(ids[0][3:])
assert ids == ['AI-%d' % (start + i) for i in range(3)]
got = {d['id']: d for d in reqdb.decisions(c)}
assert got[ids[0]]['reqId'] == 'RQ_QPM_0002' and got[ids[2]]['newReqHint'] == '설계서 PDF 출력'
assert got[ids[0]]['meeting'] == '2026.11.16 월 오후 2:00'
reqdb.save_review(ids[0], {'reviewed': True, 'status': 'ok', 'history': [{'ts': 't', 'who': 'PL', 'what': '반영 확정'}]})
reqdb.clear_ai_decisions('sample_meeting.txt')
left = [d['id'] for d in reqdb.decisions(c) if d['meetingFile'] == 'sample_meeting.txt']
assert left == [ids[0]], left
# 시드 결정사항(D*)은 지우지 않음
assert any(d['id'] == 'D1' for d in reqdb.decisions(c))
reqdb.upsert_meeting('sample_meeting.txt', '', '')  # 빈 값으로 덮어쓰지 않음
assert [m for m in reqdb.meetings(c) if m['file'] == 'sample_meeting.txt'][0]['label'] == '2026.11.16 월 오후 2:00'
c.close()
print('OK: minutes / LLM 분석 저장 점검 통과')
