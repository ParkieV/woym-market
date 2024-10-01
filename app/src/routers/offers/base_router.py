from pathlib import Path, PurePath

from fastapi import APIRouter, Depends, UploadFile, File, Query, Body
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import require_staff, get_current_user
from src.schemas.offer_schemas import OfferChange, OfferOut, Market, ImportType
from src.services import offer_service as service
from src.services.base_utils import clean_up_files
from .pricing_schemes_router import router as pricing_schemes_router
from ...schemas.filters.filter_schemas import PagingFilter
from ...schemas.filters.offers_filter import OffersFilter

router = APIRouter(
    prefix="/offers",
    tags=['Товары']
)


@router.post('', response_model=list[OfferOut], tags=['Карточки товаров'], dependencies=[Depends(get_current_user)], summary='Список карточек товаров')
async def get_offers(filter: OffersFilter | None = None, paging: PagingFilter | None = None):
    return await service.get_offers_list(paging_filter=paging, offers_filter=filter)


@router.post('/reset-track-markers', tags=['Debug'], dependencies=[Depends(require_staff)])
async def reset_track_markers():
    await service.reset_track_markers()
    return {'status': 'OK'}


@router.patch('', tags=['Карточки товаров'], summary='Изменение карточек товаров')
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(require_staff)):
    """
    Параметр `id` товара обязательно должен передаваться. Параметры `market`, `name_of_shop` передаются для валидации значений для конкретного.
    """
    return await service.change_offers(offers_data, current_user.id)


@router.put('/media/images', tags=['Карточки товаров', 'Медиа'], dependencies=[Depends(require_staff)], deprecated=True)
async def add_image_to_offer(file: UploadFile = File(...), offer_id: int = Query()):
    """**Реализация отложена**"""
    return file.filename, offer_id


@router.post('/setup', tags=['Debug'], include_in_schema=False)
async def setup_offers_data(current_user=Depends(require_staff)):
    """Создает **все** карточки товаров, которые отдают подключенные магазины """
    await service.setup_offers_data(current_user.id)
    return {'status': 'OK'}


@router.post('/export', dependencies=[Depends(get_current_user)], tags=['Экспорт', 'Карточки товаров'], summary='Экспорт карточек товаров')
async def export_offers(filter: OffersFilter | None = Body(None)):
    path = Path(await service.export_offers(filter))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


# @router.post('/import', tags=['Импорт', 'Карточки товаров'], dependencies=[Depends(require_staff)], summary='Импорт карточек товаров', description='Обновляет существующие карточки, но не создает новые или удаляет неуказанные')
# async def import_offers(import_type: ImportType = Body(), data: UploadFile = File(), market: Market | None = Body(None), name_of_shop: str | None = Body(None), current_user=Depends(require_staff)):
#     content = await data.read()
#     await service.import_data(content, market, import_type, name_of_shop, current_user.id, PurePath(data.filename).suffix)
#     return {'status': 'OK'}

@router.post('/import', tags=['Импорт', 'Карточки товаров'], dependencies=[Depends(require_staff)], summary='Импорт карточек товаров', description='Обновляет существующие карточки, но не создает новые или удаляет неуказанные')
async def import_offers_table(data: UploadFile = File(), market: Market | None = Body(None), name_of_shop: str | None = Body(None)):
    content = await data.read()
    await service.import_offers(content, market=market, name_of_shop=name_of_shop, file_extension='.xlsx')

@router.post('/import/sizes', tags=['Импорт', 'Карточки товаров'], dependencies=[Depends(require_staff)], summary='Импорт карточек товаров', description='Обновляет существующие карточки, но не создает новые или удаляет неуказанные')
async def import_offers_size_list(data: UploadFile = File(), name_of_shop: str | None = Body(None)):
    content = await data.read()
    await service.import_sizes(content, name_of_shop='.xlsx')


@router.post('/import/prices', tags=['Импорт', 'Карточки товаров'], dependencies=[Depends(require_staff)], summary='Импорт карточек товаров', description='Обновляет существующие карточки, но не создает новые или удаляет неуказанные')
async def import_offers_price_list(data: UploadFile = File(), market: Market | None = Body(None), name_of_shop: str | None = Body(None)):
    content = await data.read()
    await service.import_prices(content, name_of_shop=name_of_shop, market=market, file_extension='.xlsx')


@router.post('/violators/export', dependencies=[Depends(get_current_user)], tags=['Карточки товаров', 'Экспорт'], summary='Экспорт нарушителей РРЦ')
async def export_violators(market: Market | None = Body(None), name_of_shop: str | None = Body(None)):
    path = Path(await service.create_violators_file(market, name_of_shop))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data',
                        background=BackgroundTask(clean_up_files, str(path)))


router.include_router(pricing_schemes_router)
