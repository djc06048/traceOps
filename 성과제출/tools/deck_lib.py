# -*- coding: utf-8 -*-
"""성과 제출 HTML 공통 라이브러리 (v4).

사용 순서
    import deck_lib as D
    D.configure('shots/')                 # 캡처 이미지 폴더(HTML 기준 상대 경로). 에셋·글꼴은 ../assets/, ../fonts/ 가 기본값
    slides = [D.cover(...), D.contents(...), D.frame(...), D.detail(...), ..., D.ending()]
    D.write(slides, out_html, '문서 제목')

좌표는 모두 inch(A4 가로 11.69 x 8.27)이며 디자인 규칙은 ../작성가이드.md 를 따른다.
"""
import os, html, re
HERE = os.path.dirname(os.path.abspath(__file__))
SH = 'shots/'
ASSETS = '../assets/'
FONTS = '../fonts/'
L, CW = 0.7, 10.29
ORANGE = '#F46A25'


def configure(shots, assets=None, fonts=None):
    """캡처 이미지 폴더(shots)와, 필요하면 공용 에셋·글꼴 폴더를 HTML 기준 상대 경로로 지정한다."""
    global SH, ASSETS, FONTS
    SH = shots
    if assets: ASSETS = assets
    if fonts: FONTS = fonts


def e(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'&lt;(/?b)&gt;', r'<\1>', s)
    s = s.replace('&lt;br&gt;', '<br>')
    return re.sub(r'\{\{(.+?)\}\}', r'<em class="tg">\1</em>', s)
def I(v): return f'{v:.3f}in'
def box(cls, l, t, w=None, h=None, inner='', style=''):
    st = f'left:{I(l)};top:{I(t)};'
    if w is not None: st += f'width:{I(w)};'
    if h is not None: st += f'height:{I(h)};'
    return f'<div class="a {cls}" style="{st}{style}">{inner}</div>'

PAGE = [0]
def frame(badge, title, chip, msg, body, ai=False):
    PAGE[0] += 1
    h = '<section class="slide">'
    h += box('badge', L, 0.55, 0.78, 0.36, e(badge))
    h += box('ttl', 1.65, 0.45, 7.4, 0.56, e(title) + ('<i class="aitag">AI 활용</i>' if ai else ''))
    if chip: h += box('chip', 9.19, 0.55, 1.8, 0.34, e(chip))
    h += box('msg', L, 1.18, CW, 0.8, e(msg))
    h += body
    h += f'<img class="a flogo" src="{ASSETS}logo-footer.png" alt="한화시스템">'
    h += box('pgno', 9.99, 7.82, 1.0, 0.2, str(PAGE[0]))
    return h + '</section>'

def svg(inner, size):
    return (f'<svg viewBox="0 0 48 48" width="{I(size)}" height="{I(size)}" fill="none" stroke="{ORANGE}" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')
ICON = {
 'check': '<rect x="8" y="6" width="32" height="36" rx="5"/><path d="M15 17l3 3 5-6M27 18h9M15 30l3 3 5-6M27 31h9"/>',
 'branch': '<circle cx="14" cy="10" r="5"/><circle cx="14" cy="38" r="5"/><circle cx="35" cy="20" r="5"/><path d="M14 15v18M14 30c14 0 21-3 21-10"/>',
 'stack': '<rect x="6" y="7" width="36" height="9" rx="3"/><rect x="6" y="20" width="36" height="9" rx="3"/><rect x="6" y="33" width="36" height="9" rx="3"/>',
 'spark': '<path d="M24 5l4.6 13.4L42 23l-13.4 4.6L24 41l-4.6-13.4L6 23l13.4-4.6z"/><path d="M38 6v8M34 10h8"/>',
 'window': '<rect x="5" y="9" width="38" height="30" rx="4"/><path d="M5 17h38M11 13h.1M16 13h.1"/>',
}



# ---------- 표지 / 목차 / 엔딩 (템플릿 형태 유지) ----------
def cover(subtitle, title_html, info):
    """subtitle: 영문 부제, title_html: 제목(줄바꿈은 <br>), info: 참여자. 날짜는 넣지 않는다."""
    PAGE[0] += 1
    return f'''<section class="slide cover">
<div class="coverbg"></div>
<img class="a ctab" src="{ASSETS}logo-title-tab.png" alt="한화시스템">
{box('csub',0.78,2.60,8,0.45,html.escape(subtitle))}
{box('ctitle',0.78,3.08,9.6,1.7,title_html)}
{box('cinfo',1.08,5.26,9,0.3,html.escape(info))}
<div class="cline"></div>
{box('copy',0.65,7.86,4,0.15,'ⓒ Hanwha Systems. All rights reserved')}
<img class="a flogo" style="left:10.25in;top:7.84in;height:0.26in" src="{ASSETS}logo-footer.png" alt="">
</section>'''


def contents(parts):
    """parts: [(y, '파트 제목', [(번호, '항목'), ...]), ...]  (y는 파트 띠의 세로 위치, 예: 2.8, 5.0, 6.7)"""
    PAGE[0] += 1
    out = '<section class="slide gray"><div class="coverbg contbg"></div>' + box('ctt', 1.12, 1.4, 5, 0.95, 'CONTENTS')
    for t, title, items in parts:
        out += box('pbar', 1.12, t, 5.6, 0.14)
        out += box('ptag', 1.12, t - 0.38, 5, 0.32, e(title))
        out += box('pitems', 1.12, t + 0.2, 8, 1.7, '<br>'.join(f'<b>{i:02d}</b>&nbsp;&nbsp;{e(s)}' for i, s in items))
    out += box('copy', 0.65, 7.86, 4, 0.15, 'ⓒ Hanwha Systems. All rights reserved')
    out += f'<img class="a flogo" style="left:10.25in;top:7.84in;height:0.26in" src="{ASSETS}logo-footer.png" alt="">'
    return out + '</section>'


def ending():
    PAGE[0] += 1
    return '''<section class="slide endslide"><div class="coverbg endbg"></div>
<div class="a endbox" style="left:1.5in;top:3.5in;width:5.2in;height:1.3in"><span>End of document</span><b>감사합니다</b></div></section>'''


# ---------- 화면 상세 (패턴 P6) ----------
def detail(title, chip, msg, img, W, H, items, points, effect, path, badge='구현', ai=False):
    b = ''
    SL, SW = L, 5.0
    sh_t = 2.1
    sh_h = SW * H / W
    px = lambda v: SL + v / W * SW
    py = lambda v: sh_t + v / H * sh_h
    ZX, ZW = 6.35, 4.64
    y = 2.05
    polys = ''; zooms = ''; hls = ''
    rects = []
    for n, it in enumerate(items, 1):
        zx, zy, zw, zh = it['zoom']
        # 글자가 테두리에 닿거나 잘리지 않도록 확대 영역에 여백을 더한다(이미지 경계 안으로 제한)
        px_, py_ = it.get('padx', 10), it.get('pady', 8)
        x0, y0 = max(0, zx - px_), max(0, zy - py_)
        x1, y1 = min(W, zx + zw + px_), min(H, zy + zh + py_)
        zx, zy, zw, zh = x0, y0, x1 - x0, y1 - y0
        for r0, t0 in rects:
            ox = min(zx + zw, r0[0] + r0[2]) - max(zx, r0[0]); oy = min(zy + zh, r0[1] + r0[3]) - max(zy, r0[1])
            if ox > 0 and oy > 0:
                print(f'  [경고] 강조 영역 겹침: {title} / "{t0}" x "{it["t"]}" ({ox:.0f}x{oy:.0f}px)')
        rects.append(((zx, zy, zw, zh), it['t']))
        s = min(ZW / zw, it.get('capH', 1.1) / zh)
        ph = zh * s; zcw = zw * s
        zooms += box('ntag', ZX, y, 0.28, 0.28, str(n))
        zooms += box('zt', ZX + 0.4, y - 0.02, ZW - 0.4, 0.32, e(it['t']))
        cy = y + 0.38
        st = (f'background-image:url({SH}{img});background-size:{I(W*s)} {I(H*s)};background-position:-{I(zx*s)} -{I(zy*s)};')
        zooms += box('zoom', ZX, cy, zcw, ph, '', st)
        zooms += box('zd', ZX, cy + ph + 0.07, ZW, 0.45, e(it['d']))
        pts = [(px(zx + zw), py(zy)), (px(zx + zw), py(zy + zh)), (ZX, cy + ph), (ZX, cy)]
        poly = ' '.join(f'{a:.3f},{c:.3f}' for a, c in pts)
        polys += (f'<polygon points="{poly}" fill="rgba(244,106,37,0.10)"/>'
                  f'<line x1="{pts[0][0]:.3f}" y1="{pts[0][1]:.3f}" x2="{pts[3][0]:.3f}" y2="{pts[3][1]:.3f}" stroke="{ORANGE}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/>'
                  f'<line x1="{pts[1][0]:.3f}" y1="{pts[1][1]:.3f}" x2="{pts[2][0]:.3f}" y2="{pts[2][1]:.3f}" stroke="{ORANGE}" stroke-width="0.012" stroke-dasharray="0.05 0.04"/>')
        hls += (f'<i class="hl" style="left:{zx/W*100:.2f}%;top:{zy/H*100:.2f}%;width:{zw/W*100:.2f}%;height:{zh/H*100:.2f}%"><b>{n}</b></i>')
        y = cy + ph + 0.52 + 0.1
    assert y <= 6.45, f'확대 카드가 하단 영역과 겹침: y={y:.2f} ({title})'
    b += f'<svg class="a" viewBox="0 0 11.69 8.27" style="left:0;top:0;width:11.69in;height:8.27in;pointer-events:none">{polys}</svg>'
    b += box('shot', SL, sh_t, SW, sh_h, f'<img src="{SH}{img}" alt="">{hls}', 'overflow:visible')
    b += zooms
    b += box('pth', SL, sh_t + sh_h + 0.12, SW, 0.3, f'<b>화면 위치</b>{e(path)}')
    # 하단: 핵심 포인트 카드 2개 + 기대 효과
    pw = 3.2; gp = 0.12
    for i, (kw, tx) in enumerate(points):
        b += box('pcard', L + i * (pw + gp), 6.55, pw, 1.0, f'<div class="pk">{e(kw)}</div><p>{e(tx)}</p>')
    ex = L + 2 * (pw + gp)
    b += box('effb', ex, 6.55, L + CW - ex, 1.0, f'<div class="pk">기대 효과</div><div class="et">{e(effect)}</div>')
    return frame(badge, title, chip, msg, b, ai)


# ---------- 타일 갤러리 (패턴 P7) ----------
def gallery(msg, title, chip, items, cols, rows, ih, badge='구현'):
    body = ''
    gap = 0.27
    cw = (CW - gap * (cols - 1)) / cols
    top = 2.1
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
    return frame(badge, title, chip, msg, body)


def write(slides, out, title, css='deck.css'):
    """슬라이드 HTML 조각들을 한 문서로 합쳐 저장한다."""
    css_text = open(os.path.join(HERE, css), encoding='utf8').read()
    css_text = css_text.replace('{{ASSETS}}', ASSETS).replace('{{FONTS}}', FONTS)
    doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css_text}</style></head><body>
{''.join(slides)}
</body></html>'''
    open(out, 'w', encoding='utf8').write(doc)
    print('slides:', len(slides), '->', os.path.abspath(out))
