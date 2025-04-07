import aiohttp

async def wildberries_customer_price(vendor_code):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={vendor_code}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            product = data['data']['products'][0]
            return {
                "salePrice": product["salePriceU"] / 100
            }


async def ozon_customer_price(vendor_code):
    pass

async def yandex_customer_price(vendor_code):
    pass