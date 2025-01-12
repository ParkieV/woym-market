from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, Query
from requests import session

from src.api.gateway_template import get_api_session
from src.api.yandex_disk import YandexDiscApi
from src.dependencies.users import require_staff
from src.params.config import config
from src.schemas.media_schemas import UploadResult, StorageItem

router = APIRouter(
    prefix="/media",
    tags=['Медиа', 'Debug'],
    dependencies=[Depends(require_staff)]
)
async with get_api_session() as api_session:
    disk = YandexDiscApi(
        token=config.yandex_disk_token,
        work_dir=config.yandex_disk_work_dir,
        session=api_session
    )


@router.delete("")
async def delete_source(path: str):
    disk.delete_source(Path(path))
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