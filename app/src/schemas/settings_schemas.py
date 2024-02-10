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


class BaseTableInfo(BaseModel):
    name: str
    data: str | None = None


class TableInfoCreate(BaseTableInfo):
    pass


class TableInfoUpdate(BaseTableInfo):
    pass


class TableInfoOut(TableInfoUpdate):
    updated_at: datetime





