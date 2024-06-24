from datetime import datetime
from enum import Enum

from pydantic import BaseModel, computed_field

from src.schemas.base_api_schemas import WarehouseType
from src.schemas.settings_schemas import MarketOut
from dataclasses import dataclass


class WarehouseTypes(str, Enum):
    WAREHOUSE = 'warehouse'
    CLUSTER = 'cluster'


class BaseWarehouse(BaseModel):
    name: str
    warehouse_type: WarehouseType


class WarehouseCreate(BaseWarehouse):
    market: str


class WarehouseOut(BaseWarehouse):
    id: int
    market: str
    from_file_updated_at: datetime | None


class BaseOfferStock(BaseModel):
    current_stock: int = 0
    min_stock: int = 0
    for_delivery: int = 0
    can_be_delivered: bool = False
    advice_from_the_store: str = ''
    in_box: int = 1
    is_deliver_in_boxes: bool = False


class OfferStockUpdate(BaseModel):
    id: int
    min_stock: int
    in_box: int
    is_deliver_in_boxes: bool


class OfferStockCreate(BaseOfferStock):
    offer_id: int
    warehouse_id: int


class OfferStockOut(BaseOfferStock):
    id: int



class OfferStockWithWarehouseOut(OfferStockOut):
    warehouse: WarehouseOut


class OfferWithStocks(BaseModel):
    id: int
    sku: str
    name: str
    photo: str | None
    name_of_shop: str
    market: str
    note_1: str
    note_2: str
    note_3: str
    supplier_available: bool
    margin: float | None
    cost_price: float | None
    profit: float | None
    self_weight: float | None
    volume: float | None
    hidden: bool
    stocks: list[OfferStockWithWarehouseOut]

    @property
    def total_for_delivery(self) -> int:
        return sum([i.for_delivery for i in self.stocks])

    @computed_field
    @property
    def total_volume(self) -> float | None:
        if self.volume is None:
            return None
        return self.volume * self.total_for_delivery

    @computed_field
    @property
    def total_cost_price(self) -> float | None:
        if self.cost_price is None:
            return None
        return self.cost_price * self.total_for_delivery

    @computed_field
    @property
    def total_weight(self) -> float | None:
        if self.self_weight is None:
            return None
        return self.self_weight * self.total_for_delivery

    @computed_field
    @property
    def total_margin(self) -> float | None:
        if self.margin is None:
            return None
        return self.margin * self.total_for_delivery

    @computed_field
    @property
    def total_profit(self) -> float | None:
        if self.profit is None:
            return None
        return self.profit * self.total_for_delivery



class OfferWithStocksUpdate(BaseModel):
    id: int
    note_1: str = ''
    note_2: str = ''
    note_3: str = ''
    supplier_available: bool
    hidden: bool
    stocks: list[OfferStockUpdate]


class OwnStorageCreate(BaseModel):
    sku: str
    value: int = 0


class OwnStorageOut(BaseModel):
    id: int
    value: int = 0


class OwnStorageUpdate(BaseModel):
    id: int
    value: int = 0


class OfferStorageStock(BaseModel):
    name_of_shop: str
    market: str
    value: int


class OfferStorage(BaseModel):
    sku: str
    name: list[str]
    photo: list[str | None]
    name_of_shop: list[str]
    market: list[str]
    note_1: list[str]
    note_2: list[str]
    note_3: list[str]
    own_storage: OwnStorageOut
    stocks: list[OfferStorageStock]


class OwnStorages(BaseModel):
    markets: list[MarketOut]
    data: list[OfferStorage]


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
