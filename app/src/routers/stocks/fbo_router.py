from pathlib import PurePath
from fastapi import APIRouter, Depends, Body, UploadFile, File, HTTPException
from starlette import status
from src.dependencies.users import get_current_user, require_staff
from src.schemas.stocks.fbo_schemas import OfferFBOStockUpdate, OfferStockOut, AggOfferFBOStock
from src.services import stocks_service as service

router = APIRouter(
    prefix='/fbo',
    tags=['FBO']
)


@router.post('',  dependencies=[Depends(get_current_user)], response_model=list[AggOfferFBOStock], summary='Данные FBO', description='Данные о FBO остатках, аггрегированные по товарам')
async def get_fbo_data(
        warehouse_ids: list[int] | None = Body(
            default=None,
            title='Список ID складов',
            description='ID складов или кластеров, по которым будет проходить аггрегация остатков. Если не передан / пуст, то аггрегация будет по всем остаткам.'
        ),
        ignore_clusters: bool = Body(
            default=True,
            title='Игнорировать кластеры',
            description='Если true, то данные будут считаться только по складам (без учета кластеров).'
        )
):
    return await service.aggregate_offers_fbo_stocks(warehouse_ids, ignore_clusters)


@router.patch('', dependencies=[Depends(require_staff)], summary='Изменение данных об остатках товаров')
async def change_fbo_stocks(stocks: list[OfferFBOStockUpdate]):
    await service.change_fbo_stocks(stocks)
    return {'status': 'OK'}


@router.get('/offers/{offer_id}', response_model=list[OfferStockOut], dependencies=[Depends(get_current_user)], summary='Остатки товара', description='Список данных и настроек остатков товара по каждому складу, которые доступен для маркетплейса')
async def get_fbo_stocks_for_offer(offer_id: int):
    return await service.get_offer_fbo_stocks(offer_id)


@router.post('/additions/import', dependencies=[Depends(require_staff)], tags=['Импорт'], summary='Импорт дополнительных данных для данных ФБО', description='Из таблицы импортируются данные "Совет", "Можно ли поставить товар?"')
async def import_fbo_additions_data(data: UploadFile = File(), name_of_shop: str | None = Body(None), warehouse_id: int | None = Body(None)):
    content = await data.read()
    await service.import_fbo_data(content, name_of_shop, warehouse_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@router.post('/import',  dependencies=[Depends(require_staff)], tags=['Импорт'], deprecated=True)
async def import_fbo(data: UploadFile = File(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    raise HTTPException(status.HTTP_410_GONE, 'Данное действие больше недотупно. Обратитесь к администратору')


@router.post('/export', dependencies=[Depends(get_current_user)], tags=['Экспорт'], deprecated=True)
async def export_fbo_stocks(name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    raise HTTPException(status.HTTP_410_GONE, 'Данное действие больше недотупно. Обратитесь к администратору')
