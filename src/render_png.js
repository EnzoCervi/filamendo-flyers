// Captura cada HTML como PNG (Chromium). Uso: node src/render_png.js trabajo.json
// trabajo.json = [{"html": "...", "png": "...", "w": 1080, "h": 1350, "scale": 2}, ...]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const job of jobs) {
    const page = await browser.newPage({ viewport: { width: job.w, height: job.h }, deviceScaleFactor: job.scale || 1 });
    await page.goto('file://' + path.resolve(job.html), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.png, clip: { x: 0, y: 0, width: job.w, height: job.h } });
    await page.close();
  }
  await browser.close();
})();
