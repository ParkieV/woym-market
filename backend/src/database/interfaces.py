from abc import abstractmethod
from collections.abc import Sequence, Iterable, Callable
from typing import Protocol, TypeVar, AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.filters.interface import IBaseFilter

T = TypeVar('T')
IDbSessionFabric = Callable[[], AsyncContextManager[AsyncSession]]

class ICatalogRepository(Protocol[T]):

    @abstractmethod
    async def get(self,
                  identification: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def list(self,
                     chunk_size: int | None,
                     query_filter: IBaseFilter | None = None) -> AsyncGenerator[list[T], None]:
        raise NotImplementedError

    @abstractmethod
    async def create(self,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_many(self,
                    data: Sequence[T]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self,
               identification: str,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_many(self,
                          data: Sequence[T],
                          query_filter: IBaseFilter | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def synchronization_catalog_from_offer(self,
                 updating_columns: Iterable[str],
                 skus: Sequence[str] | None = None) -> None:
        raise NotImplementedError

class IOfferRepository(Protocol[T]):

    @abstractmethod
    async def get(self,
                  identification: str) -> T:
        raise NotImplementedError

    @abstractmethod
    async def list(self,
                     chunk_size: int | None,
                     query_filter: IBaseFilter | None = None) -> AsyncGenerator[list[T], None]:
        raise NotImplementedError

    @abstractmethod
    async def create(self,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_many(self,
                    data: Sequence[T]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self,
               identification: str,
               data: T) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_many(self,
                          data: Sequence[T],
                          query_filter: IBaseFilter | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def synchronization_offer_from_catalog(self,
                 updating_columns: Iterable[str],
                 skus: Sequence[str] | None = None) -> None:
        raise NotImplementedError
