from pydantic import Field, BaseModel

from src.database.models.models import Warehouse, OfferStock
from src.schemas.filters.filter_schemas import BaseFilter, BasePydanticFilter
from src.schemas.stocks.warehouses_schemas import WarehouseTypes


class WarehousesFilter(BasePydanticFilter):
    warehouse_type: WarehouseTypes | None = Field(default=None, title='Тип склада')
    market: str | None = Field(default=None, title='Маркетплейс')

    def __call__(self, query):
        if self.warehouse_type:
            query = query.where(Warehouse.warehouse_type == self.warehouse_type)

        if self.market:
            query = query.where(Warehouse.market == self.market)

        return query


class FBOStocksFilter(BasePydanticFilter):
    warehouse_ids: list[int] | None = Field(default=None, title='Id складов в системе сервиса')
    offer_ids: list[int] | None = Field(default=None, title='Id карточек товаров')

    def __call__(self, query):
        if self.warehouse_ids:
            query = query.where(OfferStock.warehouse_id.in_(self.warehouse_ids))

        if self.offer_ids:
            query = query.where(OfferStock.offer_id.in_(self.offer_ids))

        return query
