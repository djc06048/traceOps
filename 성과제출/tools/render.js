// 슬라이드를 PNG로 저장하고, 필요하면 PDF도 만든다. 글꼴 로딩을 기다린 뒤 촬영한다.
// 사용: node tools/render.js [HTML 경로] [PNG 폴더] [--pdf 출력.pdf]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
const args = process.argv.slice(2);
const pdfIdx = args.indexOf('--pdf');
const pdfOut = pdfIdx >= 0 ? path.resolve(args[pdfIdx + 1]) : null;
const pos = args.filter((a, i) => !a.startsWith('--') && (pdfIdx < 0 || i !== pdfIdx + 1));
const target = path.resolve(pos[0] || path.join(__dirname, '..', 'prowin', '성과제출_ProWin.html'));
const outDir = path.resolve(pos[1] || path.join(process.cwd(), 'slides_png'));
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(target).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(2000);
  const els = await p.$$('.slide');
  for (let i = 0; i < els.length; i++) {
    await els[i].screenshot({ path: path.join(outDir, `s${String(i + 1).padStart(2, '0')}.png`) });
  }
  console.log('slides', els.length, '->', outDir);
  if (pdfOut) {
    await p.pdf({ path: pdfOut, preferCSSPageSize: true, printBackground: true });
    console.log('pdf ->', pdfOut);
  }
  await b.close();
})();
