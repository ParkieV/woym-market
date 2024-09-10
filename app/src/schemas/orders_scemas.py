from datetime import datetime
from src.schemas.stocks.warehouses_schemas import WarehouseOut
from pydantic import BaseModel


class OrderCreate(BaseModel):
    sku: str
    name_of_shop: str
    offer_id: int
    market: str
    quantity: int
    price: float | None
    warehouse_id: int
    created_at: datetime
    updated_at: datetime | None


class OrderOut(OrderCreate):
    id: int


class OrderWithWarehouseOut(OrderOut):
    warehouse: WarehouseOut


class OffersOrderQuantityStat(BaseModel):
    offer_id: int
    quantity: int
    warehouse_id: int

