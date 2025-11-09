from typing import Iterable

from playwright.async_api import async_playwright
from sqlalchemy.ext.asyncio import AsyncSession

from logs import parser_logger
from src.database.interfaces import MarketplacePageParser, IOfferRepository
from src.infra.api.parser_fabric import ParserFactory
from src.schemas.offer_schemas import OfferListing, OfferTargetPrice


async def get_target_price(
        offer_listing: OfferListing,
        parser: MarketplacePageParser
) -> OfferTargetPrice:
    """Получить целевую цену"""
    try:
        price: float = await parser.get_price(offer_listing.vendor_code)
        return OfferTargetPrice(
            offer_listing=offer_listing,
            price=price
        )
    except Exception as e:
        raise Exception(f"Ошибка получения цены для {offer_listing.vendor_code}: {str(e)}")


async def update_target_price(
        offer_listing_iter: Iterable[OfferListing],
        offer_repository: IOfferRepository,
        playwright_client: async_playwright
) -> None:
    """Обновить целевые цены"""
    for offer_listing in offer_listing_iter:
        try:
            parser: MarketplacePageParser = ParserFactory.create_parser(offer_listing.market, playwright_client)
            target_price: OfferTargetPrice = await get_target_price(offer_listing, parser)

            # Формируем идентификатор и данные для обновления
            identification: str = str(offer_listing.id)

            # Обновляем через репозиторий
            await offer_repository.update(identification, target_price)

        except Exception as e:
            parser_logger.error(f"Error processing {offer_listing.vendor_code}: {e}")
            continue


# async def main():
#     async with AsyncSession() as db_session:
#         offer_repo = OfferRepository(db_session)
#         offer_listings = await offer_repo.offer_list()
#
#         async with async_playwright() as playwright:
#             await update_target_price(db_session, offer_listings, offer_repo, playwright)