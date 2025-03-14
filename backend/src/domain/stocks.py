from collections.abc import Sequence, Iterable

from src.common.fbo_stocks import FboOffer, FboStock
from src.common.infra.uow import AbstractUoW


async def update_stocks(uow: AbstractUoW, stocks: Sequence[FboStock]):
    """ Обновление информации об остатках карточки товара на складах """
    for stock in stocks:
        await uow.mappers.offer_stocks_mapper.update_object(stock, stock.offer_id)
    await uow.commit()

async def update_offers(uow: AbstractUoW, offers: Sequence[FboOffer]):
    async with uow as _uow:
        for offer in offers:
            await _uow.mappers.mutable_fbo_stocks_mapper.update_offer(offer)
        await _uow.commit()
