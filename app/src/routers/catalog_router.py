from pathlib import PurePath

from fastapi import APIRouter, UploadFile, File, Depends, Body
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from src.dependencies.users import get_current_user, require_staff
from src.schemas.catalog_schemas import CatalogItem, CatalogItemUpdate
from src.services import catalog_service as service
from src.services.base_utils import clean_up_files

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)


@router.get('', response_model=list[CatalogItem], dependencies=[Depends(get_current_user)])
async def get_catalog_items():
    return await service.get_catalog_items()


@router.post('', dependencies=[Depends(require_staff)])
async def change_catalog_items(items: list[CatalogItemUpdate]):
    await service.change_catalog_items(items)


@router.post('/setup', tags=["Debug"], dependencies=[Depends(require_staff)])
async def setup_catalog_items():
    await service.setup_catalog_items()


@router.post('/synchronization', tags=["Debug"], dependencies=[Depends(require_staff)])
async def synchronize_catalog_items(skus: list[str] = Body(embed=True)):
    await service.sync_catalog_items_with_offers(skus=skus)


@router.post('/export', tags=["Export"], dependencies=[Depends(get_current_user)])
async def export_catalog_items():
    path = await service.export_catalog_items()
    return FileResponse(path, filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@router.post('/import', tags=["Import"], dependencies=[Depends(require_staff)])
async def import_catalog_items(data: UploadFile = File()):
    content = await data.read()
    await service.import_catalog_items(content, PurePath(data.filename).suffix)

