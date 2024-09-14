from pydantic import Field

from src.database.models.models import Offer
from src.schemas.filters.filter_schemas import BaseFilter


class BaseOffersFilter(BaseFilter):
    pass


class OffersSourceFilter(BaseOffersFilter):
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

    def __call__(self, query, *args, **kwargs):
        query = super().__call__(query, *args, **kwargs)

        if self.offer_ids:
            query = query.where(Offer.id.in_(self.offer_ids))

        if self.pricing_scheme_name:
            query = query.where(Offer.pricing_scheme_name == self.pricing_scheme_name)

        if self.synchronization is not None:
            query = query.where(Offer.synchronization == self.synchronization)

        return query


