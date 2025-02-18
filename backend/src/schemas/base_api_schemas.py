import json
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Union, Any

import numpy as np
from pydantic import BaseModel, field_validator, ValidationError, Field
from pydantic_core.core_schema import FieldValidationInfo


class WarehouseType(str, Enum):
    WAREHOUSE = 'warehouse'
    CLUSTER = 'cluster'
    SUPER_WAREHOUSE = 'super_warehouse'
    SUPER_CLUSTER = 'super_cluster'


class APIOffer(BaseModel):
    sku: str
    name: str
    name_of_shop: str
    description: str | None = None
    self_weight: float | None = None
    self_length: float | None = None
    self_width: float | None = None
    self_height: float | None = None
    volume: float | None = None
    photo: str | None = None
    current_price: float | None = None
    seller_discount: float | None = None
    business_id: int | None = None
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
    price_index: str | None = None
    # артикул - product id
    vendor_code: int | None = None
    search_words: str | None = None
    market: str = 'yandex'

    @field_validator('self_length', 'self_width', 'self_height', 'self_weight', mode='before')
    @classmethod
    def convert_sizes(cls, value: Any, info: FieldValidationInfo) -> float | None:
        match value:
            case float():
                return value
            case int():
                return float(value)
            case None:
                return None
            case _:
                raise ValidationError(f"Attribute '{info.field_name}' should be an float")


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
    vendor_code: int | None = None
    discount_base_price: float | None = None

    def is_valid_target_price(self) -> bool:
        return isinstance(self.target_price, (float, int)) and not np.isnan(self.target_price)

    def is_valid_min_price(self) -> bool:
        return isinstance(self.min_price, (float, int)) and not np.isnan(self.min_price)

    def is_valid_auto_min_price(self) -> bool:
        return isinstance(self.auto_min_price, (float, int)) and not np.isnan(self.auto_min_price)

    def is_valid_discount_base_price(self) -> bool:
        return isinstance(self.discount_base_price, (float, int)) and not np.isnan(self.discount_base_price)

    def is_valid_vendor_code(self) -> bool:
        return isinstance(self.vendor_code, int) and not np.isnan(self.vendor_code)


class APIOfferChangeData(BaseModel):
    sku: str
    market: str
    name_of_shop: str
    name: str | None = None
    description: str | None = None
    vendor_code: int | None = None
    search_words: str | None = None
    barcodes: str | None = None
    self_weight: float | None = None
    self_length: float | None = Field(default=None, strict=False)
    self_width: float | None = Field(default=None, strict=False)
    self_height: float | None = Field(default=None, strict=False)

    def is_valid_vendor_code(self) -> bool:
        return isinstance(self.vendor_code, int) and not np.isnan(self.vendor_code)

    def is_valid_barcodes(self) -> bool:
        return isinstance(self.barcodes, str)

    def is_valid_name(self) -> bool:
        return isinstance(self.name, str)

    def is_valid_description(self) -> bool:
        return isinstance(self.description, str)

    def is_valid_search_words(self) -> bool:
        return isinstance(self.search_words, str)

    def is_valid_sizes(self) -> (bool, dict):
        dimensions = namedtuple('dimensions', ('self_weight', 'self_width', 'self_height', 'self_length'))
        sizes = dimensions(self.self_weight, self.self_width, self.self_height, self.self_length)
        invalid_sizes = {}
        fl = True

        for i in sizes:
            if not isinstance(i, (int, float)):
                fl = False
                invalid_sizes[i.__name__] = i
            elif np.isnan(i):
                fl = False
                invalid_sizes[i.__name__] = i

        if fl:
            return True, dict()
        else:
            return False, invalid_sizes

    @property
    def valid_barcodes(self) -> list[str]:
        if not self.is_valid_barcodes():
            raise ValueError(f'Invalid barcodes for sku {self.sku}: "{self.barcodes}"')

        return self.barcodes.replace(';', ' ').replace(',', ' ').split()

    @field_validator('vendor_code', mode='before')
    @classmethod
    def validate_vendor_code(cls, value: Any, info: FieldValidationInfo) -> int | None:
        match value:
            case int():
                return value
            case float():
                if np.isnan(value):
                    return None
                else:
                    return int(value)
            case _:
                raise ValidationError(f"Attribute '{info.field_name}' should be an integer")

    @field_validator('self_length', 'self_width', 'self_height', 'self_weight', mode='before')
    @classmethod
    def validate_dimensions(cls, value: Any, info: FieldValidationInfo) -> float | None:
        match value:
            case int():
                return float(value)
            case float():
                if np.isnan(value):
                    raise ValidationError(f"Attribute '{info.field_name}' cannot be NaN")
                else:
                    return value
            case _:
                raise ValidationError(f"Attribute '{info.field_name}' should be an float")


class APIOrderData(BaseModel):
    internal_order_id: str
    sku: str
    market: str
    name_of_shop: str
    quantity: int
    created_at: datetime
    updated_at: datetime | None
    price: float | None
    warehouse_name: str | None


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if Singleton._instance is None:
            Singleton._instance = super().__call__(*args, **kwargs)
        return Singleton._instance


class InvalidOffers(metaclass=Singleton):
    _skus: list[str] | None = []
    _invalid_offers: dict[str, dict[str, Any]] | None = {}

    @property
    def offers(self) -> dict[str, dict[str, Any]]:
        return self._invalid_offers

    def __len__(self) -> int:
        return len(self._skus)

    def to_json(self, filename: Path = Path('output.json')) -> None:
        with open(filename, 'w+') as f:
            f.write(json.dumps(self.offers, indent=4))

    def add(self, offers: dict[str, dict[str, Any]]) -> None:
        for key, offer_data in offers.items():
            self._skus.append(key)
            self._invalid_offers[key] = offer_data
