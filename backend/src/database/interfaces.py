from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, TypeVar

from src.schemas.filters.interface import IBaseFilter
from src.services.catalog_service import UpdateCatalogService

T = TypeVar('T')
Repository = TypeVar('Repository')


class IAsyncCatalogRepository(Protocol[T]):

    @abstractmethod
    async def update(self,
               identification: str,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_many(self,
               query_filter: IBaseFilter,
               data: Sequence[T]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self,
                  identification: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def list(self,
                     chunk_size: int | None,
                     query_filter: IBaseFilter) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def create(self,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_many(self,
                    data: Sequence[T]) -> None:
        raise NotImplementedError


class IUnitOfWork(Protocol[Repository]):
    repository: Repository

    @abstractmethod
    def __enter__(self) -> 'IUnitOfWork':
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class IAsyncReverseSyncUnitOfWork(Protocol):
    reverse_sync_service: UpdateCatalogService

    @abstractmethod
    async def __aenter__(self) -> 'IAsyncReverseSyncUnitOfWork':
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError