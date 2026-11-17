# -*- coding: utf-8 -*-
"""ProWin 성과 제출 HTML 생성기. 사용: python3 성과제출/prowin/build_prowin.py -> 성과제출/prowin/성과제출_ProWin.html
공통 부품은 ../tools/deck_lib.py, 디자인 규칙은 ../작성가이드.md 참고."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))   # 공용 라이브러리: 성과제출/tools
import deck_lib as D
from deck_lib import L, CW, ORANGE, e, box, frame, svg, ICON, detail, gallery

OUT = os.path.join(HERE, '성과제출_ProWin.html')
D.configure('shots/')

slides = []

# ---------- 1 표지 ----------
slides.append(D.cover('PROPOSAL MANAGEMENT SYSTEM', 'ProWin<br>제안관리 시스템 성과 보고', '황금빛, 홍건의, 박혜림, 서준혁'))

# ---------- 2 목차 ----------
slides.append(D.contents([
    (2.7, 'Part. 1  개요', [(1, '성과 요약'), (2, 'ProWin 소개'), (3, '추진 배경'), (4, '목표 및 기대효과')]),
    (4.85, 'Part. 2  AI 설계와 구현 내용', [(5, '업무 흐름'), (6, 'AI 활용 설계'), (7, '주요 기능'), (8, '부가 기능 및 기술 구성')]),
    (6.75, 'Part. 3  고도화 계획', [(9, '고도화 계획')])]))

# ---------- 3 성과 요약 ----------
body = ''
cw = (CW - 3 * 0.2) / 4
sumdata = [('AI 도입', 'AI 초안 생성과 사례 추천', ['RFP에서 요구사항과 목차 초안을 로컬 LLM이 만들고 PM이 확정하는 구조를 설계', '요구사항 기준으로 과거 제안서의 유사 사례를 RAG 저장소에서 추천하는 구조를 설계']),
           ('효율화', '제안 업무 화면 구현', ['제안 현황, 일정, 소통, 조견표 등 제안 업무 전반의 화면', '역할별 화면과 권한 구성']),
           ('PoC', '핵심 기능과 기술 검증', ['RFP · 요구사항, 목차, 제안서 검토, 제안서 관리가 데이터 저장과 함께 동작', 'PPT 업로드 시 제목 자동 추출과 목차 연결, 미리보기, 합본의 실현성 검증']),
           ('4단계', '표준 업무 흐름 정립', ['착수, 작성, 검토, 확정 단계별 역할과 화면의 연결', '역할별 업무가 하나의 흐름으로 연결'])]
for i, (hero, t, ds) in enumerate(sumdata):
    l = L + i * (cw + 0.2)
    body += box('card', l, 2.1, cw, 5.2)
    body += box('hero', l + 0.25, 2.55, cw - 0.4, 0.8, e(hero), 'font-size:30pt' if i == 0 else '')
    body += box('ct16', l + 0.25, 3.6, cw - 0.4, 0.45, e(t), 'font-size:14.5pt')
    body += box('hl-line', l + 0.25, 4.2, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 4.4, cw - 0.45, 2.7, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:14pt')
slides.append(frame('개요', '성과 요약', 'AI 설계와 구현 성과',
    '<b>제안 업무 전 과정을 담은 시스템</b>을 구현하고, <b>AI 기반 요구사항 초안 생성과 유사 사례 추천을 설계</b>했습니다.<br>AI는 TraceOps ReqSync에서 구현한 로컬 LLM 방식을 적용하며, 확정은 사람이 맡도록 구성했습니다.', body, ai=True))

# ---------- 3 ProWin 소개 ----------
body = ''
data3 = [('check', '표준 절차', ['제안 전 과정을 표준 절차와 템플릿으로 체계화', '임시 TF와 개인 역량에 의존하는 구조에서 탈피', '목차를 기준으로 진척 관리']),
         ('stack', '자산 라이브러리', ['과거 제안서를 페이지 단위로 적재', '검색과 재활용으로 반복 재작성 제거', '요구사항 기준 유사 사례 추천 설계']),
         ('branch', '버전관리', ['PPT를 올리면 이력(커밋)이 자동으로 보존', '전체 섹션 최신본을 목차 순서로 합본', '합본은 불변 스냅샷으로 관리'])]
cw = 3.25; gp = (CW - 3 * cw) / 2
for i, (ic, t, ds) in enumerate(data3):
    l = L + i * (cw + gp)
    body += box('card', l, 2.1, cw, 3.6)
    body += box('', l + 0.3, 2.35, 0.7, 0.7, svg(ICON[ic], 0.7))
    body += box('ct20', l + 0.3, 3.2, cw - 0.6, 0.45, e(t))
    body += box('cd', l + 0.3, 3.8, cw - 0.55, 1.85, ''.join(f'<p>{e(d)}</p>' for d in ds))
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">운영 원칙</span><span class="tx">작성은 <b>익숙한 PPT와 엑셀</b>로 하고, 시스템은 업로드한 파일의 <b>내용 추출, 미리보기, 이력 관리, 합본</b>으로 제안 과정을 표준화</span>')
slides.append(frame('개요', 'ProWin 소개', '시스템 소개',
    '제안 업무를 <b>사람의 역량이 아닌 표준 절차와 축적된 자산</b>으로 수행하는 제안관리 시스템입니다.<br>제안(Proposal)을 통해 수주(Win)를 이끌어내는 것이 목적입니다.', body))

# ---------- 4 추진 배경 ----------
body = ''
data4 = [('전담 조직 부재', ['RFP(제안요청서)마다 임시 TF를 구성', '매 건 처음부터 반복, 담당자 역량에 따라 품질 좌우']),
         ('수작업 산출물', ['조견표, 합본, 목차를 수작업으로 작성', '작성 오류, 버전 혼선, 마감 리스크 상시 발생']),
         ('자산의 분산과 미활용', ['과거 제안 자산이 개인 단위로 분산', '재활용이 어려워 매 제안마다 재작성']),
         ('구두 중심의 리뷰', ['리뷰와 의사결정이 구두로 진행', '결정 근거가 남지 않아 추적과 인수인계가 어려움'])]
cw = (CW - 3 * 0.22) / 4
for i, (t, ds) in enumerate(data4):
    l = L + i * (cw + 0.22)
    body += box('card', l, 2.1, cw, 3.45)
    body += box('idx', l + 0.25, 2.3, 1.2, 0.5, f'{i+1:02d}')
    body += box('ct16', l + 0.25, 2.95, cw - 0.45, 0.6, e(t))
    body += box('hl-line', l + 0.25, 3.58, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 3.72, cw - 0.45, 1.75, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:12.5pt')
imps = [('표준 절차 확립', '조직과 개인 역량에 의존하지 않는 수행'), ('산출물 처리 체계화', '업로드 기반의 이력 관리와 합본'), ('자산과 기록 중심 운영', '재활용 자산 축적, 근거 기록 기반 의사결정')]
body += box('rbar brown', L, 5.75, CW, 1.3, '<span class="lb">시사점</span><div class="imp3">' + ''.join(f'<div>{e(a)}<span>{e(b)}</span></div>' for a, b in imps) + '</div>')
slides.append(frame('개요', '추진 배경', '현행 제안 업무',
    '현행 제안 업무는 <b>전담 조직과 표준, 시스템 없이 개인 역량과 수작업</b>에 의존하고 있습니다.<br>제안 건수가 늘수록 <b>품질과 생산성이 하락하는 구조</b>입니다.', body))

# ---------- 5 목표 ----------
body = ''
rows5 = [('', '효율화', '제안 전 과정을 표준 절차와 템플릿으로 체계화하여 임시 TF와 개인 역량 의존 구조에서 탈피', '표준 절차 기반 수행 체계'),
         ('b', '자산화', '과거 제안 산출물을 검색과 재활용이 가능한 자산 라이브러리로 축적하여 반복 재작성 제거', '재활용 가능한 제안 자산'),
         ('t', '경쟁력', '소수 인력으로 제안 품질을 유지하고 제안 투입 인건비 절감', '제안 경쟁력 강화')]
for i, (c, t, d, r) in enumerate(rows5):
    y = 2.1 + i * 1.45
    if i: body += box('rowline', L, y - 0.08, CW, 0.01)
    body += box(f'big {c}', L, y + 0.25, 1.2, 0.7, f'{i+1:02d}')
    body += box('vrule', 2.0, y + 0.12, 0.01, 0.95)
    body += box('rt', 2.3, y + 0.05, 5.5, 0.5, e(t))
    body += box('rd', 2.3, y + 0.55, 5.5, 0.85, e(d))
    body += box('outp', 8.15, y + 0.3, 2.84, 0.6, e(r))
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">실현 방안</span><span class="tx">표준 절차, 버전관리, 자산 라이브러리로 목표를 구현하고, AI 초안 생성과 유사 사례 추천으로 확장하도록 설계했습니다</span>', 'font-size:13.5pt')
slides.append(frame('개요', '목표', '효율화 · 자산화 · 경쟁력',
    '제안 수행 체계를 <b>효율화, 자산화, 경쟁력 확보</b>의 세 방향으로 전환하는 것이 목표입니다.<br>제안을 ‘사람 수’가 아닌 <b>‘축적된 자산과 표준 절차’</b>로 수행합니다.', body))

# ---------- 6 기대효과 ----------
body = box('colh', 2.15, 2.0, 3.9, 0.3, '<span style="color:#8a8a8a">도입 전</span>')
body += box('colh', 6.6, 2.0, 4.39, 0.3, f'<span style="color:{ORANGE}">도입 후</span>')
rows6 = [('수행 방식', '임시 TF 구성, 담당자 역량에 따른 품질 편차', '표준 절차와 템플릿 기반 수행, 목차 기준 진척 관리'),
         ('산출물', '조견표, 합본, 목차의 수작업 작성과 버전 혼선', 'PPT 업로드 기반 이력 관리, 목차 순서 합본 자동 생성'),
         ('자산', '개인 단위 분산, 재활용 불가', '자산 라이브러리 축적, 검색과 재활용'),
         ('의사결정', '구두 중심, 결정 근거 미기록', '리뷰 코멘트와 변경 이력으로 근거 기록')]
for i, (k, a, b) in enumerate(rows6):
    t = 2.4 + i * 1.3
    body += box('cat', L, t, 1.35, 1.15, e(k))
    body += box('pan as', 2.15, t, 3.9, 1.15, e(a))
    body += box('tri', 6.12, t + 0.42, 0.3, 0.32)
    body += box('pan tb', 6.6, t, 4.39, 1.15, e(b))
slides.append(frame('개요', '기대효과', '도입 전후 비교',
    'ProWin 도입으로 제안 수행이 <b>개인 의존에서 표준 절차와 축적 자산 기반</b>으로 바뀝니다.<br>수행 방식, 산출물, 자산, 의사결정 네 영역에서 변화가 나타납니다.', body))

# ---------- 7 업무 흐름 ----------
body = ''
steps = [('o', '제안 착수', 'PM · 사업관리', ['RFP 정보와 요구사항 등록', '제안 일정 등록', '커뮤니케이션 관리 (공지, Q&A)'], 'RFP, 제안 일정, 커뮤니케이션'),
         ('b', '제안서 작성', '작업자', ['요구사항과 목차를 기준으로 작성 범위 확인', '자산 라이브러리의 자료를 참고하여 작성', '작성본을 제안서 관리에 업로드'], '자산 라이브러리, 제안서 관리'),
         ('t', '제안서 검토', '제안 참여 인원 전원', ['제안서 검토 화면에서 슬라이드 확인', '슬라이드별 검토 의견 등록', '의견 이력으로 결정 근거 기록'], '제안서 검토'),
         ('o', '최종 확정', 'PM · 사업관리', ['최종본 합본 생성', '목차와 조견표 검토', '제출본 확정'], '제안서 관리, 목차, 조견표')]
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
body += box('rbar sand', L, 6.65, CW, 0.85, '<span class="lb">기대 효과</span><span class="tx">요구사항 기준의 일정과 소통 일원화, 과거 사례 참조 기반 작성, 업로드만으로 이력과 합본 처리, 의견 기록의 축적</span>', 'font-size:13pt')
slides.append(frame('구현', '업무 흐름', '역할별 프로세스',
    'RFP 접수부터 최종 합본까지 <b>역할별 업무가 하나의 흐름으로 연결</b>됩니다.<br>PM·사업관리가 제안을 열고, 작업자가 작성하고, 참여 인원 전원이 검토한 뒤 PM·사업관리가 확정합니다.', body))

# ---------- 설계 ① AI 초안 생성 ----------
body = ''
fw = 1.8; fg = (CW - 5 * fw) / 4
fl = [('card', '<b>RFP 업로드</b>PDF 텍스트와 표 추출<small>구간을 나누어 분석</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>후보 추출</b>요구사항 표 파싱, LLM 추출<small>근거 페이지와 원문 인용</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>2차 검증</b>요구 여부, 복합 요구 확인<small>필수·권고 강도 보정</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>목차 배치</b>지정 목차에 요구사항 배치<small>조견표 초안 생성</small>'),
      ('humbox', '<b>PM 검토 · 확정</b>채택, 제외, 수정<small>확정 권한은 PM</small>')]
for i, (cls, txt) in enumerate(fl):
    x = L + i * (fw + fg)
    body += box(f'flowbox {cls}', x, 2.1, fw, 1.55, txt)
    if i < 4: body += box('tri', x + fw + (fg - 0.12) / 2, 2.72, 0.12, 0.3)
body += box('lab', L, 3.9, 6, 0.3, '로컬 LLM 스펙')
chips = [('실행 도구', 'Ollama', 'MIT 라이선스, 무료'), ('모델', 'Qwen3', 'Apache 2.0, 상업 사용 무료'),
         ('호출 규격', 'OpenAI 호환 API', 'vLLM 등 다른 서버와 호환'), ('적용 방식', 'ProWin 서버 연동', 'Spring Boot 서버에서 직접 호출')]
tw = (CW - 3 * 0.2) / 4
for i, (c, v, sub) in enumerate(chips):
    body += box('tchip', L + i * (tw + 0.2), 4.25, tw, 1.0, f'<div class="tcat">{e(c)}</div><div class="tval">{e(v)}</div><div style="font-size:10.5pt;color:#6B6B6B;margin-top:0.03in">{e(sub)}</div>')
mw2 = (CW - 0.2) / 2
body += box('mini', L, 5.38, mw2, 1.05, '<b>초안 생성이 해결하는 일</b><span>RFP를 읽고 요구사항을 정리하는 수작업을 줄이고, 근거 페이지와 함께 후보를 제시합니다</span>')
body += box('mini', L + mw2 + 0.2, 5.38, mw2, 1.05, '<b>지정 목차 보호</b><span>RFP가 지정한 제안서 목차는 잠금 상태로 유지하고, 신규 세부 목차만 AI가 제안합니다</span>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">AI는 초안까지 맡고 채택과 확정은 PM과 사업관리가 하며, 재분석을 해도 확정한 항목은 유지됩니다</span>', 'font-size:13.5pt')
slides.append(frame('설계', '요구사항·목차 초안 자동 생성 설계', 'AI 초안 생성',
    'RFP를 올리면 <b>AI가 요구사항과 목차 초안을 만들고 PM이 확정</b>하도록 설계했습니다.<br>TraceOps ReqSync에서 구현한 로컬 LLM 방식(추출, 2차 검증, 확정은 사람)을 같은 구조로 적용합니다.', body, ai=True))

# ---------- 설계 ② 요구사항 목차 장표 연결 ----------
body = ''
gap2 = 0.55
cw3 = (CW - 2 * gap2) / 3
cols = [('STEP 01 · 요구사항', 'RFP 요구사항', False, ['RFP에서 추출한 요구사항 후보를 PM이 확정', '근거 페이지와 원문을 함께 보존']),
        ('STEP 02 · 목차', '요구사항 목차 배치', True, ['요구사항을 답변할 세부 목차에 배치', '예상 장수를 계산하고 신규 세부 목차를 제안']),
        ('STEP 03 · 장표', '요구사항 장표 매핑', True, ['업로드한 PPT에서 요구사항에 답하는 슬라이드를 판정', '합본 기준 쪽번호로 환산'])]
for i, (stp, t, ai_, ds) in enumerate(cols):
    x = L + i * (cw3 + gap2)
    body += box('card', x, 2.1, cw3, 2.6)
    body += box('cbar o', x, 2.1, cw3, 0.06)
    body += box('stp o', x + 0.25, 2.32, cw3 - 0.4, 0.25, e(stp))
    body += box('ct16', x + 0.25, 2.65, cw3 - 0.4, 0.4, ('<span class="aitag o sm">AI</span>' if ai_ else '') + e(t), 'font-size:16pt')
    body += box('hl-line', x + 0.25, 3.2, cw3 - 0.5, 0.01)
    body += box('cd', x + 0.25, 3.35, cw3 - 0.4, 1.3, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:12.5pt;line-height:1.4')
    if i < 2: body += box('tri', x + cw3 + (gap2 - 0.14) / 2, 3.25, 0.14, 0.3)
mw3 = (CW - 2 * 0.2) / 3
minis = [('조견표 쪽수 자동 채움', '요구사항별 답변 쪽번호를 수작업 없이 조견표에 반영합니다'),
         ('미답변 요구사항 감지', '목차별 미답변 요구사항을 알리고, 필수 요구사항은 지연 항목으로 표시합니다'),
         ('TraceOps 연계', '수주 후 확정 요구사항을 RFP 코드와 페이지 출처와 함께 TraceOps 요구사항으로 내보냅니다')]
for i, (t, d) in enumerate(minis):
    body += box('mini', L + i * (mw3 + 0.2), 4.95, mw3, 1.4, f'<b>{e(t)}</b><span>{e(d)}</span>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추적 체계</span><span class="tx">제안 단계의 요구사항이 목차와 장표를 거쳐 <b>수행 단계의 요구사항으로 이어지는 하나의 흐름</b>으로 관리합니다</span>', 'font-size:13.5pt')
slides.append(frame('설계', '요구사항·목차·장표 연결 설계', '조견표 자동화',
    '요구사항이 <b>어느 목차에 배치되고 어느 장표에서 답변되는지</b>를 연결해 누락을 사전에 확인하도록 설계했습니다.<br>조견표 쪽수를 자동으로 채우고, 수주 후에는 확정 요구사항을 TraceOps로 이어줍니다.', body, ai=True))

# ---------- 설계 ③ 유사 사례 추천 (RAG) ----------
body = ''
fl = [('card', '<b>과거 제안서 PPT</b>슬라이드 단위로 분해<small>제목, 본문, 미리보기, 출처</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>RAG 저장소</b>임베딩으로 의미 검색 구성<small>연도, 부문, 수주 여부 포함</small>'),
      ('card', '<b>요구사항 질의</b>요구사항 제목과 설명으로 검색<small>RFP · 요구사항 화면</small>'),
      ('aibox', '<b><span class="aitag o sm">AI</span>사례 추천</b>상위 슬라이드와 출처 제시<small>유사도와 한 줄 요약</small>'),
      ('humbox', '<b>작성자 활용</b>참고 슬라이드 열기<small>요구사항에 연결, 유용 여부 기록</small>')]
for i, (cls, txt) in enumerate(fl):
    x = L + i * (fw + fg)
    body += box(f'flowbox {cls}', x, 2.1, fw, 1.55, txt)
    if i < 4: body += box('tri', x + fw + (fg - 0.12) / 2, 2.72, 0.12, 0.3)
body += box('lab', L, 3.9, 6, 0.3, '검색 구성')
chips = [('검색 1단계', '키워드 · 메타 검색', '연도, 부문, 수주 여부 필터'), ('검색 2단계', '의미 검색', '표현이 달라도 유사한 사례 검색'),
         ('검색 3단계', '결합과 재정렬', 'AI가 요구사항 적합 여부를 재판정'), ('접근 제어', '비밀 등급 관리', '제안별, 등급별로 노출 범위 제한')]
for i, (c, v, sub) in enumerate(chips):
    body += box('tchip', L + i * (tw + 0.2), 4.25, tw, 1.0, f'<div class="tcat">{e(c)}</div><div class="tval" style="font-size:13.5pt">{e(v)}</div><div style="font-size:10.5pt;color:#6B6B6B;margin-top:0.03in">{e(sub)}</div>')
body += box('mini', L, 5.38, mw2, 1.05, '<b>자산화 목표와 연결</b><span>개인 단위로 흩어진 과거 제안서를 검색 가능한 자산으로 축적하고 새 제안에 재활용합니다</span>')
body += box('mini', L + mw2 + 0.2, 5.38, mw2, 1.05, '<b>고객 자료 보호</b><span>고객사별 비밀 등급과 접근 제어를 적용하고, 모델과 저장소는 사내 환경에서 실행합니다</span>')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">운영 원칙</span><span class="tx">추천은 작성 참고 자료로 제시하고, 채택 여부는 작성자가 판단하며 유용 여부 기록으로 정확도를 높입니다</span>', 'font-size:13.5pt')
slides.append(frame('설계', '유사 사례 추천 설계', 'RAG 저장소',
    '과거 제안서를 <b>슬라이드 단위의 RAG 저장소</b>로 구축해 요구사항별 유사 사례를 추천하도록 설계했습니다.<br>키워드 검색에서 의미 검색, AI 재정렬까지 단계로 구성하며, 비밀 등급에 따라 노출 범위를 제한합니다.', body, ai=True))


slides.append(detail('RFP · 요구사항 관리', '핵심 기능 1/4',
    'RFP(제안요청서)와 요구사항을 <b>한 화면에서 정리</b>하고, 요구사항별로 <b>과거 제안 사례를 추천</b>받습니다.<br>RFP 문서 정보와 요구사항 목록을 등록하고, 이후 목차와 조견표 작업의 기준으로 활용합니다.',
    'rfp_ai.png', 1440, 900,
    [dict(t='요구사항 목록', d='RFP 문서 정보와 함께 코드, 제목, 설명 단위로 등록, 수정, 삭제하며 삭제 사유는 이력으로 남깁니다', zoom=(255, 370, 440, 135), capH=1.0),
     dict(t='유사 사례 추천', d='요구사항을 선택하면 과거 제안서의 유사 슬라이드를 관련도와 함께 제시합니다', zoom=(839, 312, 565, 168), padx=0, pady=0, capH=1.4)],
    [('기준 일원화', 'RFP 문서와 요구사항을 한 화면에서 관리'), ('사례 추천', '요구사항별 과거 제안 사례를 관련도와 함께 제시')],
    '요구사항 기준 관리와 사례 재활용', '제안 워크스페이스 > RFP / 요구사항  ·  시연용 예시 데이터', ai=True))
slides.append(detail('목차 관리', '핵심 기능 2/4',
    '<b>목차 하나로 담당자와 진척 상태</b>를 일원화합니다.<br>세부 목차가 PPT 업로드와 검토의 단위가 되어 모든 화면이 목차로 연결됩니다.',
    'toc.png', 1440, 900,
    [dict(t='목차 구성', d='대분류와 세부 목차를 구분하며 세부 목차가 업로드와 검토의 단위입니다', zoom=(255, 562, 420, 112), capH=1.1),
     dict(t='담당과 진척 현황', d='담당자, 예상 장수, 상태(완료, 진행중, 보완)를 한눈에 관리합니다', zoom=(715, 562, 400, 112), capH=1.1)],
    [('화면 연결', '세부 목차가 업로드와 검토의 단위'), ('즉시 갱신', '담당, 장수, 상태를 목차에서 수정')],
    '진척 현황을 목차 한 화면에서 확인', '제안 워크스페이스 > 목차  ·  시연용 예시 데이터'))
_rv = (detail('제안서 검토', '핵심 기능 3/4',
    '슬라이드를 보며 <b>참여 인원 전원이 의견을 남기고</b> 결정 근거를 기록합니다.<br>업로드한 PPT의 제목과 핵심 내용이 검토 화면에 자동으로 반영됩니다.',
    'review_t.png', 1440, 1000,
    [dict(t='슬라이드 미리보기', d='업로드한 PPT의 제목과 핵심 내용이 자동으로 반영됩니다', zoom=(583, 556, 512, 172), capH=1.05),
     dict(t='리뷰 코멘트', d='작성자별 의견을 일시와 함께 남겨 결정 근거를 보존합니다', zoom=(583, 852, 520, 132), capH=1.05)],
    [('자동 반영', 'PPT의 제목과 핵심 내용을 자동 반영'), ('의견 기록', '작성자와 일시를 남기고 발표 자료 지정')],
    '구두 중심 리뷰를 기록 중심으로 전환', '제안 워크스페이스 > 제안서 검토  ·  시연용 예시 데이터'))
# 제출 전 삭제: 화면 교체 안내 도형 (SHOW_REPLACE_MARK = False 로 끄면 사라진다)
SHOW_REPLACE_MARK = True
if SHOW_REPLACE_MARK:
    _rv = _rv.replace('</section>', box('', 8.3, 0.38, 2.7, 0.7, '사진 교체 필요<br>홍건의 프로 화면 교체 필요', 'border:2px dashed #D92D20;color:#D92D20;font-weight:700;font-size:11pt;line-height:1.35;text-align:center;display:flex;align-items:center;justify-content:center;background:#FFF1F0;border-radius:0.08in') + '</section>')
slides.append(_rv)
slides.append(detail('제안서 관리 (버전 · 합본)', '핵심 기능 4/4',
    '<b>PPT 업로드만으로 이력이 쌓이고 합본이 자동으로 완성</b>됩니다.<br>세부 목차별 최신본이 목차 순서대로 묶여 하나의 제안서가 됩니다.',
    'versions.png', 1440, 900,
    [dict(t='업로드와 합본', d='세부 목차 단위로 PPT를 올리고, 합본으로 전체 제안서를 만듭니다', zoom=(246, 206, 440, 80)),
     dict(t='버전 이력(커밋)', d='누가 언제 어떤 목차를 올렸는지 이력으로 남고, 합본은 변경 불가한 스냅샷으로 보관합니다', zoom=(256, 480, 372, 108))],
    [('이력 추적', '업로드마다 누가 언제 올렸는지 기록'), ('스냅샷 보관', '목차 순서 합본을 변경 불가로 보관')],
    '수작업 합치기와 버전 혼선 해소', '제안 워크스페이스 > 제안서 관리  ·  시연용 예시 데이터'))


full = (220, 52, 1220, 748)
slides.append(gallery('핵심 기능 외에도 <b>제안 업무 전반을 지원하는 화면</b>을 갖추고 있습니다.<br>진행 현황, 일정, 소통, 조견표, 자산 라이브러리를 하나의 메뉴 체계로 제공합니다.', '부가 기능 (1/2)', '진행 · 소통 · 자산',
    [('제안 현황', '기간별 제안 진행 현황', 'proposals.png', full), ('제안서 홈', '제안 개요, 오늘 할 일, 지연 항목', 'home.png', full),
     ('제안 일정', '일정 등록과 색상 구분', 'schedule.png', full), ('커뮤니케이션', '제안팀 공지, 공유 게시판', 'comm.png', full),
     ('RFP Q&A, 참고 자료', '제안 전용 게시판', 'board-1.png', full), ('조견표', '요구사항과 목차 매핑', 'matrix.png', full),
     ('자산 라이브러리', '과거 제안서 페이지 적재, 검색', 'assets.png', (470, 212, 340, 240)), ('워크스페이스 관리', '제안 전용 게시판 관리', 'workspace.png', full)], 4, 2, 1.8))
slides.append(gallery('<b>비용, 인력, 권한, 이력</b>까지 하나의 시스템에서 관리합니다.<br>경비와 공수, 제안·시스템 단위 권한, 변경 이력을 제공합니다.', '부가 기능 (2/2)', '비용 · 권한 · 운영',
    [('제안 경비 관리', '자사, 외주 인건비, 디자인·인쇄비', 'expense.png', full), ('수행 공수 관리', '투입 M/M, 직급별 공수', 'effort.png', full),
     ('제안 권한관리', '제안 단위 멤버와 권한', 'wsperm.png', full), ('시스템 접근 권한관리', '프로젝트와 무관한 시스템 권한', 'sysperm.png', full),
     ('사용 가이드', '사이트 사용법 통합 안내', 'guide.png', full), ('변경 이력', '추가, 수정, 삭제 이력', 'history.png', full)], 3, 2, 1.85))

# ---------- 14 기술 구성 ----------
body = ''
T0 = 2.0; BH = 2.3
body += box('blk', L, T0, 2.5, BH, '')
body += box('', L + 0.3, T0 + 0.25, 0.55, 0.55, svg(ICON['window'], 0.55))
body += box('bt', L + 0.3, T0 + 0.95, 2.0, 0.4, '사용자 브라우저')
body += box('bs', L + 0.3, T0 + 1.4, 2.0, 0.6, 'HTML, CSS, JavaScript')
body += box('arrl', 3.3, T0 + 1.15, 0.6, 0.02) + box('arrh', 3.86, T0 + 1.08, 0.12, 0.16) + box('alb', 3.1, T0 + 0.75, 1.0, 0.3, 'REST API')
body += box('blk sd', 4.05, T0, 4.1, BH, '')
body += box('bt', 4.35, T0 + 0.15, 3.6, 0.4, 'ProWin Backend')
body += box('bs', 4.35, T0 + 0.55, 3.6, 0.3, 'Spring Boot 3.3 · Java 17')
for k, nm in enumerate(['RFP', '목차', '검토', '버전관리']):
    body += box('chipw', 4.35 + (k % 2) * 1.82, T0 + 0.95 + (k // 2) * 0.5, 1.7, 0.42, nm)
body += box('chipw', 4.35, T0 + 1.92, 3.52, 0.34, 'PPTX 추출, 미리보기, 합본 (Apache POI)', 'font-size:10.5pt')
body += box('arrl', 8.2, T0 + 1.15, 0.45, 0.02) + box('arrh', 8.6, T0 + 1.08, 0.12, 0.16) + box('alb', 8.0, T0 + 0.75, 0.9, 0.3, 'JDBC')
body += box('blk', 8.75, T0, 2.24, BH, '')
body += box('bt', 9.0, T0 + 0.15, 1.9, 0.4, '저장소')
body += box('chipw', 9.0, T0 + 0.7, 1.75, 0.62, '<div>SQLite<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">RFP, 목차, 리뷰, 이력</span></div>')
body += box('chipw', 9.0, T0 + 1.45, 1.75, 0.62, '<div>파일 저장소<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">업로드 PPTX</span></div>')
body += box('lab', L, 4.5, 3, 0.3, '기술 스택')
tech = [('프론트엔드', 'HTML, CSS, JavaScript'), ('백엔드', 'Spring Boot 3.3.5'), ('언어', 'Java 17'), ('데이터', 'SQLite (JDBC)'), ('문서 처리', 'Apache POI 5.3.0')]
tw = (CW - 4 * 0.13) / 5
for i, (c, v) in enumerate(tech):
    body += box('tchip', L + i * (tw + 0.13), 4.82, tw, 0.8, f'<div class="tcat">{e(c)}</div><div class="tval" style="font-size:12pt">{e(v)}</div>')
body += box('lab', L, 5.8, 6, 0.3, 'PPT 처리 흐름')
pf = [('업로드', '세부 목차 단위로 PPT 등록'), ('내용 추출', '제목과 핵심 내용 추출'), ('미리보기', '슬라이드 이미지 생성'),
      ('이력 저장', '커밋으로 버전 보존'), ('합본', '목차 순서 스냅샷 생성')]
fw = 1.9; fg = (CW - 5 * fw) / 4
for i, (a, t) in enumerate(pf):
    x = L + i * (fw + fg)
    body += box('flowbox card', x, 6.15, fw, 1.2, f'<b>{e(a)}</b>{e(t)}')
    if i < 4: body += box('tri', x + fw + (fg - 0.12) / 2, 6.62, 0.12, 0.26)
slides.append(frame('구현', '기술 구성', '시스템 구성',
    '<b>단일 서버</b>가 화면과 API를 함께 제공하여 가볍게 구축했습니다.<br>업로드한 PPT는 추출, 미리보기, 이력 저장, 합본까지 서버에서 처리합니다.', body))

# ---------- 15 고도화 계획 ----------
body = ''
fut = [('설계 ①', 'AI 요구사항·목차 초안 생성 구현', 'RFP에서 요구사항과 목차 초안을 로컬 LLM으로 생성하고, PM이 검토하여 확정하는 기능을 구현합니다.'),
       ('설계 ②', '요구사항·목차·장표 연결 구현', 'PPT 장표와 요구사항을 매핑해 조견표 쪽수를 자동으로 채우고, 미답변 요구사항을 알립니다.'),
       ('설계 ③', '유사 사례 추천(RAG) 구현', '과거 제안서를 슬라이드 단위로 적재한 저장소를 구축하고, 요구사항별 유사 사례를 추천합니다.')]
for i, (tag, t, d) in enumerate(fut):
    y = 2.1 + i * 1.45
    body += box('fut', L, y, 6.4, 1.33, '')
    body += box('', L + 0.3, y + 0.12, 2.4, 0.3, f'<span class="futtag">{e(tag)}</span>')
    body += box('futt', L + 0.3, y + 0.42, 5.8, 0.4, e(t), 'font-size:15pt')
    body += box('futd', L + 0.3, y + 0.82, 5.8, 0.5, e(d), 'font-size:11pt;line-height:1.3')
body += box('lab', 7.4, 2.1, 3.5, 0.3, '추가 고도화')
adds = [('경비, 공수 자동 합계', '입력값을 항목별, 전체 합계로 자동 계산'),
        ('데이터 연동과 권한 정비', '전 화면 데이터 연동 확대, 권한 체계 정비'), ('상용화 기반 보완', '서버형 DB, 사내 계정 연동, 파일 스토리지, 운영 체계')]
for i, (t, d) in enumerate(adds):
    y = 2.55 + i * 1.3
    body += box('sq', 7.4, y + 0.1, 0.1, 0.1)
    body += box('rst', 7.65, y - 0.05, 3.35, 0.4, e(t), 'font-size:14.5pt')
    body += box('rsd', 7.65, y + 0.38, 3.35, 0.75, e(d), 'font-size:12pt;line-height:1.3')
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추진 방향</span><span class="tx">설계를 마친 AI 초안 생성과 유사 사례 추천을 구현하여 제안 업무 전 과정에 적용합니다</span>', 'font-size:13.5pt')
slides.append(frame('계획', '고도화 계획', 'AI 설계 구현',
    '<b>설계를 마친 AI 초안 생성, 요구사항 연결, 유사 사례 추천을 구현</b>하여 제안 작성 업무의 효율을 높이겠습니다.<br>업무 흐름의 요구사항 등록과 작성 단계에 적용하며, 상용화를 위한 기반 보완도 함께 추진합니다.', body))


# ---------- 16 엔딩 ----------
slides.append(D.ending())

D.write(slides, OUT, 'ProWin 성과 제출')
