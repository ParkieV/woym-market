from datetime import datetime
from enum import Enum
from pydantic import BaseModel, json, Json

from src.api.factory import APITypes


class LogsOut(BaseModel):
    updated_at: datetime | None


class SettingsOut(BaseModel):
    id: int
    user_id: int
    rate: float
    fbo_sales_commission: float


class SettingsUpdate(BaseModel):
    rate: float
    fbo_sales_commission: float = 19


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


class BaseTableInfo(BaseModel):
    data: str | None = None
    name: str


class TableInfoCreate(BaseTableInfo):
    pass


class TableInfoUpdate(BaseTableInfo):
    pass


class TableInfoOut(TableInfoUpdate):
    updated_at: datetime


class MarketOut(BaseModel):
    id: int
    name: str
    tax: float = 0
    type: APITypes
    discount_purchase: float
    long_term_storage_cost: float | None


class MarketUpdate(BaseModel):
    tax: float = 0
    discount_purchase: float
    long_term_storage_cost: float | None = None


class MarketFullOut(MarketOut):
    token: str
    entity_id: int


class MarketFullUpdate(MarketFullOut):
    pass


class MarketCreate(BaseModel):
    name: str
    tax: float = 0
    type: APITypes
    token: str
    entity_id: int

