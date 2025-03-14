from collections.abc import Sequence

from logs import backend_logger
from src.common.infra.uow import AbstractUoW
from src.common.infra.mapper import AbstractMapperAggregator, AbstractMapper, AbstractMutableMapper
from src.database.db import async_session


class SQLAlchemyUnitOfWork(AbstractUoW):
    def __init__(
            self,
            mappers: Sequence[type[AbstractMapper] | type[AbstractMutableMapper]],
            mapper_aggregator: type[AbstractMapperAggregator],
            session_factory=async_session,
    ):
        self.session_factory = session_factory
        backend_logger.debug(f'session factory type: {self.session_factory}')
        self.mappers = mapper_aggregator(mappers)


    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def __aenter__(self):
        self.session = self.session_factory()
        backend_logger.debug(type(self.session))
        self.mappers.session = self.session
        return self

    async def __aexit__(self, *args):
        await self.session.close()

