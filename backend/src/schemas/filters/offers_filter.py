from collections.abc import Sequence

from pydantic import Field
from sqlalchemy import select

from src.database.models.models import Offer, CatalogItem
from src.schemas.filters.filter_schemas import BaseFilter



class OffersSourceFilter(BaseFilter):
    market: str | None = Field(default=None, title='Маркетплейс')
    name_of_shop: str | None = Field(default=None, title='Название магазина на маркетплейсе')

    def __call__(self, query, *args, **kwargs):
        if self.market:
            query = query.where(Offer.market == self.market)

        if self.name_of_shop:
            query = query.where(Offer.name_of_shop == self.name_of_shop)

        return query

class OffersFilter(OffersSourceFilter):
    offer_ids: list[int] | None = Field(default=None, title='ID Карточки товара в системе')
    pricing_scheme_name: str | None = Field(default=None, title='Схема ценообразования')
    synchronization: bool | None = Field(default=None, title='Синхронизация карточки товара с каталогом')
    reverse_synchronization: bool | None = Field(default=None, title='Обратная синхронизация')

    def __call__(self, query, *args, **kwargs):
        query = super().__call__(query, *args, **kwargs)

        if self.offer_ids:
            query = query.where(Offer.id.in_(self.offer_ids))

        if self.pricing_scheme_name:
            query = query.where(Offer.pricing_scheme_name == self.pricing_scheme_name)

        if self.synchronization is not None:
            query = query.where(Offer.synchronization == self.synchronization)

        return query

class SKUOnlyOffersFilter(BaseFilter):
    """ Filter for getting DB objects, which there are in Offer, but no in CatalogItem. """

    markets: Sequence[str] | None = Field(default=None, title='Маркетплейс')
    names_of_shops: Sequence[str] | None = Field(default=None, title='Название магазина на маркетплейсе')
    offer_ids: Sequence[int] | None = Field(default=None, title='ID Карточки товара в системе')

    def __call__(self, query):
        if self.markets:
            query = query.where(Offer.market.in_(self.markets))

        if self.names_of_shops:
            query = query.where(Offer.name_of_shop.in_(self.names_of_shops))

        if self.offer_ids:
            query = query.where(Offer.id.in_(self.offer_ids))

        query = query.where(~Offer.sku.in_(select(CatalogItem.sku)))

        return query
