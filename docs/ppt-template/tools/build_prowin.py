# -*- coding: utf-8 -*-
"""ProWin 성과 제출 HTML 생성기. 사용: python3 tools/build_prowin.py -> ../성과제출_ProWin.html"""
import os, html, re
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '성과제출_ProWin.html')
SH = 'shots/prowin/'
CH = {1: 'Chapter I. 개요', 2: 'Chapter II. 구현 내용', 3: 'Chapter III. 향후 계획'}

def e(s):
    s = html.escape(s, quote=False)
    return re.sub(r'\{\{(.+?)\}\}', r'<em class="tg">\1</em>', s)
def I(v): return f'{v:.3f}in'
def box(cls, l, t, w=None, h=None, inner='', style=''):
    s = f'left:{I(l)};top:{I(t)};'
    if w is not None: s += f'width:{I(w)};'
    if h is not None: s += f'height:{I(h)};'
    return f'<div class="a {cls}" style="{s}{style}">{inner}</div>'

PAGE = [0]
def frame(ch, num, title, body, pre=''):
    PAGE[0] += 1
    h = '<section class="slide">' + pre
    h += '<div class="topband"></div><div class="diag"></div>'
    h += box('lbl', 1.53, 0.40, 6, 0.2, e(CH[ch]))
    h += box('pnum', 0.80, 0.51, 0.7, 0.61, f'{num:02d}')
    h += box('ptitle', 1.49, 0.63, 9, 0.5, e(title))
    h += body
    h += '<div class="fline"></div>'
    h += box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved')
    h += box('pgno', 5.45, 7.90, 0.79, 0.16, f'- {PAGE[0]} -')
    h += '<img class="a flogo" src="assets/logo-footer.png" alt="한화시스템">'
    return h + '</section>'

def bullets(items, cls=''):
    return f'<ul class="bl {cls}">' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>'
def checks(items, cls=''):
    return f'<ul class="ck {cls}">' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>'
def pill(text, l=0.65, t=1.3, w=5.2):
    return box('pillbar', l, t, w, 0.42, f'<i class="dot"></i><span>{e(text)}</span>')
def quote(a, b, t=1.3):
    return box('quote', 0.65, t, 10.39, 0.95,
               f'<span class="qm">&ldquo;</span><div>{e(a)}<br><b>{e(b)}</b></div><span class="qm">&rdquo;</span>')
def banner(t, h, label, items):
    out = box('bnl', 0.65, t, 1.9, h, f'<div>{e(label)}</div>')
    out += box('bnr', 2.55, t, 8.49, h, checks(items))
    return out

slides = []

# ---------- 1 표지 ----------
slides.append(f'''<section class="slide cover">
<div class="coverbg"></div>
<img class="a ctab" src="assets/logo-title-tab.png" alt="한화시스템">
{box('csub',0.78,2.60,8,0.45,'PROPOSAL MANAGEMENT SYSTEM')}
{box('ctitle',0.78,3.08,9.6,1.7,'ProWin<br>제안관리 시스템 성과 보고')}
{box('cinfo',1.08,5.26,9,0.3,'황금빛, 홍건의, 박혜림, 서준혁')}
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
slides.append('<section class="slide gray"><div class="coverbg contbg"></div>' +
    box('ctt', 1.12, 1.62, 5, 0.7, 'CONTENTS') +
    part(2.95, 'Part. 1  개요', [(1, 'ProWin 소개'), (2, '추진 배경'), (3, '목표'), (4, '기대효과')]) +
    part(5.0, 'Part. 2  구현 내용', [(5, '업무 흐름'), (6, '주요 기능'), (7, '부가 기능 및 기술 구성')]) +
    part(6.7, 'Part. 3  향후 계획', [(8, '고도화 과제 및 하반기 계획')]) +
    '<div class="fline"></div>' + box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved') +
    box('pgno', 5.45, 7.90, 0.79, 0.16, '- 2 -') + '<img class="a flogo" src="assets/logo-footer.png" alt="">' + '</section>')
PAGE[0] += 1

# ---------- 3 ProWin 소개 ----------
body = quote('제안을 ‘사람 수’가 아닌', '축적된 자산과 표준 절차로 수행하는 제안관리 시스템', 1.3)
cw3, g3 = 3.3, 0.245
data3 = [('표준 절차', '표준화', ['제안 전 과정을 표준 절차와 템플릿으로 체계화', '임시 TF, 개인 역량 의존 구조에서 탈피', '목차 기준의 진척 관리']),
         ('버전관리', '이력', ['PPT 업로드 시 이력(커밋) 자동 보존', '전체 섹션 최신본을 목차 순서로 합본', '합본은 불변 스냅샷으로 관리']),
         ('자산 라이브러리', '자산화', ['과거 제안서를 페이지 단위로 적재', '검색과 재활용으로 반복 재작성 제거', '축적된 자산을 신규 제안에 활용'])]
for i, (hd, kw, it) in enumerate(data3):
    l = 0.65 + i * (cw3 + g3)
    body += box('bar br', l, 2.45, cw3, 0.5, e(hd))
    body += box('cbody', l, 2.95, cw3, 2.75, '')
    body += box('hex', l + (cw3 - 1.5) / 2, 3.1, 1.5, 0.9, f'<span>{e(kw)}</span>')
    body += box('cbl', l + 0.15, 4.12, cw3 - 0.3, 1.55, checks(it, 'sm'))
body += banner(5.95, 1.4, '운영 원칙', ['문서 작성은 기존 오피스(PPT, 엑셀)를 그대로 활용', '시스템은 업로드, 처리, 다운로드를 담당'])
slides.append(frame(1, 1, 'ProWin 소개', body))

# ---------- 4 추진 배경 ----------
body = pill('현행 제안 업무 현황')
rows4 = [('조직', '전담 조직 부재', ['RFP마다 임시 TF를 구성하여 매 건 처음부터 반복', '담당자 역량에 따라 품질이 좌우']),
         ('산출물', '수작업 중심의 산출물 작성', ['조견표, 합본, 목차를 수작업으로 작성', '휴먼 에러, 버전 꼬임, 마감 리스크 상존']),
         ('자산', '제안 자산의 분산 및 사장', ['과거 제안 자산이 개인 단위로 분산', '재활용이 불가하여 매 제안마다 재작성']),
         ('의사결정', '구두 중심의 리뷰', ['리뷰와 의사결정이 구두로 진행', '결정 근거가 남지 않아 추적과 이관 곤란'])]
for i, (k, t, b) in enumerate(rows4):
    y = 1.95 + i * 1.38
    body += box('k4', 0.65, y, 1.0, 1.25, e(k))
    body += box('t4', 1.8, y, 4.6, 0.4, f'<b>{e(t)}</b>')
    body += box('b4', 1.8, y + 0.42, 4.6, 0.85, bullets(b, 'sm'))
body += box('rpanel', 6.75, 1.95, 4.29, 5.45, '')
body += box('rph', 6.75, 1.95, 4.29, 0.5, '시사점')
imps = [('표준 절차 확립', '조직과 개인 역량에 의존하지 않는 수행 체계'), ('산출물 처리 체계화', '업로드 기반의 이력 관리와 합본'), ('자산과 기록 중심 운영', '재활용 자산 축적, 근거 기록 기반 의사결정')]
for i, (t, d) in enumerate(imps):
    y = 2.7 + i * 1.55
    body += box('hexn', 6.95, y, 0.95, 0.85, f'<span>{i+1}</span>')
    body += box('imp', 8.05, y - 0.05, 2.9, 1.3, f'<b>{e(t)}</b><br><span>{e(d)}</span>')
slides.append(frame(1, 2, '추진 배경', body))

# ---------- 5 목표 ----------
body = quote('제안 수행 방식의 전환', '효율화 · 자산화 · 경쟁력 확보', 1.3)
cw5, g5 = 3.3, 0.245
data5 = [('표준 절차 기반의', '효율화', '임시 TF, 개인 역량 의존 탈피', ['제안 전 과정을 표준 절차와 템플릿으로 체계화', '목차 기준 진척 관리'], '표준 절차 기반 수행 체계'),
         ('축적 자산 기반의', '자산화', '검색, 재활용 가능한 자산 축적', ['과거 제안 산출물을 자산 라이브러리로 축적', '반복 재작성 제거'], '재활용 가능한 제안 자산'),
         ('소수 인력 기반의', '경쟁력', '품질 유지와 투입 비용 절감', ['소수 인력으로 제안 품질 유지', '제안 투입 인건비 절감'], '제안 경쟁력 강화')]
for i, (a, b, sub, it, res) in enumerate(data5):
    l = 0.65 + i * (cw5 + g5)
    body += box('cardhd', l, 2.45, cw5, 0.95, f'<div><small>{e(a)}</small><br><b>{e(b)}</b></div>')
    body += box('cbody gbg', l, 3.4, cw5, 3.6, '')
    body += box('subbox', l + 0.15, 3.55, cw5 - 0.3, 0.45, e(sub))
    body += box('cbl', l + 0.2, 4.2, cw5 - 0.4, 1.8, checks(it, 'sm'))
    body += box('resbox', l + 0.15, 6.15, cw5 - 0.3, 0.7, f'<b>{e(res)}</b>')
    if i < 2: body += box('plus', l + cw5 - 0.02, 5.0, 0.28, 0.28, '+')
slides.append(frame(1, 3, '목표', body))

# ---------- 6 기대효과 ----------
body = pill('도입 전후 비교', 0.65, 1.3, 4.0)
body += box('th as', 0.65, 1.95, 4.55, 0.46, '도입 전 (AS-IS)') + box('th tb', 5.85, 1.95, 5.19, 0.46, '도입 후 (TO-BE)')
rows6 = [('수행 방식', '임시 TF 구성, 담당자 역량에 따른 품질 편차', '표준 절차와 템플릿 기반 수행, 목차 기준 진척 관리'),
         ('산출물', '조견표, 합본, 목차의 수작업 작성과 버전 혼선', 'PPT 업로드 기반 이력 관리, 목차 순서 합본 자동 생성'),
         ('자산', '개인 단위 분산, 재활용 불가', '자산 라이브러리 축적, 검색과 재활용'),
         ('의사결정', '구두 중심, 결정 근거 미기록', '리뷰 코멘트와 변경 이력으로 근거 기록')]
for i, (k, a, b) in enumerate(rows6):
    t = 2.52 + i * 1.2
    body += box('r6k', 0.65, t, 1.0, 1.05, e(k))
    body += box('r6a', 1.7, t, 3.5, 1.05, e(a))
    body += box('r6arr', 5.2, t + 0.28, 0.65, 0.5, '')
    body += box('r6b', 5.85, t, 5.19, 1.05, e(b))
slides.append(frame(1, 4, '기대효과', body))

# ---------- 7 업무 흐름 ----------
body = pill('역할별 제안 업무 흐름', 0.65, 1.3, 5.0)
steps = [('STEP 1', '제안 착수', 'PM · 사업관리', 'o1',
          ['RFP 업로드 및 요구사항 추출 {{고도화}}', '제안 일정 등록', '커뮤니케이션 관리 (공지, Q&A)'], 'RFP / 요구사항, 제안 일정, 커뮤니케이션'),
         ('STEP 2', '제안서 작성', '작업자', 'o2',
          ['요구사항별 유사 과거 사례 검색 {{고도화}}', '자산 라이브러리의 관련 자료 참고', '작성본을 제안서 관리에 업로드하여 최신화'], '자산 라이브러리, 제안서 관리'),
         ('STEP 3', '제안서 검토', '제안 참여 인원 전원', 'br',
          ['제안서 검토 화면에서 슬라이드 확인', '검토 의견 등록', '의견 이력으로 결정 근거 기록'], '제안서 검토'),
         ('STEP 4', '최종 확정', 'PM · 사업관리', 'tan',
          ['최종본 합본 생성', '목차와 조견표 검토', '제출본 확정'], '제안서 관리, 목차, 조견표')]
sw, sg = 2.37, 0.303
for i, (s, t, role, col, its, scr) in enumerate(steps):
    l = 0.65 + i * (sw + sg)
    body += box(f'chev {col}', l, 1.95, sw + (0.18 if i < 3 else 0), 0.75, f'<small>{s}</small><b>{e(t)}</b>')
    body += box('rolep', l + 0.1, 2.85, sw - 0.2, 0.36, e(role))
    body += box('cbody', l, 3.3, sw, 2.2, '')
    body += box('cbl', l + 0.1, 3.4, sw - 0.2, 2.05, checks(its, 'xs'))
    body += box('scrtag', l, 5.5, sw, 0.8, f'<small>관련 화면</small><br>{e(scr)}')
body += banner(6.5, 1.0, '기대 효과', ['요구사항 기준의 일정과 소통 일원화, 과거 사례 참조 기반 작성', '업로드만으로 이력과 합본이 처리되고, 리뷰 의견이 기록으로 축적'])
slides.append(frame(2, 5, '업무 흐름', body))

# ---------- 8~11 상세 ----------
RED = '#E60000'
def detail(ch, num, title, km, img, W, H, boxes, zoom_i, zreg, items, caption, zlabel=None):
    ZL, ZW = 0.65, 6.3
    zx, zy, zw, zh = zreg
    s = min(ZW / zw, 2.3 / zh)
    ph = zh * s
    ZWa = zw * s
    zt = 1.95
    st = (f'background-image:url({SH}{img});background-size:{I(W*s)} {I(H*s)};'
          f'background-position:-{I(zx*s)} -{I(zy*s)};')
    shot_t = zt + ph + 0.42
    sh_h = 7.18 - shot_t
    sh_w = sh_h * W / H
    if sh_w > ZW: sh_w = ZW; sh_h = sh_w * H / W
    sh_l = ZL + (ZW - sh_w) / 2
    bx, by, bw, bh = boxes[zoom_i - 1]
    px = lambda v: sh_l + v / W * sh_w
    py = lambda v: shot_t + v / H * sh_h
    pts = [(ZL, zt + ph), (ZL + ZWa, zt + ph), (px(bx + bw), py(by)), (px(bx), py(by))]
    poly = ' '.join(f'{x:.3f},{y:.3f}' for x, y in pts)
    svg = (f'<svg class="a fun" viewBox="0 0 11.69 8.27" style="left:0;top:0;width:11.69in;height:8.27in">'
           f'<polygon points="{poly}" fill="rgba(230,0,0,0.12)"/>'
           f'<line x1="{pts[0][0]:.3f}" y1="{pts[0][1]:.3f}" x2="{pts[3][0]:.3f}" y2="{pts[3][1]:.3f}" stroke="{RED}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/>'
           f'<line x1="{pts[1][0]:.3f}" y1="{pts[1][1]:.3f}" x2="{pts[2][0]:.3f}" y2="{pts[2][1]:.3f}" stroke="{RED}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/></svg>')
    b = svg
    b += box('zoom', ZL, zt, ZWa, ph, f'<i class="bd">{zlabel or zoom_i}</i>', st)
    inner = f'<img src="{SH}{img}" alt="">'
    for i, (x, y, rw, rh) in enumerate(boxes, 1):
        inner += (f'<i class="hl" style="left:{x/W*100:.2f}%;top:{y/H*100:.2f}%;width:{rw/W*100:.2f}%;height:{rh/H*100:.2f}%"><b>{i}</b></i>')
    b += box('shot', sh_l, shot_t, sh_w, sh_h, inner)
    b += box('cap', ZL, 7.24, ZW, 0.25, e(caption))
    # 우측 설명
    RL, RW = 7.3, 3.74
    b += box('kmh', RL, 1.95, RW, 0.42, 'Key Message')
    b += box('kmb', RL, 2.37, RW, 1.25, f'<div>{e(km)}</div>')
    y = 3.85
    for i, (t, d) in enumerate(items, 1):
        b += box('nb', RL, y + 0.02, 0.3, 0.3, str(i))
        b += box('nt', RL + 0.42, y, RW - 0.42, 1.1, f'<b>{e(t)}</b><br><span>{e(d)}</span>')
        y += 1.18
    return frame(ch, num, title, b)

slides.append(detail(2, 6, '주요 기능 | RFP · 요구사항 관리',
    'RFP 정보와 요구사항을 한 화면에서 정리하여 제안 작업의 기준 확립',
    'rfp.png', 1440, 900,
    [(257, 214, 1147, 82), (257, 312, 566, 458)], 2, (247, 305, 640, 200),
    [('RFP 문서 정보', '파일명, 페이지 수, 수령일을 등록하여 제안 대상 문서를 관리'),
     ('요구사항 목록', '코드, 제목, 설명 단위로 등록, 수정, 삭제하며 삭제 시 사유를 이력으로 기록')],
    '그림. RFP / 요구사항 화면'))
slides.append(detail(2, 6, '주요 기능 | 목차 관리',
    '목차를 진척 관리의 기준으로 삼아 담당자와 상태를 일원화',
    'toc.png', 1440, 900,
    [(257, 300, 420, 560), (700, 259, 450, 610)], 2, (247, 551, 900, 285),
    [('목차 구성', '대분류와 세부 목차를 구분하고 세부 목차가 업로드와 검토의 단위'),
     ('담당 및 진척 현황', '담당자, 예상 장수, 상태(완료, 진행중, 보완)를 한눈에 관리')],
    '그림. 목차 화면', '1·2'))
slides.append(detail(2, 6, '주요 기능 | 제안서 검토',
    '슬라이드를 보며 참여 인원 전원이 의견을 남기는 검토 체계',
    'review_t.png', 1440, 1000,
    [(585, 560, 775, 170), (585, 800, 810, 190), (585, 745, 120, 45)], 1, (575, 540, 790, 270),
    [('슬라이드 미리보기', '업로드한 PPT의 슬라이드 제목과 핵심 내용이 검토 화면에 자동 반영'),
     ('리뷰 코멘트', '작성자별 의견을 등록하고 일시와 함께 기록하여 결정 근거 보존'),
     ('설명회 발표자료 지정', '최종 발표에 사용할 슬라이드를 지정')],
    '그림. 제안서 검토 화면'))
slides.append(detail(2, 6, '주요 기능 | 제안서 관리 (버전 · 합본)',
    '업로드만으로 이력이 쌓이고 합본이 자동으로 생성되는 버전관리',
    'versions.png', 1440, 900,
    [(256, 213, 245, 62), (256, 333, 360, 560)], 2, (246, 330, 380, 232),
    [('업로드와 합본', '세부 목차 단위로 PPT를 업로드하면 커밋이 되고, 합본으로 목차 순서의 전체 제안서를 병합'),
     ('버전 이력과 스냅샷', '누가 언제 무엇을 올렸는지 추적하고, 합본은 불변 스냅샷으로 보관하여 다운로드')],
    '그림. 제안서 관리 화면'))

# ---------- 12~13 부가 기능 ----------
def grid(ch, num, title, items, cols, rows):
    body = ''
    gap = 0.2
    cw = (10.39 - gap * (cols - 1)) / cols
    top = 1.95
    ch_ = (7.52 - top - gap * (rows - 1)) / rows
    for i, (name, note, img, reg) in enumerate(items):
        r, c = divmod(i, cols)
        l = 0.65 + c * (cw + gap); t = top + r * (ch_ + gap)
        x, y, w, h = reg
        ih = ch_ - 0.85
        h = min(w * ih / cw, 900 - y)
        s = cw / w
        st = (f'background-image:url({SH}{img});background-size:{I(1440*s)} {I(900*s)};background-position:-{I(x*s)} -{I(y*s)};')
        body += box('gcard', l, t, cw, ch_, f'<div class="gimg" style="height:{I(ih)};{st}"></div><div class="gname">{e(name)}</div><div class="gnote">{e(note)}</div>')
    return frame(ch, num, title, body)
full = (220, 52, 1220, 748)
slides.append(grid(2, 7, '부가 기능 (1/2) 제안 진행 · 소통 · 자산',
    [('제안 현황', '기간별 제안 진행 현황', 'proposals.png', full), ('제안서 홈', '제안 개요, 오늘 할 일, 지연 항목', 'home.png', full),
     ('제안 일정', '일정 등록과 색상 구분', 'schedule.png', full), ('커뮤니케이션', '제안팀 공지, 공유 게시판', 'comm.png', full),
     ('RFP Q&A · 참고 자료', '제안 전용 게시판', 'board-1.png', full), ('조견표', '요구사항과 목차 매핑', 'matrix.png', full),
     ('자산 라이브러리', '과거 제안서 페이지 적재, 검색', 'assets.png', full), ('워크스페이스 관리', '제안 전용 게시판 관리', 'workspace.png', full)], 4, 2))
slides.append(grid(2, 7, '부가 기능 (2/2) 비용 · 권한 · 운영',
    [('제안 경비 관리', '자사, 외주 인건비, 디자인·인쇄비', 'expense.png', full), ('수행 공수 관리', '투입 M/M, 직급별 공수', 'effort.png', full),
     ('제안 권한관리', '제안 단위 멤버와 권한', 'wsperm.png', full), ('시스템 접근 권한관리', '프로젝트와 무관한 시스템 권한', 'sysperm.png', full),
     ('사용 가이드', '사이트 사용법 통합 안내', 'guide.png', full), ('변경 이력', '추가, 수정, 삭제 이력', 'history.png', full)], 3, 2))

# ---------- 14 기술 구성 ----------
body = pill('시스템 구성', 0.65, 1.3, 3.4)
body += box('abox', 0.65, 1.95, 6.1, 0.85, '<div><b>사용자 브라우저</b><br>HTML / CSS / JavaScript</div>')
body += box('alab', 1.2, 2.88, 5.5, 0.3, '▼ HTTP, REST API (JSON)')
body += box('bbar o1', 0.65, 3.25, 6.1, 0.46, 'ProWin Backend (Spring Boot 3.3, Java 17)')
body += box('bbody', 0.65, 3.71, 6.1, 1.6, bullets(['REST API: RFP, 목차, 검토, 버전관리', 'PPTX 추출, 미리보기, 합본 (Apache POI)', '화면과 API를 하나의 서버로 제공']))
body += box('alab', 1.2, 5.38, 5.5, 0.3, '▼ 데이터 저장')
body += box('dbox', 0.65, 5.75, 2.95, 1.25, '<div><b>SQLite</b><br>RFP, 목차, 리뷰, 커밋 이력</div>')
body += box('dbox', 3.8, 5.75, 2.95, 1.25, '<div><b>파일 저장소</b><br>업로드된 PPTX</div>')
rows14 = [('프론트엔드', 'HTML, CSS, JavaScript'), ('백엔드', 'Spring Boot 3.3.5, Java 17'), ('데이터', 'SQLite (JDBC)'), ('문서 처리', 'Apache POI 5.3.0'), ('주요 처리', 'PPTX 추출, 미리보기, 합본')]
body += box('th2', 7.05, 1.95, 3.99, 0.42, '기술 요소')
for i, (k, v) in enumerate(rows14):
    t = 2.37 + i * 0.66
    body += box('tk', 7.05, t, 1.25, 0.66, e(k)) + box('tv', 8.3, t, 2.74, 0.66, e(v))
body += box('note14', 7.05, 5.8, 3.99, 1.2, '<b>구성의 특징</b><br>별도 빌드 도구 없이 가볍게 구축하고, 단일 서버로 화면과 API를 함께 제공')
slides.append(frame(2, 7, '기술 구성', body))

# ---------- 15 향후 계획 ----------
body = pill('고도화 과제 및 하반기 계획', 0.65, 1.3, 5.6)
body += box('bar br', 0.65, 1.95, 5.095, 0.5, '고도화 과제') + box('cbody', 0.65, 2.45, 5.095, 3.6, checks([
    'RFP 업로드 시 요구사항 자동 추출', '목차 자동 인식', '요구사항 기반 유사 과거 사례 추천 및 의미 기반 검색',
    '경비, 공수 자동 합계', '전 화면 데이터 연동 확대 및 권한 체계 정비']))
body += box('bar o1', 5.945, 1.95, 5.095, 0.5, '하반기 계획') + box('cbody', 5.945, 2.45, 5.095, 3.6, checks([
    '상세 설계: 화면별 상세 규격 및 잔여 설계 과제 확정', '구현 방안 검증(PoC): 핵심 기술 요소의 실현성 검증',
    '정량 성과 측정: 개선 전후 효율 및 적용 결과 (구현 방안 확정 후 착수)']))
body += banner(6.3, 1.1, '추진 방향', ['상반기 설계와 프로토타입 성과를 구현 단계로 확대', '자동 추출과 사례 추천으로 제안 작성 업무의 효율 고도화'])
slides.append(frame(3, 8, '향후 계획', body))

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
