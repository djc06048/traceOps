# -*- coding: utf-8 -*-
"""TraceOps + ReqSync 성과 제출 HTML 생성기.
사용: python3 성과제출/traceOpsReqSync/build_traceopsreqsync.py -> 성과제출/traceOpsReqSync/성과제출_TraceOps_ReqSync.html
공통 부품은 ../tools/deck_lib.py, 디자인 규칙은 ../작성가이드.md, 작성 방침은 README.md 참고.
AI 활용(KPI)을 부각하기 위해 AI 관련 장에는 제목 옆 `AI 활용` 표시를, 흐름·카드에는 `AI` 태그를 단다."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
import deck_lib as D
from deck_lib import L, CW, ORANGE, e, box, frame, svg, ICON, detail, gallery

OUT = os.path.join(HERE, '성과제출_TraceOps_ReqSync.html')
D.configure('shots/')

slides = []

# ---------- 1 표지 ----------
slides.append(D.cover('AI-ASSISTED TRACEABILITY MANAGEMENT', 'TraceOps · ReqSync<br>AI 활용 성과 보고', '황금빛, 홍건의, 박혜림, 서준혁'))

# ---------- 2 목차 ----------
slides.append(D.contents([
    (2.7, 'Part. 1  개요', [(1, '성과 요약'), (2, 'TraceOps · ReqSync 소개'), (3, '프로젝트 수행주기와 적용 지점'), (4, '추진 배경'), (5, '목표 및 기대효과')]),
    (4.85, 'Part. 2  AI 활용과 구현 내용', [(6, '업무 흐름'), (7, 'ReqSync 구성과 AI 역할'), (8, '주요 기능과 연계관리'), (9, '단계별 화면 및 기술 구성')]),
    (6.75, 'Part. 3  향후 계획', [(10, '고도화 계획')])]))

# ---------- 3 성과 요약 ----------
body = ''
cw = (CW - 3 * 0.2) / 4
sumdata = [('AI', 'ReqSync 요구사항 개정', ['로컬 LLM이 회의록에서 결정사항을 추출하고 요구사항 매칭과 개정안 제시까지 수행', 'AI 추출 결과를 PL이 원문과 비교해 확정하는 검토 화면을 구현']),
           ('6단계', '추적 관계 관리 구현', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결하여 관리', '삭제·변경 시 영향을 안내하고 검토 후 진행하도록 구현']),
           ('연계관리', '연계 프로세스 관리', ['프로세스 단위로 메서드 누락을 확인하고 연계 테스트케이스로 검증', '호출구조 정적분석을 연계관리 화면에서 실행해 AS-IS 콜트리를 반영']),
           ('정합성', '단계 간 정합성 관리', ['요구사항부터 통합테스트까지 연결을 DB 제약과 검증으로 보장', '상위 항목이 바뀌면 하위에 재검증을 표시하고, 요구사항 변경 이력을 자동 기록'])]
for i, (hero, t, ds) in enumerate(sumdata):
    l = L + i * (cw + 0.2)
    body += box('card', l, 2.1, cw, 5.2)
    body += box('hero', l + 0.25, 2.55, cw - 0.4, 0.8, e(hero))
    body += box('ct16', l + 0.25, 3.6, cw - 0.4, 0.45, e(t), 'font-size:14.5pt')
    body += box('hl-line', l + 0.25, 4.2, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 4.4, cw - 0.45, 2.7, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:14pt')
slides.append(frame('개요', '성과 요약', 'AI 활용 성과',
    '<b>AI 기반 요구사항 개정 검토(ReqSync)와 연계관리</b>를 포함한 TraceOps로 요구사항부터 연계 검증까지 추적 체계를 구현했습니다.<br>로컬 LLM이 회의 결정사항을 추출하고, 연계관리는 프로세스 단위로 누락을 확인하고 검증합니다.', body, ai=True))

# ---------- 4 소개 ----------
body = ''
data = [('check', '추적 관리', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결', '삭제·변경 시 영향을 안내하고 하위가 참조 중이면 삭제 차단', '상위 단계의 요구사항과 물리ID를 자동 상속']),
        ('spark', 'ReqSync (AI)', ['회의록 결정사항을 AI가 추출해 요구사항과 매칭', '개정안을 원문과 비교해 PL이 확정', '근거 회의가 변경 이력에 남음']),
        ('stack', '연계 관리', ['프로세스의 메서드가 개발 대상에 빠짐없이 포함되도록 관리', '소스 호출구조(클래스·메서드)를 캔버스에 매핑', '프로세스별 연계 테스트케이스(E2E)로 검증'])]
cw = 3.25; gp = (CW - 3 * cw) / 2
for i, (ic, t, ds) in enumerate(data):
    l = L + i * (cw + gp)
    body += box('card', l, 2.1, cw, 3.6, '', 'border:2px solid #F46A25;' if i == 1 else '')
    body += box('', l + 0.3, 2.35, 0.7, 0.7, svg(ICON[ic], 0.7))
    body += box('ct20', l + 0.3, 3.2, cw - 0.6, 0.45, e(t))
    body += box('cd', l + 0.3, 3.8, cw - 0.55, 1.85, ''.join(f'<p>{e(d)}</p>' for d in ds))
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">구성 원칙</span><span class="tx">ReqSync는 TraceOps 안의 요구사항 모듈입니다. <b>AI는 추출과 제안</b>까지 맡고, <b>확정은 사람</b>이 합니다</span>')
slides.append(frame('개요', 'TraceOps · ReqSync 소개', '플랫폼 구성',
    '<b>요구사항부터 연계까지 추적</b>하는 TraceOps에 <b>AI 요구사항 어시스턴트(ReqSync)</b>를 더한 플랫폼입니다.<br>회의 결정사항은 근거와 함께 요구사항에 반영되고, 하위 단계는 같은 요구사항 기준을 사용합니다.', body, ai=True))

# ---------- 수행주기 ----------
body = ''
cwp = (CW - 5 * 0.12) / 6
stg = [('착수', '프로젝트 시작', 'o'), ('기술협상', '요구사항 상세화', 'o'), ('분석', '현황업무분석', 'b'), ('설계', '화면·프로그램 설계', 'b'), ('개발 · 단위테스트', '개발과 단위 검증', 't'), ('통합테스트', '프로세스 전체 검증', 't')]
def colx(n): return L + n * (cwp + 0.12)
for n, (t, sub, c) in enumerate(stg):
    x = colx(n)
    body += box(f'cbar {c}', x, 2.05, cwp, 0.06)
    body += box(f'stp {c}', x, 2.2, cwp, 0.22, f'STEP {n+1:02d}')
    body += box('st', x, 2.4, cwp, 0.4, e(t), 'font-size:13pt')
    body += box('scr', x, 2.78, cwp, 0.3, e(sub), 'font-size:10pt')
body += box('flowbox aibox', colx(1), 3.25, cwp * 2 + 0.12, 1.1, '<div><b><span class="aitag o sm">AI</span>ReqSync</b>회의록으로 요구사항 보완·확정<small>고객사 협의 내용을 근거와 함께 반영</small></div>')
body += box('flowbox aibox', colx(3), 3.25, cwp * 3 + 0.24, 1.1, '<div><b>연계관리</b>프로세스 설계(PL·메인 설계자) → 개발 항목 배분 → 연계 테스트케이스로 프로세스 완결 확인<small>메서드 누락이 없는지 프로세스 단위로 확인</small></div>')
body += box('flowbox card', colx(1), 4.5, cwp * 5 + 0.48, 0.75, '<div><b>요구사항 → 분석 → 설계 → 개발 → 테스트 정합성 관리 (상시)</b>삭제·변경 시 영향 안내, 하위 연결 누락과 재검증 표시</div>')
for n in range(2, 6):
    body += box('flowbox', colx(n), 5.4, cwp, 0.82, f'<div><b style="font-size:11pt">산출물 스냅샷</b>{["분석", "설계", "개발·단위", "통합"][n-2]} 확정</div>', 'background:#fff;border:1.5px solid #AF947E;font-size:10.5pt;padding:0.06in 0.1in;')
body += box('rbar sand', L, 6.4, CW, 0.95, '<span class="lb">단계별 변경 통제</span><span class="tx">단계 산출물은 스냅샷으로 확정하고, 확정 이후의 변경은 <b>품질 검토를 거쳐 반영</b>합니다</span>', 'font-size:13pt')
slides.append(frame('개요', '프로젝트 수행주기와 적용 지점', '수행주기 관점',
    '프로젝트는 <b>착수, 기술협상, 분석, 설계, 개발·단위테스트, 통합테스트</b> 순서로 진행되며 단계마다 산출물이 확정됩니다.<br><b>ReqSync는 기술협상·분석</b>에서 요구사항을 확정하고, <b>연계관리는 설계부터 통합테스트까지</b> 프로세스 완결을 확인합니다.', body, ai=True))

# ---------- 추진 배경 ----------
body = ''
data4 = [('요구사항 상세화와 증적', ['RFP 요구사항은 상세화되어 있지 않아 기술협상과 분석 단계에서 고객사와 협의하며 보완', '보완 근거가 회의록에만 남고 반영은 수작업']),
         ('프로세스 단위 연계 누락', ['한 프로세스에 여러 메서드가 있고 담당 개발자가 서로 다름', '메서드 하나가 개발 대상에서 빠지면 프로세스 전체가 동작하지 않음']),
         ('수작업 관리와 매핑 누락', ['요구사항, 분석, 설계, 개발, 테스트를 엑셀과 PMS로 수작업 관리해 정합성 보장이 어려움', '개발 목록을 실수로 삭제하면 요구사항이 어디에도 매핑되지 않아 누락될 수 있음'])]
cw3 = (CW - 2 * 0.25) / 3
tags = ['ReqSync', '연계관리', '정합성']
for i, (t, ds) in enumerate(data4):
    l = L + i * (cw3 + 0.25)
    body += box('card', l, 2.1, cw3, 3.45, '', 'border:2px solid #F46A25;' if i < 2 else '')
    body += box('idx', l + 0.28, 2.3, 1.2, 0.5, f'{i+1:02d}')
    body += box('', l + cw3 - 1.5, 2.4, 1.25, 0.34, f'<span class="aitag o sm" style="font-size:10pt">{tags[i]}</span>', 'text-align:right;')
    body += box('ct16', l + 0.28, 2.95, cw3 - 0.5, 0.45, e(t), 'font-size:15pt')
    body += box('hl-line', l + 0.28, 3.55, cw3 - 0.56, 0.01)
    body += box('cd', l + 0.28, 3.7, cw3 - 0.5, 1.8, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:12.5pt')
imps = [('회의 기반 요구사항 확정', 'ReqSync로 보완하고 증적 이력으로 보존'), ('프로세스 단위 완결 확인', '연계관리로 메서드를 빠짐없이 개발 대상에 포함'), ('정합성과 제출 활용', '요구사항~테스트 정합성 보장, 단계말 검토와 제출 산출물 활용')]
body += box('rbar brown', L, 5.8, CW, 1.3, '<span class="lb">해결 방향</span><div class="imp3">' + ''.join(f'<div>{e(a)}<span>{e(b)}</span></div>' for a, b in imps) + '</div>')
slides.append(frame('개요', '추진 배경', '현행 업무의 불편',
    '요구사항 상세화, 프로세스 연계, 단계 간 정합성이 <b>회의록과 엑셀·PMS 중심의 수작업</b>에 의존하고 있습니다.<br><b>ReqSync와 연계관리</b>로 상세화와 연계 누락을 해결하고, 정합성이 보장되는 체계를 만들고자 했습니다.', body))

# ---------- 6 목표 ----------
body = ''
rows5 = [('', '자산화', '요구사항, 프로세스, 화면, 테이블, 대내외 연계의 연결고리를 프로젝트 공유 자산으로 관리', '공유되는 연결 자산'),
         ('b', 'AI 활용 자동화', 'AI, 연계 분석, 수행 관리의 자동화로 요구사항 반영 정확도를 높이고 변경 영향 분석과 범위 관리를 효율화', 'AI 기반 추출과 매칭'),
         ('t', '정합성 있는 추적성', '요구사항, 분석, 설계, 개발, 테스트 전 단계의 정합성을 보장하고, 단계말 검토와 제출 산출물에 활용하여 누락 리스크 최소화', '정합성 보장')]
for i, (c, t, d, r) in enumerate(rows5):
    y = 2.1 + i * 1.45
    if i: body += box('rowline', L, y - 0.08, CW, 0.01)
    body += box(f'big {c}', L, y + 0.25, 1.2, 0.7, f'{i+1:02d}')
    body += box('vrule', 2.0, y + 0.12, 0.01, 0.95)
    body += box('rt', 2.3, y + 0.05, 5.5, 0.5, e(t))
    body += box('rd', 2.3, y + 0.55, 5.5, 0.85, e(d))
    body += box('outp', 8.15, y + 0.3, 2.84, 0.6, e(r), 'background:#FFF0E6;' if i == 1 else '')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">달성 수단</span><span class="tx">추적 관리 화면, ReqSync(AI), 연계 캔버스로 세 가지 목표를 구현</span>', 'font-size:13.5pt')
slides.append(frame('개요', '목표', '자산화 · AI · 정합성',
    'TraceOps의 목표는 <b>자산화, AI 활용 자동화, 정합성이 보장되는 추적성 확보</b>의 세 가지입니다.<br>개인의 경험이 아니라 프로젝트가 공유하는 표준과 자산으로 일하는 체계를 만듭니다.', body))

# ---------- 7 기대효과 ----------
body = box('colh', 2.15, 2.0, 3.9, 0.3, '<span style="color:#8a8a8a">도입 전</span>')
body += box('colh', 6.6, 2.0, 4.39, 0.3, f'<span style="color:{ORANGE}">도입 후</span>')
rows6 = [('요구사항 보완', '고객 협의 내용을 회의록에서 찾아 수작업으로 반영', 'AI가 결정사항을 추출하고 매칭, PL이 확정'),
         ('증적 이력', '보완 근거가 개인 문서에만 남음', '요구사항 변경 이력에 근거 회의를 자동 연결'),
         ('연계 관계', '프로세스 안의 메서드 누락을 담당자 각자가 확인', '호출 관계 기준으로 프로세스를 설계하고 개발 항목에 연결'),
         ('누락 방지', '개발 목록 삭제 등 실수로 요구사항이 매핑에서 빠질 수 있음', '삭제·변경 시 오류 가능성 안내, 검토 후 진행')]
for i, (k, a, b) in enumerate(rows6):
    t = 2.4 + i * 1.3
    body += box('cat', L, t, 1.35, 1.15, e(k))
    body += box('pan as', 2.15, t, 3.9, 1.15, e(a))
    body += box('tri', 6.12, t + 0.42, 0.3, 0.32)
    body += box('pan tb', 6.6, t, 4.39, 1.15, e(b))
slides.append(frame('개요', '기대효과', '도입 전후 비교',
    '<b>AI와 추적 체계</b>를 도입하면 요구사항 반영과 연계 관리가 개인 의존에서 공유 체계로 바뀝니다.<br>요구사항 반영, 변경 이력, 연계 관계, 범위 관리 네 영역에서 변화가 나타납니다.', body))

# ---------- 10 업무 흐름 ----------
HUM = '<span style="display:inline-block;font-size:9pt;font-weight:700;color:#fff;background:#6E5744;border-radius:0.08in;padding:0 0.07in;margin-right:0.08in;vertical-align:2px">사람</span>'
AUTO = '<span style="display:inline-block;font-size:9pt;font-weight:700;color:#6E5744;background:#fff;border:1.5px solid #6E5744;border-radius:0.08in;padding:0 0.07in;margin-right:0.08in;vertical-align:2px">자동</span>'
def act(a):
    if a.startswith('AI|'): return '<p><span class="aitag o sm">AI</span>' + e(a[3:]) + '</p>'
    if a.startswith('사람|'): return '<p>' + HUM + e(a[3:]) + '</p>'
    if a.startswith('자동|'): return '<p>' + AUTO + e(a[3:]) + '</p>'
    return f'<p>{e(a)}</p>'
body = ''
steps = [('o', '요구사항 개정', 'PL', ['AI|결정사항 추출, 요구사항 매칭, 개정안 제시', '사람|원문과 비교해 편집하고 PL이 확정', '근거 회의가 변경 이력에 기록'], '요구사항 개정 검토(ReqSync)'),
         ('b', '상세공정 관리', '작업자 · PL', ['사람|분석, 설계, 개발 항목에 요구사항 연결', '계획, 실적, 증적 관리', '삭제·변경 시 영향 안내'], '분석 · 설계 · 개발단계'),
         ('o', '연계 관리', 'PL · 메인 설계자', ['사람|프로세스 설계(기간계, 채널, AI Agent)', '메서드를 개발 항목으로 연결해 개발자에게 배분', '자동|호출구조 정적분석으로 AS-IS 반영'], '연계관리, AS-IS 목록'),
         ('t', '테스트 관리', '작업자', ['사람|단위테스트 등록과 수행', '프로세스 기준 연계 테스트케이스로 전체 흐름 검증', '요구사항, 물리ID 자동 연결'], '단위 · 통합테스트, 연계 테스트케이스')]
sw = 2.31; sg = (CW - 4 * sw) / 3
for i, (c, t, role, acts, scr) in enumerate(steps):
    l = L + i * (sw + sg)
    body += box(f'cbar {c}', l, 2.1, sw, 0.06)
    body += box(f'stp {c}', l, 2.28, sw, 0.25, f'STEP {i+1:02d}')
    body += box('st', l, 2.52, sw, 0.45, e(t))
    body += box(f'rtag {c}', l, 3.05, sw, 0.36, e(role))
    body += box('card', l, 3.5, sw, 2.3)
    body += box('cd', l + 0.2, 3.68, sw - 0.35, 2.1, ''.join(act(a) for a in acts), 'font-size:12pt')
    body += box('scr', l, 5.92, sw, 0.6, f'<small>관련 화면</small>{e(scr)}')
    if i < 3: body += box('tri', l + sw + 0.1, 4.5, 0.14, 0.24)
body += box('rbar sand', L, 6.65, CW, 0.85, '<span class="lb">역할 분담</span><span class="tx">AI는 추출과 제안까지, 확정과 이후 단계는 사람이 맡아 <b>같은 요구사항 기준의 하나의 흐름</b>으로 관리합니다</span>', 'font-size:13pt')
slides.append(frame('구현', '업무 흐름', '단계별 프로세스',
    '<b>ReqSync를 도입하면</b> 회의 결정사항이 요구사항으로 반영되고, 개발, 테스트, 연계까지 <b>하나의 추적 흐름</b>으로 이어집니다.<br>AI는 추출과 제안을, 사람은 확정과 설계, 개발, 테스트를 맡아 역할을 나눕니다.', body, ai=True))

# ---------- 8 AI 활용 구조: 로컬 LLM 구성과 동작 ----------
body = ''
fw = 1.8; fg = (CW - 5 * fw) / 4
fl = [('card', '<b>회의록</b>텍스트(.txt) 업로드<small>12분 단위로 분할</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>결정사항 추출</b>근거 발언과 상태<small>원문에 없는 문장은 표시</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>2차 검증</b>앞뒤 발언과 대조<small>합의가 아니면 제외</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>요구사항 매칭</b>유사 후보 15건 비교<small>신뢰도와 개정안 제시</small>'),
      ('humbox', '<b>PL 검토 · 확정</b>원문과 비교<small>문구 편집, 확정 권한</small>')]
for i, (cls, txt) in enumerate(fl):
    x = L + i * (fw + fg)
    body += box(f'flowbox {cls}', x, 2.1, fw, 1.55, txt)
    if i < 4: body += box('tri', x + fw + (fg - 0.12) / 2, 2.72, 0.12, 0.3)
body += box('lab', L, 3.9, 6, 0.3, '로컬 LLM 스펙')
chips = [('실행 도구', 'Ollama', 'MIT 라이선스, 무료'), ('모델', 'Qwen3', 'Apache 2.0, 상업 사용 무료'),
         ('호출 규격', 'OpenAI 호환 API', 'vLLM 등 다른 서버와 호환'), ('실행 환경', 'CPU · GPU', '서버 사양에 맞춰 모델 선택')]
tw = (CW - 3 * 0.2) / 4
for i, (c, v, sub) in enumerate(chips):
    body += box('tchip', L + i * (tw + 0.2), 4.25, tw, 1.0, f'<div class="tcat">{e(c)}</div><div class="tval">{e(v)}</div><div style="font-size:10.5pt;color:#6B6B6B;margin-top:0.03in">{e(sub)}</div>')
mw2 = (CW - 0.2) / 2
body += box('mini', L, 5.38, mw2, 1.05, '<b>ReqSync가 해결하는 일</b><span>회의에서 합의한 내용이 요구사항에 누락되지 않고 근거와 함께 반영되도록 돕습니다</span>')
body += box('mini', L + mw2 + 0.2, 5.38, mw2, 1.05, '<b>설정만으로 모델 교체</b><span>서버 주소와 모델 이름을 설정값으로 분리해 GPU 서버로 코드 수정 없이 교체합니다</span>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">AI는 추출과 제안까지 맡고, 최종 확정 권한은 PL에게 두어 AI 오판 위험을 통제합니다</span>', 'font-size:13.5pt')
slides.append(frame('AI', 'ReqSync 구성과 동작', 'AI 요구사항 어시스턴트',
    '<b>ReqSync</b>는 회의록의 결정사항을 AI가 추출해 요구사항에 반영하도록 돕는 <b>AI 요구사항 어시스턴트</b>입니다.<br>로컬 LLM으로 구성했으며, 추출, 2차 검증, 요구사항 매칭 순서로 처리하고 확정은 PL이 합니다.', body, ai=True))

# ---------- 9 ReqSync AI 역할 설계 ----------
body = ''
gp = 0.2
cw3 = (CW - 2 * gp) / 3
roles = [
    ('STEP 01 · 추출', '회의록 분석가', '너는 … 프로젝트의 회의록 분석가다', '회의록 조각(약 12분)', '결정사항, 근거 발언, 상태, 판단 근거', ['잡담과 일정 조율은 제외', '발언 원문 그대로 인용, 지어내지 않음']),
    ('STEP 02 · 검증', '2차 검토자', '너는 … 결과를 검증하는 2차 검토자다', '결정사항과 앞뒤 대화', '예·아니오 3문항과 판단 근거', ['예·아니오 질문으로만 판단', '남은 승인·확인이 있으면 확정 불가']),
    ('STEP 03 · 매칭', '요구사항 매핑 분석가', '너는 … 요구사항 등록부에 매핑하는 분석가다', '결정사항과 후보 요구사항 15건', '대상 요구사항, 신뢰도, 개정 문구', ['목록에 있는 요구사항ID만 선택', '보류여도 관련 ID, 없으면 신규']),
]
for i, (stp, t, q, inp, outp, rules) in enumerate(roles):
    x = L + i * (cw3 + gp)
    body += box('card', x, 2.1, cw3, 4.6)
    body += box('cbar o', x, 2.1, cw3, 0.06)
    body += box('stp o', x + 0.25, 2.32, cw3 - 0.4, 0.25, e(stp))
    body += box('ct16', x + 0.25, 2.62, cw3 - 0.4, 0.4, '<span class="aitag o sm">AI</span>' + e(t), 'font-size:16pt')
    body += box('', x + 0.25, 3.1, cw3 - 0.4, 0.3, e('“' + q + '”'), 'font-size:10pt;color:#AF947E')
    body += box('hl-line', x + 0.25, 3.55, cw3 - 0.5, 0.01)
    for j, (k, v) in enumerate((('입력', inp), ('출력', outp))):
        y = 3.75 + j * 0.65
        body += box('tcat', x + 0.25, y + 0.02, 0.5, 0.3, k, 'font-size:11pt')
        body += box('', x + 0.8, y, cw3 - 1.0, 0.6, e(v), 'font-size:12pt;line-height:1.3')
    body += box('tcat', x + 0.25, 5.15, cw3 - 0.4, 0.25, '핵심 규칙', 'color:#F46A25;font-size:11pt')
    body += box('cd', x + 0.25, 5.5, cw3 - 0.4, 1.5, ''.join(f'<p>{e(r)}</p>' for r in rules), 'font-size:12pt;line-height:1.4')
slides.append(frame('AI', 'ReqSync AI 역할 설계', '역할 지시문',
    'ReqSync는 단계마다 AI에게 <b>역할과 판단 규칙</b>을 부여해, 같은 모델로 추출, 검증, 매칭을 나눠 수행합니다.<br>역할 지시문은 모델과 분리되어 있어, 실제 회의록으로 다듬으며 정확도를 높일 수 있습니다.', body, ai=True))

# ---------- 10~14 주요 기능 ----------
slides.append(detail('ReqSync 요구사항 개정 검토', '핵심 기능 1/5',
    '회의 결정사항을 <b>AI가 추출해 요구사항과 매칭</b>하고, 개정안을 원문과 비교해 PL이 확정합니다.<br>좌측은 AI 추출 결과, 우측은 PL 편집으로 나란히 놓은 병렬 검토 화면입니다.',
    'review_modal.png', 1440, 900,
    [dict(t='AI 결정사항 추출과 매칭', d='회의록에서 결정사항을 추출하고 기존 요구사항과 신뢰도, 발언 원문과 함께 제시합니다', zoom=(258, 240, 445, 150), capH=1.2),
     dict(t='AI 개정안과 PL 확정', d='기존 문구 대비 개정안을 diff로 보여 주고, PL이 편집한 뒤 확정합니다', zoom=(739, 472, 445, 150), capH=1.2)],
    [('원문 근거 · 사람 확정', '발언 원문을 보고 PL이 확정, 이력 기록'), ('로컬 LLM 추출 · 2차 검증', '추출 결과를 한 번 더 검증해 오추출을 줄이고, 근거 발언과 신뢰도를 함께 표시')],
    '결정사항의 요구사항 반영을 근거와 함께 관리', '요구사항관리 > ReqSync(요구사항 개정 검토)', ai=True))
slides.append(detail('요구사항 관리와 변경 이력', '핵심 기능 2/5',
    '요구사항을 <b>목록 하나로 관리</b>하고, 변경은 이전 값과 비교한 이력으로 자동 기록합니다.<br>ReqSync 확정 내용도 같은 목록과 이력에 반영됩니다.',
    'req.png', 1440, 900,
    [dict(t='ReqSync 진입과 목록 관리', d='ReqSync 버튼으로 개정 검토에 들어가고 추가, 내보내기, 저장을 합니다', zoom=(1050, 300, 350, 65)),
     dict(t='요구사항 목록과 변경 이력', d='요구사항을 목록으로 관리하며 수정, 삭제 시 이전 값과 비교한 이력이 남습니다', zoom=(40, 420, 440, 120), capH=1.2)],
    [('단일 기준', '분석, 설계, 개발, 테스트가 등록된 목록만 선택'), ('이력 보존', '근거 회의록과 결정사항을 이력에 연결')],
    '요구사항 변경 근거를 이력으로 보존', '상세공정관리 > 요구사항관리'))
slides.append(detail('상세공정관리', '핵심 기능 3/5',
    '분석, 설계, 개발 항목의 <b>계획, 실적, 증적</b>을 한 화면에서 관리합니다.<br>요구사항이 매핑된 항목을 지우거나 바꾸면 <b>영향 범위와 오류 가능성을 안내</b>하고, 사용자가 검토한 뒤 진행합니다.',
    'analysis.png', 1440, 900,
    [dict(t='단계별 항목과 진행 상태', d='항목 ID, 작업자, 진행상태(완료, 지연, 진행중, 미착수)를 조회하고 관리합니다', zoom=(40, 564, 440, 110), capH=1.1),
     dict(t='계획 · 실적과 증적', d='작업자 계획·실적 일자와 증적을 관리하고, 실적 입력 시 증적이 필수입니다', zoom=(661, 488, 440, 125), capH=1.1)],
    [('누락 방지 안내', '삭제·변경 시 영향 범위를 안내하고 검토 후 진행'), ('자동 상속과 검증', '상위 값은 자동 상속, 하위 연결 누락 시 표시')],
    '매핑 누락 가능성을 안내하고 단계 간 연결을 관리', '상세공정관리 > 분석단계 (설계단계, 개발단계 동일 구조)'))
slides.append(detail('테스트관리', '핵심 기능 4/5',
    '단위테스트와 통합테스트를 <b>요구사항과 개발 항목에 연결</b>하여 관리합니다.<br>통합테스트는 개발 항목 기준으로 단위테스트를 묶은 것이며, 연결 정보는 묶은 단위에서 자동으로 계산됩니다.',
    'integration.png', 1440, 900,
    [dict(t='통합테스트와 묶인 단위테스트', d='통합테스트가 묶은 단위테스트와 연결 개발ID를 한 줄로 보여 줍니다', zoom=(371, 523, 426, 100), padx=3),
     dict(t='요구사항 · 물리ID 자동 연결', d='묶인 단위테스트의 요구사항ID와 물리ID가 합집합으로 자동 반영됩니다', zoom=(803, 523, 330, 100), padx=3)],
    [('자동 연결', '개발ID, 요구사항ID, 물리ID를 묶은 단위에서 계산'), ('변경 영향 안내', '연결 변경과 삭제 시 영향 범위를 팝업으로 안내')],
    '요구사항부터 통합테스트까지 한 줄로 추적', '테스트관리 > 통합테스트'))
# ---------- 연계관리 1/3: 개념과 필요성 ----------
body = ''
body += box('card', L, 2.0, CW, 2.2)
body += box('lab', L + 0.3, 2.1, 6, 0.3, '관리 범위')
sw = [1.95, 4.95, 1.95]; sg = 0.36
sx = L + 0.3
body += box('flowbox', sx, 2.5, sw[0], 1.45, '<div><b>채널</b>CM, TM, 콜센터 등<small>기간계 바깥의 요청</small></div>', 'background:#F3ECE5;border:2px solid #6E5744;')
body += box('tri', sx + sw[0] + 0.11, 3.1, 0.16, 0.3)
mx0 = sx + sw[0] + sg
body += box('flowbox', mx0, 2.5, sw[1], 1.45, '', 'background:#fff;border:2px solid #F46A25;')
body += box('', mx0 + 0.2, 2.55, 4.6, 0.3, '<b style="font-size:12pt">기간계 메인 프로세스</b>')
for n, (t, miss) in enumerate([('메서드 1', 0), ('메서드 2', 0), ('메서드 3', 1), ('메서드 4', 0)]):
    bx = mx0 + 0.2 + n * 1.13
    body += box('flowbox', bx, 2.95, 1.0, 0.85, f'<div><b style="font-size:11.5pt">{t}</b><small>{"누락" if miss else "담당 개발자"}</small></div>', 'background:#fff;border:2px dashed #F46A25;' if miss else 'background:#F7F5F3;border:1px solid #E5E0DB;')
body += box('tri', mx0 + sw[1] + 0.11, 3.1, 0.16, 0.3)
ax = mx0 + sw[1] + sg
body += box('flowbox aibox', ax, 2.5, sw[2], 1.45, '<div><b><span class="aitag o sm">AI</span>AI Agent</b>호출하는 기간계 기능<small>AI 기능의 의존 관계</small></div>')
cw3 = (CW - 2 * 0.2) / 3
why = [('필요한 이유 1', '메서드 누락 방지', '메인 프로세스의 메서드는 담당 개발자가 서로 달라 한 사람이 전체를 파악하기 어렵고, 하나만 빠져도 프로세스가 동작하지 않음'),
       ('필요한 이유 2', '연계 테스트케이스', '프로세스 기준으로 단위테스트를 묶어 처음부터 끝까지(E2E) 수행하고, 어떤 프로세스를 테스트해야 하는지 파악'),
       ('필요한 이유 3', '기간계 외 연계 관리', '채널이 기간계의 어떤 메서드를 호출하는지, AI 기능이 어떤 기간계 호출에 의존하는지 확인')]
for n, (k1, t, d) in enumerate(why):
    l = L + n * (cw3 + 0.2)
    body += box('pcard', l, 4.4, cw3, 1.65, f'<div class="pk">{e(k1)}</div><p style="font-weight:700;font-size:13.5pt">{e(t)}</p><p style="font-size:11pt;color:#555;margin-top:0.04in">{e(d)}</p>')
body += box('rbar sand', L, 6.25, CW, 1.1, '<span class="lb">운영 방식</span><div class="tx" style="font-size:12.5pt;line-height:1.5">PL과 메인 설계자가 프로세스를 등록·설계하고, 하위 메서드는 개발 항목이 되어 개발자별로 배분됩니다.<br>개발 항목 기준의 통합테스트와 달리, 프로세스 기준으로 단위테스트를 묶은 연계 테스트케이스를 구성해 테스트 대상과 결과를 확인합니다.</div>')
slides.append(frame('구현', '연계관리 개요', '개념과 필요성',
    '연계관리는 <b>기간계의 메인 프로세스</b>뿐 아니라 <b>채널과 AI Agent 등 기간계 바깥의 연계</b>까지 프로세스로 관리하는 기능입니다.<br>프로세스 안의 메서드가 하나만 빠져도 동작하지 않으므로, 누락을 막고 연계 테스트케이스로 검증하기 위해 필요합니다.', body))

# ---------- 연계관리 2/3: 관리 예시 ----------
body = ''
def chain(y, label, items):
    out = box('lab', L, y, 9, 0.3, label)
    n = len(items); gap = 0.3
    w = (CW - gap * (n - 1)) / n
    for i, (kind, title, sub) in enumerate(items):
        x = L + i * (w + gap)
        if kind == 'ch':
            cls, st = 'flowbox', 'background:#F3ECE5;border:2px solid #6E5744;'
        elif kind == 'ai':
            cls, st = 'flowbox aibox', ''
        elif kind == 'ret':
            cls, st = 'flowbox', 'background:#fff;border:2px dashed #AF947E;'
        else:
            cls, st = 'flowbox card', 'background:#fff;border:1px solid #E5E0DB;'
        tag = '<span class="aitag o sm">AI</span>' if kind == 'ai' else ''
        out += box(cls, x, y + 0.34, w, 0.95, f'<div><b style="font-size:12.5pt">{tag}{e(title)}</b><span style="font-size:11pt">{e(sub)}</span></div>', st)
        if i < n - 1: out += box('tri', x + w + 0.07, y + 0.34 + 0.33, 0.16, 0.28)
    return out
body += chain(1.95, '예 1. 기간계 내부 메인 프로세스 (인수지침검사)', [
    ('m', '보험료 체크', '프로세스의 첫 메서드'),
    ('m', '담보 인수지침', 'inquireCvrUdchk'),
    ('m', '위배내용 저장', 'saveVioDtl'),
    ('ret', '프로세스 완료', '3개 메서드가 모두 개발 대상이어야 동작')])
body += chain(3.4, '예 2. 채널에서 요청한 경우 (콜센터 설계 목록 조회)', [
    ('ch', '채널: 콜센터', '설계 목록 조회 요청'),
    ('m', '기간계 메서드', '설계 대상건 조회'),
    ('m', '기간계 메서드', '설계 내용 조회'),
    ('ret', '채널로 리턴', '수행된 메서드 확인')])
body += chain(4.85, '예 3. AI 기능을 구현하는 경우 (AI 인수지침 위배해소)', [
    ('ch', '프론트', 'AI 인수지침 위배해소 액션'),
    ('m', '기간계: Input 생성', '설계 대상건 조회 → 위배내용 조회 → …'),
    ('ai', 'AI Agent', 'AI 인수지침 위배해소')])
body += box('rbar sand', L, 6.4, CW, 0.95, '<span class="lb">관리 효과</span><span class="tx" style="font-size:12.5pt">세 경우 모두 호출 경로에 빠진 메서드가 없는지 확인하고, <b>연계 테스트케이스(E2E)</b>로 프로세스 전체 동작을 검증합니다.</span>')
slides.append(frame('구현', '연계관리 예시', '기간계 · 채널 · AI Agent',
    '기간계 내부의 <b>메인 프로세스</b>, 채널의 요청, AI Agent의 호출을 모두 <b>프로세스</b>로 관리할 수 있습니다.<br>각 프로세스가 어떤 메서드를 거쳐 응답되는지 보여 주므로 누락 확인과 연계 테스트케이스 구성에 활용합니다.', body))

slides.append(detail('연계관리 화면', '핵심 기능 5/5',
    '실제 화면에서는 프로세스를 <b>연계 캔버스</b>에 노드와 연결선으로 그려, 메서드 단위로 설계하고 관리합니다.<br>연계관리 화면에서 호출구조 정적분석을 실행해 반영한 AS-IS 콜트리(클래스·메서드)를 캔버스 노드에 매핑합니다.',
    'linkage_asis.png', 1440, 900,
    [dict(t='연계 프로세스 캔버스', d='업무 흐름을 노드와 연결선으로 그리고 동기·비동기 호출을 구분합니다', zoom=(95, 300, 700, 120), capH=1.0),
     dict(t='호출구조 분석 실행과 콜트리 매핑', d='버튼으로 호출구조 정적분석을 실행하면 AS-IS 콜트리가 갱신되어 캔버스 노드에 매핑됩니다', zoom=(1116, 180, 275, 175), capH=1.35)],
    [('호출구조 기반', '클래스·메서드 호출 관계를 노드와 연결'), ('조회와 설계 분리', 'AS-IS는 조회 전용, TO-BE는 PL·메인 설계자가 설계')],
    '프로세스를 메서드 단위로 설계해 개발 누락 방지', '연계관리 > AS-IS 프로세스'))

# ---------- 15 단계별 화면 ----------
full = (0, 52, 1440, 832)
slides.append(gallery('상세공정, 테스트, 기준정보까지 <b>같은 화면 체계</b>로 관리합니다.<br>단계마다 같은 조회, 검색, 저장 방식을 사용하므로 사용 방법을 한 번만 익히면 됩니다.', '단계별 화면', '상세공정 · 테스트 · 기준정보',
    [('분석단계', '현황업무분석 항목 관리', 'analysis.png', full), ('설계단계', '화면, 프로그램, 인터페이스 설계 관리', 'design.png', full),
     ('개발단계', '설계 항목 기준 개발 관리', 'dev.png', full), ('단위테스트', '개발 항목별 테스트 케이스와 결과', 'unit.png', full),
     ('AS-IS 물리ID 관리', '개발 대상 물리ID 기준 정보', 'asis.png', full), ('ReqSync 회의 목록', '회의록별 AI 분석 결과와 업로드', 'review.png', full)], 3, 2, 1.85))

# ---------- 16 기술 구성 ----------
body = ''
T0 = 2.0; BH = 1.95
body += box('blk', L, T0, 2.5, BH, '')
body += box('', L + 0.3, T0 + 0.2, 0.5, 0.5, svg(ICON['window'], 0.5))
body += box('bt', L + 0.3, T0 + 0.8, 2.0, 0.4, '사용자 브라우저')
body += box('bs', L + 0.3, T0 + 1.25, 2.0, 0.6, 'HTML, JavaScript')
body += box('arrl', 3.3, T0 + 1.0, 0.6, 0.02) + box('arrh', 3.86, T0 + 0.93, 0.12, 0.16) + box('alb', 3.1, T0 + 0.6, 1.0, 0.3, 'REST API')
body += box('blk sd', 4.05, T0, 4.1, BH, '')
body += box('bt', 4.35, T0 + 0.12, 3.6, 0.4, 'TraceOps 서버 (Python)')
body += box('bs', 4.35, T0 + 0.5, 3.6, 0.3, 'Python 표준 라이브러리 기반')
for k, nm in enumerate(['요구사항', '추적(분석~통합)', 'ReqSync 검토', '연계']):
    body += box('chipw', 4.35 + (k % 2) * 1.82, T0 + 0.9 + (k // 2) * 0.48, 1.7, 0.4, nm, 'font-size:11pt')
body += box('arrl', 8.2, T0 + 1.0, 0.45, 0.02) + box('arrh', 8.6, T0 + 0.93, 0.12, 0.16) + box('alb', 8.0, T0 + 0.6, 0.9, 0.3, 'SQL')
body += box('blk', 8.75, T0, 2.24, BH, '')
body += box('bt', 9.0, T0 + 0.15, 1.9, 0.4, '데이터')
body += box('chipw', 9.0, T0 + 0.7, 1.75, 0.95, '<div>SQLite<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">traceops.db<br>요구사항, 단계별 항목, 연결, 회의·결정사항, 연계</span></div>', 'font-size:12pt')
ay = T0 + BH + 0.2
body += box('flowbox aibox', L, ay, 5.05, 1.0, '<div><b><span class="aitag o sm">AI</span>로컬 LLM 서버 (Ollama · Qwen3)</b>ReqSync의 결정사항 추출, 검증, 매칭을 수행</div>')
body += box('flowbox card', L + 5.24, ay, 5.05, 1.0, '<div><b>호출구조 정적분석</b>연계관리 화면에서 실행해 AS-IS 콜트리를 연계 데이터로 반영</div>')
body += box('lab', L, 5.45, 4, 0.3, '상용화 시 보완 방향')
comm = [('데이터 저장', 'SQLite를 서버형 DB로 전환하여 동시 접속, 백업 확보'),
        ('인증과 권한', '사내 계정 연동과 서버 측 권한 검증 (현재는 화면의 PL·작업자 미리보기)'),
        ('AI 실행 환경', 'GPU 서버 적용, 모델 반입·갱신 절차, 회의록 보관 정책'),
        ('운영 체계', '배포 자동화, 모니터링, 정기 백업, 보안 점검')]
mw = (CW - 3 * 0.15) / 4
for i, (a, t) in enumerate(comm):
    body += box('mini', L + i * (mw + 0.15), 5.8, mw, 1.55, f'<b>{e(a)}</b><span>{e(t)}</span>')
slides.append(frame('구현', '기술 구성', '시스템 구성',
    '<b>Python 서버와 SQLite</b>로 가볍게 구현하고, AI 기능은 로컬 LLM 서버(Ollama)와 연동합니다.<br>호출구조 분석은 연계관리 화면에서 실행하며, 상용화 단계에서는 데이터, 보안, 운영 영역을 보완합니다.', body))

# ---------- 17 고도화 계획 ----------
body = ''
fut = [('ReqSync · AI 활용', 'AI 정확도와 활용 범위 확대', 'GPU 서버와 더 큰 모델을 적용하고, 실회의록 검증으로 역할 지시문을 개선합니다. RFP 등 문서에서 요구사항 후보를 추출하는 기능으로도 확장합니다.'),
       ('연계관리', '연계 범위와 검증 확대', '채널(CM, TM, 콜센터)과 AI Agent를 노드로 구분해 호출 경로를 관리하고, 변경 영향을 추적해 인터페이스 누락을 사전에 차단합니다.')]
for i, (tag, t, d) in enumerate(fut):
    y = 2.1 + i * 2.15
    body += box('fut', L, y, 6.4, 1.95, '')
    body += box('', L + 0.3, y + 0.22, 2.4, 0.3, f'<span class="futtag">{e(tag)}</span>')
    body += box('futt', L + 0.3, y + 0.55, 5.8, 0.5, e(t))
    body += box('futd', L + 0.3, y + 1.05, 5.8, 0.8, e(d))
body += box('lab', 7.4, 2.1, 3.5, 0.3, '수행관리 자동화')
adds = [('단계말 스냅샷 확정', '분석, 설계, 개발·단위, 통합 산출물을 스냅샷으로 확정'), ('단계별 변경 통제', '확정된 단계 산출물을 수정할 때 품질 검토를 거치도록 관리'), ('제출 산출물과 진척 관리', '단계별 제출 산출물 생성과 진척 모니터링'), ('엑셀 · PMS 연동', '기존 관리 도구와 연동해 이중 입력 제거')]
for i, (t, d) in enumerate(adds):
    y = 2.45 + i * 1.0
    body += box('sq', 7.4, y + 0.1, 0.1, 0.1)
    body += box('rst', 7.65, y - 0.05, 3.35, 0.4, e(t), 'font-size:14.5pt')
    body += box('rsd', 7.65, y + 0.33, 3.35, 0.6, e(d), 'font-size:11pt;line-height:1.3')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추진 방향</span><span class="tx">AI 활용 정확도 향상과 연계관리 확장을 우선 추진하고, 이후 수행관리 자동화로 확대합니다</span>', 'font-size:13.5pt')
slides.append(frame('계획', '고도화 계획', '추후 추진',
    '<b>AI 활용 범위 확대와 연계관리 확장</b>을 우선 추진하고, 수행관리 자동화로 이어가겠습니다.<br>로컬 LLM은 정확도와 처리 속도를, 연계관리는 채널과 AI Agent까지 관리 범위를 넓힙니다.', body))

# ---------- 18 엔딩 ----------
slides.append(D.ending())

D.write(slides, OUT, 'TraceOps · ReqSync 성과 제출')
