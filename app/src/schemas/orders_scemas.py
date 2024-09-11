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


class OffersOrderQuantity(BaseModel):
    offer_id: int
    quantity: int
    warehouse_id: int


class OrdersQuantityStatOnlyOffers(BaseModel):
    offer_id: int
    today: int
    yesterday: int
    for_7_days: int
    for_14_days: int
    for_28_days: int
    for_60_days: int
    for_120_days: int
    smart_delivery: float

class OrdersQuantityStatOffersWithWarehouses(OrdersQuantityStatOnlyOffers):
    warehouse_id: int | None = None

