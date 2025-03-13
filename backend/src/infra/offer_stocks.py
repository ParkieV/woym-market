from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.infra.mapper import AbstractMutableMapper, Model, ID
from src.database.models.models import OfferStock, Offer
from src.domain.stocks import FboStock


class OfferStocksMapper(AbstractMutableMapper[FboStock, int]):

    def __init__(self, session: AsyncSession):
        self._session = session

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise ValueError("No session provided")
        return self._session

    @session.setter
    def session(self, session: AsyncSession):
        self._session = session

    async def update_object(self, new_object: Model, object_id: ID) -> None:

        stmt = update(Offer).where(OfferStock.id == object_id).values(**new_object)
        await self._session.execute(stmt)

    async def create_object(self, object: FboStock) -> None:
        raise NotImplementedError

    async def delete_object(self, object_id: int) -> None:
        raise NotImplementedError
