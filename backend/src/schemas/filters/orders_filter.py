
from pydantic import Field

from src.database.models.models import Order
from src.schemas.filters.filter_schemas import BasePydanticFilter


class OrderFilter(BasePydanticFilter):
    __model = Order

    warehouse_ids: list[int] = Field(default_factory=list)
    offer_ids: list[int] = Field(default_factory=list)


    def __call__(self, query):
        if self.warehouse_ids:
            query = query.where(Order.warehouse_id.in_(self.warehouse_ids))

        if self.offer_ids:
            query = query.where(Order.offer_id.in_(self.offer_ids))

        return query
