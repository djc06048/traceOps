# -*- coding: utf-8 -*-
"""로컬 LLM 회의록 분석(ReqSync) 성과 제출 장표 6장.

성과제출/tools/deck_lib.py 와 같은 디자인 규칙(../../성과제출/작성가이드.md)으로 만든다.
- 미리보기:   python local_llm_slides.py            → 로컬LLM_장표_미리보기.html (이 폴더에서 바로 열림)
- 붙여넣기용: 같은 명령으로 함께 생성                 → 로컬LLM_장표_붙여넣기용.html (<section> 6개, 경로는 ../assets/)
- 빌드 연동:  build_traceopsreqsync.py 에서 import 후 slides += local_llm_slides.slides()

내용 근거: traceops-simple 의 llm.py, minutes.py, server.py 구현과 2026-11 CPU 노트북 실측값.
"""
import html, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, '..', '..', '성과제출', 'tools')
sys.path.insert(0, TOOLS)
import deck_lib as D
from deck_lib import L, CW, e, box, frame

MONO = "font-family:Consolas,'D2Coding',monospace;"


def _blocks():
    """장표 1: 로컬 LLM 구성 (패턴 P8 구조도 + 기술 칩)."""
    b = ''
    bw, top, bh = 2.25, 2.1, 1.85
    gap = (CW - 4 * bw) / 3
    blocks = [
        ('blk', '브라우저', '요구사항 개정 검토 화면', ['회의록 업로드', '진행 상황 표시', 'PL 검토와 확정']),
        ('blk', 'TraceOps 서버', 'server.py · Python', ['분석 작업 생성과 관리', 'LLM 호출과 결과 보정', '결과 저장(SQLite)']),
        ('aibox', '로컬 LLM 서버', 'Ollama · localhost:11434', ['모델 적재와 추론 실행', 'OpenAI 호환 API 제공', 'CPU·GPU 자동 선택']),
        ('aibox', 'LLM 모델', 'Qwen3 4B · CPU 실행', ['결정사항 추출', '요구사항 매칭', '보완 문장 제안']),
    ]
    for i, (cls, t, sub, its) in enumerate(blocks):
        x = L + i * (bw + gap)
        tag = '<span class="aitag o sm">AI</span>' if cls == 'aibox' else ''
        b += box(cls, x, top, bw, bh)
        b += box('bt', x + 0.2, top + 0.15, bw - 0.3, 0.35, tag + e(t))
        b += box('bs', x + 0.2, top + 0.52, bw - 0.3, 0.3, e(sub), 'font-size:10.5pt;color:#AF947E;font-weight:700')
        b += box('cd', x + 0.2, top + 0.88, bw - 0.3, 0.95, ''.join(f'<p>{e(s)}</p>' for s in its), 'font-size:11pt;line-height:1.35')
        if i < 3:
            ax = x + bw + 0.06
            b += box('arrl', ax, top + 0.92, gap - 0.2, 0.02)
            b += box('arrh', ax + gap - 0.22, top + 0.86, 0.1, 0.14)
    # 사내 PC 경계 (서버 ~ 모델)
    x2 = L + (bw + gap)
    b += box('', x2, top + bh + 0.12, CW - (bw + gap), 0.32,
             '<b style="color:#6E5744">사내 PC 내부에서만 동작</b>&nbsp;&nbsp;회의록과 요구사항은 외부로 전송되지 않습니다',
             'border-top:2px dashed #AF947E;font-size:11pt;color:#6B6B6B;padding-top:0.06in')
    # 기술 칩
    chips = [('실행 도구', 'Ollama', 'MIT 라이선스, 무료'), ('모델', 'Qwen3', 'Apache 2.0, 상업 사용 무료'),
             ('호출 규격', 'OpenAI 호환 API', 'vLLM 등 다른 서버와 호환'), ('서버 · 저장소', 'Python · SQLite', '표준 라이브러리만 사용')]
    cw = (CW - 3 * 0.2) / 4
    for i, (c, v, s) in enumerate(chips):
        x = L + i * (cw + 0.2)
        b += box('tchip', x, 4.65, cw, 0.95, f'<div class="tcat">{e(c)}</div><div class="tval">{e(v)}</div>'
                 f'<div style="font-size:10.5pt;color:#6B6B6B;margin-top:0.03in">{e(s)}</div>')
    b += box('rbar brown', L, 5.95, CW, 1.2, '<span class="lb">교체 방식</span><span class="tx">서버 주소와 모델 이름을 설정값으로 분리해,'
             ' GPU 서버나 사내 승인 LLM으로 <b>코드 수정 없이 교체</b>합니다</span>', 'font-size:14pt')
    return frame('AI', '로컬 LLM 구성', '시스템 구성',
                 '보안상 외부 LLM API를 쓸 수 없어 <b>사내 PC에서 동작하는 로컬 LLM</b>으로 구성했습니다.<br>'
                 '회의록은 외부로 전송되지 않으며, 무료로 공개된 모델과 실행 도구만 사용합니다.', b, ai=True)


def _flow():
    """장표 2: 기동부터 확정까지 처리 흐름 (패턴 P5, 5단계)."""
    b = ''
    n, gp = 5, 0.2
    sw = (CW - (n - 1) * gp) / n
    steps = [
        ('t', '로컬 LLM 기동', '운영자', ['Ollama 서버 실행', 'Qwen3 모델 적재', '연결 상태를 화면 상단에 표시'], 'ollama serve<br>/api/llm/status'),
        ('b', '회의록 업로드', 'PL', ['클로바노트 텍스트 업로드', '화자와 발언 시각 단위로 읽기', '약 12분 단위 조각으로 분할'], '요구사항 개정 검토 화면'),
        ('o', '추출 · 2차 검증', 'AI · 로컬 LLM', ['조각마다 결정사항과 근거 발언 추출', '앞뒤 발언과 대조해 AI가 다시 판단', '합의가 아니면 제외, 상태 보정'], '1단계 추출, 2단계 검증 (minutes.py)'),
        ('o', '요구사항 매칭', 'AI · 로컬 LLM', ['유사 요구사항 15건을 후보로 선별', '대상 요구사항과 신뢰도 판단', '보완 문장 또는 신규 후보 제시'], '3단계 매칭 (minutes.py)'),
        ('b', '검토 · 확정', 'PL', ['원문 발췌와 보완안 비교', '문구 편집 후 확정', '변경 이력에 근거 회의 기록'], '요구사항 개정 검토 화면'),
    ]
    for i, (c, t, role, acts, scr) in enumerate(steps):
        x = L + i * (sw + gp)
        b += box(f'cbar {c}', x, 2.1, sw, 0.06)
        b += box(f'stp {c}', x, 2.26, sw, 0.25, f'STEP {i + 1:02d}')
        b += box('st', x, 2.5, sw, 0.42, e(t), 'font-size:15pt')
        b += box(f'rtag {c}', x, 3.0, sw, 0.34, e(role), 'font-size:10.5pt')
        b += box('aibox' if c == 'o' else 'card', x, 3.45, sw, 2.2)
        b += box('cd', x + 0.15, 3.62, sw - 0.25, 2.0, ''.join(f'<p>{e(a)}</p>' for a in acts), 'font-size:11.5pt;line-height:1.4')
        b += box('scr', x, 5.78, sw, 0.6, f'<small>관련 위치</small>{e(scr)}', 'font-size:10pt')
        if i < n - 1:
            b += box('tri', x + sw + 0.05, 4.4, 0.1, 0.22)
    b += box('rbar sand', L, 6.6, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">AI는 추출과 보완안 제시까지 맡고,'
             ' 반영 확정은 PL이 하여 <b>AI 오판 위험을 통제</b>합니다</span>', 'font-size:13.5pt')
    return frame('AI', '로컬 LLM 분석 흐름', '처리 흐름',
                 '로컬 LLM을 기동한 뒤 회의록을 올리면 <b>결정사항 추출, 2차 검증, 요구사항 매칭</b>이 자동으로 진행됩니다.<br>'
                 'AI 결과는 보완안으로만 제시되고, PL이 원문과 비교해 확정해야 요구사항에 반영됩니다.', b, ai=True)


def _roles():
    """장표: AI 역할 설계 (단계별 역할 지시문 3종 + 고도화 방향)."""
    b = ''
    gp = 0.2
    cw = (CW - 2 * gp) / 3
    roles = [
        ('STEP 01 · 추출', '회의록 분석가', '너는 … 프로젝트의 회의록 분석가다', '회의록 조각(약 12분)',
         '결정사항, 근거 발언, 상태, 판단 근거', ['잡담과 일정 조율은 제외', '발언 원문 그대로 인용, 지어내지 않음']),
        ('STEP 02 · 검증', '2차 검토자', '너는 … 결과를 검증하는 2차 검토자다', '결정사항과 앞뒤 대화',
         '예·아니오 3문항과 판단 근거', ['예·아니오 질문으로만 판단', '남은 승인·확인이 있으면 확정 불가']),
        ('STEP 03 · 매칭', '요구사항 매핑 분석가', '너는 … 요구사항 등록부에 매핑하는 분석가다', '결정사항과 후보 요구사항 15건',
         '대상 요구사항, 신뢰도, 보완 문장', ['목록에 있는 요구사항ID만 선택', '보류여도 관련 ID, 없으면 신규']),
    ]
    for i, (stp, t, q, inp, outp, rules) in enumerate(roles):
        x = L + i * (cw + gp)
        b += box('card', x, 2.1, cw, 3.3)
        b += box('cbar o', x, 2.1, cw, 0.06)
        b += box('stp o', x + 0.25, 2.26, cw - 0.4, 0.25, e(stp))
        b += box('ct16', x + 0.25, 2.5, cw - 0.4, 0.4, '<span class="aitag o sm">AI</span>' + e(t), 'font-size:15.5pt')
        b += box('', x + 0.25, 2.9, cw - 0.4, 0.28, e('“' + q + '”'), 'font-size:9.5pt;color:#AF947E')
        b += box('hl-line', x + 0.25, 3.25, cw - 0.5, 0.01)
        for j, (k, v) in enumerate((('입력', inp), ('출력', outp))):
            y = 3.35 + j * 0.42
            b += box('tcat', x + 0.25, y + 0.02, 0.5, 0.3, k)
            b += box('', x + 0.75, y, cw - 0.95, 0.38, e(v), 'font-size:11pt;line-height:1.3')
        b += box('tcat', x + 0.25, 4.25, cw - 0.4, 0.25, '핵심 규칙', 'color:#F46A25')
        b += box('cd', x + 0.25, 4.5, cw - 0.4, 0.85, ''.join(f'<p>{e(r)}</p>' for r in rules), 'font-size:11pt;line-height:1.35')
    b += box('lab', L, 5.6, CW, 0.3, '고도화 방향<em class="tg">고도화</em>')
    ups = [('오판 사례 예시 추가', '실제 회의록에서 나온 오판을 예시로 넣어 판단 기준 보강'),
           ('프로젝트 용어집 반영', '업무 약어와 시스템명을 역할 지시문에 추가'),
           ('지시문 버전 관리', '지시문 변경 전후 결과를 비교해 개선 효과 확인')]
    for i, (t, d) in enumerate(ups):
        b += box('mini', L + i * (cw + gp), 5.95, cw, 1.0, f'<b>{e(t)}</b><span>{e(d)}</span>')
    return frame('AI', 'AI 역할 설계', '역할 지시문',
                 'AI에게 단계마다 <b>역할과 판단 규칙</b>을 부여해, 같은 모델로 추출, 검증, 매칭을 나눠 수행합니다.<br>'
                 '역할 지시문은 모델과 분리되어 있어, 실제 회의록으로 다듬으며 정확도를 계속 높일 수 있습니다.', b, ai=True)


def _backend():
    """장표 3: 백엔드에서 모델을 호출하는 방식 (비동기 작업 + 호출 요청 예시)."""
    b = ''
    rows = [
        ('업로드 요청', 'POST /api/meetings/analyze', 'LLM 연결을 확인한 뒤 작업 ID를 바로 돌려줌'),
        ('백그라운드 작업', 'threading.Thread (1건씩)', '조각마다 추출, 검증, 매칭 순서로 LLM 호출'),
        ('결과 저장', 'decisions 테이블 (ID AI-n)', '매칭이 끝난 결정사항을 한 건씩 바로 저장'),
        ('진행 조회', 'GET /api/jobs/{id} (1.5초 간격)', '진행 단계와 새 결정사항을 화면에 추가'),
    ]
    lw = 5.55
    for i, (t, code, d) in enumerate(rows):
        y = 2.1 + i * 0.98
        if i: b += box('rowline', L, y - 0.07, lw, 0.01)
        b += box('big', L, y + 0.12, 0.8, 0.6, f'{i + 1:02d}', 'font-size:26pt')
        b += box('vrule', L + 0.85, y + 0.08, 0.01, 0.72)
        b += box('', L + 1.05, y + 0.02, lw - 1.05, 0.3, f'<b style="font-size:14pt">{e(t)}</b>')
        b += box('', L + 1.05, y + 0.33, lw - 1.05, 0.25, html.escape(code), MONO + 'font-size:10.5pt;color:#F46A25;font-weight:700')
        b += box('', L + 1.05, y + 0.58, lw - 1.05, 0.3, e(d), 'font-size:11.5pt;color:#555')
    # 오른쪽: 호출 요청 예시
    rx = L + lw + 0.3
    rw = L + CW - rx
    b += box('lab', rx, 2.05, rw, 0.3, '로컬 LLM 호출 요청 (OpenAI 호환)')
    req = ('POST http://localhost:11434/v1/chat/completions\n'
           '{\n'
           '  "model": "qwen3:4b",\n'
           '  "temperature": 0,\n'
           '  "messages": [\n'
           '    {"role": "system", "content": "추출 규칙"},\n'
           '    {"role": "user", "content": "회의록 조각"}\n'
           '  ],\n'
           '  "response_format": {"type": "json_schema", ...},\n'
           '  "reasoning_effort": "none"\n'
           '}')
    b += box('', rx, 2.4, rw, 2.5, f'<pre style="margin:0;white-space:pre;{MONO}font-size:9.5pt;line-height:1.45">{html.escape(req)}</pre>',
             'background:#F7F5F3;border:1px solid #E5E0DB;border-radius:0.12in;padding:0.14in 0.18in;overflow:hidden')
    b += box('mini', rx, 5.05, rw, 0.8, '<b>응답 예시 (JSON)</b><span style="' + MONO + 'font-size:9.5pt;white-space:nowrap">'
             + html.escape('{"reqId": "RQ_QPM_0002", "confidence": "high"}') + '</span>')
    pts = [('형식 강제', 'JSON 스키마로 고정, 틀리면 재요청'), ('AI 2차 검증', '앞뒤 발언과 대조해 상태 보정·제외'),
           ('결과 보정', '목록에 없는 ID는 신규 후보로 처리')]
    pw = (CW - 2 * 0.15) / 3
    for i, (k, t) in enumerate(pts):
        b += box('pcard', L + i * (pw + 0.15), 6.1, pw, 1.0, f'<div class="pk">{e(k)}</div><p>{e(t)}</p>')
    return frame('AI', '백엔드 모델 호출 구조', '호출 방식',
                 '분석은 수 분 이상 걸리므로 서버가 <b>백그라운드 작업</b>으로 처리하고, 화면은 진행 상황을 주기적으로 조회합니다.<br>'
                 '결정사항은 한 건씩 저장되어, 분석이 끝나기 전에도 화면에서 먼저 검토할 수 있습니다.', b, ai=True)


def _speed():
    """장표 4: 처리 시간 단축과 대기 대응 (패턴 P4 전후 비교)."""
    b = box('colh', 2.25, 2.0, 3.85, 0.3, '<span style="color:#8a8a8a">적용 전</span>')
    b += box('colh', 6.6, 2.0, 4.39, 0.3, '<span style="color:#F46A25">적용 후</span>')
    rows = [('결정사항 추출', '사고 과정까지 출력해 조각당 약 5분', '사고 과정 출력을 꺼 조각당 25~60초'),
            ('요구사항 매칭', '요구사항 77건 전체를 입력해 건당 약 5분', '유사 후보 15건만 입력해 건당 1분 이내'),
            ('화면 대기', '분석이 모두 끝나야 결과를 확인', '결정사항이 추출되는 대로 목록에 표시'),
            ('LLM 서버 중단', '분석 요청이 실패해 화면 사용 불가', '저장된 분석 결과로 동작(시연 모드)')]
    for i, (k, a, c) in enumerate(rows):
        t = 2.4 + i * 0.98
        b += box('cat', L, t, 1.5, 0.85, e(k))
        b += box('pan as', 2.25, t, 3.85, 0.85, e(a))
        b += box('tri', 6.17, t + 0.27, 0.3, 0.32)
        b += box('pan tb', 6.6, t, 4.39, 0.85, e(c))
    b += box('note9', L, 6.35, CW, 0.25, '측정 환경: CPU 노트북(i7-1360P, RAM 16GB), Qwen3 4B. 25분 분량 샘플 회의록을 2차 검증까지 포함해 3분 41초에 처리')
    b += box('rbar sand', L, 6.65, CW, 0.8, '<span class="lb">운영 전환</span><span class="tx">GPU 서버로 옮기면 같은 구조에서'
             ' <b>더 큰 모델로 정확도와 속도</b>를 함께 높일 수 있습니다</span>', 'font-size:13.5pt')
    return frame('AI', '처리 시간 단축과 대기 대응', '성능 대응',
                 'CPU만 있는 노트북에서도 쓸 수 있도록 <b>모델의 출력과 입력 길이를 줄여</b> 처리 시간을 단축했습니다.<br>'
                 'LLM 서버가 꺼져 있으면 저장된 분석 결과로 동작하여 시연과 검토가 중단되지 않습니다.', b, ai=True)


def _roadmap():
    """장표 5: 로컬 LLM 고도화 방향 (패턴 P9)."""
    b = ''
    b += box('ptl', L, 2.1, 4.3, 0.3, '현재 구현')
    done = ['로컬 LLM(Ollama, Qwen3) 기동과 연결 확인', '회의록 조각 분할과 결정사항 자동 추출', 'AI 2차 검증으로 상태 보정과 오추출 제외',
            '요구사항 후보 선별과 매칭, 보완 문장 제안',
            '백그라운드 분석과 진행 상황 표시', 'LLM 서버 중단 시 시연 모드 자동 전환']
    b += box('pts', L, 2.45, 4.3, 3.4, ''.join(f'<p>{e(s)}</p>' for s in done))
    b += box('vline', L + 4.55, 2.1, 0.02, 3.9)
    steps = [('GPU 서버 이전', '설정값만 바꿔 GPU 서버로 옮기고 14B 이상 모델로 정확도 향상'),
             ('묶음 매칭', '한 조각의 결정사항을 한 번에 매칭해 호출 횟수 감소'),
             ('실회의록 검증', '실제 회의록으로 결과를 점검하고 AI 역할 지시문(프롬프트) 개선')]
    rx = L + 4.85
    for i, (t, d) in enumerate(steps):
        y = 2.1 + i * 1.3
        b += box(f'big{" b" if i == 1 else " t" if i == 2 else ""}', rx, y + 0.08, 0.9, 0.6, f'{i + 1:02d}', 'font-size:30pt')
        b += box('rst', rx + 1.0, y + 0.02, CW - 5.85, 0.4, e(t) + '<em class="tg">고도화</em>')
        b += box('rsd', rx + 1.0, y + 0.45, CW - 5.85, 0.7, e(d))
    b += box('rbar brown', L, 6.2, CW, 1.1, '<span class="lb">기대 효과</span><span class="tx">외부 API 없이 사내에서 <b>회의록 결정사항의 요구사항 반영</b>을'
             ' 자동화하는 기반을 확보합니다</span>', 'font-size:14pt')
    return frame('계획', '로컬 LLM 고도화 방향', '향후 계획',
                 '로컬 LLM으로 <b>기동부터 추출, 검증, 매칭, 확정까지</b> 동작하는 흐름을 구현했습니다.<br>'
                 '운영 환경에서는 GPU 서버 이전과 실회의록 검증으로 정확도와 처리 속도를 높입니다.', b, ai=True)


def slides():
    """장표 6장의 <section> HTML 목록. deck_lib.PAGE 기준으로 쪽번호가 이어진다."""
    return [_blocks(), _flow(), _roles(), _backend(), _speed(), _roadmap()]


if __name__ == '__main__':
    # 1) 미리보기: 이 폴더 기준 경로
    D.configure('shots/', assets='../../성과제출/assets/', fonts='../../성과제출/fonts/')
    D.PAGE[0] = 0
    D.write(slides(), os.path.join(HERE, '로컬LLM_장표_미리보기.html'), '로컬 LLM 회의록 분석')
    # 2) 붙여넣기용: 성과제출/traceOpsReqSync/ 의 HTML 안에 넣을 <section> 6개 (경로 ../assets/)
    D.configure('shots/', assets='../assets/', fonts='../fonts/')
    D.PAGE[0] = 9  # 기존 자료 9장(AI 활용 구조) 다음에 넣는 기준. 넣는 위치에 따라 쪽번호만 고치면 된다
    out = os.path.join(HERE, '로컬LLM_장표_붙여넣기용.html')
    open(out, 'w', encoding='utf8').write('<!-- 로컬 LLM 장표 6장: 성과제출_TraceOps_ReqSync.html 의 </body> 앞 또는 원하는 <section> 사이에 붙여넣기 -->\n'
                                          + '\n'.join(slides()) + '\n')
    print('paste ->', out)
