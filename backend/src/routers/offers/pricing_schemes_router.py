from fastapi import APIRouter, Depends, Body

from src.dependencies.users import require_staff, get_current_user
from src.schemas.offer_schemas import PricingSchemeOut, PricingSchemeCreate, PricingSchemeChange, \
    PricingSchemeFieldCreate, PricingSchemeFieldChange
from src.services import offer_service as service

router = APIRouter(
    prefix="/pricing-schemes",
    tags=["Схемы ценообразования"],
)


@router.get('', response_model=list[PricingSchemeOut], dependencies=[Depends(get_current_user)], summary='Список схем ценообразования')
async def get_pricing_schemes():
    schemes_dict = await service.get_pricing_schemes()
    return list(schemes_dict.values())


@router.post('', dependencies=[Depends(require_staff)], summary='Создание схемы ценообразования')
async def create_pricing_schemes(data: PricingSchemeCreate):
    await service.create_pricing_scheme(data)
    return {'status': 'OK'}


@router.patch('', summary='Обновление схемы ценообразования')
async def update_pricing_schemes(data: PricingSchemeChange, current_user=Depends(require_staff)):
    await service.change_pricing_scheme(current_user.id, data)
    return {'status': 'OK'}


@router.delete('', dependencies=[Depends(require_staff)], summary='Удаление схем ценообразования')
async def delete_pricing_schemes(names: list[str] = Body(embed=True, title='Названия схем')):
    await service.delete_pricing_scheme(names)
    return {'status': 'OK'}


@router.get('/fields', dependencies=[Depends(require_staff)], deprecated=True)
async def get_pricing_schemes_fields(pricing_scheme_name: str | None = None):
    raise NotImplementedError("Endpoint not implemented")


@router.post('/fields', dependencies=[Depends(require_staff)], summary='Добавление поля для схемы')
async def create_pricing_schemes_fields(data: PricingSchemeFieldCreate):
    await service.create_pricing_scheme_field(data)
    return {'status': 'OK'}


@router.patch('/fields', dependencies=[Depends(require_staff)], summary='Изменение значений полей схем')
async def update_pricing_schemes_fields(data: list[PricingSchemeFieldChange]):
    await service.change_pricing_scheme_field(data)
    return {'status': 'OK'}


@router.delete('/fields', dependencies=[Depends(require_staff)], summary='Удаление полей из схемы')
async def delete_pricing_schemes_fields(ids: list[int] = Body(embed=True, title='ID поля схемы')):
    await service.delete_pricing_scheme_fields(ids)
    return {'status': 'OK'}
