from fastapi import APIRouter

from src.common.routers.offers import FboStocksOffers
from src.domain.stocks import update_offers
from src.infra.base_mapper import MapperAggregator
from src.infra.fbo_stocks import MutableFboStocksMapper
from src.infra.uow import SQLAlchemyUnitOfWork

router = APIRouter(prefix='/offers')

@router.patch('/fbo-stocks')
async def update_fbo_stocks_offers(
    body: FboStocksOffers
):
    await update_offers(
        uow=SQLAlchemyUnitOfWork(
            [MutableFboStocksMapper],
            MapperAggregator
        ),
        offers=body.offers
    )