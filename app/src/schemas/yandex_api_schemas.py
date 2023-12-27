from pydantic.main import BaseModel


class YandexOfferInfo(BaseModel):
    sku: str
    name: str
    weight: float
    length: float
    width: float
    height: float
    volume_from_yandex: float
    photo: str | None
    market_price: float


class ExtendedYandexOfferInfo(YandexOfferInfo):
    remaining_stock: int
    minimum_group_price: float
    name_of_shop: str
    group_sellers_amount: int


class CampaignInfo(BaseModel):
    id: int
    business_id: int
    business_name: str