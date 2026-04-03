import { test, expect } from '@playwright/test';

test('verify print styles', async ({ page }) => {
  await page.goto('http://localhost:5173/documents/1');
  await page.waitForSelector('.document-edit');

  // Set to print media
  await page.emulateMedia({ media: 'print' });

  // Take screenshot of the form in print mode
  await page.screenshot({ path: 'verification/screenshots/print_verification.png', fullPage: true });
});
