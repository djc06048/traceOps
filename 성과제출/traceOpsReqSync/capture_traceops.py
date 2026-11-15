# -*- coding: utf-8 -*-
"""TraceOps(+ReqSync) 화면 촬영.

원본 traceops-simple 의 DB와 데이터는 건드리지 않는다.
  1) 빈 임시 DB로 서버를 띄운다 (시드 JSON 으로 채워짐)
  2) capture.js(Playwright)로 shots/ 에 저장한다

사용: python3 성과제출/traceOpsReqSync/capture_traceops.py
"""
import os, socket, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(REPO, 'traceops-simple')
OUT = os.path.join(HERE, 'shots')


def free_port():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    tmp = tempfile.mkdtemp(prefix='traceops_cap_')
    port = free_port()
    env = dict(os.environ, PORT=str(port), TRACEOPS_DB=os.path.join(tmp, 'cap.db'))
    srv = subprocess.Popen([sys.executable, 'server.py'], cwd=SRC, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(3)
        os.makedirs(OUT, exist_ok=True)
        r = subprocess.run(['node', os.path.join(HERE, 'capture.js'), f'http://127.0.0.1:{port}', OUT])
        if r.returncode:
            sys.exit('촬영 실패')
    finally:
        srv.terminate()
    print('임시 DB 폴더:', tmp, '(필요 없으면 직접 삭제해도 됩니다)')


if __name__ == '__main__':
    main()
