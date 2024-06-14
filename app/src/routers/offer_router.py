from typing import Callable

from fastapi import APIRouter, File, Depends, UploadFile, status, Body, Form
from fastapi.responses import FileResponse
from pathlib import PurePath, Path

from pydantic import BaseModel
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
from src.services.base_utils import clean_up_files, import_handler_factory, export_handler_factory

data_router = APIRouter(
    prefix='/data',
    tags=['Data']
)



@data_router.get('/offers', response_model=list[OfferOut])
async def get_offers(offset: int = 0, limit: int | None = None):
    return await service.get_offers(offset=offset, limit=limit)


@data_router.patch('/offers', response_model=list[OfferOut])
async def change_offer_fields(offers_data: list[OfferChange], current_user=Depends(require_staff)):
    return await service.change_offers(offers_data, current_user.id)


@data_router.get('/pricing-schemes', response_model=list[PricingSchemeOut])
async def get_pricing_schemes():
    return await service.get_pricing_schemes()


@data_router.post('/pricing-schemes', dependencies=[Depends(require_staff)])
async def create_pricing_schemes(data: PricingSchemeCreate):
    await service.create_pricing_scheme(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes')
async def update_pricing_schemes(data: PricingSchemeChange, current_user=Depends(require_staff)):
    await service.change_pricing_scheme(current_user.id, data)
    return {'status': 'OK'}


@data_router.delete('/pricing-schemes', dependencies=[Depends(require_staff)])
async def delete_pricing_schemes(names: list[str]):
    await service.delete_pricing_scheme(names)
    return {'status': 'OK'}


@data_router.get('/pricing-schemes/fields', dependencies=[Depends(require_staff)])
async def get_pricing_schemes_fields(pricing_scheme_name: str | None = None):
    raise NotImplementedError("Endpoint not implemented")


@data_router.post('/pricing-schemes/fields', dependencies=[Depends(require_staff)])
async def create_pricing_schemes_fields(data: PricingSchemeFieldCreate):
    await service.create_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.patch('/pricing-schemes/fields', dependencies=[Depends(require_staff)])
async def update_pricing_schemes_fields(data: list[PricingSchemeFieldChange]):
    await service.change_pricing_scheme_field(data)
    return {'status': 'OK'}


@data_router.delete('/pricing-schemes/fields', dependencies=[Depends(require_staff)])
async def delete_pricing_schemes_fields(ids: list[int]):
    await service.delete_pricing_scheme_fields(ids)
    return {'status': 'OK'}


@data_router.post('/setup')
async def setup_offers_data(current_user=Depends(require_staff)):
    await service.setup_offers_data(current_user.id)
    return {'status': 'OK'}


class BodyDTO(BaseModel):
    market: Market | None = Form(None)
    name_of_shop: str | None = Form(None)
    warehouses: list[int] | None = Form(None)
    offers: list[int] | None = Form(None)
    warehouse_id: int | None = Form(None)


@data_router.post('/export', dependencies=[Depends(require_staff)])
async def export_offers(export_type: ExportType, data: BodyDTO = Depends()):
    path = Path(await export_handler_factory(export_type, **data.model_dump()))
    return FileResponse(path=str(path), filename=path.name, media_type='multipart/form-data', background=BackgroundTask(clean_up_files, path))


@data_router.post('/import')
async def import_offers(import_type: ImportType, data: BodyDTO = Depends(), file: UploadFile = File(...), current_user=Depends(require_staff)):
    content = await file.read()
    await import_handler_factory(import_type, data=content, user_id=current_user.id, file_extension=PurePath(file.filename).suffix, **data.model_dump())
    return {'status': 'OK'}






