from fastapi import APIRouter, File, Depends, UploadFile, status, Body
from fastapi.responses import FileResponse
from pathlib import PurePath, Path
from starlette.background import BackgroundTask
from src.dependencies.users import get_current_user, require_staff
from src.schemas.offer_schemas import (
    OfferOut,
    OfferChange,
    ImportType,
    ExportType,
    Market,
    PricingSchemeOut,
    PricingSchemeCreate,
    PricingSchemeFieldCreate,
    PricingSchemeFieldChange, PricingSchemeChange
)
from src.services import offer_service as service
from src.services.base_utils import clean_up_files

data_router = APIRouter(
    prefix='/data',
    tags=['Data']
)


@data_router.get('/offers', response_model=list[OfferOut], tags=['Offers'])
async def get_offers(offset: int = 0, limit: int | None = None):
    return await service.get_offers(offset=offset, limit=limit)


@data_router.patch('/offers', response_model=list[OfferOut], tags=['Offers'])
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(require_staff)):
    return await service.change_offers(offers_data, current_user.id)


@data_router.get('/pricing-schemes', response_model=list[PricingSchemeOut], tags=['Pricing Schemes'])
async def get_pricing_schemes():
    return await service.get_pricing_schemes()


@data_router.post('/pricing-schemes', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def create_pricing_schemes(data: PricingSchemeCreate):
    await service.create_pricing_scheme(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes', tags=['Pricing Schemes'])
async def update_pricing_schemes(data: PricingSchemeChange, current_user=Depends(require_staff)):
    await service.change_pricing_scheme(current_user.id, data)
    return {'status': 'OK'}


@data_router.delete('/pricing-schemes', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def delete_pricing_schemes(names: list[str]):
    await service.delete_pricing_scheme(names)
    return {'status': 'OK'}


@data_router.get('/pricing-schemes/fields', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def get_pricing_schemes_fields(pricing_scheme_name: str | None = None):
    raise NotImplementedError("Endpoint not implemented")


@data_router.post('/pricing-schemes/fields', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def create_pricing_schemes_fields(data: PricingSchemeFieldCreate):
    await service.create_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes/fields', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def update_pricing_schemes_fields(data: list[PricingSchemeFieldChange]):
    await service.change_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.delete('/pricing-schemes/fields', dependencies=[Depends(require_staff)], tags=['Pricing Schemes'])
async def delete_pricing_schemes_fields(ids: list[int]):
    await service.delete_pricing_scheme_fields(ids)
    return {'status': 'OK'}


@data_router.post('/setup', tags=['Debug'])
async def setup_offers_data(current_user=Depends(require_staff)):
    await service.setup_offers_data(current_user.id)
    return {'status': 'OK'}


@data_router.post('/export', dependencies=[Depends(require_staff)], tags=['Export', 'Offers'])
async def export_offers(market: Market | None = Body(None), name_of_shop: str | None = Body(None)):
    path = Path(await service.export_offers(name_of_shop, market))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, str(path)))


@data_router.post('/import', tags=['Import'])
async def import_offers(import_type: ImportType = Body(), data: UploadFile = File(), market: Market | None = Body(None), name_of_shop: str | None = Body(None), current_user=Depends(require_staff)):
    content = await data.read()
    await service.import_data(content, market, import_type, name_of_shop, current_user.id, PurePath(data.filename).suffix)
    return {'status': 'OK'}


@data_router.post('/violators/export', dependencies=[Depends(require_staff)], tags=['Offers', 'Export'])
async def export_violators(market: Market | None = Body(None), name_of_shop: str | None = Body(None)):
    path = Path(await service.create_violators_file(market, name_of_shop))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data',
                        background=BackgroundTask(clean_up_files, str(path)))







