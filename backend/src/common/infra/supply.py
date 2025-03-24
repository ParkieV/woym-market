from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from src.common.export import Supply
from src.common.infra.mapper import AbstractMapper

sku = str

class AbstractSupplyMapper(AbstractMapper[Supply, sku]):

    @abstractmethod
    async def read_object_by_id(self, object_id: str) -> Supply:
        raise NotImplementedError

    @abstractmethod
    async def read_list(self) -> Sequence[Supply]:
        raise NotImplementedError

    @abstractmethod
    async def read_list_by_delivery_order(self, orders: Sequence[Any]) -> Sequence[Supply]: ...
