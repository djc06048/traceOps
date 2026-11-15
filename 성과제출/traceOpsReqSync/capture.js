// TraceOps + ReqSync 화면 촬영 (capture_traceops.py 가 호출). 사용: node capture.js <baseUrl> <outDir>
// 화면 텍스트에 원본 이름이 남아 있으면(MASK_NAMES 환경변수) 촬영을 중단한다.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const [base, outDir] = process.argv.slice(2);
const MASK = JSON.parse(process.env.MASK_NAMES || '[]');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  const shots = [];
  async function check(label) {
    const txt = await p.evaluate(() => document.body.innerText);
    const hit = MASK.filter(n => txt.includes(n));
    if (hit.length) throw new Error(`${label}: 화면에 원본 이름이 남아 있습니다 (${hit.length}건)`);
  }
  async function shot(name, label) {
    await check(name);
    await p.screenshot({ path: path.join(outDir, name + '.png') });
    shots.push(name);
    console.log('saved', name, label || '');
  }
  async function go(url, wait = 1500) {
    await p.goto(base + '/' + url, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(wait);
  }

  // 요구사항 관리 / ReqSync
  await go('requirements.html');
  await shot('req', '요구사항 관리');
  await go('requirements-review.html');
  await shot('review', 'ReqSync 회의 목록');
  const card = await p.$('.rv-card:not(.muted)');
  if (card) {
    await card.click();
    await p.waitForTimeout(3500);
    await shot('review_modal', 'ReqSync 검토 창');
  } else console.log('skip review_modal (card not found)');

  // 상세공정관리 / 테스트관리
  for (const n of ['analysis', 'design', 'dev', 'unit', 'integration']) {
    await go('index.html#' + n, 1800);
    await shot(n);
  }
  // AS-IS 물리ID
  await go('asis.html');
  await shot('asis');

  // 연계관리 (목록 → TO-BE 캔버스 → AS-IS 조회)
  await go('linkage.html', 1800);
  const asisHd = await p.$('.lk-group-hd[data-group-toggle="asis"]');
  if (asisHd) {
    const t = await asisHd.innerText();
    if (t.includes('▸')) { await asisHd.click(); await p.waitForTimeout(400); }
  }
  await shot('linkage_list', '연계관리 목록');
  const count = (await p.$$('.lk-row[data-pid]')).length;
  console.log('linkage rows', count);
  for (let i = 0; i < count; i++) {
    const rr = (await p.$$('.lk-row[data-pid]'))[i];
    const txt = await rr.innerText();
    await rr.click();
    await p.waitForTimeout(1500);
    const nodes = await p.$$('.lk-node');
    const isAsis = (await p.innerText('#lkPMeta')).includes('AS-IS');
    console.log('row', i, JSON.stringify(txt.slice(0, 20)), 'nodes', nodes.length, isAsis ? 'AS-IS' : 'TO-BE');
    if (nodes.length) {
      const name = isAsis ? 'linkage_asis' : 'linkage_canvas';
      if (!shots.includes(name)) await shot(name, txt.slice(0, 16).replace(/\s+/g, ' '));
    }
    await p.click('#lkBack');
    await p.waitForTimeout(800);
    if (shots.includes('linkage_asis') && shots.includes('linkage_canvas')) break;
  }
  await b.close();
  console.log('done:', shots.join(', '));
})().catch(e => { console.error('ERROR', e.message); process.exit(1); });
