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

print('OK')
