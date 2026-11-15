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
    (2.7, 'Part. 1  개요', [(1, '성과 요약'), (2, 'TraceOps · ReqSync 소개'), (3, '추진 배경'), (4, '목표 및 기대효과')]),
    (4.55, 'Part. 2  AI 활용과 구현 내용', [(5, 'AI 활용 구조'), (6, '업무 흐름'), (7, '주요 기능'), (8, '단계별 화면 및 기술 구성')]),
    (6.45, 'Part. 3  향후 계획', [(9, '고도화 계획')])]))

# ---------- 3 성과 요약 ----------
body = ''
cw = (CW - 3 * 0.2) / 4
sumdata = [('AI', 'ReqSync 요구사항 개정', ['회의록 결정사항 추출, 요구사항 매칭, 개정안 제시를 AI 기반으로 설계', 'AI 추출 결과를 PL이 원문과 비교해 확정하는 검토 화면 구현']),
           ('6단계', '추적 관계 관리 구현', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결', '삭제·변경 시 영향을 안내하고 검토 후 진행']),
           ('POC', '호출구조 연계 분석', ['소스 호출구조(클래스·메서드)를 추출해 연계 데이터 구성', '프로세스별 매핑 현황(N / M)으로 누락 확인']),
           ('정합성', '단계 간 정합성 관리', ['요구사항부터 통합테스트까지 연결을 DB 제약과 검증으로 보장', '상위 변경 시 하위에 재검증 표시, 요구사항 변경 이력 자동 기록'])]
for i, (hero, t, ds) in enumerate(sumdata):
    l = L + i * (cw + 0.2)
    body += box('card', l, 2.1, cw, 3.65)
    body += box('hero', l + 0.25, 2.35, cw - 0.4, 0.7, e(hero))
    body += box('ct16', l + 0.25, 3.15, cw - 0.4, 0.4, e(t), 'font-size:13.5pt')
    body += box('hl-line', l + 0.25, 3.65, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 3.8, cw - 0.45, 1.9, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:11.5pt')
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">다음 단계</span><span class="tx">로컬 LLM 기반 결정사항 추출 연동과 호출구조 분석의 TraceOps 통합을 보완하여 AI 활용을 완성</span>')
slides.append(frame('개요', '성과 요약', 'AI 활용 성과',
    '<b>AI 기반 요구사항 개정 검토(ReqSync)</b>를 포함한 TraceOps로 요구사항부터 연계까지 추적 체계를 구현했습니다.<br>AI 추출은 설계와 검토 화면으로 검증했고, 로컬 LLM 연동과 호출구조 분석 통합은 보완 대상입니다.', body, ai=True))

# ---------- 4 소개 ----------
body = ''
data = [('check', '추적 관리', ['요구사항부터 분석, 설계, 개발, 단위·통합 테스트까지 연결', '삭제·변경 시 영향을 안내하고 하위가 참조 중이면 삭제 차단', '상위 단계의 요구사항과 물리ID를 자동 상속']),
        ('spark', 'ReqSync (AI)', ['회의록 결정사항을 AI가 추출해 요구사항과 매칭', '개정안을 원문과 비교해 PL이 확정', '근거 회의가 변경 이력에 남음']),
        ('stack', '연계 관리', ['프로세스의 메서드가 빠짐없이 준비되었는지 확인', '소스 호출구조(클래스·메서드)를 캔버스에 매핑', 'AS-IS는 조회, TO-BE는 설계'])]
cw = 3.25; gp = (CW - 3 * cw) / 2
for i, (ic, t, ds) in enumerate(data):
    l = L + i * (cw + gp)
    body += box('card', l, 2.1, cw, 3.6, '', 'border:2px solid #F46A25;' if i == 1 else '')
    body += box('', l + 0.3, 2.35, 0.7, 0.7, svg(ICON[ic], 0.7))
    body += box('ct20', l + 0.3, 3.2, cw - 0.6, 0.45, e(t))
    body += box('cd', l + 0.3, 3.8, cw - 0.55, 1.85, ''.join(f'<p>{e(d)}</p>' for d in ds))
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">구성 원칙</span><span class="tx">ReqSync는 TraceOps 안의 요구사항 모듈이며, <b>AI는 추출과 제안</b>까지, <b>확정은 사람</b>이 합니다</span>')
slides.append(frame('개요', 'TraceOps · ReqSync 소개', '플랫폼 구성',
    '<b>요구사항부터 연계까지 추적</b>하는 TraceOps에 <b>AI 요구사항 어시스턴트(ReqSync)</b>를 더한 플랫폼입니다.<br>회의 결정사항이 요구사항에 근거와 함께 반영되고, 하위 단계가 같은 기준을 사용하도록 합니다.', body, ai=True))

# ---------- 5 추진 배경 ----------
body = ''
data4 = [('엑셀 · PMS 이원 관리', ['요구사항, 분석, 설계, 개발, 테스트를 엑셀과 PMS로 나누어 수작업 관리', '단계 간 정합성을 보장하기 어렵고 제출 산출물과도 따로 관리']),
         ('매핑 누락 위험', ['요구사항을 분석, 설계, 개발에 매핑해 관리', '개발 목록을 실수로 삭제하면 요구사항이 어디에도 매핑되지 않아 누락될 수 있음']),
         ('프로세스 단위 연계 누락', ['한 프로세스에 여러 메서드가 있고 담당 개발자가 서로 다름', '메서드 하나가 개발 대상에서 빠지면 프로세스 전체가 동작하지 않음']),
         ('요구사항 상세화와 증적', ['RFP 요구사항은 상세화되어 있지 않아 분석 단계에서 고객사와 협의하며 보완', '보완 근거가 회의록에만 남고 반영은 수작업'])]
cw = (CW - 3 * 0.22) / 4
for i, (t, ds) in enumerate(data4):
    l = L + i * (cw + 0.22)
    body += box('card', l, 2.1, cw, 3.5)
    body += box('idx', l + 0.25, 2.3, 1.2, 0.5, f'{i+1:02d}')
    body += box('ct16', l + 0.25, 2.95, cw - 0.45, 0.6, e(t))
    body += box('hl-line', l + 0.25, 3.58, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 3.72, cw - 0.45, 1.85, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:11.5pt')
imps = [('단계 간 정합성 보장', '요구사항부터 테스트까지 하나의 체계로 관리'), ('검토와 제출에 활용', '단계말 검토와 제출 산출물에 그대로 활용'), ('누락 안내와 증적', '누락 가능성을 안내하고 회의 근거를 이력으로 보존')]
body += box('rbar brown', L, 5.8, CW, 1.3, '<span class="lb">해결 방향</span><div class="imp3">' + ''.join(f'<div>{e(a)}<span>{e(b)}</span></div>' for a, b in imps) + '</div>')
slides.append(frame('개요', '추진 배경', '현행 업무의 불편',
    '엑셀과 PMS로 나누어 수작업 관리하다 보니 <b>요구사항부터 테스트까지 정합성을 보장하기 어렵습니다</b>.<br>정합성이 보장되고, 단계말 검토와 제출 산출물에도 활용할 수 있는 체계가 필요했습니다.', body))

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
         ('연계 관계', '프로세스 안의 메서드 누락을 개인이 확인', '프로세스 단위로 매핑 현황 확인, 누락 표시'),
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
fl = [('card', '<b>회의록</b>텍스트(.txt)로 업로드<small>회의 12건 등록</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>결정사항 추출</b>로컬 LLM 활용<small>1차 생성 후 2차 검증</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>매칭 · 개정안</b>신뢰도 표시<small>원문 발췌와 diff 제시</small>'),
      ('humbox', '<b>PL 검토 · 확정</b>원문과 비교<small>문구 직접 편집, 확정 권한</small>'),
      ('card', '<b>반영과 이력</b>요구사항 내역 반영<small>근거 회의를 이력에 기록</small>')]
x = L
for i, ((cls, txt), w) in enumerate(zip(fl, fw)):
    body += box(f'flowbox {cls}', x, 2.1, w, 1.55, txt)
    if i < 4: body += box('tri', x + w + (fg - 0.12) / 2, 2.72, 0.12, 0.3)
    x += w + fg
cols = [('AI가 하는 일', ['회의록에서 결정사항과 미정사항 추출', '기존 요구사항과 매칭하고 신뢰도 표시', '개정안을 기존 문구와 비교해 제시']),
        ('사람(PL)이 하는 일', ['발언 원문 근거를 보고 판단', '문구를 직접 편집', '반영 확정과 이력 기록은 PL 권한']),
        ('현재 상태와 보완', ['설계 완료, 병렬 검토 화면 구현', 'AI 추출 결과(사전 분석)를 API로 조회', '로컬 LLM 실행 연동 {{보완 필요}}', '구현 방안은 TraceOps 담당 개발자가 작성'])]
cw3 = (CW - 2 * 0.2) / 3
for i, (t, its) in enumerate(cols):
    l = L + i * (cw3 + 0.2)
    body += box('statcol', l, 3.9, cw3, 2.45, f'<div class="st">{e(t)}</div>' + '<ul class="ck sm">' + ''.join(f'<li>{e(a)}</li>' for a in its) + '</ul>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">AI는 추출과 제안까지, 최종 확정 권한은 PL에게 유지하여 AI 오판 위험을 통제</span>', 'font-size:13.5pt')
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
body += box('rbar sand', L, 6.65, CW, 0.85, '<span class="lb">기대 효과</span><span class="tx">회의 결정사항이 요구사항으로 이어지고, 같은 기준으로 개발, 테스트, 연계까지 하나의 추적 흐름으로 관리</span>', 'font-size:13pt')
slides.append(frame('구현', '업무 흐름', '단계별 프로세스',
    '회의 결정사항이 요구사항으로 반영되고, 이어서 개발, 테스트, 연계까지 <b>하나의 추적 흐름</b>으로 연결됩니다.<br>PL이 ReqSync로 요구사항을 확정하면 이후 단계가 같은 기준을 따릅니다.', body))

# ---------- 10~14 주요 기능 ----------
slides.append(detail('ReqSync 요구사항 개정 검토', '핵심 기능 1/6',
    '회의 결정사항을 <b>AI가 추출해 요구사항과 매칭</b>하고, 개정안을 원문과 비교해 PL이 확정합니다.<br>좌측은 AI 추출 결과, 우측은 PL 편집으로 나란히 놓은 병렬 검토 화면입니다.',
    'review_modal.png', 1440, 900,
    [dict(t='AI 결정사항 추출과 매칭', d='회의록에서 결정사항을 추출하고 기존 요구사항과 신뢰도, 발언 원문과 함께 제시합니다', zoom=(258, 240, 445, 150), capH=1.2),
     dict(t='AI 개정안과 PL 확정', d='기존 문구 대비 개정안을 diff로 보여 주고, PL이 편집한 뒤 확정합니다', zoom=(739, 472, 445, 150), capH=1.2)],
    [('원문 근거 · 사람 확정', '발언 원문을 보고 PL이 확정, 이력 기록'), ('로컬 LLM 추출', '실행 연동은 구현 방안 작성 후 적용 {{보완 필요}}')],
    '결정사항의 요구사항 반영을 근거와 함께 관리', '요구사항관리 > ReqSync(요구사항 개정 검토)', ai=True))
slides.append(detail('요구사항 관리와 변경 이력', '핵심 기능 2/6',
    '요구사항을 <b>목록 하나로 관리</b>하고, 변경은 이전 값과 비교한 이력으로 자동 기록합니다.<br>ReqSync 확정 내용도 같은 목록과 이력에 반영됩니다.',
    'req.png', 1440, 900,
    [dict(t='ReqSync 진입과 목록 관리', d='ReqSync 버튼으로 개정 검토에 들어가고 추가, 내보내기, 저장을 합니다', zoom=(1050, 300, 350, 65)),
     dict(t='요구사항 목록과 변경 이력', d='요구사항을 목록으로 관리하며 수정, 삭제 시 이전 값과 비교한 이력이 남습니다', zoom=(40, 420, 440, 120), capH=1.2)],
    [('단일 기준', '분석, 설계, 개발, 테스트가 등록된 목록만 선택'), ('이력 보존', '근거 회의록과 결정사항을 이력에 연결')],
    '요구사항 변경 근거를 이력으로 보존', '상세공정관리 > 요구사항관리'))
slides.append(detail('상세공정관리', '핵심 기능 3/6',
    '분석, 설계, 개발 항목의 <b>계획, 실적, 증적</b>을 한 화면에서 관리합니다.<br>요구사항이 매핑된 항목을 지우거나 바꾸면 <b>영향 범위와 오류 가능성을 안내</b>하고, 사용자가 검토한 뒤 진행합니다.',
    'analysis.png', 1440, 900,
    [dict(t='단계별 항목과 진행 상태', d='항목 ID, 작업자, 진행상태(완료, 지연, 진행중, 미착수)를 조회하고 관리합니다', zoom=(40, 564, 440, 110)),
     dict(t='계획 · 실적과 증적', d='작업자 계획·실적 일자와 증적을 관리하고, 실적 입력 시 증적이 필수입니다', zoom=(661, 488, 440, 125), capH=1.15)],
    [('누락 방지 안내', '삭제·변경 시 영향 범위를 안내하고 검토 후 진행'), ('자동 상속과 검증', '상위 값은 자동 상속, 하위 연결 누락 시 표시')],
    '매핑 누락을 막고 단계 간 연결을 보장', '상세공정관리 > 분석단계 (설계단계, 개발단계 동일 구조)'))
slides.append(detail('테스트관리', '핵심 기능 4/6',
    '단위테스트와 통합테스트를 <b>요구사항과 개발 항목에 연결</b>하여 관리합니다.<br>통합테스트는 단위테스트를 묶은 것이며, 연결 정보는 묶은 단위에서 자동으로 계산됩니다.',
    'integration.png', 1440, 900,
    [dict(t='통합테스트와 묶인 단위테스트', d='통합테스트가 묶은 단위테스트와 연결 개발ID를 한 줄로 보여 줍니다', zoom=(371, 523, 440, 100)),
     dict(t='요구사항 · 물리ID 자동 연결', d='묶인 단위테스트의 요구사항ID와 물리ID가 합집합으로 자동 반영됩니다', zoom=(798, 523, 350, 100))],
    [('자동 연결', '개발ID, 요구사항ID, 물리ID를 묶은 단위에서 계산'), ('변경 영향 안내', '연결 변경과 삭제 시 영향 범위를 팝업으로 안내')],
    '요구사항부터 통합테스트까지 한 줄로 추적', '테스트관리 > 통합테스트'))
# ---------- 연계관리가 필요한 이유 ----------
body = ''
# 프로세스 덩어리와 메서드
body += box('card', L, 2.05, CW, 2.25)
body += box('lab', L + 0.3, 2.15, 6, 0.3, '하나의 프로세스 (예: 인수지침검사)')
mx = L + 0.3; mw = 1.6; mg = 0.24
meths = [('메서드 1', '담당 A', 0), ('메서드 2', '담당 B', 0), ('메서드 3', '담당 C', 1), ('메서드 4', '담당 D', 0)]
for n, (m, o, miss) in enumerate(meths):
    x = mx + n * (mw + mg)
    if miss:
        body += box('flowbox', x, 2.55, mw, 1.1, f'<div><b>{m}</b>{o}<small>개발 대상에서 누락</small></div>', 'background:#fff;border:2px dashed #F46A25;')
    else:
        body += box('flowbox card', x, 2.55, mw, 1.1, f'<div><b>{m}</b>{o}<small>분석·설계·개발 완료</small></div>', 'background:#fff;border:1px solid #E5E0DB;')
    if n < 3: body += box('tri', x + mw + 0.06, 2.95, 0.16, 0.3)
body += box('flowbox', mx + 4 * (mw + mg) - 0.1, 2.55, 2.45, 1.1, '<div><b>프로세스 동작 불가</b>한 메서드만 빠져도 전체가 멈춤</div>', 'background:#FFF0E6;border:2px solid #F46A25;')
body += box('cap', mx, 3.8, CW - 0.6, 0.3, 'PL(메인 설계자)이 프로세스를 설계하고, 하위 메서드는 개발 항목이 되어 개발자별로 배분됩니다', 'text-align:left;')
cw3 = (CW - 2 * 0.2) / 3
why = [('필요한 이유 1', '프로세스는 여러 메서드의 연결', ['담당 개발자가 서로 달라 전체 누락 여부를 한 사람이 파악하기 어려움']),
       ('필요한 이유 2', '한 곳의 누락이 전체 장애', ['분석, 설계, 개발 대상에서 메서드 하나가 빠지면 프로세스가 동작하지 않음']),
       ('필요한 이유 3', '통합테스트는 프로세스 단위', ['연계 관점에서는 프로세스 전체가 끝까지 동작해야 정상으로 판단'])]
for i, (k1, t, ds) in enumerate(why):
    l = L + i * (cw3 + 0.2)
    body += box('pcard', l, 4.5, cw3, 1.2, f'<div class="pk">{e(k1)}</div><p style="font-weight:700">{e(t)}</p><p style="font-size:11pt;color:#555">{e(ds[0])}</p>')
body += box('rbar sand', L, 5.9, CW, 1.45, '<span class="lb">TraceOps 대응</span><div class="tx" style="font-size:12.5pt;line-height:1.5">호출구조(클래스·메서드) 전체를 기준으로 <b>매핑 현황(예: 3 / 6 매핑)</b>을 보여 주고, 매핑되지 않은 메서드와 <b>TO-BE 없음</b>을 표시합니다.<br>개발 항목 기반 캔버스는 <b>개발 완료 현황</b>을 계산합니다. 프로세스와 통합테스트의 직접 연결은 <em class="tg">보완 필요</em></div>')
slides.append(frame('구현', '연계관리가 필요한 이유', '연계 관점',
    '프로세스 안의 <b>메서드 하나만 빠져도 프로세스는 동작하지 않기</b> 때문에, 프로세스 단위로 누락을 확인해야 합니다.<br>통합테스트도 연계 프로세스 전체가 동작하는지로 판단합니다.', body))

slides.append(detail('연계관리 (프로세스 완결성)', '핵심 기능 5/6',
    'AS-IS 프로세스별로 <b>메서드가 얼마나 매핑되었는지</b>를 보여 주어 누락을 한눈에 확인합니다.<br>TO-BE가 없는 프로세스는 별도로 표시해 설계 누락을 막습니다.',
    'linkage_list.png', 1440, 900,
    [dict(t='프로세스별 매핑 현황', d='콜트리 전체 메서드 대비 캔버스에 매핑된 수를 N / M으로 표시합니다 (예: 3 / 3 확정, 0 / 6)', zoom=(40, 364, 700, 115), capH=0.9),
     dict(t='TO-BE 누락 표시', d='TO-BE 프로세스가 없는 AS-IS는 TO-BE 없음으로 표시하고, TO-BE로 복사해 시작합니다', zoom=(40, 438, 700, 42), capH=0.45)],
    [('메서드 단위 확인', '프로세스 전체 메서드의 매핑 여부 확인'), ('설계 누락 방지', 'TO-BE 없음 표시와 복사로 시작')],
    '프로세스 전체가 빠짐없이 준비되었는지 확인', '연계관리 > 프로세스 목록 (AS-IS / TO-BE)', ai=False))

slides.append(detail('연계관리 (캔버스와 콜트리)', '핵심 기능 6/6',
    '업무 흐름을 <b>연계 캔버스</b>에 노드와 연결선으로 그려 공유 자산으로 관리합니다.<br>호출구조 정적분석 POC로 추출한 AS-IS 콜트리(클래스·메서드)를 캔버스 노드에 매핑합니다.',
    'linkage_asis.png', 1440, 900,
    [dict(t='연계 프로세스 캔버스', d='업무 흐름을 노드와 연결선으로 그리고 동기·비동기 호출을 구분합니다', zoom=(95, 300, 560, 120)),
     dict(t='AS-IS 콜트리 매핑', d='정적분석으로 추출한 호출구조를 캔버스 노드에 매핑합니다', zoom=(1100, 250, 300, 112), capH=1.2)],
    [('호출구조 기반', '클래스·메서드 호출 관계를 연계 노드와 연결'), ('조회와 설계 분리', 'AS-IS는 조회 전용, TO-BE는 설계와 저장')],
    '개인 기억의 연계 관계를 공유 자산으로', '연계관리 > AS-IS 프로세스 (POC 추출 데이터)'))

# ---------- 15 단계별 화면 ----------
full = (0, 52, 1440, 832)
slides.append(gallery('상세공정, 테스트, 기준정보까지 <b>같은 화면 체계</b>로 관리합니다.<br>단계마다 동일한 조회, 검색, 저장 방식을 사용해 학습 부담을 줄입니다.', '단계별 화면', '상세공정 · 테스트 · 기준정보',
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
    '<b>Python 서버와 SQLite</b>로 가볍게 구현하여 별도 설치 없이 실행됩니다.<br>AI 추출과 호출구조 분석은 연동·통합 작업이 남아 있어 상용화 단계에서 보완합니다.', body))

# ---------- 17 고도화 계획 ----------
body = ''
fut = [('ReqSync · AI 활용', '로컬 LLM 기반 결정사항 추출', '회의록을 올리면 로컬 LLM이 결정사항을 추출하고 요구사항과 매칭하도록 실제 연동합니다. 구현 방안은 TraceOps 담당 개발자가 작성해야 합니다.', '보완 필요'),
       ('연계관리', '호출구조 정적분석 TraceOps 통합', 'POC로 구현된 호출구조 추출을 TraceOps 안으로 통합하여 연계 데이터를 자동으로 적재합니다.', '보완 필요')]
for i, (tag, t, d, eff) in enumerate(fut):
    y = 2.1 + i * 2.15
    body += box('fut', L, y, 6.4, 1.95, '')
    body += box('', L + 0.3, y + 0.22, 2.4, 0.3, f'<span class="futtag">{e(tag)}</span>')
    body += box('futt', L + 0.3, y + 0.55, 5.8, 0.5, e(t))
    body += box('futd', L + 0.3, y + 1.05, 5.8, 0.8, e(d))
    body += box('outp', L + 4.9, y + 0.2, 1.25, 0.4, e(eff), 'font-size:11pt')
body += box('lab', 7.4, 2.1, 3.5, 0.3, '추가 고도화')
adds = [('연계 기반 우선순위 수립', '연계 관계를 기준으로 개발 우선순위를 자동 제안'), ('변경 영향 추적', '변경 영향을 추적해 인터페이스 누락을 사전 차단'), ('수행관리 자동화', '스냅샷 확정, 산출물 생성, 진척 모니터링, 통합테스트 시나리오 구성')]
for i, (t, d) in enumerate(adds):
    y = 2.55 + i * 1.3
    body += box('sq', 7.4, y + 0.1, 0.1, 0.1)
    body += box('rst', 7.65, y - 0.05, 3.35, 0.4, e(t), 'font-size:14.5pt')
    body += box('rsd', 7.65, y + 0.38, 3.35, 0.75, e(d), 'font-size:12.5pt')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추진 방향</span><span class="tx">AI 추출의 실제 연동과 호출구조 분석 통합을 우선하고, 이후 수행관리 자동화로 확대</span>', 'font-size:13.5pt')
slides.append(frame('계획', '고도화 계획', '추후 추진',
    '<b>로컬 LLM 기반 결정사항 추출과 호출구조 분석 통합</b>을 보완하여 AI 활용을 완성하겠습니다.<br>두 과제의 구현 방안은 TraceOps 담당 개발자가 작성하며, 보완 사항은 별도 문서로 전달합니다.', body, ai=True))

# ---------- 18 엔딩 ----------
slides.append(D.ending())

D.write(slides, OUT, 'TraceOps · ReqSync 성과 제출')
