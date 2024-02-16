from pydantic import BaseModel


class BaseWarehouse(BaseModel):
    name: str
    warehouse_id_in_marketplace: int


class WarehouseCreate(BaseWarehouse):
    market: str


class WarehouseOut(BaseWarehouse):
    id: int


class BaseOfferStock(BaseModel):
    current_stock: int = 0
    min_stock: int = 0
    for_delivery: int = 0


class OfferStockUpdate(BaseModel):
    id: int
    min_stock: int = 0


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
    hidden: bool
    stocks: list[OfferStockWithWarehouseOut]


class OfferWithStocksUpdate(BaseModel):
    id: int
    note_1: str = ''
    note_2: str = ''
    note_3: str = ''
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



