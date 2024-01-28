from datetime import datetime
from enum import Enum
from pydantic import BaseModel


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


class BaseColumn(BaseModel):
    index: int
    width: float = 120
    is_visible: bool = True


class ColumnUpdate(BaseColumn):
    key: str


class ColumnOut(ColumnUpdate):
    name: str
    data_type: ColumnDataType
    editable: bool
    tooltip: str = ''
    pinned: bool = False


class ColumnCreate(ColumnOut):
    pass


class ColumnFullUpdate(ColumnOut):
    pass



