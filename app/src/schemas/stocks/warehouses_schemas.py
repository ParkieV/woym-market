from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from src.schemas.base_api_schemas import WarehouseType


class WarehouseTypes(str, Enum):
    WAREHOUSE = 'warehouse'
    CLUSTER = 'cluster'
    SUPER_CLUSTER = 'super_cluster'


class BaseWarehouse(BaseModel):
    name: str
    warehouse_type: WarehouseType


class WarehouseCreate(BaseWarehouse):
    market: str


class WarehouseOut(BaseWarehouse):
    id: int
    market: str
    from_file_updated_at: datetime | None
