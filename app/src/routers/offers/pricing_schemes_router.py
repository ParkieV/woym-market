from fastapi import APIRouter, Depends

from src.dependencies.users import require_staff, get_current_user
from src.schemas.offer_schemas import PricingSchemeOut, PricingSchemeCreate, PricingSchemeChange, \
    PricingSchemeFieldCreate, PricingSchemeFieldChange
from src.services import offer_service as service

router = APIRouter(
    prefix="/pricing-schemes",
    tags=["Схемы ценообразования"],
)


@router.get('', response_model=list[PricingSchemeOut], dependencies=[Depends(get_current_user)])
async def get_pricing_schemes():
    return await service.get_pricing_schemes()


@router.post('', dependencies=[Depends(require_staff)])
async def create_pricing_schemes(data: PricingSchemeCreate):
    await service.create_pricing_scheme(data)
    return {'status': 'OK'}


@router.patch('')
async def update_pricing_schemes(data: PricingSchemeChange, current_user=Depends(require_staff)):
    await service.change_pricing_scheme(current_user.id, data)
    return {'status': 'OK'}


@router.delete('', dependencies=[Depends(require_staff)])
async def delete_pricing_schemes(names: list[str]):
    await service.delete_pricing_scheme(names)
    return {'status': 'OK'}


@router.get('/fields', dependencies=[Depends(require_staff)])
async def get_pricing_schemes_fields(pricing_scheme_name: str | None = None):
    raise NotImplementedError("Endpoint not implemented")


@router.post('/fields', dependencies=[Depends(require_staff)])
async def create_pricing_schemes_fields(data: PricingSchemeFieldCreate):
    await service.create_pricing_scheme_field(data)
    return {'status': 'OK'}


@router.patch('/fields', dependencies=[Depends(require_staff)])
async def update_pricing_schemes_fields(data: list[PricingSchemeFieldChange]):
    await service.change_pricing_scheme_field(data)
    return {'status': 'OK'}


@router.delete('/fields', dependencies=[Depends(require_staff)])
async def delete_pricing_schemes_fields(ids: list[int]):
    await service.delete_pricing_scheme_fields(ids)
    return {'status': 'OK'}
