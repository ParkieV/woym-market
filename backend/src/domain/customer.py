import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import async_session
from src.database.offer import get_offers_vendor_data
from src.infra.api.marketplace_interface import MarketplaceParsing

vendor_code_list = [
    ("wildberries", "388096307"),
    ("wildberries", "346611840"),
    ("wildberries", "245096308"),
    ("ozon", "204953794"),
]


async def set_target_price(session: AsyncSession, vendor_code_list: list[tuple[str, str]]):
    prices = []

    for marketplace, vendor_code in vendor_code_list:
        try:
            parser = MarketplaceParsing(marketplace)

            price = await parser.get_marketplace_price_for_vendor_code(int(vendor_code))

            prices.append({
                'marketplace': marketplace,
                'vendor_code': vendor_code,
                'price': price
            })

        except Exception as e:
            print(f"Ошибка {marketplace} с vendor_code {vendor_code}: {str(e)}")

    return prices


async def get_and_set_prices(
        session: AsyncSession,
) -> list[dict[str, Any]]:
    offers = await get_offers_vendor_data(session)

    vendor_code_list = [
        (offer['market'], str(offer['vendor_code']))
        for offer in offers
        if offer['vendor_code'] is not None
    ]

    prices = await set_target_price(session, vendor_code_list)

    offer_map = {
        (offer['market'], str(offer['vendor_code'])): offer['id']
        for offer in offers
        if offer['vendor_code'] is not None
    }

    for price_data in prices:
        key = (price_data['marketplace'], price_data['vendor_code'])
        price_data['offer_id'] = offer_map.get(key)

    return prices


async def main():
    async with async_session() as session:
        prices = await get_and_set_prices(session)
        print(prices)


if __name__ == '__main__':
    result = asyncio.run(main())
    print(result)
