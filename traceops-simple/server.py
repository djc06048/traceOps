"""정적 파일 + API(SQLite). 실행: python3 server.py  → http://localhost:8000 (PORT 환경변수로 변경)
관계형: /api/requirements, /api/meetings, /api/decisions, /api/reviews[/<id>],
       /api/analysis, /api/design, /api/dev, /api/unit, /api/integration (GET) + /api/trace (PUT, 한 번에 저장),
       /api/asis (물리ID: GET/PUT)
그 외(마스터 등)는 JSON 문서 저장: /api/store[/<key>]
"""
import json, os, sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

import reqdb

PORT = int(os.environ.get('PORT', 8000))
os.chdir(reqdb.ROOT)


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
            self._send(404)
        finally:
            c.close()

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
