from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel


class SupplyData(BaseModel):
    sku: str
    name: str
    market: str
    name_of_shop: str
    for_delivery: int
    warehouse_name: str
    own_storage_value: int | None
    barcodes: str | None
    current_price: float | None


class GeneralOrderData(BaseModel):
    sku: str
    name: str
    volume: float | None
    cost_price: float | None
    self_weight: float | None
    for_delivery: float | None
    own_storage_value: int | None


class SupplyExportType(str, Enum):
    ONLY_OWN_STORAGE = "ONLY_OWN_STORAGE"
    ONLY_STOCKS = "ONLY_STOCKS"
    WITH_OWN_STORAGE = "WITH_OWN_STORAGE"
