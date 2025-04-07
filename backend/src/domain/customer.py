from src.database.db import async_session
from src.database.models.models import Offer
from src.database.offer import get_offers_fields, update_price_in_db
from src.services.parse_marketplace import wildberries_customer_price, ozon_customer_price, yandex_customer_price


async def change_price():
    with async_session() as session:
        vendor_codes = await get_offers_fields(session, [Offer.market, Offer.vendor_code])

        for vendor_code in vendor_codes:
            market = vendor_code["market"]
            vendor_code = vendor_code["vendor_code"]

            if market == "wildberries":
                price = await wildberries_customer_price(vendor_code)
            elif market == "ozon":
                price = await ozon_customer_price(vendor_code)
            elif market == "yandex":
                price = await yandex_customer_price(vendor_code)

            if price is not None:
                await update_price_in_db(session, vendor_code, price)
