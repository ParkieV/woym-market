from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class LogsOut(BaseModel):
    updated_at: datetime | None


class SettingsOut(BaseModel):
    id: int
    user_id: int
    rate: float
    discount: float = 20
    discount_promotional: float = 0


class SettingsUpdate(BaseModel):
    rate: float
    discount: float = 20
    discount_promotional: float = 0


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
    width: float = 0
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



