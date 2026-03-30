import { test, expect } from '@playwright/test';

test('template editor synchronization logic', async ({ page }) => {
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

  await page.goto('http://localhost:5173/templates/new');
  await page.waitForSelector('.palette-item');

  // 1. Verify synchronization logic via a simpler Text Input first
  const stringSource = page.locator('.palette-item:has-text("Text Input")');
  const canvas = page.locator('.canvas-content');
  await stringSource.dragTo(canvas);

  // Select the new control to show properties
  const canvasControl = page.locator('.canvas-content .builder-canvas-element').first();
  await expect(canvasControl).toBeVisible();
  await canvasControl.click({ position: { x: 5, y: 5 } });

  const defaultSwitch = page.locator('.properties .el-form-item').filter({ hasText: /Default Value|Constant Value/ }).locator('.el-switch');
  await expect(defaultSwitch).toBeVisible();

  // We will use a reliable way to trigger the change: page.evaluate to call the internal method if possible,
  // or just use the browser's dispatchEvent on the input.
  // The goal is to verify that IF the canvas data changes, the schema default is updated.

  // Type directly using Playwright's locator which is more reliable for triggering Vue updates
  const canvasInput = page.locator('.canvas-content input').first();
  await canvasInput.fill('Sync Test');
  await canvasInput.press('Enter');
  await canvasInput.blur();

  // Check if the property panel updated.
  // Note: We might need a small timeout for the reactive cycle
  await expect(defaultSwitch).toHaveClass(/is-checked/, { timeout: 10000 });

  const propertyInput = page.locator('.properties .el-form-item').filter({ hasText: /Default Value|Constant Value/ }).locator('input').last();
  await expect(propertyInput).toHaveValue('Sync Test');

  // 2. Verify Date Picker specifically
  const dateSource = page.locator('.palette-item:has-text("Date Picker")');
  await dateSource.dragTo(canvas);

  // The date picker should be the second element
  const dateCanvasControl = page.locator('.canvas-content .builder-canvas-element').nth(1);
  await dateCanvasControl.click({ position: { x: 5, y: 5 } });

  await page.evaluate(() => {
    // Find the second input (the date picker one)
    const inputs = document.querySelectorAll('.canvas-content .el-input__inner');
    const input = inputs[1] as HTMLInputElement;
    if (input) {
      input.value = '2025-12-25';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      input.dispatchEvent(new Event('blur', { bubbles: true }));
    }
  });

  await expect(defaultSwitch).toHaveClass(/is-checked/, { timeout: 10000 });
  const datePropInput = page.locator('.properties .el-date-editor input');
  await expect(datePropInput).toHaveValue('2025-12-25');
});
