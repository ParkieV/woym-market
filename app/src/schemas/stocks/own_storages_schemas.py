from pydantic import BaseModel


class OwnStorageCreate(BaseModel):
    sku: str
    value: int = 0
    storage_place_id: int


class OwnStorageStockOut(BaseModel):
    id: int
    sku: str
    value: int = 0
    storage_place_id: int | None


class OwnStorageUpdate(BaseModel):
    id: int
    value: int = 0
    storage_place_id: int


class OwnStoragePlaceCreate(BaseModel):
    name: str


class OwnStoragePlaceOut(BaseModel):
    id: int
    name: str


class OwnStoragePlaceUpdate(BaseModel):
    id: int
    name: str


class OwnStorageAggOfferOut(BaseModel):
    sku: str
    name: list[str]
    photo: list[str | None]
    market: list[str]
    name_of_shop: list[str]
    note_1: list[str | None]
    note_2: list[str | None]
    note_3: list[str | None]
    barcodes: list[str | None]


class OwnStorageOfferStockOut(BaseModel):
    sku: str
    name_of_shop: str
    market: str
    stock: int


class OwnStorageOut(BaseModel):
    offer: OwnStorageAggOfferOut
    storages: list[OwnStorageStockOut]
    stocks: list[OwnStorageOfferStockOut]
