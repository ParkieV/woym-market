from datetime import datetime

from pydantic import Field

from src.database.models.models import Order
from src.schemas.filters.filter_schemas import BaseFilter


class OrderFilter(BaseFilter):
    __model = Order

    warehouse_ids: list[int] = Field(default_factory=list)
    offer_ids: list[int] = Field(default_factory=list)
    created_at_gte: datetime | None = None
    updated_at_lte: datetime | None = None

    def filter(self, query):
        if self.warehouse_ids:
            query = query.where(Order.warehouse_id.in_(self.warehouse_ids))

        if self.offer_ids:
            query = query.where(Order.offer_id.in_(self.offer_ids))

        if self.created_at_gte:
            query = query.where(Order.created_at >= self.created_at_gte)

        if self.created_at_lte:
            query = query.where(Order.created_at <= self.created_at_lte)

        return query
