from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.database.db import engine
from src.database.interfaces_repos import IAsyncReverseSyncUnitOfWork
from src.services.catalog_service import UpdateCatalogService

DEFAULT_SESSION_FACTORY = async_sessionmaker(engine, expire_on_commit=False)

class ReverseSyncUnitOfWork(IAsyncReverseSyncUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession] = DEFAULT_SESSION_FACTORY) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> 'ReverseSyncUnitOfWork':
        self._session = self._session_factory()
        self.reverse_sync_service = UpdateCatalogService(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()

    async def commit(self) -> None:
        try:
            await self._session.commit()
        except:
            await self.rollback()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()