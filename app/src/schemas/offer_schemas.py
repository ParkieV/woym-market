from pydantic import BaseModel


class OfferOut(BaseModel):
    # from yandex api
    sku: str
    name: str
    weight: float
    length: float
    width: float
    height: float
    current_price: float
    volume_yandex: float
    photo: str | None
    remaining_stock: int
    minimum_group_price: float
    name_of_shop: str
    group_sellers_amount: int
    business_id: int

    # countable/editable values
    dollar_cost_price: float
    total_price_coeff: float
    volume: float
    cost_price: float
    total_price_min_additional: float
    total_price: float
    discount_base_price: float
    profit: float
    margin: float
    fby: float

    current_price: float | None

    # User additional fields
    note_1: str | None = None
    note_2: str | None = None
    note_3: str | None = None

    use_manual_min_price: bool = True # использовать ли автоматический расчет нижней планки цены
    auto_min_price: float # в процентах
    manual_min_price: float | None = None

    auto_price_control: bool = False # автоматическое управление ценами

    # auto_min_price: float
    # use_manual_min_price: bool = False

    class Config:
        orm_mode = True


class OfferChange(BaseModel):
    sku: str
    dollar_cost_price: float
    total_price_min_additional: float
    total_price_coeff: float

    note_1: str | None = None
    note_2: str | None = None
    note_3: str | None = None

    use_manual_min_price: bool = True # использовать ли автоматический расчет нижней планки цены
    auto_min_price: float # в процентах
    manual_min_price: float | None = None
    auto_price_control: bool = False # ручное управление ценами


class OfferDelete(BaseModel):
    sku: str

