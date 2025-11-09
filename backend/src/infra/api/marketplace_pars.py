import re

from logs import parser_logger
from src.database.interfaces import MarketplacePageParser
from playwright.async_api import async_playwright

class OzonPageParser(MarketplacePageParser):
    """
    Ozon-парсер
    """
    def __init__(self, base_uri: str, client: async_playwright):
        self._base_uri = base_uri
        self._client = client

    async def get_price(self, vendor_code: str) -> float | None:
        """
        Получение актуальной цены товара по вендор коду
        """
        url = f"{self._base_uri}/product/{vendor_code}"

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
                        'span.lz8_28.l8z_28.m3m_28',
                        'span[data-test-id="price"]',
                        '.ozon-price',
                        'span:has-text("₽")'
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
                    price_text = None
                    for selector in selectors:
                        element = await page.query_selector(selector)
                        if element and await element.is_visible():
                            price_text = await element.inner_text()
                            break

                    if not price_text:
                        raise Exception("Ценовой элемент не найден")

                    clean_price = re.sub(r'[^\d,.]', '', price_text)
                    clean_price = clean_price.replace(',', '.')
                    parts = clean_price.split('.')
                    if len(parts) > 2:
                        clean_price = parts[0] + '.' + ''.join(parts[1:])
                    price_value = float(clean_price)

                    return price_value

                except Exception as e:
                    parser_logger.error("Ошибка при получении цены: " + e)
                    return 0.0

                finally:
                    await browser.close()

        except Exception as e:
            parser_logger.error("Критическая ошибка: " + e)
            return 0.0


class WBPageParser(MarketplacePageParser):
    """
    WB-парсер
    """
    def __init__(self, base_uri: str, client: async_playwright()):
        self._base_uri = base_uri
        self._client = client

    async def get_price(self, vendor_code: str) -> float | None:
        """
        Получение актуальной цены товара по вендор коду у не авторизированного пользователя
        """
        url = f"{self._base_uri}/catalog/{vendor_code}/detail.aspx"
        # url = "https://www.wildberries.ru/catalog/160233100/detail.aspx"
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
                    locale='ru-RU'
                )
                page = await context.new_page()

                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=60000)

                    # Ожидание появления нужного элемента
                    await page.wait_for_selector('ins.price-block__final-price.wallet', state='attached', timeout=15000)

                    # Получение текста цены
                    element = await page.query_selector('ins.price-block__final-price.wallet')
                    price_text = await element.inner_text() if element else None

                    if not price_text:
                        return None

                    price_number = re.sub(r'[^\d]', '', price_text)

                    if not price_number:
                        return None
                    print(price_number)
                    return float(price_number)

                except Exception as e:
                    parser_logger.error("Ошибка при парсинге цены WB: "+e)
                    return None

                finally:
                    await browser.close()

        except Exception as e:
            parser_logger.error("Критическая ошибка браузера WB: " + e)
            return None