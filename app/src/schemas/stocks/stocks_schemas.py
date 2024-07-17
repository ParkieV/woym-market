from dataclasses import dataclass


@dataclass(frozen=True)
class SupplyData:
    sku: str
    name: str
    market: str
    name_of_shop: str
    for_delivery: int
    warehouse_name: str
    supplier_available: bool
    own_storage_value: int | None
    barcodes: str | None
    current_price: float | None


@dataclass(frozen=True)
class GeneralOrderData:
    sku: str
    name: str
    volume: float | None
    cost_price: float | None
    self_weight: float | None
    for_delivery: float | None
