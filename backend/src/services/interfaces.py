from abc import abstractmethod
from typing import Protocol
from collections.abc import Sequence


class IDBMetadataService(Protocol):

    @abstractmethod
    def get_columns(self, table_name: str) -> Sequence[str]:
        raise NotImplementedError