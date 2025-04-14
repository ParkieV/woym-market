import asyncio
import re

import aiohttp
from playwright.async_api import async_playwright


async def wildberries_customer_price_api(vendor_code):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={vendor_code}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            product = data['data']['products'][0]
            return {
                "salePrice": product["salePriceU"] / 100
            }


async def wildberries_customer_price(vendor_code):
    url = f"https://www.wildberries.ru/catalog/{vendor_code}/detail.aspx"
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

        # Ожидание появления нужного элемента
        await page.wait_for_selector('ins.price-block__final-price.wallet', state='attached', timeout=15000)
        # Получение текста цены без дополнительных проверок
        element = await page.query_selector('ins.price-block__final-price.wallet')
        price_text = await element.inner_text() if element else None
        await browser.close()

        if not price_text:
            return None

        price_number = re.sub(r'[^\d]', '', price_text)
        return int(price_number) if price_number else "Ошибка при извлечении числа"

if __name__ == '__main__':
    result = asyncio.run(wb_customer_price("189328347"))
    print(result)