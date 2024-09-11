from pathlib import Path, PurePath

from fastapi import APIRouter, Depends, Body, File, UploadFile
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.schemas.stocks.own_storages_schemas import OwnStorageOut, OwnStorageUpdate, OwnStoragePlaceCreate, \
    OwnStoragePlaceUpdate
from src.services import stocks_service as service
from src.dependencies.users import get_current_user, require_staff
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix='/own-storage',
    tags=['Собственные остатки продавца'],
)


@router.get('', dependencies=[Depends(get_current_user)], response_model=list[OwnStorageOut], summary='Информация о собственных остатках')
async def get_own_storages():
    return await service.get_own_storages()


@router.patch('', dependencies=[Depends(require_staff)], summary='Изменение остатков на собственных складах')
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@router.get('/places', dependencies=[Depends(get_current_user)], summary='Список складов продавца')
async def get_own_storage_places():
    return await service.get_all_own_storage_places()


@router.post('/places', dependencies=[Depends(require_staff)], summary='Создание склада продавца')
async def create_own_storage_places(data: list[OwnStoragePlaceCreate]):
    await service.create_own_storage_places(data)
    return {'status': 'OK'}


@router.patch('/places', dependencies=[Depends(require_staff)], summary='Изменение склада продавца')
async def change_own_storage_place(data: list[OwnStoragePlaceUpdate]):
    await service.change_own_storage_places(data)
    return {'status': 'OK'}


@router.post('/export', dependencies=[Depends(get_current_user)], tags=['Экспорт'], summary='Экспорт собственных остатков')
async def export_own_storage(place_id: int = Body(embed=True)):
    path = Path(await service.export_own_storages(place_id))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@router.post('/coming/import', dependencies=[Depends(require_staff)], tags=['Импорт'], summary='Приход товаров', description='Для каждого товара из таблицы значение остатка на складе продавца повышается на указанное кол-во')
async def import_own_storage_coming(data: UploadFile = File(), place_id: int = Body()):
    content = await data.read()
    await service.increment_own_storage_values(content, place_id, PurePath(data.filename).suffix, 1)
    return {'status': 'OK'}


@router.post('/consumption/import', dependencies=[Depends(require_staff)], tags=['Импорт'], summary='Расход товаров', description='Для каждого товара из таблицы значение остатка на складе продавца уменьшается на указанное кол-во')
async def import_own_storage_consumption(data: UploadFile = File(), place_id: int = Body()):
    content = await data.read()
    await service.increment_own_storage_values(content, place_id, PurePath(data.filename).suffix, -1)
    return {'status': 'OK'}


@router.post('/import', dependencies=[Depends(require_staff)], tags=['Импорт'], summary='Импорт данных о собственных остатках')
async def import_own_storage(data: UploadFile = File(), place_id: int = Body()):
    content = await data.read()
    await service.import_own_storages(content, place_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}

