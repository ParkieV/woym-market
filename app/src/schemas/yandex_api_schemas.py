from dataclasses import dataclass


@dataclass(frozen=True)
class YandexOfferInfoPartial:
    sku: str
    name: str
    yandex_weight: float
    yandex_length: float
    yandex_width: float
    yandex_height: float
    yandex_volume: float
    photo: str | None
    current_price: float | None
    business_id: int


@dataclass(frozen=True)
class YandexOfferInfo(YandexOfferInfoPartial):
    remaining_stock: int
    name_of_shop: str
    group_sellers_amount: int

    attractive_price_threshold: float | None
    moderately_attractive_price_threshold: float | None
    best_place_wm: str | None
    best_price_wm: float | None
    best_place_im: str | None
    best_price_im: float | None
    minimum_group_price: float | None
    your_price_for_buyers: float | None

    market: str = 'yandex'


@dataclass(frozen=True)
class BusinessInfo:
    id: int
    name: str


@dataclass(frozen=True)
class CampaignInfo:
    id: int
    client_id: int
    domain: str
    business: BusinessInfo

