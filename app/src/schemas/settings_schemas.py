from datetime import datetime
from enum import Enum
from pydantic import BaseModel, json, Json


class LogsOut(BaseModel):
    updated_at: datetime | None


class SettingsOut(BaseModel):
    id: int
    user_id: int
    rate: float
    discount_purchase: float
    fby_sales_commission: float


class SettingsUpdate(BaseModel):
    rate: float
    discount_purchase: float
    fby_sales_commission: float = 19


class ColumnDataType(str, Enum):
    STRING = 'string'
    INTEGER = 'int'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    IMAGE = 'image'
    RUB = 'ruble'
    USD = 'dollar'
    PERCENT = 'percent'
    URL = 'url'
    COMBOBOX = 'combobox'


class Tables(str, Enum):
    OFFERS = 'offers'
    MATRIX_STOCKS = 'matrix_stocks'
    MATRIX_WAREHOUSES = 'matrix_warehouses'


class BaseColumn(BaseModel):
    table: Tables = Tables.OFFERS
    data: list | dict | None = None


class ColumnCreate(BaseColumn):
    pass


class ColumnUpdate(BaseColumn):
    id: int


class ColumnOut(ColumnUpdate):
    updated_at: datetime





