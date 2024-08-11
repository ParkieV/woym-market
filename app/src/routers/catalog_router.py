from fastapi import APIRouter, UploadFile, File
from src.schemas.catalog_schemas import SynchronizationOffer, CatalogItem, CatalogItemUpdate, SynchronizationOfferUpdate
from src.services import catalog_service as service

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"]
)


@router.get('', response_model=list[CatalogItem])
async def get_catalog_items():
    return await service.get_catalog_items()


@router.post('')
async def change_catalog_items(data: list[CatalogItemUpdate]):
    pass


@router.post('/synchronization')
async def synchronize_catalog_items(data: list[SynchronizationOfferUpdate]):
    pass


@router.post('/setup', tags=["Debug"])
async def setup_catalog_items():
    await service.setup_catalog_items()


@router.post('/export', tags=["Export"])
async def export_catalog_items():
    pass


@router.post('/import', tags=["Import"])
async def import_catalog_items(data: UploadFile = File()):
    pass

