# -*- coding: utf-8 -*-
"""TraceOps(+ReqSync) 화면을 실명 마스킹한 데이터로 촬영한다.

원본 traceops-simple 은 수정하지 않는다.
  1) traceops-simple 을 임시 폴더에 복사
  2) 데이터(JSON)와 화면 파일에서 사람 이름을 자동으로 찾아 가명으로 치환 (이름 목록은 저장·출력하지 않음)
  3) 임시 서버(빈 DB)를 띄우고 capture.js(Playwright)로 shots/ 에 저장

사용: python3 성과제출/traceOpsReqSync/capture_traceops.py
"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(REPO, 'traceops-simple')
OUT = os.path.join(HERE, 'shots')

# 이름이 들어 있는 필드 (값이 아니라 필드명으로 찾는다)
WORKER_KEYS = {'worker', 'author', 'who', 'confirmedBy'}
CUST_KEYS = {'owner'}
VENDOR_KEYS = {'vendorOwner'}
NAME_RE = re.compile(r'^[가-힣]{2,4}$')


def split_names(v):
    return [x for x in re.split(r'[·,/ ]+', v.strip()) if NAME_RE.match(x)]


def discover(data_dir):
    groups = {'pl': [], 'worker': [], 'cust': [], 'vendor': [], 'other': []}

    def add(g, n):
        for x in split_names(n):
            for k in groups:
                if x in groups[k]: return
            groups[g].append(x)

    def walk(o, key=None, parent=None):
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, k, o)
        elif isinstance(o, list):
            for v in o: walk(v, key, parent)
        elif isinstance(o, str):
            if key in WORKER_KEYS: add('worker', o)
            elif key in VENDOR_KEYS: add('vendor', o)
            elif key in CUST_KEYS and parent is not None:
                add('cust' if 'team' in parent else 'other', o)

    for fn in sorted(os.listdir(data_dir)):
        if not fn.endswith('.json'): continue
        d = json.load(open(os.path.join(data_dir, fn), encoding='utf8'))
        walk(d)
        if fn == 'master.json':
            pl = (d.get('pl') or {}).get('name')
            if pl: groups['pl'] = [pl]
            for w in d.get('workers', []):
                if isinstance(w, str): add('worker', w)
    return groups


def build_map(groups):
    m = {}
    for n in groups['pl']: m[n] = 'PL'
    def seq(prefix, names, letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        i = 0
        for n in sorted(names):
            if n in m: continue
            m[n] = prefix + letters[i]; i += 1
    seq('작업자', groups['worker'])
    seq('고객담당', groups['cust'])
    seq('담당자', groups['other'])
    for n in groups['vendor']:
        if n not in m: m[n] = '수행담당'
    return m


def mask_tree(root, mapping):
    names = sorted(mapping, key=len, reverse=True)
    if not names: return 0
    pat = re.compile('|'.join(re.escape(n) for n in names))
    changed = 0
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(('.json', '.html', '.js', '.py', '.md')): continue
            p = os.path.join(dp, f)
            try: s = open(p, encoding='utf8').read()
            except Exception: continue
            t = pat.sub(lambda mo: mapping[mo.group(0)], s)
            if t != s:
                open(p, 'w', encoding='utf8').write(t); changed += 1
    # 헤더 아바타(첫 글자)처럼 이름이 한 글자로 쪼개져 있는 곳은 PL 가명의 첫 글자로 바꾼다
    for n in names:
        if mapping[n] == 'PL':
            for dp, _, fs in os.walk(root):
                for f in fs:
                    if f.endswith(('.html', '.js')):
                        p = os.path.join(dp, f); s = open(p, encoding='utf8').read()
                        t = s.replace('>' + n[0] + '</div>', '>P</div>')
                        if t != s: open(p, 'w', encoding='utf8').write(t)
    return changed


def leftover(root, mapping):
    names = list(mapping)
    hits = 0
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(('.json', '.html', '.js')): continue
            s = open(os.path.join(dp, f), encoding='utf8').read()
            hits += sum(s.count(n) for n in names)
    return hits


def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    tmp = tempfile.mkdtemp(prefix='traceops_mask_')
    work = os.path.join(tmp, 'traceops-simple')
    shutil.copytree(SRC, work, ignore=shutil.ignore_patterns('__pycache__', '*.db', '*.db-journal'))
    groups = discover(os.path.join(work, 'data'))
    mapping = build_map(groups)
    changed = mask_tree(work, mapping)
    left = leftover(work, mapping)
    print(f'마스킹: 이름 {len(mapping)}명 → 가명, 파일 {changed}개 수정, 남은 원본 이름 {left}건')
    if left: sys.exit('마스킹이 덜 됐습니다. 촬영을 중단합니다.')
    port = free_port()
    env = dict(os.environ, PORT=str(port), TRACEOPS_DB=os.path.join(tmp, 'masked.db'))
    srv = subprocess.Popen([sys.executable, 'server.py'], cwd=work, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        os.makedirs(OUT, exist_ok=True)
        env2 = dict(os.environ, MASK_NAMES=json.dumps(list(mapping), ensure_ascii=False))   # 화면 검사용(메모리 전달만)
        r = subprocess.run(['node', os.path.join(HERE, 'capture.js'), f'http://127.0.0.1:{port}', OUT], env=env2)
        if r.returncode: sys.exit('촬영 실패')
    finally:
        srv.terminate()
    print('임시 폴더(마스킹 복사본):', tmp, '- 필요 없으면 직접 삭제해도 됩니다')


if __name__ == '__main__':
    main()
