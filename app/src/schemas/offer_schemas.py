from pydantic import BaseModel


class OfferOut(BaseModel):
    # from yandex api
    sku: str
    name: str
    weight: float
    length: float
    width: float
    height: float
    volume_from_yandex: float
    photo: str | None
    remaining_stock: int
    minimum_group_price: float
    name_of_shop: str
    group_sellers_amount: int

    # countable/editable values
    parches: float
    settlement_price_factor: float
    volume: float
    cost_price: float
    settlement_price_factor: float
    minimum_markup: float
    settlement_price: float
    price_before_discount: float
    profit: float
    payback: float
    fby: float

    # User additional fields
    notation_1: str | None = None
    notation_2: str | None = None
    notation_3: str | None = None

    automatic_price_management: bool = True
    manual_control_min_price: bool = False

    class Config:
        orm_mode = True


class OfferChange(BaseModel):
    sku: str
    parches: float
    minimum_markup: float
    settlement_price_factor: float

    notation_1: str | None = None
    notation_2: str | None = None
    notation_3: str | None = None

    automatic_price_management: bool = True
    manual_control_min_price: bool = False
