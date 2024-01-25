from datetime import datetime

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


class BaseColumn(BaseModel):
    index: int
    width: float = 0
    is_visible: bool = True


class ColumnUpdate(BaseColumn):
    id: int


class ColumnOut(ColumnUpdate):
    name: str
    key: str
    data_type: str
    editable: bool = True


