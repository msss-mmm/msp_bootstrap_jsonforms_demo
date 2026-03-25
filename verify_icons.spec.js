const { test, expect } = require('@playwright/test');

test('Verify icons in designer and detail views', async ({ page }) => {
  // Go to Home
  await page.goto('http://localhost:5173/');
  await page.waitForSelector('.el-table');
  await page.screenshot({ path: 'home_view.png' });

  // Go to first document detail (if exists)
  const firstDoc = await page.locator('.el-table__row').first();
  if (await firstDoc.isVisible()) {
      await firstDoc.click();
      await page.waitForSelector('.document-detail');
      await page.screenshot({ path: 'document_detail.png' });
  }

  // Go to Designer
  await page.goto('http://localhost:5173/templates/new');
  await page.waitForSelector('.fc-designer');

  // Wait for the custom menu to be registered
  await page.waitForTimeout(2000);

  // Expand Workflow menu if it's collapsed
  const workflowMenu = page.locator('.el-collapse-item__header', { hasText: 'Workflow' });
  if (await workflowMenu.isVisible()) {
      const isExpanded = await workflowMenu.getAttribute('aria-expanded');
      if (isExpanded !== 'true') {
          await workflowMenu.click();
      }
  }

  await page.screenshot({ path: 'designer_view.png' });
});
