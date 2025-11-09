from playwright.async_api import async_playwright

from src.database.interfaces import MarketplacePageParser
from src.infra.api.marketplace_pars import OzonPageParser, WBPageParser
from src.schemas.offer_schemas import Market


class ParserFactory:
    @staticmethod
    def create_parser(market: Market, client: async_playwright) -> MarketplacePageParser:
        base_uris = {
            Market.OZON: "https://www.ozon.ru",
            Market.WILDBERRIES: "https://www.wildberries.ru",
        }

        parsers = {
            Market.OZON: OzonPageParser,
            Market.WILDBERRIES: WBPageParser,
        }

        if market not in parsers:
            raise ValueError(f"Парсер для маркета {market} не реализован")

        return parsers[market](base_uris[market], client)
