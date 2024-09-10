from datetime import datetime

from pydantic import BaseModel, Field


class GroupStatFilter(BaseModel):
    days_interval: int = Field(title='Интервал', description='Количество последних дней, за которые будет генерироваться информация о заказах.')
    field_name: str = Field(title='Выходное поле', description='Название поля, в котором будет находиться информация о количестве заказов')


class OrderStatisticFilter(BaseModel):
    # periods: list[GroupStatFilter] = Field(default_factory=list, title='Периоды', description='Периоды, по которым генерируются статистические данные')
    group_by_warehouses: bool = Field(default=False, title='Агрегирровать данные по складам', description='Если false, то группировка будет выполнена без участия складов, warehouse_id в таком случае приходить не будет')
    warehouse_ids: list[int] = Field(default_factory=list, title='Список id складов', description='Если передан пустой / не передан, то информация придет по всем складам. Параметр игнорируется, если group_by_warehouses = false')
    offer_ids: list[int] = Field(default_factory=list, title='Список id товаров', description='Если передан пустой / не передан, то информация придет по всем товарам')

