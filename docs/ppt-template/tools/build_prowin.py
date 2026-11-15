# -*- coding: utf-8 -*-
"""ProWin 성과 제출 HTML 생성기 (v2 디자인). 사용: python3 tools/build_prowin.py -> ../성과제출_ProWin.html"""
import os, html, re
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '성과제출_ProWin.html')
SH = 'shots/prowin/'
L, CW = 0.7, 10.29
ORANGE = '#F46A25'

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
def frame(gov, body):
    PAGE[0] += 1
    h = '<section class="slide">'
    h += box('acc', L, 0.42, 0.5, 0.05)
    h += box('gov', L, 0.62, CW, 0.95, e(gov))
    h += body
    h += '<img class="a flogo" src="assets/logo-footer.png" alt="한화시스템">'
    h += box('pgno', 9.99, 7.82, 1.0, 0.2, str(PAGE[0]))
    return h + '</section>'

def svg(inner, size):
    return (f'<svg viewBox="0 0 48 48" width="{I(size)}" height="{I(size)}" fill="none" stroke="{ORANGE}" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')
ICON = {
 'check': '<rect x="8" y="6" width="32" height="36" rx="5"/><path d="M15 17l3 3 5-6M27 18h9M15 30l3 3 5-6M27 31h9"/>',
 'branch': '<circle cx="14" cy="10" r="5"/><circle cx="14" cy="38" r="5"/><circle cx="35" cy="20" r="5"/><path d="M14 15v18M14 30c14 0 21-3 21-10"/>',
 'stack': '<rect x="6" y="7" width="36" height="9" rx="3"/><rect x="6" y="20" width="36" height="9" rx="3"/><rect x="6" y="33" width="36" height="9" rx="3"/>',
 'window': '<rect x="5" y="9" width="38" height="30" rx="4"/><path d="M5 17h38M11 13h.1M16 13h.1"/>',
}

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
<img class="a flogo" style="left:10.25in;top:7.84in;height:0.26in" src="assets/logo-footer.png" alt="">
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
    box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved') +
    '<img class="a flogo" style="left:10.25in;top:7.84in;height:0.26in" src="assets/logo-footer.png" alt="">' + '</section>')
PAGE[0] += 1

# ---------- 3 P1 원칙 카드 ----------
body = ''
data3 = [('check', '표준 절차', ['제안 전 과정을 표준 절차와 템플릿으로 체계화', '임시 TF와 개인 역량에 의존하는 구조에서 탈피', '목차를 기준으로 진척 관리']),
         ('branch', '버전관리', ['PPT를 올리면 이력(커밋)이 자동으로 보존', '전체 섹션 최신본을 목차 순서로 합본', '합본은 불변 스냅샷으로 관리']),
         ('stack', '자산 라이브러리', ['과거 제안서를 페이지 단위로 적재', '검색과 재활용으로 반복 재작성 제거', '축적된 자산을 새 제안에 활용'])]
cw = 3.25; gp = (CW - 3 * cw) / 2
for i, (ic, t, ds) in enumerate(data3):
    l = L + i * (cw + gp)
    body += box('card', l, 1.95, cw, 3.7)
    body += box('', l + 0.3, 2.25, 0.7, 0.7, svg(ICON[ic], 0.7))
    body += box('ct20', l + 0.3, 3.15, cw - 0.6, 0.45, e(t))
    body += box('cd', l + 0.3, 3.75, cw - 0.55, 1.85, ''.join(f'<p>{e(d)}</p>' for d in ds))
body += box('rbar brown', L, 5.95, CW, 1.05, '<span class="lb">운영 원칙</span><span class="tx">문서 작성은 <b>기존 오피스(PPT, 엑셀)</b>를 그대로 활용하고, 시스템은 <b>업로드, 처리, 다운로드</b>를 담당</span>')
slides.append(frame('제안 업무를 사람의 역량이 아닌 표준 절차와 축적된 자산으로 수행하는 시스템', body))

# ---------- 4 P2 문제 4열 ----------
body = ''
data4 = [('전담 조직 부재', ['RFP마다 임시 TF를 구성', '매 건 처음부터 반복, 담당자 역량에 따라 품질 좌우']),
         ('수작업 산출물', ['조견표, 합본, 목차를 수작업으로 작성', '휴먼 에러, 버전 꼬임, 마감 리스크 상존']),
         ('자산의 분산과 사장', ['과거 제안 자산이 개인 단위로 분산', '재활용 불가, 매 제안마다 재작성']),
         ('구두 중심의 리뷰', ['리뷰와 의사결정이 구두로 진행', '결정 근거가 남지 않아 추적과 이관 곤란'])]
cw = (CW - 3 * 0.22) / 4
for i, (t, ds) in enumerate(data4):
    l = L + i * (cw + 0.22)
    body += box('card', l, 1.95, cw, 3.5)
    body += box('idx', l + 0.25, 2.2, 1.2, 0.5, f'{i+1:02d}')
    body += box('ct16', l + 0.25, 2.85, cw - 0.45, 0.6, e(t))
    body += box('hl-line', l + 0.25, 3.5, cw - 0.5, 0.01)
    body += box('cd', l + 0.25, 3.65, cw - 0.45, 1.75, ''.join(f'<p>{e(d)}</p>' for d in ds), 'font-size:12.5pt')
imps = [('표준 절차 확립', '조직과 개인 역량에 의존하지 않는 수행'), ('산출물 처리 체계화', '업로드 기반의 이력 관리와 합본'), ('자산과 기록 중심 운영', '재활용 자산 축적, 근거 기록 기반 의사결정')]
body += box('rbar brown', L, 5.7, CW, 1.3, '<span class="lb">시사점</span><div class="imp3">' + ''.join(f'<div>{e(a)}<span>{e(b)}</span></div>' for a, b in imps) + '</div>')
slides.append(frame('개인 역량과 수작업에 기댄 제안 업무는 건수가 늘수록 품질과 생산성이 하락', body))

# ---------- 5 P3 번호 행 ----------
body = ''
rows5 = [('o', '효율화', '제안 전 과정을 표준 절차와 템플릿으로 체계화하여 임시 TF와 개인 역량 의존 구조에서 탈피', '표준 절차 기반 수행 체계'),
         ('b', '자산화', '과거 제안 산출물을 검색과 재활용이 가능한 자산 라이브러리로 축적하여 반복 재작성 제거', '재활용 가능한 제안 자산'),
         ('t', '경쟁력', '소수 인력으로 제안 품질을 유지하고 제안 투입 인건비 절감', '제안 경쟁력 강화')]
for i, (c, t, d, r) in enumerate(rows5):
    y = 2.0 + i * 1.8
    if i: body += box('rowline', L, y - 0.07, CW, 0.01)
    body += box(f'nc {c}', L, y + 0.3, 0.95, 0.95, f'{i+1}')
    body += box('rt', 1.95, y + 0.18, 5.8, 0.5, e(t))
    body += box('rd', 1.95, y + 0.72, 5.8, 0.9, e(d))
    body += box('outp', 8.15, y + 0.45, 2.84, 0.6, e(r))
slides.append(frame('효율화, 자산화, 경쟁력의 세 가지 목표로 제안 수행 체계를 전환', body))

# ---------- 6 P4 전후 비교 ----------
body = box('colh', 2.15, 1.85, 3.9, 0.3, '<span style="color:#8a8a8a">도입 전</span>')
body += box('colh', 6.6, 1.85, 4.39, 0.3, f'<span style="color:{ORANGE}">도입 후</span>')
rows6 = [('수행 방식', '임시 TF 구성, 담당자 역량에 따른 품질 편차', '표준 절차와 템플릿 기반 수행, 목차 기준 진척 관리'),
         ('산출물', '조견표, 합본, 목차의 수작업 작성과 버전 혼선', 'PPT 업로드 기반 이력 관리, 목차 순서 합본 자동 생성'),
         ('자산', '개인 단위 분산, 재활용 불가', '자산 라이브러리 축적, 검색과 재활용'),
         ('의사결정', '구두 중심, 결정 근거 미기록', '리뷰 코멘트와 변경 이력으로 근거 기록')]
for i, (k, a, b) in enumerate(rows6):
    t = 2.3 + i * 1.25
    body += box('cat', L, t, 1.35, 1.08, e(k))
    body += box('pan as', 2.15, t, 3.9, 1.08, e(a))
    body += box('tri', 6.12, t + 0.38, 0.3, 0.32)
    body += box('pan tb', 6.6, t, 4.39, 1.08, e(b))
slides.append(frame('제안 수행이 개인 의존에서 표준 절차와 축적 자산 기반으로 전환', body))

# ---------- 7 P5 역할별 프로세스 ----------
body = ''
steps = [('o', 'o', '제안 착수', 'PM · 사업관리', ['RFP 업로드, 요구사항 추출 {{고도화}}', '제안 일정 등록', '커뮤니케이션 관리 (공지, Q&A)'], 'RFP, 제안 일정, 커뮤니케이션'),
         ('b', 'b', '제안서 작성', '작업자', ['요구사항별 유사 사례 검색 {{고도화}}', '자산 라이브러리의 자료를 참고하여 작성', '작성본을 제안서 관리에 업로드'], '자산 라이브러리, 제안서 관리'),
         ('t', 't', '제안서 검토', '제안 참여 인원 전원', ['제안서 검토 화면에서 슬라이드 확인', '슬라이드별 검토 의견 등록', '의견 이력으로 결정 근거 기록'], '제안서 검토'),
         ('o', 'o', '최종 확정', 'PM · 사업관리', ['최종본 합본 생성', '목차와 조견표 검토', '제출본 확정'], '제안서 관리, 목차, 조견표')]
sw = 2.31; sg = (CW - 4 * sw) / 3
for i, (nc, rc, t, role, acts, scr) in enumerate(steps):
    l = L + i * (sw + sg)
    body += box(f'sn {nc}', l, 1.95, 0.62, 0.62, str(i + 1))
    body += box('st', l + 0.75, 2.05, sw - 0.75, 0.45, e(t))
    if i < 3:
        body += box('conn', l + sw - 0.05, 2.25, sg + 0.05, 0.02)
        body += box('arrh', l + sw + sg - 0.1, 2.18, 0.11, 0.16)
    body += box(f'rtag {rc}', l, 2.8, sw, 0.36, e(role))
    body += box('card', l, 3.3, sw, 2.45)
    body += box('cd', l + 0.2, 3.5, sw - 0.35, 2.2, ''.join(f'<p>{e(a)}</p>' for a in acts), 'font-size:12.5pt')
    body += box('scr', l, 5.9, sw, 0.6, f'<small>관련 화면</small>{e(scr)}')
body += box('rbar sand', L, 6.6, CW, 0.85, '<span class="lb">기대 효과</span><span class="tx">요구사항 기준의 일정과 소통 일원화, 과거 사례 참조 기반 작성, 업로드만으로 이력과 합본 처리, 의견 기록의 축적</span>', 'font-size:13pt')
slides.append(frame('RFP 접수부터 최종 합본까지 역할별 업무가 하나의 흐름으로 연결', body))

# ---------- 8~11 P6 화면 쇼케이스 ----------
def detail(gov, img, W, H, boxes, zoom_i, zreg, items, caption, zlabel=None):
    ZL, ZW = L, 6.3
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
    b = (f'<svg class="a" viewBox="0 0 11.69 8.27" style="left:0;top:0;width:11.69in;height:8.27in;pointer-events:none">'
         f'<polygon points="{poly}" fill="rgba(244,106,37,0.10)"/>'
         f'<line x1="{pts[0][0]:.3f}" y1="{pts[0][1]:.3f}" x2="{pts[3][0]:.3f}" y2="{pts[3][1]:.3f}" stroke="{ORANGE}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/>'
         f'<line x1="{pts[1][0]:.3f}" y1="{pts[1][1]:.3f}" x2="{pts[2][0]:.3f}" y2="{pts[2][1]:.3f}" stroke="{ORANGE}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/></svg>')
    b += box('zoom', ZL, zt, ZWa, ph, f'<i class="bd">{zlabel or zoom_i}</i>', st)
    inner = f'<img src="{SH}{img}" alt="">'
    for i, (x, y, rw, rh) in enumerate(boxes, 1):
        inner += f'<i class="hl" style="left:{x/W*100:.2f}%;top:{y/H*100:.2f}%;width:{rw/W*100:.2f}%;height:{rh/H*100:.2f}%"><b>{i}</b></i>'
    b += box('shot', sh_l, shot_t, sh_w, sh_h, inner, 'overflow:visible')
    b += box('cap', ZL, 7.24, ZW, 0.25, e(caption))
    RL, RW = 7.45, 3.54
    b += box('lab', RL, 1.95, RW, 0.3, '화면 설명')
    y = 2.45
    for i, (t, d) in enumerate(items, 1):
        b += box('nb', RL, y + 0.02, 0.32, 0.32, str(i))
        b += box('nt', RL + 0.47, y, RW - 0.47, 1.3, f'<b>{e(t)}</b>{e(d)}')
        y += 1.4
    return frame(gov, b)

slides.append(detail('RFP와 요구사항을 한곳에서 정리해 제안 작업의 기준 확립',
    'rfp.png', 1440, 900,
    [(257, 214, 1147, 82), (257, 312, 566, 458)], 2, (247, 305, 640, 200),
    [('RFP 문서 정보', '파일명, 페이지 수, 수령일을 등록하여 제안 대상 문서를 관리'),
     ('요구사항 목록', '코드, 제목, 설명 단위로 등록, 수정, 삭제하며 삭제 시 사유를 이력으로 기록')],
    '그림. RFP / 요구사항 화면'))
slides.append(detail('목차 하나로 담당자와 진척 상태를 일원화',
    'toc.png', 1440, 900,
    [(257, 300, 420, 560), (700, 259, 450, 610)], 2, (247, 551, 900, 285),
    [('목차 구성', '대분류와 세부 목차를 구분하고, 세부 목차가 업로드와 검토의 단위'),
     ('담당 및 진척 현황', '담당자, 예상 장수, 상태(완료, 진행중, 보완)를 한눈에 관리')],
    '그림. 목차 화면', '1·2'))
slides.append(detail('슬라이드를 보며 참여 인원 전원이 의견을 남기고 결정 근거를 기록',
    'review_t.png', 1440, 1000,
    [(585, 560, 775, 170), (585, 800, 810, 190), (585, 745, 120, 45)], 1, (575, 540, 790, 270),
    [('슬라이드 미리보기', '업로드한 PPT의 슬라이드 제목과 핵심 내용이 검토 화면에 자동 반영'),
     ('리뷰 코멘트', '작성자별 의견을 일시와 함께 등록하여 결정 근거 보존'),
     ('설명회 발표자료 지정', '최종 발표에 사용할 슬라이드를 지정')],
    '그림. 제안서 검토 화면'))
slides.append(detail('PPT 업로드만으로 이력이 쌓이고 합본이 자동으로 완성',
    'versions.png', 1440, 900,
    [(256, 213, 245, 62), (256, 333, 360, 560)], 2, (246, 330, 380, 232),
    [('업로드와 합본', '세부 목차 단위로 PPT를 업로드하면 커밋이 되고, 합본으로 목차 순서의 전체 제안서를 병합'),
     ('버전 이력과 스냅샷', '누가 언제 무엇을 올렸는지 추적하고, 합본은 불변 스냅샷으로 보관하여 다운로드')],
    '그림. 제안서 관리 화면'))

# ---------- 12~13 P7 타일 갤러리 ----------
def gallery(gov, items, cols, rows, ih):
    body = ''
    gap = 0.27
    cw = (CW - gap * (cols - 1)) / cols
    top = 1.95
    th = ih + 0.7
    for i, (name, note, img, reg) in enumerate(items):
        r, c = divmod(i, cols)
        l = L + c * (cw + gap); t = top + r * (th + 0.3)
        x, y, w, h = reg
        h = min(w * ih / cw, 900 - y)
        s = cw / w
        st = (f'background-image:url({SH}{img});background-size:{I(1440*s)} {I(900*s)};background-position:-{I(x*s)} -{I(y*s)};height:{I(ih)};')
        body += box('timg', l, t, cw, ih, '', st)
        body += box('tn', l, t + ih + 0.1, cw, 0.3, e(name))
        body += box('tnote', l, t + ih + 0.38, cw, 0.3, e(note))
    return frame(gov, body)
full = (220, 52, 1220, 748)
slides.append(gallery('핵심 기능 외에도 제안 업무 전반을 지원하는 화면을 구성',
    [('제안 현황', '기간별 제안 진행 현황', 'proposals.png', full), ('제안서 홈', '제안 개요, 오늘 할 일, 지연 항목', 'home.png', full),
     ('제안 일정', '일정 등록과 색상 구분', 'schedule.png', full), ('커뮤니케이션', '제안팀 공지, 공유 게시판', 'comm.png', full),
     ('RFP Q&A, 참고 자료', '제안 전용 게시판', 'board-1.png', full), ('조견표', '요구사항과 목차 매핑', 'matrix.png', full),
     ('자산 라이브러리', '과거 제안서 페이지 적재, 검색', 'assets.png', full), ('워크스페이스 관리', '제안 전용 게시판 관리', 'workspace.png', full)], 4, 2, 1.7))
slides.append(gallery('비용, 인력, 권한, 이력까지 하나의 시스템에서 관리',
    [('제안 경비 관리', '자사, 외주 인건비, 디자인·인쇄비', 'expense.png', full), ('수행 공수 관리', '투입 M/M, 직급별 공수', 'effort.png', full),
     ('제안 권한관리', '제안 단위 멤버와 권한', 'wsperm.png', full), ('시스템 접근 권한관리', '프로젝트와 무관한 시스템 권한', 'sysperm.png', full),
     ('사용 가이드', '사이트 사용법 통합 안내', 'guide.png', full), ('변경 이력', '추가, 수정, 삭제 이력', 'history.png', full)], 3, 2, 1.8))

# ---------- 14 P8 구조 ----------
body = ''
body += box('blk', L, 2.0, 2.5, 2.7, '')
body += box('', L + 0.3, 2.3, 0.6, 0.6, svg(ICON['window'], 0.6))
body += box('bt', L + 0.3, 3.1, 2.0, 0.4, '사용자 브라우저')
body += box('bs', L + 0.3, 3.55, 2.0, 0.8, 'HTML, CSS, JavaScript')
body += box('arrl', 3.3, 3.35, 0.6, 0.02) + box('arrh', 3.86, 3.28, 0.12, 0.16) + box('alb', 3.1, 2.95, 1.0, 0.3, 'REST API')
body += box('blk sd', 4.05, 2.0, 4.1, 2.7, '')
body += box('bt', 4.35, 2.2, 3.6, 0.4, 'ProWin Backend')
body += box('bs', 4.35, 2.62, 3.6, 0.3, 'Spring Boot 3.3 · Java 17')
for k, nm in enumerate(['RFP', '목차', '검토', '버전관리']):
    body += box('chipw', 4.35 + (k % 2) * 1.82, 3.05 + (k // 2) * 0.55, 1.7, 0.45, nm)
body += box('chipw', 4.35, 4.15, 3.52, 0.42, 'PPTX 추출, 미리보기, 합본 (Apache POI)', 'font-size:11pt')
body += box('arrl', 8.2, 3.35, 0.45, 0.02) + box('arrh', 8.6, 3.28, 0.12, 0.16) + box('alb', 8.0, 2.95, 0.9, 0.3, 'JDBC')
body += box('blk', 8.75, 2.0, 2.24, 2.7, '')
body += box('bt', 9.0, 2.2, 1.9, 0.4, '저장소')
body += box('chipw', 9.0, 2.85, 1.75, 0.7, '<div>SQLite<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">RFP, 목차, 리뷰, 이력</span></div>')
body += box('chipw', 9.0, 3.7, 1.75, 0.7, '<div>파일 저장소<br><span style="font-size:10pt;font-weight:400;color:#6B6B6B">업로드 PPTX</span></div>')
body += box('lab', L, 5.05, 3, 0.3, '기술 스택')
tech = [('프론트엔드', 'HTML, CSS, JavaScript'), ('백엔드', 'Spring Boot 3.3.5'), ('언어', 'Java 17'), ('데이터', 'SQLite (JDBC)'), ('문서 처리', 'Apache POI 5.3.0')]
tw = (CW - 4 * 0.13) / 5
for i, (c, v) in enumerate(tech):
    body += box('tchip', L + i * (tw + 0.13), 5.4, tw, 0.85, f'<div class="tcat">{e(c)}</div><div class="tval">{e(v)}</div>')
body += box('rbar sand', L, 6.5, CW, 0.8, '<span class="lb">구성의 특징</span><span class="tx">별도 빌드 도구 없이 단일 서버가 화면과 API를 함께 제공</span>', 'font-size:13.5pt')
slides.append(frame('가볍게 구축하고 빠르게 확장할 수 있는 단일 서버 구조', body))

# ---------- 15 P9 로드맵 ----------
body = box('lab', L, 1.95, 4, 0.3, '고도화 과제')
for i, t in enumerate(['RFP 업로드 시 요구사항 자동 추출', '제안서 목차 자동 인식', '요구사항 기반 유사 과거 사례 추천과 의미 기반 검색', '경비, 공수 자동 합계', '전 화면 데이터 연동 확대와 권한 체계 정비']):
    y = 2.45 + i * 0.78
    body += box('dot', L, y + 0.1, 0.1, 0.1)
    body += box('li14', L + 0.3, y, 4.4, 0.7, e(t))
body += box('lab', 5.95, 1.95, 4, 0.3, '하반기 계획')
plan = [('상세 설계', '화면별 상세 규격과 잔여 설계 과제 확정'), ('구현 방안 검증 (PoC)', '핵심 기술 요소의 실현성 검증'), ('정량 성과 측정', '개선 전후 효율과 적용 결과, 구현 방안 확정 후 착수')]
body += box('vline', 6.19, 3.0, 0.02, 2.35)
for i, (t, d) in enumerate(plan):
    y = 2.45 + i * 1.45
    body += box('sn' + ('' if i == 0 else ' b' if i == 1 else ' t'), 5.95, y, 0.5, 0.5, str(i + 1), 'font-size:13pt')
    body += box('rst', 6.7, y - 0.02, 4.3, 0.4, e(t))
    body += box('rsd', 6.7, y + 0.4, 4.3, 0.8, e(d))
body += box('rbar sand', L, 6.55, CW, 0.85, '<span class="lb">추진 방향</span><span class="tx">상반기 설계와 프로토타입 성과를 구현 단계로 확대하고, 자동 추출과 사례 추천으로 작성 업무의 효율을 고도화</span>', 'font-size:13.5pt')
slides.append(frame('자동 추출과 사례 추천으로 제안 작성 업무를 한 단계 더 고도화', body))

# ---------- 16 엔딩 ----------
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
