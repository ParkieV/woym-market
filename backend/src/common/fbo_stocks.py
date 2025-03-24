from pydantic import BaseModel


class FboOffer(BaseModel, frozen=True):
    id: int
    note_1: str
    note_2: str
    note_3: str
    supplier_available: bool
    hidden: bool

class FboStock(BaseModel, frozen=True):
    stock_id: int
    offer_id: int
    warehouse_id: int
    can_be_delivered: bool
    advice_from_the_store: str
    current_stock: int
    in_box: int
    is_deliver_in_boxes: int
    min_stock: int
    for_deliver: int
