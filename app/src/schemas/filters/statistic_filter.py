from datetime import datetime

from pydantic import BaseModel, Field


class OrderStatisticFilter(BaseModel):
    warehouse_ids: list[int] = Field(default_factory=list, title='Список id складов', description='Если передан пустой / не передан, то информация придет по всем складам')
    offer_ids: list[int] = Field(default_factory=list, title='Список id товаров', description='Если передан пустой / не передан, то информация придет по всем товарам')

