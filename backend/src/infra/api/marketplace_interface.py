from src.infra.api.ozon import ozon_customer_price
from src.infra.api.wildberries import wildberries_customer_price
from src.infra.api.yandex import yandex_customer_price
from src.schemas.offer_schemas import Market


class MarketplaceParsing:
    def __init__(self, marketplace: str):
        self.marketplace = marketplace

    async def get_marketplace_price_for_vendor_code(self, vendor_code: int):
        if self.marketplace == Market.OZON:
            return await ozon_customer_price(vendor_code)
        elif self.marketplace == Market.YANDEX:
            return await yandex_customer_price(vendor_code)
        elif self.marketplace == Market.WILDBERRIES:
            return await wildberries_customer_price(vendor_code)
        else:
            raise Exception(f"Unknown marketplace {self.marketplace}")