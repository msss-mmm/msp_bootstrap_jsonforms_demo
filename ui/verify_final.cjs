const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Navigate to document 1
  await page.goto('http://localhost:5173/documents/1');

  // Wait for the document title to appear or skeleton to disappear
  // In the app, the document title is in the header
  await page.waitForSelector('.document-edit', { timeout: 10000 });

  // Wait for specific data fields to be populated to ensure data is there
  await page.waitForFunction(() => {
    const inputs = document.querySelectorAll('input');
    return inputs.length > 0 && Array.from(inputs).some(i => i.value !== '');
  }, { timeout: 10000 });

  // Screen screenshot
  await page.screenshot({ path: 'verification/screenshots/final_screen.png' });

  // Print screenshot
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'verification/screenshots/final_print.png' });

  await browser.close();
  console.log('Final screenshots saved.');
})();
