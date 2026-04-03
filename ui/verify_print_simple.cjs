const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/documents/1');
  await page.waitForSelector('.document-edit');

  // Emulate print media
  await page.emulateMedia({ media: 'print' });

  // Wait a bit for styles to settle
  await page.waitForTimeout(1000);

  await page.screenshot({ path: 'verification/screenshots/print_view.png', fullPage: true });
  await browser.close();
  console.log('Print view screenshot saved to verification/screenshots/print_view.png');
})();
