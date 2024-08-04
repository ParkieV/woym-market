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
    tags=['Own storage'],
)


@router.get('', dependencies=[Depends(get_current_user)], response_model=list[OwnStorageOut])
async def get_own_storages():
    return await service.get_own_storages()


@router.patch('', dependencies=[Depends(require_staff)])
async def change_own_storages(data: list[OwnStorageUpdate]):
    await service.change_own_storages(data)
    return {'status': 'OK'}


@router.post('/places', dependencies=[Depends(require_staff)], tags=['Own storage places'])
async def create_own_storage_places(data: list[OwnStoragePlaceCreate]):
    await service.create_own_storage_places(data)
    return {'status': 'OK'}


@router.patch('/places', dependencies=[Depends(require_staff)], tags=['Own storage places'])
async def change_own_storage_place(data: list[OwnStoragePlaceUpdate]):
    await service.change_own_storage_places(data)
    return {'status': 'OK'}


@router.get('/places', dependencies=[Depends(get_current_user)], tags=['Own storage places'])
async def get_own_storage_places():
    return await service.get_all_own_storage_places()


@router.post('/export', dependencies=[Depends(require_staff)], tags=['Export'])
async def export_own_storage(place_id: int = Body(), name_of_shop: str | None = Body(None), market: str | None = Body(None)):
    path = Path(await service.export_own_storages(place_id, name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@router.post('/coming/import', dependencies=[Depends(require_staff)], tags=['Import'], description='Offers with increased availability')
async def import_own_storage_coming(file: UploadFile = File(), place_id: int = Body()):
    content = await file.read()
    await service.increment_own_storage_values(content, place_id, PurePath(file.filename).suffix, 1)
    return {'status': 'OK'}


@router.post('/consumption/import', dependencies=[Depends(require_staff)], tags=['Import'], description='Offers with decreased availability')
async def import_own_storage_consumption(file: UploadFile = File(), place_id: int = Body()):
    content = await file.read()
    await service.increment_own_storage_values(content, place_id, PurePath(file.filename).suffix, -1)
    return {'status': 'OK'}


@router.post('/import', dependencies=[Depends(require_staff)], tags=['Import'])
async def import_own_storage(data: UploadFile = File(), place_id: int = Body()):
    content = await data.read()
    await service.import_own_storages(content, place_id, PurePath(data.filename).suffix)
    return {'status': 'OK'}

