import asyncio
import re

from playwright.async_api import async_playwright


async def ozon_customer_price(vendor_code):
    url = f"https://www.ozon.ru/product/{vendor_code}"

    try:
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
                locale='ru-RU',
                color_scheme='light'
            )

            page = await context.new_page()

            try:
                await page.goto(url, wait_until='networkidle', timeout=90000)

                selectors = [
                    'span.lz8_28.l8z_28.m3m_28',  # Новые классы
                    'span[data-test-id="price"]',  # Data-атрибут
                    '.ozon-price',  # Общий класс
                    'span:has-text("₽")'  # По наличию символа валюты
                ]

                await page.wait_for_selector(
                    ','.join(selectors),
                    state='attached',
                    timeout=15000
                )

                # Прокрутка для активации ленивой загрузки
                await page.mouse.wheel(0, 500)
                await page.wait_for_timeout(1000)

                # Поиск по приоритету селекторов
                for selector in selectors:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        price_text = await element.inner_text()
                        break
                else:
                    raise Exception("Ценовой элемент не найден")

                # Очистка и преобразование цены
                price = re.sub(r'[^\d]', '', price_text)
                if not price:
                    raise ValueError("Не удалось извлечь цену")

                return f"Актуальная цена: {price} руб."

            except Exception as e:
                return f'Ошибка: {str(e)}'

            finally:
                await browser.close()

    except Exception as e:
        return f'Критическая ошибка: {str(e)}'

if __name__ == '__main__':
    result = asyncio.run(ozon_customer_price(1875949425))
    print(result)