import asyncio
from playwright.async_api import async_playwright
import time
import os

async def verify_date_time_debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        await page.goto('http://localhost:5173/templates/new')
        await page.wait_for_selector('.palette-item')

        # Drag Date Picker
        await page.locator('.palette-item:has-text("Date Picker")').drag_to(page.locator('.canvas-content'))

        # Click Date Picker on canvas to select it (so property panel shows it)
        await page.locator('.canvas-content .el-input__inner').first.click()

        # Instead of trying to click the calendar, let's use JS to trigger a change
        # This will test if our @change and watchers work.
        # We need to find the correct el-date-picker instance
        await page.evaluate('''() => {
            const input = document.querySelector('.canvas-content .el-input__inner');
            // Element Plus DatePicker uses a custom change event but also standard ones.
            // Better to trigger the internal Vue update if possible,
            // but since we are in a headless browser, we can try to emit the event.
            input.value = '2025-05-20';
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }''')

        await page.wait_for_timeout(2000)

        # Now check properties panel
        default_val = await page.locator('.properties input.el-input__inner').nth(3).get_attribute('value') # nth(3) is a guess, let's be more specific

        # Let's take a screenshot
        os.makedirs('/home/jules/verification/screenshots', exist_ok=True)
        await page.screenshot(path='/home/jules/verification/screenshots/verification_debug.png')

        print(f"Default Value in Props: {default_val}")

        await browser.close()

if __name__ == '__main__':
    time.sleep(5)
    asyncio.run(verify_date_time_debug())
