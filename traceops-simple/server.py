"""정적 파일 + API(SQLite). 실행: python3 server.py  → http://localhost:8000 (PORT 환경변수로 변경)
관계형: /api/requirements, /api/meetings, /api/decisions, /api/reviews[/<id>],
       /api/analysis, /api/design, /api/dev, /api/unit, /api/integration (GET) + /api/trace (PUT, 한 번에 저장),
       /api/asis (물리ID: GET/PUT)
연계관리(기존 추적 체인과 독립): /api/linkage/processes (GET/POST), /api/linkage/processes/<id> (GET/PUT/DELETE),
       /api/linkage/processes/<id>/canvas (PUT), /api/linkage/transactions (GET, AS-IS 콜트리),
       /api/linkage/map (POST), /api/linkage/map/<callNodeId> (DELETE)
       TO-BE 프로세스는 nodeSource('free'|'design'|'dev')를 가지며, free가 아니면 캔버스 노드가 /api/design, /api/dev 항목(refId)을 참조한다.
그 외(마스터 등)는 JSON 문서 저장: /api/store[/<key>]
로컬 LLM 회의록 분석: POST /api/meetings/analyze {file, text} → {jobId}, GET /api/jobs/<id> (진행 상황), GET /api/llm/status
"""
import json, os, sqlite3, threading, uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

import llm
import minutes
import reqdb

PORT = int(os.environ.get('PORT', 8000))
os.chdir(reqdb.ROOT)

# 회의록 분석 작업 상태(메모리). 로컬 LLM은 동시에 여러 건을 돌리면 느려지므로 한 번에 하나만 실행한다.
JOBS = {}
JOBS_LOCK = threading.Lock()


def _analyze(job, file, text):
    def progress(p):
        job.update(p)

    def decision(d):
        job['decisionIds'].append(reqdb.insert_decision(file, d))
    try:
        c = reqdb.connect()
        try:
            reqs = reqdb.req_items(c)
        finally:
            c.close()
        minutes.run(text, reqs, llm.chat_json, progress, decision)
        job['state'] = 'done'
    except Exception as e:  # 스레드 안에서 끝나므로 모든 오류를 작업 상태로 남긴다
        job['state'] = 'error'
        job['error'] = str(e)


def start_analysis(body):
    file = os.path.basename(str(body.get('file') or '')).strip()
    text = str(body.get('text') or '')
    if not file or not text.strip():
        raise ValueError('회의록 파일명과 내용이 필요합니다')
    with JOBS_LOCK:
        if any(j['state'] == 'running' for j in JOBS.values()):
            raise ValueError('다른 회의록을 분석하는 중입니다. 끝난 뒤 다시 시도하세요.')
        st = llm.status()
        if not st['ok']:
            raise ValueError(st['error'])
        parsed = minutes.parse_clova(text)
        reqdb.upsert_meeting(file, parsed['label'], parsed['duration'])
        reqdb.clear_ai_decisions(file)
        jid = uuid.uuid4().hex[:12]
        job = JOBS[jid] = {'id': jid, 'file': file, 'state': 'running', 'step': '회의록을 읽는 중', 'done': 0,
                           'total': 0, 'decisionIds': [], 'error': None, 'model': st['model']}
    threading.Thread(target=_analyze, args=(job, file, text), daemon=True).start()
    return {'jobId': jid}


class H(SimpleHTTPRequestHandler):
    def _send(self, code, body=b''):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode())

    def _body(self):
        return json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'null')

    def _tail(self, prefix):
        p = self.path.split('?')[0]
        return unquote(p[len(prefix):]) if p.startswith(prefix) else None

    def _api(self, fn):
        try:
            fn()
        except (ValueError, KeyError, TypeError, sqlite3.Error) as e:
            self._json({'error': str(e)}, 400)

    def do_GET(self):
        p = self.path.split('?')[0]
        if not p.startswith('/api/'):
            return super().do_GET()
        c = reqdb.connect()
        try:
            if p == '/api/store':
                return self._json(dict(c.execute('SELECT key, json FROM store').fetchall()))
            if p == '/api/requirements':
                return self._json({'kind': 'requirements', 'items': reqdb.req_items(c)})
            if p in ('/api/analysis', '/api/design', '/api/dev', '/api/unit', '/api/integration'):
                k = p[len('/api/'):]
                return self._json({'kind': k, 'items': reqdb.trace_all(c)[k]})
            if p == '/api/asis':
                return self._json({'kind': 'asis', 'items': reqdb.phys_items(c)})
            if p == '/api/meetings':
                return self._json({'kind': 'meetings', 'items': reqdb.meetings(c)})
            if p == '/api/decisions':
                return self._json({'kind': 'decisions', 'items': reqdb.decisions(c)})
            if p == '/api/reviews':
                return self._json(reqdb.reviews(c))
            if p == '/api/llm/status':
                return self._json(llm.status())
            k = self._tail('/api/jobs/')
            if k:
                return self._json(JOBS[k]) if k in JOBS else self._json({'error': '작업을 찾을 수 없습니다'}, 404)
            if p == '/api/linkage/processes':
                return self._json({'kind': 'processes', 'items': reqdb.lk_processes(c)})
            if p == '/api/linkage/transactions':
                return self._json({'kind': 'transactions', 'items': reqdb.lk_transactions(c)})
            k = self._tail('/api/linkage/processes/')
            if k:
                return self._json(reqdb.lk_process_detail(c, k))
            self._send(404)
        finally:
            c.close()

    def do_POST(self):
        def run():
            p = self.path.split('?')[0]
            b = self._body()
            if p == '/api/linkage/processes':
                return self._json(reqdb.create_process(b))
            if p == '/api/linkage/map':
                reqdb.save_mapping(b['callNodeId'], b['nodeId'])
                return self._send(204)
            if p == '/api/meetings/analyze':
                return self._json(start_analysis(b))
            self._send(404)
        self._api(run)

    def do_PUT(self):
        def run():
            p = self.path.split('?')[0]
            b = self._body()
            if p == '/api/requirements':
                items = reqdb.save_reqs(b['items'], b.get('who'), b.get('ctx'))
                return self._json({'kind': 'requirements', 'items': items})
            if p == '/api/asis':
                return self._json({'kind': 'asis', 'items': reqdb.save_phys(b['items'])})
            if p == '/api/trace':
                return self._json(reqdb.save_trace(b))
            k = self._tail('/api/reviews/')
            if k:
                reqdb.save_review(k, b)
                return self._send(204)
            k = self._tail('/api/linkage/processes/')
            if k and k.endswith('/canvas'):
                return self._json(reqdb.save_canvas(k[:-len('/canvas')], b.get('nodes'), b.get('edges')))
            if k:
                return self._json(reqdb.update_process(k, b))
            k = self._tail('/api/store/')
            if k:
                json.dumps(b)  # 유효한 JSON만 (본문은 이미 파싱됨)
                c = reqdb.connect()
                with c:
                    c.execute('INSERT INTO store VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET json = excluded.json',
                              (k, json.dumps(b, ensure_ascii=False)))
                c.close()
                return self._send(204)
            self._send(404)
        self._api(run)

    def do_DELETE(self):
        def run():
            k = self._tail('/api/linkage/map/')
            if k:
                reqdb.delete_mapping(k)
                return self._send(204)
            k = self._tail('/api/linkage/processes/')
            if k:
                reqdb.delete_process(k)
                return self._send(204)
            k = self._tail('/api/store/')
            if not k:
                return self._send(404)
            c = reqdb.connect()
            with c:
                c.execute('DELETE FROM store WHERE key = ?', (k,))
            c.close()
            self._send(204)
        self._api(run)


if __name__ == '__main__':
    reqdb.init()
    print('http://localhost:%d  (DB: traceops.db)' % PORT)
    ThreadingHTTPServer(('', PORT), H).serve_forever()
