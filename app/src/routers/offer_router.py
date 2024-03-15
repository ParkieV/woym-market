from fastapi import APIRouter, File, Depends, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from pathlib import PurePath
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

data_router = APIRouter(
    prefix='/data',
    tags=['Data']
)


@data_router.get('/offers', response_model=list[OfferOut], dependencies=[Depends(get_current_user)])
async def get_offers():
    return await service.get_offers()


@data_router.patch('/offers', response_model=list[OfferOut])
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(require_staff)):
    return await service.change_offers(offers_data, current_user.id)


@data_router.get('/pricing-schemes', response_model=list[PricingSchemeOut])
async def get_pricing_schemes():
    return await service.get_pricing_schemes()


@data_router.post('/pricing-schemes')
async def create_pricing_schemes(data: PricingSchemeCreate):
    await service.create_pricing_scheme(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes')
async def update_pricing_schemes(data: PricingSchemeChange):
    await service.change_pricing_scheme(data)
    return {'status': 'OK'}


@data_router.delete('/pricing-schemes')
async def delete_pricing_schemes(names: list[str]):
    await service.delete_pricing_scheme(names)
    return {'status': 'OK'}


@data_router.get('/pricing-schemes/fields')
async def get_pricing_schemes_fields(pricing_scheme_name: str | None = None):
    raise NotImplementedError("Endpoint not implemented")


@data_router.post('/pricing-schemes/fields')
async def create_pricing_schemes_fields(data: PricingSchemeFieldCreate):
    await service.create_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes/fields')
async def update_pricing_schemes_fields(data):
    await service.change_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.post('/setup')
async def setup_offers_data(current_user=Depends(require_staff)):
    await service.setup_offers_data(current_user.id)
    return {'status': 'OK'}


@data_router.get('/export', dependencies=[Depends(require_staff)])
async def export_offers(market: Market = Market.YANDEX, export_type: ExportType = ExportType.TABLE, name_of_shop: str | None = None):
    path = await service.export_data(market, export_type, name_of_shop)
    return FileResponse(path=path, filename='out.xlsx', media_type='multipart/form-data')


@data_router.post('/import')
async def import_offers(data: UploadFile = File(), market: Market = None, import_type: ImportType = ImportType.TABLE, name_of_shop: str | None = None, current_user=Depends(require_staff)):
    content = await data.read()
    await service.import_data(content, market, import_type, name_of_shop, current_user.id, PurePath(data.filename).suffix)
    return {'status': 'OK'}







