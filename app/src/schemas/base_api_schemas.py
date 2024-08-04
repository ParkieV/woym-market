from dataclasses import dataclass
from enum import Enum
from typing import Union

import numpy as np


class WarehouseType(str, Enum):
    WAREHOUSE = 'warehouse'
    CLUSTER = 'cluster'


@dataclass(frozen=True)
class APIOffer:
    sku: str
    name: str
    name_of_shop: str

    yandex_weight: float | None = None
    yandex_length: float | None = None
    yandex_width: float | None = None
    yandex_height: float | None = None
    yandex_volume: float | None = None
    photo: str | None = None
    current_price: float | None = None
    business_id: int | None = None
    remaining_stock: int | None = None
    group_sellers_amount: int | None = None

    attractive_price_threshold: float | None = None
    moderately_attractive_price_threshold: float | None = None
    best_place_wm: str = ''
    min_price_without_market: float | None = None
    best_place_im: str = ''
    best_place_im_link: str = ''
    min_price_in_market: float | None = None
    min_general_markets_price: float | None = None
    your_price_for_buyers: float | None = None
    fbo: float | None = None
    barcodes: str | None = None
    your_promotion_price: float | None = None

    content_rating: float | None = None
    price_index: float | None = None
    # артикул - product id
    vendor_code: int | None = None
    search_words: str | None = None

    market: str = 'yandex'


@dataclass
class APIWarehouseOffer:
    sku: str
    name_of_shop: str
    current_stock: int = 0


@dataclass
class APIWarehouse:
    market: str
    name: str
    offers: list[APIWarehouseOffer]
    warehouse_type: WarehouseType = WarehouseType.WAREHOUSE
    related_warehouses_name: list[str] | None = None


@dataclass
class APIPriceChangeData:
    sku: str
    market: str
    name_of_shop: str
    target_price: Union[int, float, None]
    min_price: float
    auto_participation_in_promotions: bool
    auto_min_price: float | None = None
    search_words: str | None = None

    def is_valid_target_price(self) -> bool:
        return isinstance(self.target_price, (float, int)) and not np.isnan(self.target_price)

    def is_valid_min_price(self) -> bool:
        return isinstance(self.min_price, (float, int)) and not np.isnan(self.min_price)

    def is_valid_auto_min_price(self) -> bool:
        return isinstance(self.auto_min_price, (float, int)) and not np.isnan(self.auto_min_price)

    def is_valid_search_words(self) -> bool:
        return isinstance(self.search_words, str)

