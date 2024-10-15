from datetime import datetime
from src.schemas.stocks.warehouses_schemas import WarehouseOut
from pydantic import BaseModel


class OrderCreate(BaseModel):
    internal_order_id: str
    sku: str
    name_of_shop: str
    offer_id: int
    market: str
    quantity: int
    price: float | None
    warehouse_id: int | None
    created_at: datetime
    updated_at: datetime | None


class OrderOut(OrderCreate):
    id: int


class OrderWithWarehouseOut(OrderOut):
    warehouse: WarehouseOut | None


class OffersOrderQuantity(BaseModel):
    offer_id: int
    quantity: int
    warehouse_id: int | None


class OrdersQuantityStatOnlyOffers(BaseModel):
    offer_id: int
    today: int
    yesterday: int
    for_7_days: int
    for_14_days: int
    for_28_days: int
    for_60_days: int
    for_120_days: int
    smart_delivery: float = 0


class OrdersQuantityStatOffersWithWarehouses(OrdersQuantityStatOnlyOffers):
    warehouse_id: int | None = None

