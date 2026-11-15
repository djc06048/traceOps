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
    (4.85, 'Part. 2  AI 활용과 구현 내용', [(6, 'AI 활용 구조'), (7, '업무 흐름'), (8, '주요 기능'), (9, '단계별 화면 및 기술 구성')]),
    (6.75, 'Part. 3  향후 계획', [(10, '고도화 계획')])]))

# ---------- 3 성과 요약 ----------
body = ''
cw = (CW - 3 * 0.2) / 4
sumdata = [('AI', 'ReqSync 요구사항 개정', ['회의록에서 결정사항을 추출하고 요구사항 매칭과 개정안 제시까지 AI 기반으로 설계', 'AI 추출 결과를 PL이 원문과 비교해 확정하는 검토 화면을 구현']),
           ('6단계', '추적 관계 관리 구현', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결하여 관리', '삭제·변경 시 영향을 안내하고 검토 후 진행하도록 구현']),
           ('POC', '호출구조 연계 분석', ['소스 호출구조(클래스·메서드)를 추출해 연계 데이터로 구성', '연계 캔버스 노드에 매핑해 연계 관계를 팀이 공유']),
           ('정합성', '단계 간 정합성 관리', ['요구사항부터 통합테스트까지 연결을 DB 제약과 검증으로 보장', '상위 항목이 바뀌면 하위에 재검증을 표시하고, 요구사항 변경 이력을 자동 기록'])]
for i, (hero, t, ds) in enumerate(sumdata):
    l = L + i * (cw + 0.2)
    body += box('card', l, 2.1, cw, 3.65)
    body += box('hero', l + 0.25, 2.35, cw - 0.4, 0.7, e(hero))
    body += box('ct16', l + 0.25, 3.15, cw - 0.4, 0.4, e(t), 'font-size:13.5pt')
    body += box('hl-line', l + 0.25, 3.65, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 3.8, cw - 0.45, 1.9, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:11.5pt')
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">다음 단계</span><span class="tx">로컬 LLM 기반 결정사항 추출 연동과 호출구조 분석의 TraceOps 통합을 보완하여 AI 활용을 완성합니다</span>')
slides.append(frame('개요', '성과 요약', 'AI 활용 성과',
    '<b>AI 기반 요구사항 개정 검토(ReqSync)</b>를 포함한 TraceOps로 요구사항부터 연계까지 추적 체계를 구현했습니다.<br>AI 추출은 설계와 검토 화면으로 검증했으며, 로컬 LLM 연동과 호출구조 분석 통합은 보완할 예정입니다.', body, ai=True))

# ---------- 4 소개 ----------
body = ''
data = [('check', '추적 관리', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결', '삭제·변경 시 영향을 안내하고 하위가 참조 중이면 삭제 차단', '상위 단계의 요구사항과 물리ID를 자동 상속']),
        ('spark', 'ReqSync (AI)', ['회의록 결정사항을 AI가 추출해 요구사항과 매칭', '개정안을 원문과 비교해 PL이 확정', '근거 회의가 변경 이력에 남음']),
        ('stack', '연계 관리', ['프로세스의 메서드가 개발 대상에 빠짐없이 포함되도록 관리', '소스 호출구조(클래스·메서드)를 캔버스에 매핑', 'AS-IS는 조회, TO-BE는 설계'])]
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
body += box('flowbox aibox', colx(3), 3.25, cwp * 3 + 0.24, 1.1, '<div><b>연계관리</b>프로세스 설계(PL) → 개발 항목 배분 → 통합테스트로 프로세스 완결 확인<small>메서드 누락이 없는지 프로세스 단위로 확인</small></div>')
body += box('flowbox card', colx(1), 4.5, cwp * 5 + 0.48, 0.75, '<div><b>요구사항 → 분석 → 설계 → 개발 → 테스트 정합성 관리 (상시)</b>삭제·변경 시 영향 안내, 하위 연결 누락과 재검증 표시</div>')
for n in range(2, 6):
    body += box('flowbox', colx(n), 5.4, cwp, 0.82, f'<div><b style="font-size:11pt">산출물 스냅샷</b>{["분석", "설계", "개발·단위", "통합"][n-2]} 확정 <em class="tg">고도화</em></div>', 'background:#fff;border:1.5px solid #AF947E;font-size:10.5pt;padding:0.06in 0.1in;')
body += box('flowbox card', colx(0), 5.4, cwp, 0.82, '<div><b style="font-size:11pt">현황</b>엑셀·PMS 수작업 관리</div>', 'font-size:10.5pt;padding:0.06in 0.1in;')
body += box('rbar sand', L, 6.4, CW, 0.95, '<span class="lb">확정 후 수정</span><span class="tx">단계 산출물은 스냅샷으로 확정하고, 확정 이후에 수정할 때는 <b>품질 검토를 거치도록</b> 합니다 <em class="tg">고도화</em></span>', 'font-size:13pt')
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

# ---------- 8 AI 활용 구조 ----------
body = ''
fw = [1.55, 2.2, 2.2, 2.0, 1.74]; fg = (CW - sum(fw)) / 4
fl = [('card', '<b>회의록</b>텍스트(.txt)로 업로드<small>회의록 단위로 분석 결과 관리</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>결정사항 추출</b>로컬 LLM 활용<small>1차 생성 후 2차 검증</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>매칭 · 개정안</b>신뢰도 표시<small>원문 발췌와 diff 제시</small>'),
      ('humbox', '<b>PL 검토 · 확정</b>원문과 비교<small>문구 직접 편집, 확정 권한</small>'),
      ('card', '<b>반영과 이력</b>요구사항 내역 반영<small>근거 회의를 이력에 기록</small>')]
x = L
for i, ((cls, txt), w) in enumerate(zip(fl, fw)):
    body += box(f'flowbox {cls}', x, 2.1, w, 1.55, txt)
    if i < 4: body += box('tri', x + w + (fg - 0.12) / 2, 2.72, 0.12, 0.3)
    x += w + fg
cols = [('AI가 하는 일', ['회의록에서 결정사항과 미정사항을 추출', '기존 요구사항과 매칭하고 신뢰도를 표시', '개정안을 기존 문구와 비교해 제시']),
        ('사람(PL)이 하는 일', ['발언 원문 근거를 보고 판단', '개정 문구를 직접 편집', '반영 확정과 이력 기록은 PL이 수행']),
        ('현재 상태와 보완', ['설계 완료, 병렬 검토 화면 구현', 'AI 추출 결과(사전 분석)를 API로 조회', '로컬 LLM 실행 연동 {{보완 필요}}', '구현 방안은 TraceOps 담당 개발자가 작성'])]
cw3 = (CW - 2 * 0.2) / 3
for i, (t, its) in enumerate(cols):
    l = L + i * (cw3 + 0.2)
    body += box('statcol', l, 3.9, cw3, 2.45, f'<div class="st">{e(t)}</div>' + '<ul class="ck sm">' + ''.join(f'<li>{e(a)}</li>' for a in its) + '</ul>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">AI는 추출과 제안까지 맡고, 최종 확정 권한은 PL에게 두어 AI 오판 위험을 통제합니다</span>', 'font-size:13.5pt')
slides.append(frame('AI', 'AI 활용 구조', 'KPI 핵심',
    '<b>AI는 추출과 제안</b>을 맡고 <b>확정은 사람(PL)</b>이 합니다.<br>회의 결정사항을 요구사항에 반영하는 과정에 로컬 LLM을 활용하는 구조입니다.', body, ai=True))

# ---------- 9 업무 흐름 ----------
body = ''
steps = [('o', '요구사항 개정', 'PL', ['회의록 업로드', '결정사항 추출, 요구사항 매칭 {{AI}}', '원문과 비교해 확정'], '요구사항 개정 검토(ReqSync)'),
         ('b', '상세공정 관리', '작업자 · PL', ['분석, 설계, 개발 항목에 요구사항 연결', '계획, 실적, 증적 관리', '단계 간 연결 검증'], '분석 · 설계 · 개발단계'),
         ('t', '테스트 관리', '작업자', ['단위테스트 등록과 수행', '통합테스트로 단위테스트 묶기', '요구사항, 물리ID 자동 연결'], '단위 · 통합테스트'),
         ('o', '연계 관리', 'PL', ['호출구조 기반 AS-IS 연계 조회', 'TO-BE 연계 캔버스 설계', '개발 항목과 연결'], '연계관리, AS-IS 목록')]
sw = 2.31; sg = (CW - 4 * sw) / 3
for i, (c, t, role, acts, scr) in enumerate(steps):
    l = L + i * (sw + sg)
    body += box(f'cbar {c}', l, 2.1, sw, 0.06)
    body += box(f'stp {c}', l, 2.28, sw, 0.25, f'STEP {i+1:02d}')
    body += box('st', l, 2.52, sw, 0.45, e(t))
    body += box(f'rtag {c}', l, 3.05, sw, 0.36, e(role))
    body += box('card', l, 3.5, sw, 2.3)
    body += box('cd', l + 0.2, 3.68, sw - 0.35, 2.1, ''.join(f'<p>{e(a)}</p>' for a in acts), 'font-size:12.5pt')
    body += box('scr', l, 5.92, sw, 0.6, f'<small>관련 화면</small>{e(scr)}')
    if i < 3: body += box('tri', l + sw + 0.1, 4.5, 0.14, 0.24)
body += box('rbar sand', L, 6.65, CW, 0.85, '<span class="lb">기대 효과</span><span class="tx">회의 결정사항이 요구사항으로 이어지고, 같은 기준으로 개발, 테스트, 연계까지 하나의 흐름으로 관리합니다</span>', 'font-size:13pt')
slides.append(frame('구현', '업무 흐름', '단계별 프로세스',
    '회의 결정사항이 요구사항으로 반영되고, 이어서 개발, 테스트, 연계까지 <b>하나의 추적 흐름</b>으로 연결됩니다.<br>PL이 ReqSync로 요구사항을 확정하면 이후 단계가 같은 기준을 따릅니다.', body))

# ---------- 10~14 주요 기능 ----------
slides.append(detail('ReqSync 요구사항 개정 검토', '핵심 기능 1/5',
    '회의 결정사항을 <b>AI가 추출해 요구사항과 매칭</b>하고, 개정안을 원문과 비교해 PL이 확정합니다.<br>좌측은 AI 추출 결과, 우측은 PL 편집으로 나란히 놓은 병렬 검토 화면입니다.',
    'review_modal.png', 1440, 900,
    [dict(t='AI 결정사항 추출과 매칭', d='회의록에서 결정사항을 추출하고 기존 요구사항과 신뢰도, 발언 원문과 함께 제시합니다', zoom=(258, 240, 445, 150), capH=1.2),
     dict(t='AI 개정안과 PL 확정', d='기존 문구 대비 개정안을 diff로 보여 주고, PL이 편집한 뒤 확정합니다', zoom=(739, 472, 445, 150), capH=1.2)],
    [('원문 근거 · 사람 확정', '발언 원문을 보고 PL이 확정, 이력 기록'), ('로컬 LLM 추출', '실행 연동은 구현 방안 작성 후 적용 {{보완 필요}}')],
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
    '매핑 누락을 막고 단계 간 연결을 보장', '상세공정관리 > 분석단계 (설계단계, 개발단계 동일 구조)'))
slides.append(detail('테스트관리', '핵심 기능 4/5',
    '단위테스트와 통합테스트를 <b>요구사항과 개발 항목에 연결</b>하여 관리합니다.<br>통합테스트는 단위테스트를 묶은 것이며, 연결 정보는 묶은 단위에서 자동으로 계산됩니다.',
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
       ('필요한 이유 2', '통합테스트 대상 파악', '연계 프로세스 전체가 동작해야 정상이므로, 어떤 프로세스를 통합테스트해야 하는지 알 수 있음'),
       ('필요한 이유 3', '기간계 외 연계 관리', '채널이 기간계의 어떤 메서드를 호출하는지, AI 기능이 어떤 기간계 호출에 의존하는지 확인')]
for n, (k1, t, d) in enumerate(why):
    l = L + n * (cw3 + 0.2)
    body += box('pcard', l, 4.4, cw3, 1.65, f'<div class="pk">{e(k1)}</div><p style="font-weight:700;font-size:13.5pt">{e(t)}</p><p style="font-size:11pt;color:#555;margin-top:0.04in">{e(d)}</p>')
body += box('rbar sand', L, 6.25, CW, 1.1, '<span class="lb">운영 방식</span><div class="tx" style="font-size:12.5pt;line-height:1.5">PL(메인 설계자)이 프로세스를 설계하고, 하위 메서드는 개발 항목이 되어 개발자별로 배분됩니다.<br>프로세스 단위 통합테스트 연결은 <em class="tg">보완 필요</em></div>')
slides.append(frame('구현', '연계관리란 무엇이고 왜 필요한가', '개념과 필요성',
    '연계관리는 <b>기간계의 메인 프로세스</b>뿐 아니라 <b>채널과 AI Agent 등 기간계 바깥의 연계</b>까지 프로세스로 관리하는 기능입니다.<br>프로세스 안의 메서드가 하나만 빠져도 동작하지 않으므로, 누락을 막고 통합테스트 대상을 파악하기 위해 필요합니다.', body, ai=True))

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
body += box('rbar sand', L, 6.4, CW, 0.95, '<span class="lb">관리 효과</span><span class="tx" style="font-size:12.5pt">세 경우 모두 호출 경로에 빠진 메서드가 없는지 확인하고, <b>어떤 프로세스를 통합테스트해야 하는지</b> 알 수 있습니다.</span>')
slides.append(frame('구현', '연계관리 예시', '기간계 · 채널 · AI Agent',
    '기간계 내부의 <b>메인 프로세스</b>, 채널의 요청, AI Agent의 호출을 모두 <b>프로세스</b>로 관리할 수 있습니다.<br>각 프로세스가 어떤 메서드를 거쳐 응답되는지 보여 주므로 누락 확인과 통합테스트 대상 파악에 활용합니다.', body, ai=True))

slides.append(detail('연계관리 화면', '핵심 기능 5/5',
    '실제 화면에서는 프로세스를 <b>연계 캔버스</b>에 노드와 연결선으로 그려, 메서드 단위로 설계하고 관리합니다.<br>호출구조 정적분석 POC로 추출한 AS-IS 콜트리(클래스·메서드)를 캔버스 노드에 매핑합니다.',
    'linkage_asis.png', 1440, 900,
    [dict(t='연계 프로세스 캔버스', d='업무 흐름을 노드와 연결선으로 그리고 동기·비동기 호출을 구분합니다', zoom=(95, 300, 700, 120)),
     dict(t='AS-IS 콜트리 매핑', d='정적분석으로 추출한 호출구조를 캔버스 노드에 매핑합니다', zoom=(1100, 250, 300, 112), capH=1.2)],
    [('호출구조 기반', '클래스·메서드 호출 관계를 노드와 연결'), ('조회와 설계 분리', 'AS-IS는 조회 전용, TO-BE는 PL이 설계')],
    '프로세스를 메서드 단위로 설계해 개발 누락 방지', '연계관리 > AS-IS 프로세스 (POC 추출 데이터)'))

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
body += box('bs', 4.35, T0 + 0.5, 3.6, 0.3, '표준 라이브러리 기반, 별도 설치 없음')
for k, nm in enumerate(['요구사항', '추적(분석~통합)', 'ReqSync 검토', '연계']):
    body += box('chipw', 4.35 + (k % 2) * 1.82, T0 + 0.9 + (k // 2) * 0.48, 1.7, 0.4, nm, 'font-size:11pt')
body += box('arrl', 8.2, T0 + 1.0, 0.45, 0.02) + box('arrh', 8.6, T0 + 0.93, 0.12, 0.16) + box('alb', 8.0, T0 + 0.6, 0.9, 0.3, 'SQL')
body += box('blk', 8.75, T0, 2.24, BH, '')
body += box('bt', 9.0, T0 + 0.15, 1.9, 0.4, '데이터')
body += box('chipw', 9.0, T0 + 0.7, 1.75, 0.95, '<div>SQLite<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">traceops.db<br>요구사항, 단계별 항목, 연결, 회의·결정사항, 연계</span></div>', 'font-size:12pt')
ay = T0 + BH + 0.2
body += box('flowbox aibox', L, ay, 5.05, 1.0, '<div><b><span class="aitag o sm">AI</span>로컬 LLM 결정사항 추출</b>현재는 사전 분석 결과를 API로 조회, 실행 연동 <em class="tg">보완 필요</em></div>')
body += box('flowbox card', L + 5.24, ay, 5.05, 1.0, '<div><b>호출구조 정적분석 (POC)</b>구현·추출 완료, TraceOps 통합 <em class="tg">보완 필요</em></div>')
body += box('lab', L, 5.45, 4, 0.3, '상용화 시 보완 방향')
comm = [('데이터 저장', 'SQLite를 서버형 DB로 전환하여 동시 접속, 백업 확보'),
        ('인증과 권한', '사내 계정 연동과 서버 측 권한 검증 (현재는 화면의 PL·작업자 미리보기)'),
        ('연계 분석 통합', '호출구조 분석기를 TraceOps에 편입하고 연계 데이터를 자동 적재'),
        ('운영 체계', '배포 자동화, 모니터링, 정기 백업, 보안 점검')]
mw = (CW - 3 * 0.15) / 4
for i, (a, t) in enumerate(comm):
    body += box('mini', L + i * (mw + 0.15), 5.8, mw, 1.55, f'<b>{e(a)}</b><span>{e(t)}</span>')
slides.append(frame('구현', '기술 구성', '시스템 구성',
    '<b>Python 서버와 SQLite</b>로 가볍게 구현하여 별도 설치 없이 실행됩니다.<br>AI 추출과 호출구조 분석은 연동과 통합이 남아 있어 상용화 단계에서 보완합니다.', body))

# ---------- 17 고도화 계획 ----------
body = ''
fut = [('ReqSync · AI 활용', '로컬 LLM 기반 결정사항 추출', '회의록을 올리면 로컬 LLM이 결정사항을 추출하고 요구사항과 매칭하도록 실제로 연동합니다. 구현 방안은 TraceOps 담당 개발자가 작성합니다.', '보완 필요'),
       ('연계관리', '호출구조 정적분석 TraceOps 통합', 'POC로 구현한 호출구조 추출을 TraceOps 안으로 통합하여 연계 데이터를 자동으로 적재합니다.', '보완 필요')]
for i, (tag, t, d, eff) in enumerate(fut):
    y = 2.1 + i * 2.15
    body += box('fut', L, y, 6.4, 1.95, '')
    body += box('', L + 0.3, y + 0.22, 2.4, 0.3, f'<span class="futtag">{e(tag)}</span>')
    body += box('futt', L + 0.3, y + 0.55, 5.8, 0.5, e(t))
    body += box('futd', L + 0.3, y + 1.05, 5.8, 0.8, e(d))
    body += box('outp', L + 4.9, y + 0.2, 1.25, 0.4, e(eff), 'font-size:11pt')
body += box('lab', 7.4, 2.1, 3.5, 0.3, '추가 고도화')
adds = [('채널 · AI Agent 연계 확장', '채널 종류(CM, TM, 콜센터)와 AI Agent를 노드로 구분하여 호출 경로 관리'), ('변경 영향 추적', '변경 영향을 추적해 인터페이스 누락을 사전 차단'), ('수행관리 자동화', '단계말 스냅샷 확정, 제출 산출물 생성, 진척 모니터링, 통합테스트 시나리오 구성')]
for i, (t, d) in enumerate(adds):
    y = 2.55 + i * 1.3
    body += box('sq', 7.4, y + 0.1, 0.1, 0.1)
    body += box('rst', 7.65, y - 0.05, 3.35, 0.4, e(t), 'font-size:14.5pt')
    body += box('rsd', 7.65, y + 0.38, 3.35, 0.75, e(d), 'font-size:12.5pt')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추진 방향</span><span class="tx">AI 추출 연동과 호출구조 분석 통합을 우선 추진하고, 이후 수행관리 자동화로 확대합니다</span>', 'font-size:13.5pt')
slides.append(frame('계획', '고도화 계획', '추후 추진',
    '<b>로컬 LLM 기반 결정사항 추출과 호출구조 분석 통합</b>을 보완하여 AI 활용을 완성하겠습니다.<br>두 과제의 구현 방안은 TraceOps 담당 개발자가 작성하며, 보완 사항은 별도 문서로 전달합니다.', body, ai=True))

# ---------- 18 엔딩 ----------
slides.append(D.ending())

D.write(slides, OUT, 'TraceOps · ReqSync 성과 제출')
