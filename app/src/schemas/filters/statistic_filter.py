from datetime import datetime

from pydantic import BaseModel, Field


class GroupStatFilter(BaseModel):
    days_interval: int
    group_name: str


class OrderStatisticFilter(BaseModel):
    periods: list[GroupStatFilter] | None = Field(default_factory=list)
    group_by_warehouses: bool = False
    warehouse_ids: list[int] = Field(default_factory=list)
    offer_ids: list[int] = Field(default_factory=list)

