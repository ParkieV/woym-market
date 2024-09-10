from pydantic import BaseModel, Field
from src.schemas.stocks.warehouses_schemas import WarehouseOut


class BaseOfferStock(BaseModel):
    current_stock: int = 0
    min_stock: int = 0
    for_delivery: int = 0
    can_be_delivered: bool = False
    advice_from_the_store: str = ''
    in_box: int = 1
    is_deliver_in_boxes: bool = False


class OfferFBOStockUpdate(BaseModel):
    id: int
    min_stock: int
    in_box: int
    is_deliver_in_boxes: bool


class OfferStockCreate(BaseOfferStock):
    offer_id: int
    warehouse_id: int


class OfferStockOut(BaseOfferStock):
    id: int


class OfferStockWithWarehouseOut(OfferStockOut):
    warehouse: WarehouseOut


class AggOfferFBOStock(BaseModel):
    offer_id: int = Field(title='ID карточки товара')
    min_stock: int = Field(title='Минимальный остаток товара')
    current_stock: int = Field(title='Текущий остаток по товару')
    for_delivery: int = Field(title='Требуется к поставке')
