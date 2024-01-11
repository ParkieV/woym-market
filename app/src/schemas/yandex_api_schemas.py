from pydantic import BaseModel


class YandexOfferInfo(BaseModel):
    sku: str
    name: str
    weight: float
    length: float
    width: float
    height: float
    volume_yandex: float
    photo: str | None
    current_price: float | None
    business_id: int


class ExtendedYandexOfferInfo(YandexOfferInfo):
    remaining_stock: int
    minimum_group_price: float
    name_of_shop: str
    group_sellers_amount: int
    minimum_group_price_shop: str | None


class CampaignInfo(BaseModel):
    id: int
    business_id: int
    business_name: str