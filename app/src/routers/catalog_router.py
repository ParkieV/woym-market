from pathlib import PurePath

from fastapi import APIRouter, UploadFile, File, Depends, Body, BackgroundTasks
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.schemas.catalog_schemas import CatalogItem, CatalogItemUpdate
from src.services import catalog_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix="/catalog",
    tags=['Каталов']
)


@router.get('', response_model=list[CatalogItem], dependencies=[Depends(get_current_user)], summary='Список товаров каталога')
async def get_catalog_items():
    return await service.get_catalog_items()


@router.patch('', dependencies=[Depends(require_staff)], summary='Изменение товаров каталога')
async def change_catalog_items(items: list[CatalogItemUpdate]):
    await service.change_catalog_items(items)


@router.post('/reset-track-markers', tags=['Debug'], dependencies=[Depends(require_staff)])
async def reset_track_markers():
    await service.reset_track_markers()
    return {'status': 'OK'}


@router.post('/setup', tags=["Debug"], dependencies=[Depends(require_staff)])
async def setup_catalog_items(background: BackgroundTasks):
    background.add_task(service.setup_catalog_items)
    return {'status': 'OK'}


@router.post('/synchronization', tags=["Debug"], dependencies=[Depends(require_staff)], summary='Синхронизация')
async def synchronize_catalog_items(background: BackgroundTasks, skus: list[str] = Body(embed=True)):
    """
    Запускает задачу синхронизации карточек товаров с каталогом
    """
    background.add_task(service.sync_catalog_items_with_offers, skus=skus)
    return {'status': 'OK'}


@router.post('/reverse-synchronization', tags=["Debug"], dependencies=[Depends(require_staff)], summary='Обратная синхронизация')
async def reverse_synchronize_catalog_items(background: BackgroundTasks, skus: list[str] = Body(embed=True)):
    """

    """
    background.add_task(service.reverse_sync_catalog_items_with_offer, skus=skus)
    return {'status': 'OK'}


@router.post('/export', tags=['Экспорт'], dependencies=[Depends(get_current_user)], summary='Экспорт каталога')
async def export_catalog_items():
    path = await service.export_catalog_items()
    return FileResponse(path, filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@router.post('/import', tags=['Импорт'], dependencies=[Depends(require_staff)], summary='Импорт каталога', description='Только изменяет уже существующие товары, не создает новых и не удаляет старые')
async def import_catalog_items(data: UploadFile = File()):
    content = await data.read()
    await service.import_catalog_items(content, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@router.post('/import/prices', tags=['Импорт'], dependencies=[Depends(require_staff)], summary='Импорт цен в каталог')
async def import_catalog_item_prices(data: UploadFile = File()):
    content = await data.read()
    await service.import_item_prices(content, PurePath(data.filename).suffix)
    return {'status': 'OK'}


