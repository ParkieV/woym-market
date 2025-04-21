import asyncio
import re

from playwright.async_api import async_playwright


async def yandex_customer_price(vendor_code):
    url = f"https://market.yandex.ru/product--briuki-banany-klassicheskie/322343332"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU'
        )
        page = await context.new_page()
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # Используем locator для поиска элемента
        price_locator = page.locator("span.ds-text.ds-text_weight_reg.ds-text_color_text-secondary.ds-text_typography_text.ds-text_text_loose.ds-text_text_reg")
        price_text = await price_locator.first.inner_text()

        await browser.close()

        # Удаляем все символы, кроме цифр
        digits_only = re.sub(r"[^\d]", "", price_text)

        return int(digits_only) if digits_only else -1  # -1 если не удалось извлечь цену


if __name__ == '__main__':
    result = asyncio.run(yandex_customer_price(1875949425))
    print(result)