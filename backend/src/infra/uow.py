from collections.abc import Iterable

from logs import backend_logger
from src.common.infra.uow import AbstractUoW
from src.common.infra.repository import AbstractRepositoryAggregator, AbstractRepository, AbstractMutableRepository
from src.database.db import async_session


class SQLAlchemyUnitOfWork(AbstractUoW):
    def __init__(
            self,
            repositories: Iterable[type[AbstractRepository] | type[AbstractMutableRepository]],
            repository_aggregator: type[AbstractRepositoryAggregator],
            session_factory=async_session,
    ):
        self.session_factory = session_factory
        backend_logger.debug(f'session factory type: {self.session_factory}')
        self.repositories = repository_aggregator(repositories)


    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def __aenter__(self):
        self.session = self.session_factory()
        backend_logger.debug(type(self.session))
        self.repositories.session = self.session
        return self

    async def __aexit__(self, *args):
        await self.session.close()

