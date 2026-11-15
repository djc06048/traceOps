"""reqdb 자체 점검. 실행: python3 test_reqdb.py  (임시 DB 사용, traceops.db는 건드리지 않음)"""
import copy, json, os, tempfile

os.environ['TRACEOPS_DB'] = os.path.join(tempfile.mkdtemp(), 'test.db')
import reqdb

reqdb.init()
c = reqdb.connect()


def view(sql):
    out = {}
    for a, b in c.execute(sql):
        out.setdefault(a, set()).add(b)
    return out


def must_fail(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('제약이 막지 못함: ' + label)


# 1) 시드 건수
d = reqdb.trace_all(c)
assert {k: len(v) for k, v in d.items()} == {'analysis': 13, 'design': 13, 'dev': 12, 'unit': 21, 'integration': 4}
assert len(reqdb.phys_items(c)) == 13

# 2) 파생값(Python) == 뷰(SQL) — 설계·개발·단위·통합의 요구사항ID/물리ID/개발ID
for kind, pairs in {
    'design': [('reqIds', 'design_requirements', 'design_id', 'req_id')],
    'dev': [('reqIds', 'dev_requirements', 'dev_id', 'req_id'), ('physIds', 'dev_physical', 'dev_id', 'phys_id')],
    'unit': [('reqIds', 'unit_requirements', 'unit_id', 'req_id'), ('physIds', 'unit_physical', 'unit_id', 'phys_id')],
    'integration': [('linked', 'integration_dev', 'integration_id', 'dev_id'),
                    ('reqIds', 'integration_requirements', 'integration_id', 'req_id'),
                    ('physIds', 'integration_physical', 'integration_id', 'phys_id')],
}.items():
    for field, v, a, b in pairs:
        sql_rows = view('SELECT %s, %s FROM %s' % (a, b, v))
        for x in d[kind]:
            assert set(x[field]) == sql_rows.get(x['id'], set()), (kind, x['id'], field)

# 3) 통합테스트 = 묶인 단위테스트의 합집합 (시드 JSON과도 일치)
seed = {k: {x['id']: x for x in reqdb._seed_file(k)} for k in ('unit', 'integration')}
for t in d['integration']:
    s = seed['integration'][t['id']]
    assert set(t['units']) == set(s['units']) and set(t['linked']) == set(s['linked'])
    assert set(t['reqIds']) == set(s['reqIds']) and set(t['physIds']) == set(s['physIds'])

# 4) 분석의 요구사항을 바꾸면 설계 → 개발 → 단위 → 통합까지 반영
r = reqdb.save_trace({k: v for k, v in d.items()} | {'analysis': [dict(x, reqIds=['RQ_QPM_0030']) if x['id'] == 'UI_QPM_0001' else x for x in d['analysis']]})
unit = next(x for x in r['unit'] if x['linked'] == ['UI_QPM_0001-01'])
assert unit['reqIds'] == ['RQ_QPM_0030']
assert 'RQ_QPM_0030' in next(t for t in r['integration'] if t['id'] == 'IT-0001')['reqIds']

# 5) 제약: 존재하지 않는 연결 / 참조 중 삭제
bad = copy.deepcopy(r)
bad['unit'][0]['linked'] = ['NOPE']
must_fail(lambda: reqdb.save_trace(bad), '없는 개발ID')
bad = copy.deepcopy(r)
bad['unit'] = [x for x in bad['unit'] if x['id'] != 'UI_QPM_0001-01-01']          # 통합이 묶고 있는 단위테스트 삭제
must_fail(lambda: reqdb.save_trace(bad), '통합이 참조 중인 단위테스트 삭제')
bad = copy.deepcopy(r)
bad['dev'] = [x for x in bad['dev'] if x['id'] != 'UI_QPM_0001-01']               # 단위테스트가 참조 중인 개발 삭제
must_fail(lambda: reqdb.save_trace(bad), '단위가 참조 중인 개발 삭제')
must_fail(lambda: reqdb.save_phys([x for x in reqdb.phys_items(c) if x['id'] != 'LTRA010.html']), '사용 중 물리ID 삭제')

# 6) 하위부터 함께 지우면 통과
ok = copy.deepcopy(r)
ok['integration'] = [x for x in ok['integration'] if 'UI_QPM_0003-01-01' not in x['units']]
ok['unit'] = [x for x in ok['unit'] if x['linked'] != ['UI_QPM_0003-01']]
assert len(reqdb.save_trace(ok)['unit']) < len(r['unit'])

# 7) 연계관리(연계 캔버스) — 목록 집계
lkp = {p['id']: p for p in reqdb.lk_processes(c)}
assert lkp['LP-0004']['leafTotal'] == 3 and lkp['LP-0004']['leafMapped'] == 3
assert lkp['LP-0005']['missingToBe'] is True

# 트랜잭션에서 AS-IS 프로세스 생성 → 리프가 캔버스 노드로, 1:1 매핑
new_asis = reqdb.create_process({'model': 'asis', 'fromTransactionId': 'TX_QPM_RELPC1'})
assert new_asis['process']['txCode'] == 'TX_QPM_RELPC1'
assert len(new_asis['nodes']) == 1 and new_asis['nodes'][0]['mapped'][0]['callNodeId'] == 'CN-0008'

# AS-IS 복사 → TO-BE (캔버스 + 거래코드 상속, 매핑은 새로 비워짐)
copy_tobe = reqdb.create_process({'model': 'tobe', 'copyFromProcessId': new_asis['process']['id']})
assert copy_tobe['process']['txCode'] == 'TX_QPM_RELPC1'
assert copy_tobe['process']['originProcessId'] == new_asis['process']['id']
assert len(copy_tobe['nodes']) == 1 and copy_tobe['nodes'][0]['mapped'] == []

# 캔버스 저장: 노드 추가·연결선
copy_pid = copy_tobe['process']['id']
d2 = reqdb.save_canvas(copy_pid,
    copy_tobe['nodes'] + [{'id': 'ND-T1', 'kind': 'step', 'name': '새 노드', 'x': 10, 'y': 10, 'status': 'ok'}],
    [{'from': copy_tobe['nodes'][0]['id'], 'to': 'ND-T1'}])
assert len(d2['nodes']) == 2 and len(d2['edges']) == 1
must_fail(lambda: reqdb.save_canvas(copy_pid, d2['nodes'], [{'from': 'NOPE', 'to': 'ND-T1'}]), '존재하지 않는 노드로 연결선 생성')

# 매핑 / 해제 — lk_transactions가 매핑 위치(mappedTo)까지 돌려주는지
reqdb.save_mapping('CN-0007', 'ND-T1')
tx = {t['id']: t for t in reqdb.lk_transactions(c)}['TX_QPM_RELPC1']
leaf = {n['id']: n for n in tx['nodes']}['CN-0007']
assert leaf['mapped'] and leaf['mappedTo'] == {'nodeId': 'ND-T1', 'nodeName': '새 노드', 'processId': copy_pid, 'processName': copy_tobe['process']['name']}
reqdb.delete_mapping('CN-0007')
tx = {t['id']: t for t in reqdb.lk_transactions(c)}['TX_QPM_RELPC1']
assert not {n['id']: n for n in tx['nodes']}['CN-0007']['mapped']

# 프로세스 메타데이터 수정
upd = reqdb.update_process(copy_pid, {'name': '이름변경', 'owner': '홍길동', 'status': '완료'})
assert upd['process']['name'] == '이름변경' and upd['process']['owner'] == '홍길동' and upd['process']['status'] == '완료'
must_fail(lambda: reqdb.update_process(copy_pid, {'status': '없는상태'}), '잘못된 상태값')
must_fail(lambda: reqdb.update_process(copy_pid, {'parentId': copy_pid}), '자기 자신을 상위 그룹으로 설정')
must_fail(lambda: reqdb.update_process('NOPE', {'name': 'x'}), '존재하지 않는 프로세스 수정')

# 상위 그룹 삭제 시 하위 프로세스도 함께 삭제(CASCADE)
grp = reqdb.create_process({'model': 'tobe', 'name': '그룹'})
child = reqdb.create_process({'model': 'tobe', 'name': '자식', 'parentId': grp['process']['id']})
reqdb.delete_process(grp['process']['id'])
assert child['process']['id'] not in {p['id'] for p in reqdb.lk_processes(c)}

# 유래(originProcessId) 프로세스가 참조 중이면 삭제 불가
must_fail(lambda: reqdb.delete_process(new_asis['process']['id']), 'originProcessId가 참조 중인 AS-IS 삭제')

reqdb.delete_process(copy_pid)
reqdb.delete_process(new_asis['process']['id'])

# 8) 노드가 개발 항목을 참조하는 캔버스(node_source) — 'design'은 더 이상 선택지로 제공하지 않음(free/dev 둘뿐)
asis_forced = reqdb.create_process({'model': 'asis', 'fromTransactionId': 'TX_QPM_RELPC1', 'nodeSource': 'dev'})
assert asis_forced['process']['nodeSource'] == 'free'   # AS-IS는 nodeSource를 보내도 무시
reqdb.delete_process(asis_forced['process']['id'])

dev_canvas = reqdb.create_process({'model': 'tobe', 'name': '개발 기반 캔버스', 'nodeSource': 'dev'})
dev_pid = dev_canvas['process']['id']
assert dev_canvas['process']['nodeSource'] == 'dev' and dev_canvas['nodes'] == []

must_fail(lambda: reqdb.save_canvas(dev_pid, [{'id': 'ND-D1', 'name': 'x', 'x': 0, 'y': 0}], []), 'refId 미입력')
must_fail(lambda: reqdb.save_canvas(dev_pid, [{'id': 'ND-D1', 'name': 'x', 'refId': 'NOPE', 'x': 0, 'y': 0}], []), '존재하지 않는 개발ID 참조')

r3 = reqdb.save_canvas(dev_pid, [
    {'id': 'ND-D1', 'name': '(무시됨)', 'refId': 'UI_QPM_0001-01', 'x': 0, 'y': 0},
    {'id': 'ND-D2', 'name': '', 'refId': 'UI_QPM_0002-01', 'x': 200, 'y': 0},
], [{'from': 'ND-D1', 'to': 'ND-D2'}])
real_name = [x['name'] for x in reqdb.trace_all(c)['dev'] if x['id'] == 'UI_QPM_0001-01'][0]
by_id = {n['id']: n for n in r3['nodes']}
assert by_id['ND-D1']['name'] == real_name and by_id['ND-D1']['refId'] == 'UI_QPM_0001-01' and by_id['ND-D1']['refMissing'] is False
assert len(r3['edges']) == 1

must_fail(lambda: reqdb.save_canvas(dev_pid, r3['nodes'] + [{'id': 'ND-D3', 'name': 'x', 'refId': 'UI_QPM_0001-01', 'x': 0, 'y': 0}], []),
          '같은 캔버스에 같은 개발ID 중복')

# 다른 캔버스에는 같은 개발ID를 중복해서 넣을 수 있다
dev_canvas2 = reqdb.create_process({'model': 'tobe', 'name': '개발 기반 캔버스2', 'nodeSource': 'dev'})
reqdb.save_canvas(dev_canvas2['process']['id'], [{'id': 'ND-E1', 'name': 'x', 'refId': 'UI_QPM_0001-01', 'x': 0, 'y': 0}], [])

# 참조된 개발 항목이 상세공정관리에서 삭제되면 refMissing=True로 표시(차단하지 않음)
# 테스트용 orphan 개발 항목(아무것도 참조하지 않음)을 만들어서 지워본다
all_trace = reqdb.trace_all(c)
reqdb.save_trace(dict(all_trace, dev=all_trace['dev'] + [{'id': 'TMP_DEV_01', 'system': '가입설계/청약', 'subsystem': '가입설계/청약', 'type': '프로그램개발', 'name': '임시', 'designRef': []}]))
reqdb.save_canvas(dev_pid, r3['nodes'] + [{'id': 'ND-D4', 'name': 'x', 'refId': 'TMP_DEV_01', 'x': 400, 'y': 0}], [])
all_trace = reqdb.trace_all(c)
reqdb.save_trace(dict(all_trace, dev=[x for x in all_trace['dev'] if x['id'] != 'TMP_DEV_01']))
detail = reqdb.lk_process_detail(c, dev_pid)
assert {n['id']: n for n in detail['nodes']}['ND-D4']['refMissing'] is True

reqdb.delete_process(dev_pid)
reqdb.delete_process(dev_canvas2['process']['id'])

# 9) 노드 설명(note)·성격(category), 연결선 동기/비동기(async)
note_canvas = reqdb.create_process({'model': 'tobe', 'name': '메모·카테고리 테스트'})
note_pid = note_canvas['process']['id']
r5 = reqdb.save_canvas(note_pid, [
    {'id': 'ND-N1', 'name': 'A', 'note': '짧은 설명', 'category': 'if_external', 'x': 0, 'y': 0},
    {'id': 'ND-N2', 'name': 'B', 'x': 200, 'y': 0},   # note/category 생략 → 기본값
], [{'from': 'ND-N1', 'to': 'ND-N2', 'async': True}])
by_id5 = {n['id']: n for n in r5['nodes']}
assert by_id5['ND-N1']['note'] == '짧은 설명' and by_id5['ND-N1']['category'] == 'if_external'
assert by_id5['ND-N2']['note'] == '' and by_id5['ND-N2']['category'] == 'service'
assert r5['edges'][0]['async'] is True

# 잘못된 category는 거부하지 않고 기본값(service)으로 저장 (화면에서 보낼 수 있는 값만 허용된 select라 완화)
r6 = reqdb.save_canvas(note_pid, [{'id': 'ND-N1', 'name': 'A', 'category': '없는값', 'x': 0, 'y': 0},
                                    {'id': 'ND-N2', 'name': 'B', 'x': 200, 'y': 0}], [])
assert {n['id']: n for n in r6['nodes']}['ND-N1']['category'] == 'service'

# 비동기 해제도 반영
r7 = reqdb.save_canvas(note_pid, r6['nodes'], [{'from': 'ND-N1', 'to': 'ND-N2', 'async': False}])
assert r7['edges'][0]['async'] is False

reqdb.delete_process(note_pid)

# 10) 프로세스 카테고리(domain)
dom = reqdb.create_process({'model': 'tobe', 'name': '카테고리 테스트', 'domain': '인수지침'})
dom_pid = dom['process']['id']
assert dom['process']['domain'] == '인수지침'
bad_dom = reqdb.create_process({'model': 'tobe', 'name': '잘못된 카테고리', 'domain': '없는카테고리'})
assert bad_dom['process']['domain'] == ''   # 생성 시 잘못된 값은 조용히 무시(빈값)
reqdb.delete_process(bad_dom['process']['id'])
upd_dom = reqdb.update_process(dom_pid, {'domain': '가입설계'})
assert upd_dom['process']['domain'] == '가입설계'
must_fail(lambda: reqdb.update_process(dom_pid, {'domain': '없는카테고리'}), '수정 시 잘못된 카테고리 거부')
reqdb.delete_process(dom_pid)

# 11) 개발 완료 여부(devDone) — dev_items의 실적종료일(wActEnd) 기준
# (기존 시드 개발항목은 이미 wActEnd가 채워져 있을 수 있어, 테스트 전용 항목을 새로 만든다)
all_trace = reqdb.trace_all(c)
reqdb.save_trace(dict(all_trace, dev=all_trace['dev'] + [
    {'id': 'TMP_DEV_G1', 'system': '가입설계/청약', 'subsystem': '가입설계/청약', 'type': '프로그램개발', 'name': '임시1', 'designRef': []},
    {'id': 'TMP_DEV_G2', 'system': '가입설계/청약', 'subsystem': '가입설계/청약', 'type': '프로그램개발', 'name': '임시2', 'designRef': []},
]))
done_canvas = reqdb.create_process({'model': 'tobe', 'name': '완료여부 테스트', 'nodeSource': 'dev'})
done_pid = done_canvas['process']['id']
reqdb.save_canvas(done_pid, [
    {'id': 'ND-G1', 'name': 'x', 'refId': 'TMP_DEV_G1', 'x': 0, 'y': 0},
    {'id': 'ND-G2', 'name': 'x', 'refId': 'TMP_DEV_G2', 'x': 200, 'y': 0},
], [])
detail = reqdb.lk_process_detail(c, done_pid)
assert all(n['devDone'] is False for n in detail['nodes'])   # 실적종료일 미입력 상태
procs = {p['id']: p for p in reqdb.lk_processes(c)}
assert procs[done_pid]['devTotal'] == 2 and procs[done_pid]['devDone'] == 0

all_trace = reqdb.trace_all(c)
reqdb.save_trace(dict(all_trace, dev=[dict(x, wActEnd='2026-01-01') if x['id'] == 'TMP_DEV_G1' else x for x in all_trace['dev']]))
detail = reqdb.lk_process_detail(c, done_pid)
assert {n['id']: n for n in detail['nodes']}['ND-G1']['devDone'] is True
assert {n['id']: n for n in detail['nodes']}['ND-G2']['devDone'] is False
procs = {p['id']: p for p in reqdb.lk_processes(c)}
assert procs[done_pid]['devTotal'] == 2 and procs[done_pid]['devDone'] == 1

# 정리
reqdb.delete_process(done_pid)
all_trace = reqdb.trace_all(c)
reqdb.save_trace(dict(all_trace, dev=[x for x in all_trace['dev'] if x['id'] not in ('TMP_DEV_G1', 'TMP_DEV_G2')]))

print('OK')
