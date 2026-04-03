const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Go to home first then navigate to ensure app is ready
  await page.goto('http://localhost:5173/');
  await page.waitForTimeout(1000);

  // Try to go to a document
  await page.goto('http://localhost:5173/documents/1');

  // Just wait for the main layout to be there
  await page.waitForSelector('.app-container', { timeout: 10000 });
  await page.waitForTimeout(2000);

  // Print screenshot
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'verification/screenshots/final_print_check.png', fullPage: true });

  await browser.close();
  console.log('Print check screenshot saved.');
})();
