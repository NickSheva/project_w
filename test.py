"""Using asyncio for corutines"""
import asyncio
from playwright.async_api import async_playwright


async def test_browser(p, browser_type):
    """Testing browsers"""
    browser = await browser_type.launch()
    context = await browser.new_context()
    page = await context.new_page()
    url = "https://lombard-perspectiva.ru/clocks_today/"
    await page.goto(url, wait_until="commit")
    title = await page.title()
    print(f"Testing in {browser_type.name}. Title: {title}")
    await browser.close()


async def main():
    """Running function simultaneously with asyncio.gather()"""
    async with async_playwright() as playwright:
        tasks = [
            test_browser(playwright, playwright.chromium),
            test_browser(playwright, playwright.webkit),
            test_browser(playwright, playwright.firefox),            ]
        await asyncio.gather(*tasks)

asyncio.run(main())
