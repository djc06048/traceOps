# -*- coding: utf-8 -*-
"""ProWin 성과 제출 HTML 생성기. 사용: python3 tools/build_prowin.py  → ../성과제출_ProWin.html
좌표는 작성가이드.md 의 inch 절대좌표 규칙을 따른다."""
import os, html
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '성과제출_ProWin.html')
SH = 'shots/prowin/'
LABEL = '한화시스템 내부 보고 ( ProWin )'

def e(s): return html.escape(s, quote=False)
def I(v): return f'{v:.3f}in'
def box(cls, l, t, w=None, h=None, inner='', style=''):
    s = f'left:{I(l)};top:{I(t)};'
    if w is not None: s += f'width:{I(w)};'
    if h is not None: s += f'height:{I(h)};'
    return f'<div class="a {cls}" style="{s}{style}">{inner}</div>'

PAGE = [0]
def frame(num, title, lead, body):
    PAGE[0] += 1
    h = '<section class="slide">'
    h += '<div class="topband"></div><div class="diag"></div>'
    h += box('lbl', 1.53, 0.40, 6, 0.2, e(LABEL))
    h += box('pnum', 0.80, 0.51, 0.7, 0.61, f'{num:02d}')
    h += box('ptitle', 1.49, 0.63, 8, 0.5, e(title))
    if lead: h += box('lead', 0.65, 1.31, 10.39, 0.55, lead)
    h += body
    h += '<div class="fline"></div>'
    h += box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved')
    h += box('pgno', 5.45, 7.90, 0.79, 0.16, f'- {PAGE[0]} -')
    h += '<img class="a flogo" src="assets/logo-footer.png" alt="한화시스템">'
    return h + '</section>'

def bullets(items, cls=''):
    return f'<ul class="bl {cls}">' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>'

def card(l, t, w, hh, bh, head, items, color='o1', dark=False):
    h = box(f'bar {color}' + (' dk' if dark else ''), l, t, w, hh, e(head))
    h += box('cbody', l, t + hh, w, bh, bullets(items))
    return h

# ---------- 확대(zoom) 부품 ----------
def zoom(img, W, H, reg, width, num=None):
    x, y, w, h = reg
    s = width / w
    ph = h * s
    st = (f'background-image:url({SH}{img});background-size:{I(W*s)} {I(H*s)};'
          f'background-position:-{I(x*s)} -{I(y*s)};')
    badge = f'<i class="bd">{num}</i>' if num else ''
    return ph, (lambda l, t: box('zoom', l, t, width, ph, badge, st))

def shotbox(img, W, H, height, regs, l, t):
    w = height * W / H
    inner = f'<img src="{SH}{img}" alt="">'
    for i, (x, y, rw, rh) in enumerate(regs, 1):
        inner += (f'<i class="hl" style="left:{x/W*100:.2f}%;top:{y/H*100:.2f}%;'
                  f'width:{rw/W*100:.2f}%;height:{rh/H*100:.2f}%"><b>{i}</b></i>')
    return w, box('shot', l, t, w, height, inner)

def chips(steps, l, t, w):
    n = len(steps); gap = 0.28
    cw = (w - gap * (n - 1)) / n
    h = ''
    for i, s in enumerate(steps):
        x = l + i * (cw + gap)
        h += box('chip', x, t, cw, 0.78, f'<span>{i+1}</span>{e(s)}')
        if i < n - 1: h += box('arr', x + cw, t + 0.22, gap, 0.3, '▶')
    return h

def detail(num, title, lead, img, W, H, regs, zooms, feats, steps, row1_side=None, panel_h=None):
    """zooms: [(region, width)] 같은 높이로 맞춰 가로 나열"""
    body = ''
    t1 = 1.95
    x = 0.65; maxh = 0
    for i, (reg, wd) in enumerate(zooms, 1):
        ph, fn = zoom(img, W, H, reg, wd, i)
        body += fn(x, t1); x += wd + 0.2; maxh = max(maxh, ph)
    if row1_side:
        body += box('side', x, t1, 10.39 + 0.65 - x, maxh, row1_side)
    t2 = t1 + maxh + 0.22
    sh_h = min(7.52 - t2, 3.2)
    sw, sh = shotbox(img, W, H, sh_h, regs, 0.65, t2)
    body += sh
    rx = 0.65 + sw + 0.3; rw = 11.04 - rx
    if row1_side:
        body += box('side', rx, t2, rw, 1.55, '<div class="sh">이 화면에서 할 수 있는 일</div>' + bullets(feats))
    else:
        body += box('side', rx, t2, rw, 1.55, '<div class="sh">이 화면에서 할 수 있는 일</div>' + bullets(feats))
    body += box('sh2', rx, t2 + 1.62, rw, 0.25, '업무 흐름')
    body += chips(steps, rx, t2 + 1.95, rw)
    return frame(num, title, lead, body)

def grid(num, title, lead, items, cols, rows, img_h):
    body = ''
    gap = 0.2
    cw = (10.39 - gap * (cols - 1)) / cols
    top = 2.0
    ch = (7.5 - top - gap * (rows - 1)) / rows
    for i, (name, note, img, reg) in enumerate(items):
        r, c = divmod(i, cols)
        l = 0.65 + c * (cw + gap); t = top + r * (ch + gap)
        x, y, w, h = reg
        ih = ch - 0.85
        h = min(w * ih / cw, 900 - y)
        s = cw / w
        W, H = 1440, 900
        st = (f'background-image:url({SH}{img});background-size:{I(W*s)} {I(H*s)};'
              f'background-position:-{I(x*s)} -{I(y*s)};')
        body += box('gcard', l, t, cw, ch,
                    f'<div class="gimg" style="height:{I(ih)};{st}"></div>'
                    f'<div class="gname">{e(name)}</div><div class="gnote">{e(note)}</div>')
    return frame(num, title, lead, body)

slides = []

# ---------- 1 표지 ----------
slides.append(f'''<section class="slide cover">
<div class="coverbg"></div>
<img class="a ctab" src="assets/logo-title-tab.png" alt="한화시스템">
{box('csub',0.78,2.60,8,0.45,'PROPOSAL MANAGEMENT SYSTEM')}
{box('ctitle',0.78,3.08,9.6,1.7,'ProWin<br>제안관리 시스템 성과 보고')}
{box('cinfo',1.08,5.26,9,0.3,'황금빛, 홍건의, 박혜림, 서준혁')}
{box('cdate',1.08,5.58,9,0.3,'2026.11.15')}
<div class="cline"></div>
{box('copy',0.65,7.86,4,0.15,'ⓒ Hanwha Systems. All rights reserved')}
<img class="a flogo" src="assets/logo-footer.png" alt="">
</section>''')
PAGE[0] += 1

# ---------- 2 목차 ----------
def part(t, title, items):
    h = box('pbar', 1.12, t, 5.6, 0.14)
    h += box('ptag', 1.12, t - 0.38, 5, 0.32, e(title))
    h += box('pitems', 1.12, t + 0.2, 8, 0.9, '<br>'.join(f'<b>{i:02d}</b>&nbsp;&nbsp;{e(s)}' for i, s in items))
    return h
slides.append('<section class="slide gray">' +
    '<div class="coverbg contbg"></div>' +
    box('ctt', 1.12, 1.62, 5, 0.7, 'CONTENTS') +
    part(2.95, 'Part. 1  개요', [(1, 'ProWin이란?'), (2, '추진 배경'), (3, '목표'), (4, '기대효과')]).replace('1.12', '1.12') +
    part(4.8, 'Part. 2  구현 내용', [(5, '전체 화면 구성'), (6, '주요 기능 (RFP·목차·검토·버전관리)'), (7, '그 외 기능 · 구현 기술 스택')]) +
    part(6.55, 'Part. 3  향후', [(8, '보완 필요사항 및 하반기 계획')]) +
    '<div class="fline"></div>' + box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved') +
    box('pgno', 5.45, 7.90, 0.79, 0.16, '- 2 -') + '<img class="a flogo" src="assets/logo-footer.png" alt="">' + '</section>')
PAGE[0] += 1

# ---------- 3 ProWin이란? ----------
cw3 = 3.3; g3 = 0.245
body = ''
data3 = [('표준 절차', ['제안 전 과정을 표준 절차·템플릿으로 체계화', '임시 TF·개인 역량 의존에서 탈피', '목차가 진척 관리의 기준(마스터)'], 'o1'),
         ('버전관리', ['PPT 업로드 = 커밋(이력 보존)', '전체 섹션 최신본을 자동 합본', '합본은 불변 스냅샷으로 보관'], 'o2'),
         ('자산 라이브러리', ['과거 제안 산출물을 페이지 단위로 적재', '검색·재활용으로 반복 재작성 제거', '축적된 자산으로 제안 수행'], 'br')]
for i, (hd, it, col) in enumerate(data3):
    body += card(0.65 + i * (cw3 + g3), 2.05, cw3, 0.5, 3.0, hd, it, col)
body += box('swatch', 0.65, 5.85, 1.0, 1.5, '')
body += box('callout', 1.65, 5.85, 9.39, 1.5, '<div><b>문서 작성은 기존 오피스(PPT·엑셀)를 그대로 활용</b>하고,<br>시스템은 <b>업로드 · 처리 · 다운로드</b>를 담당한다</div>')
slides.append(frame(1, 'ProWin이란?', '제안(Proposal)을 통해 수주(Win)를 이끌어내는 <b>제안관리 시스템</b> — 제안을 “사람 수”가 아닌 <b>축적된 자산과 표준 절차</b>로 수행한다', body))

# ---------- 4 추진 배경 ----------
body = ''
data4 = [('가. 전담 조직 부재', ['RFP마다 임시 TF를 구성', '매 건 처음부터 반복, 담당자 역량에 따라 품질이 좌우됨'], 'o1'),
         ('나. 수작업 산출물', ['조견표·합본·목차를 수작업으로 작성', '휴먼 에러, 버전 꼬임, 마감 리스크 발생'], 'o2'),
         ('다. 자산의 분산·사장', ['과거 제안 자산이 개인 단위로 분산', '재활용이 불가해 매 제안마다 재작성 부담'], 'br'),
         ('라. 구두 중심 의사결정', ['리뷰·의사결정이 구두로 진행', '결정 근거가 남지 않아 추적·이관 곤란'], 'tan')]
for i, (hd, it, col) in enumerate(data4):
    r, c = divmod(i, 2)
    body += card(0.65 + c * 5.295, 2.05 + r * 2.3, 5.095, 0.46, 1.5, hd, it, col, dark=(col == 'tan'))
body += box('strip', 0.65, 6.75, 10.39, 0.6, '→ 제안이 늘어날수록 품질·생산성 저하가 불가피한 구조')
slides.append(frame(1, '추진 배경 (현황)', '현행 제안 업무는 <b>전담 조직·표준·시스템 없이 수작업과 개인 역량</b>에 의존하고 있다', body))

# ---------- 5 목표 ----------
body = ''
rows5 = [('01', '효율화', '제안 전 과정을 표준 절차·템플릿으로 체계화하여 임시 TF 및 개인 역량 의존 구조에서 탈피', 'o1'),
         ('02', '자산화', '과거 제안 산출물을 검색·재활용 가능한 자산 라이브러리로 축적하여 반복 재작성 제거', 'o4'),
         ('03', '경쟁력', '소수 인력으로 제안 품질을 유지하고 제안 투입 인건비 절감', 'tan')]
for i, (n, hd, tx, col) in enumerate(rows5):
    t = 2.1 + i * 1.8
    body += box(f'circ {col}', 0.65, t + 0.2, 1.0, 1.0, n)
    body += box('rowband', 1.85, t, 5.2, 0.5, e(hd))
    body += box('rowtext', 1.85, t + 0.58, 5.2, 1.0, e(tx))
body += box('qtxt', 7.5, 2.0, 3.54, 0.5, '“ 제안 수행 방식의 전환 ”')
body += box('bigcirc', 7.75, 2.7, 3.1, 3.1, '<div>사람 수가 아닌<br><b>축적된 자산과<br>표준 절차</b>로<br>수행하는 체계</div>')
slides.append(frame(1, '목표', '효율화 · 자산화 · 경쟁력 — 세 가지 목표로 제안 수행 체계를 전환한다', body))

# ---------- 6 기대효과 ----------
body = box('th as', 0.65, 2.05, 4.55, 0.46, 'AS-IS (현재)') + box('th tb', 5.85, 2.05, 5.19, 0.46, 'TO-BE (ProWin 도입 후)')
rows6 = [('수행 방식', '임시 TF 구성, 담당자 역량에 따라 품질이 좌우됨', '표준 절차·템플릿 기반 수행, 목차가 진척 관리의 기준'),
         ('산출물', '조견표·합본·목차를 수작업으로 작성, 버전 꼬임', 'PPT 업로드만으로 목차 순서 합본 생성, 이력·확정본 관리'),
         ('자산', '개인 단위로 분산·사장되어 재활용 불가', '자산 라이브러리에 축적하여 검색·재활용'),
         ('의사결정', '구두 중심, 결정 근거가 기록되지 않음', '리뷰 코멘트와 변경 이력으로 근거를 기록')]
for i, (k, a, b) in enumerate(rows6):
    t = 2.62 + i * 1.07
    body += box('r6k', 0.65, t, 1.0, 0.95, e(k))
    body += box('r6a', 1.7, t, 3.5, 0.95, e(a))
    body += box('r6arr', 5.2, t + 0.28, 0.65, 0.4, '▶')
    body += box('r6b', 5.85, t, 5.19, 0.95, e(b))
body += box('foot', 0.65, 6.95, 10.39, 0.4, '※ 정량 성과(개선 전·후 효율, 적용 결과)는 구현 방안 확정 후 측정 예정')
slides.append(frame(1, '기대효과', '제안 수행 방식이 <b>개인 의존 → 표준·자산 기반</b>으로 바뀐다', body))

# ---------- 7 전체 화면 구성 ----------
body = ''
NW, NH = 220, 810
half = 405
s7 = 5.45 / half
def navcrop(l, y0, hl):
    st = (f'background-image:url({SH}nav.png);background-size:{I(220*s7)} {I(1513*s7)};'
          f'background-position:0 -{I(y0*s7)};')
    inner = ''
    for (y, hh) in hl:
        inner += f'<i class="hl" style="left:{I(4*s7)};top:{I((y-y0)*s7)};width:{I(212*s7)};height:{I(hh*s7)}"></i>'
    return box('navc', l, 2.0, 220 * s7, 5.45, inner, st)
body += navcrop(0.65, 0, [(266, 30), (372, 30)])
body += navcrop(0.65 + 220 * s7 + 0.12, 405, [(408, 30), (444, 30)])
gx = 0.65 + 2 * 220 * s7 + 0.12 + 0.3
gw = 11.04 - gx
body += box('legend', gx, 2.0, gw, 0.3, '<i class="lg"></i> 백엔드(Spring Boot + SQLite) 연결 화면 4개')
groups = [('전역', '제안 현황, 자산 라이브러리', 'o1'),
          ('제안 워크스페이스', '제안 단위 협업 화면 — RFP 요구사항 → 목차 → 검토 → 버전관리를 중심으로 일정·소통·비용·인력 관리', 'o2'),
          ('ProWin 관리', '시스템 접근 권한, 사용 가이드, 변경 이력', 'br')]
t = 2.45
for hd, tx, col in groups:
    hh = 1.25 if len(tx) > 40 else 0.95
    body += box(f'gh {col}', gx, t, gw, 0.4, e(hd))
    body += box('gt', gx, t + 0.4, gw, hh, e(tx))
    t += 0.4 + hh + 0.12
body += box('note7', gx, t + 0.02, gw, 0.9, '역할(작성자 · PM/사업관리 · 영업대표 · 시스템관리자)에 따라 보이는 화면과 편집 권한이 달라진다')
slides.append(frame(2, '전체 화면 구성', '좌측 메뉴 3그룹으로 제안 업무 전 과정을 한 곳에서 다룬다', body))

# ---------- 8~11 상세 ----------
slides.append(detail(2, '주요 기능 ① RFP · 요구사항 관리',
    'RFP 문서 정보와 요구사항 목록을 등록·관리한다 — 모든 제안 작업의 <b>출발점</b>',
    'rfp.png', 1440, 900,
    [(247, 303, 963, 232)], [((247, 303, 963, 232), 10.39)],
    ['RFP 문서(파일명·페이지수·수령일) 등록', '요구사항을 코드·제목·설명으로 등록·수정', '삭제 시 사유를 남기는 소프트 삭제(DB 저장)'],
    ['RFP 수신', '문서 정보 등록', '요구사항 등록', '조견표 매핑']))
slides.append(detail(2, '주요 기능 ② 목차 관리',
    '제안서 전체 목차가 <b>진척 관리의 기준(마스터)</b>이 되어 검토·버전관리 화면을 이끈다',
    'toc.png', 1440, 900,
    [(247, 551, 963, 232)], [((247, 551, 963, 232), 10.39)],
    ['대/세부 목차를 담당자·예상 장수·상태로 관리', '세부 목차(레벨 2)가 PPT 업로드·검토 단위', '삭제는 소프트 삭제, DB에 저장'],
    ['목차 뼈대 작성', '담당자 지정', '상태·장수 갱신', '업로드 단위로 사용']))
slides.append(detail(2, '주요 기능 ③ 제안서 검토',
    '회의록을 대체하는 검토 화면 — 슬라이드를 보며 <b>코멘트를 남기고 발표자료를 지정</b>한다',
    'review_t.png', 1440, 1000,
    [(575, 533, 775, 284), (575, 770, 640, 230)],
    [((575, 533, 775, 284), 5.6), ((575, 770, 640, 230), 4.59)],
    ['PPT 업로드 시 슬라이드 제목·핵심 내용 자동 반영', '슬라이드 미리보기와 리뷰 코멘트 스레드', '설명회 발표자료 지정'],
    ['초안 PPT 업로드', '슬라이드 내용 자동 반영', '리뷰어 코멘트', '설명회 자료 지정']))
slides.append(detail(2, '주요 기능 ④ 제안서 관리 (버전 · 합본)',
    'PPT를 올리면 <b>커밋</b>으로 이력이 쌓이고, <b>합본</b> 한 번으로 목차 순서의 PPTX가 만들어진다',
    'versions.png', 1440, 900,
    [(236, 205, 390, 262)], [((236, 205, 390, 262), 3.77)],
    ['세부 목차 단위 PPT 업로드 = 커밋(버전 이력)', '전체 섹션 최신본을 목차 순서로 자동 병합', '합본은 불변 스냅샷, 원본·합본 다운로드'],
    ['섹션 PPT 업로드', '검토 화면 자동 반영', 'PM 합본 생성', '다운로드·제출'],
    row1_side=('<div class="sh">왜 중요한가</div>' + bullets([
        '조견표·합본·목차 수작업이 휴먼 에러·버전 꼬임·마감 리스크의 원인',
        '업로드만으로 이력이 남고 합본이 자동 생성되어 수작업 합치기를 제거',
        'Apache POI로 슬라이드 추출·미리보기·합본 처리']))))

# ---------- 12~13 그 외 기능 ----------
full = (220, 52, 1220, 748)
slides.append(grid(2, '그 외 기능 ① 제안 진행 · 소통 · 자산',
    '백엔드 연결 4개 화면 외에도 제안 업무 전반의 화면을 갖추고 있다 (데이터는 JSON 기반)',
    [('제안 현황', '기간별 제안 진행 현황 목록', 'proposals.png', full),
     ('제안서 홈', '제안 개요, 오늘 할 일, 지연 항목', 'home.png', full),
     ('제안 일정', '2~3주 단위 일정 등록·색상 구분', 'schedule.png', full),
     ('커뮤니케이션', '제안팀 공지·공유 게시판', 'comm.png', full),
     ('RFP Q&A · 참고 자료', '제안 전용 게시판', 'board-1.png', full),
     ('조견표', '요구사항 ↔ 목차 매핑', 'matrix.png', full),
     ('자산 라이브러리', '과거 제안서 페이지 적재·검색', 'assets.png', full),
     ('워크스페이스 관리', '제안 전용 게시판 추가·수정', 'workspace.png', full)],
    4, 2, 1.25))
slides.append(grid(2, '그 외 기능 ② 비용 · 권한 · 운영',
    '제안 비용·인력 관리와 권한·가이드·이력 등 운영 기능을 포함한다',
    [('제안 경비 관리', '자사·외주 인건비, 디자인·인쇄비', 'expense.png', full),
     ('수행 공수 관리', '투입 M/M, 직급별 공수', 'effort.png', full),
     ('제안 권한관리', '제안 단위 멤버·권한 관리', 'wsperm.png', full),
     ('시스템 접근 권한관리', '프로젝트에 종속되지 않는 시스템 권한', 'sysperm.png', full),
     ('사용 가이드', '사이트 사용법 통합 안내', 'guide.png', full),
     ('변경 이력', '추가·수정·삭제 이력(감사 대응)', 'history.png', full)],
    3, 2, 1.55))

# ---------- 14 기술 스택 ----------
body = ''
body += box('abox', 0.65, 2.0, 6.1, 0.85, '<div><b>사용자 브라우저</b><br>바닐라 HTML / CSS / JS · 빌드 도구 없음</div>')
body += box('alab', 1.2, 2.92, 5.5, 0.3, '▼ HTTP · 정적 파일 + /api/* JSON')
body += box('bbar o1', 0.65, 3.3, 6.1, 0.46, 'ProWin Backend · Spring Boot 3.3 / Java 17')
body += box('bbody', 0.65, 3.76, 6.1, 1.55, bullets(['REST API — RFP · 목차 · 검토 · 버전관리', 'PPTX 추출 · 미리보기 · 합본 (Apache POI)', '정적 화면 + API를 한 프로세스(8080)로 제공']))
body += box('alab', 1.2, 5.38, 5.5, 0.3, '▼ JDBC / 파일 저장')
body += box('dbox', 0.65, 5.75, 2.95, 1.2, '<div><b>prowin.db</b><br>SQLite<br>RFP·목차·리뷰·커밋 이력</div>')
body += box('dbox', 3.8, 5.75, 2.95, 1.2, '<div><b>data/uploads</b><br>업로드된 PPTX 파일<br>(DB에는 경로·메타만)</div>')
rows14 = [('프론트엔드', '바닐라 JS (프레임워크·빌드 없음)'), ('백엔드', 'Spring Boot 3.3.5 · Java 17'),
          ('데이터', 'SQLite (JDBC)'), ('파일 처리', 'Apache POI 5.3.0'), ('데이터 규칙', 'DB가 비어 있을 때만 최초 1회 시드, 이후 DB가 정본')]
body += box('th2', 7.05, 2.0, 3.99, 0.4, '기술 요소')
for i, (k, v) in enumerate(rows14):
    t = 2.4 + i * 0.62
    body += box('tk', 7.05, t, 1.15, 0.62, e(k)) + box('tv', 8.2, t, 2.84, 0.62, e(v))
body += box('note14', 7.05, 5.65, 3.99, 1.3, '<b>단계적 DB 연결</b><br>백엔드 연결 4개 화면 외 14개 화면은 JSON 기반 — 편집분은 저장 시 반영, DB 연결은 단계적으로 진행')
slides.append(frame(2, '구현 기술 스택', '가벼운 <b>단일 프로세스 + 파일 기반 DB</b> 구조 — 별도 빌드·인프라 없이 실행된다 (mvn spring-boot:run)', body))

# ---------- 15 보완·하반기 ----------
body = card(0.65, 2.05, 5.095, 0.5, 3.7, '보완 필요사항', [
    '나머지 14개 화면의 DB 연결 (현재 JSON 기반)',
    '실제 인증·권한 체계 적용 (현재 데모 계정 기반)',
    '한글 파일명 업로드의 서버 환경(UTF-8) 의존 해소',
    '합본 파일명·버전 표기 개선',
    '동시 편집 충돌 방지 (JSON 기반 화면)',
    '자산 라이브러리 적재·유사 사례 추천(Step 2) 구현'], 'br')
body += card(5.945, 2.05, 5.095, 0.5, 3.7, '하반기 계획', [
    '상세 설계 — 화면별 상세 규격 및 잔여 설계 과제 확정',
    '구현 방안 검증(PoC) — 핵심 기술 요소 실현성 검증 (PPT 업로드·합본은 구현·동작 확인)',
    '정량 성과 측정 — 개선 전·후 효율, 적용 결과 (구현 방안 확정 후 착수)'], 'o1')
slides.append(frame(3, '보완 필요사항 및 하반기 계획', '핵심 4개 기능은 <b>백엔드까지 구현·검증</b>했고, 남은 화면의 DB 연결과 운영 요건을 보완한다', body))

# ---------- 16 마무리 ----------
slides.append('''<section class="slide endslide"><div class="coverbg endbg"></div>
<div class="a endbox" style="left:1.5in;top:3.5in;width:5.2in;height:1.3in"><span>End of document</span><b>감사합니다</b></div></section>''')

CSS = open(os.path.join(HERE, 'prowin.css'), encoding='utf8').read()
doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ProWin 성과 제출</title><style>{CSS}</style></head><body>
{''.join(slides)}
</body></html>'''
open(OUT, 'w', encoding='utf8').write(doc)
print('slides:', len(slides), '->', os.path.abspath(OUT))
