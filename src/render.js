// Renderiza cada HTML a PDF vectorial con Chromium (Playwright).
// Uso: node src/render.js trabajo.json
// trabajo.json = [{"html": "ruta.html", "pdf": "ruta.pdf", "w_mm": 111, "h_mm": 154.8}, ...]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const job of jobs) {
    await page.goto('file://' + path.resolve(job.html), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({
      path: job.pdf,
      width: `${job.w_mm}mm`,
      height: `${job.h_mm}mm`,
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    });
    console.log('  pdf →', job.pdf);
  }
  await browser.close();
})();
