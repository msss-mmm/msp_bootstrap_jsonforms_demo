import { test, expect } from '@playwright/test';

test('verify alignment between editable and read-only', async ({ page }) => {
  // Use document 1 which is seeded by seed_data
  await page.goto('http://localhost:5173/documents/1');

  // Wait for the form to be rendered
  await page.waitForSelector('.document-edit');

  // Take a screenshot of the main content
  await page.screenshot({ path: 'verification/screenshots/alignment_form_final_v4.png' });

  // Now emulate print
  await page.emulateMedia({ media: 'print' });
  // Wait for styles to apply
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'verification/screenshots/alignment_form_print_v4.png' });
});
