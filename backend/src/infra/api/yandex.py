import asyncio





async def yandex_customer_price(vendor_code):
    url = f"https://market.yandex.ru/product--oblozhka-na-studencheskii-bilet-ne-otchisliaite-mem/{vendor_code}"
    pass


if __name__ == '__main__':
    result = asyncio.run(yandex_customer_price(1875949425))
    print(result)