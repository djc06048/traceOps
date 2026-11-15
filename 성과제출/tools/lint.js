// 슬라이드별 글자 겹침, 박스 넘침, 영역 이탈을 점검한다.
// 사용: node tools/lint.js [HTML 경로]   (기본: prowin/성과제출_ProWin.html)
const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');
const target = path.resolve(process.argv[2] || path.join(__dirname, '..', 'prowin', '성과제출_ProWin.html'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(target).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(1500);
  const res = await p.evaluate(() => {
    const out = [];
    const slides = [...document.querySelectorAll('.slide')];
    slides.forEach((s, si) => {
      const sr = s.getBoundingClientRect();
      const items = [];
      s.querySelectorAll('.a').forEach(el => {
        // 직접 텍스트를 가진 요소만
        const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) ||
                        (el.children.length && [...el.querySelectorAll('*')].some(c => c.childNodes.length && [...c.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())));
        if (!hasText) return;
        const r = document.createRange(); r.selectNodeContents(el);
        const tr = r.getBoundingClientRect();
        const br = el.getBoundingClientRect();
        items.push({ el, tr, br, txt: el.textContent.trim().slice(0, 24) });
        // 박스 넘침
        if (el.scrollHeight > el.clientHeight + 3 && el.clientHeight > 0)
          out.push(`S${si + 1} 넘침(세로) "${el.textContent.trim().slice(0, 20)}" ${el.scrollHeight}>${el.clientHeight}`);
        if (el.scrollWidth > el.clientWidth + 3 && el.clientWidth > 0)
          out.push(`S${si + 1} 넘침(가로) "${el.textContent.trim().slice(0, 20)}" ${el.scrollWidth}>${el.clientWidth}`);
        // 슬라이드 밖
        const rx = (tr.right - sr.left) / 96, by = (tr.bottom - sr.top) / 96;
        if (rx > 11.05 || by > 7.62 && !el.classList.contains('pgno') && !el.classList.contains('copy'))
          out.push(`S${si + 1} 영역이탈 "${el.textContent.trim().slice(0, 20)}" right=${rx.toFixed(2)} bottom=${by.toFixed(2)}`);
      });
      // 글자끼리 겹침
      for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
        const a = items[i], c = items[j];
        if (a.el.contains(c.el) || c.el.contains(a.el)) continue;
        const A = a.tr, C = c.tr;
        if (A.width < 2 || C.width < 2 || A.height < 2 || C.height < 2) continue;
        const ox = Math.min(A.right, C.right) - Math.max(A.left, C.left);
        const oy = Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top);
        if (ox > 3 && oy > 3) out.push(`S${si + 1} 글자겹침 "${a.txt}" x "${c.txt}" (${ox.toFixed(0)}x${oy.toFixed(0)}px)`);
      }
    });
    return out;
  });
  console.log(res.length ? res.join('\n') : 'LINT OK');
  await b.close();
})();
