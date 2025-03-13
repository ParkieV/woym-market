from collections.abc import Sequence

from pydantic import BaseModel

from src.common.infra.uow import AbstractUoW


class FboStock(BaseModel, frozen=True):
    stock_id: int
    offer_id: int
    warehouse_id: int
    can_be_delivered: bool
    advice_from_the_store: str
    current_stock: int
    in_box: int
    is_deliver_in_boxes: int
    min_stock: int
    for_deliver: int

async def update_stocks(uow: AbstractUoW, stocks: Sequence[FboStock]):
    """ Обновление информации об остатках карточки товара на складах """
    for stock in stocks:
        await uow.mappers.offer_stocks_mapper.update_object(stock, stock.offer_id)
    await uow.commit()


