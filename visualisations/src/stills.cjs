// Render every chart of the page as a PNG for the READMEs: stills/vi/NN.png and stills/en/NN.png.
//   node visualisations/src/stills.cjs
// The stills leave out each chart's title and dek (the READMEs print them). Needs Playwright with Chromium; set
// PLAYWRIGHT to its package folder if `require('playwright')` does not resolve. The page loads its fonts (Be Vietnam Pro,
// Noto Serif) from Google Fonts, so run it online, or the stills fall back to the system's fonts.
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const root = path.resolve(__dirname, '..');
const page = 'file:///' + path.join(root, 'phap-luat-viet-nam-qua-20-bieu-do.html').replace(/\\/g, '/');
(async () => {
  const b = await chromium.launch();
  for (const lang of ['vi', 'en']) {
    const p = await b.newPage({ viewport: { width: 1100, height: 900 }, colorScheme: 'light', deviceScaleFactor: 1 });
    await p.goto(page + '?lang=' + lang);
    await p.evaluate(() => document.fonts && document.fonts.ready);
    await p.waitForTimeout(3000);
    await p.addStyleTag({ content: 'details.tbl{display:none} figure.chart h3, figure.chart .dek{display:none} figure.chart{padding-top:14px;padding-bottom:12px}' });
    const figs = await p.$$('figure.chart');
    for (let i = 0; i < figs.length; i++) {
      await figs[i].screenshot({ path: path.join(root, 'stills', lang, String(i + 1).padStart(2, '0') + '.png') });
    }
    console.log(lang, figs.length);
    await p.close();
  }
  await b.close();
})();
