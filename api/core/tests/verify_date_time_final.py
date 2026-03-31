import asyncio
from playwright.async_api import async_playwright
import time
import os

async def verify_date_time():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # Go to the new template page
        await page.goto('http://localhost:5173/templates/new')
        await page.wait_for_selector('.palette-item')

        # Drag Date Picker to Canvas
        date_picker_source = page.locator('.palette-item:has-text("Date Picker")')
        canvas = page.locator('.canvas-content')

        await date_picker_source.drag_to(canvas)

        # Click on the Date Picker on Canvas to select it
        # The control is rendered by JsonForms
        date_input = page.locator('.canvas-content .el-input__inner')
        await date_input.click()

        # Click on the input to open the calendar
        # Element Plus date picker opens a popup in the body
        await page.wait_for_selector('.el-picker-panel', state='visible')

        # Select a date (e.g., "15")
        # Find a cell with text "15" that is not from prev/next month
        await page.click('.el-date-table td.available:has-text("15")')

        # Wait for popup to close
        await page.wait_for_selector('.el-picker-panel', state='hidden')

        # Check if the value is in the input
        val = await date_input.get_attribute('value')
        print(f"Canvas Date Value: {val}")

        # Check if "Default Value" switch is ON and shows the value
        # It should have been automatically turned on by our watcher
        default_switch = page.locator('.properties .el-switch')
        is_on = await default_switch.get_attribute('aria-checked')
        print(f"Default Value Switch ON: {is_on}")

        default_input = page.locator('.properties .el-date-editor input')
        default_val = await default_input.get_attribute('value')
        print(f"Properties Default Value: {default_val}")

        os.makedirs('/home/jules/verification/screenshots', exist_ok=True)
        await page.screenshot(path='/home/jules/verification/screenshots/verification_final.png')

        await browser.close()

if __name__ == '__main__':
    # Give the dev server some time to start
    time.sleep(5)
    asyncio.run(verify_date_time())
