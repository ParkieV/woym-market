from abc import abstractmethod

from src.common.fbo_stocks import FboOffer, FboStock
from src.common.infra.mapper import AbstractMutableMapper


class AbstractMutableFboStocksMapper(AbstractMutableMapper[FboStock, int]):

    @abstractmethod
    async def update_offer(self, offer: FboOffer):
        raise NotImplementedError