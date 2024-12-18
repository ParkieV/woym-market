from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException
from starlette import status

from src.api.yandex.disk import YandexDiscAPI
from src.dependencies.users import require_staff
from src.params.config import config
from src.schemas.media_schemas import UploadResult, StorageItem

router = APIRouter(
    prefix="/media",
    tags=['Медиа', 'Debug'],
    dependencies=[Depends(require_staff)]
)

disk = YandexDiscAPI(
    token=config.yandex_disk_token,
    work_dir=config.yandex_disk_work_dir
)


@router.delete("")
async def delete_source(path: str):
    disk.delete_source(path)
    return {'status': 'OK'}


@router.get("/files/all", response_model=list[StorageItem])
async def get_all_files(path: str = Query('')):
    return disk.get_files(path)


@router.post("/files/upload", response_model=UploadResult | None)
async def upload_file(file: UploadFile = File(), overwrite: bool = True, publish: bool = True, keep_name: bool = False) -> UploadResult | None:
    return await disk.upload_file(file, overwrite=overwrite, publish=publish, keep_name=keep_name)


@router.post('/dirs')
async def create_dir(path: str):
    disk.create_directory(path)
    return {'status': 'OK'}