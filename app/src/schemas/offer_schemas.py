from pydantic import BaseModel, Field
from abc import ABC


class BaseModelFields(ABC):
    skip_fields = []

    @classmethod
    def fields(cls):
        return {name: field.title for name, field in cls.model_fields.items()}

    @classmethod
    def reverse_fields(cls):
        return {field.title: name for name, field in cls.model_fields.items()}


class OfferOut(BaseModel, BaseModelFields):
    # from yandex api
    sku: str = Field(title='sku')
    name: str = Field(title='Название')

    self_weight: float = Field(title='Вес')
    self_length: float = Field(title='Длинна')
    self_width: float = Field(title='Ширина')
    self_height: float = Field(title='Высота')

    yandex_weight: float = Field(title='Вес с маркета', default=0)
    yandex_length: float = Field(title='Длинна с маркета', default=0)
    yandex_width: float = Field(title='Ширина с маркета', default=0)
    yandex_height: float = Field(title='Высота с маркета', default=0)

    volume: float = Field(title='Объём (Длинна * ширина * высота / 1000)')
    yandex_volume: float = Field(title='Объём с яндекса')
    volume_difference: float | None = Field(title='Разница объемов', default=None)

    photo: str | None = Field(title='Фото')
    remaining_stock: int = Field(title='Остатки на складах')
    name_of_shop: str = Field(title='Название магазина')
    group_sellers_amount: int = Field(title='Количество продавцов в группе')
    business_id: int = Field(title='id бизнесса')

    # countable/editable values
    dollar_cost_price: float = Field(title='Закупка у. е.')
    total_price_coeff: float = Field(title='Коэфициент расчетной цены')
    cost_price: float = Field(title='Себестоимость (Закупка у. е. * курс)')
    total_price_min_additional: float = Field(title='Мин. наценка на расчетную цену')
    total_price: float = Field(title='Расчетная цена (Закупка * коэф. ?+ мин. наценка)')
    discount_base_price: float | None = Field(title='Цена до скидки (Текущая цена + 20%)')
    profit: float | None = Field(title='Прибыль (Текущая цена - закупка - FBY)')
    margin: float | None = Field(title='Окупаемость (Прибыль / закупка * 100)')
    fby: float | None = Field(title='Цена за FBY')

    attractive_price_threshold: float | None = Field(title='Порог для привлекательной цены')
    moderately_attractive_price_threshold: float | None = Field(title='Порог для умеренно привлекательной цены')
    best_place_wm: str | None = Field(title='Площадка с лучшей ценой (без учета Маркета)')
    best_price_wm: float | None = Field(title='Цена площадки (без учета Маркета)')
    best_place_im: str | None = Field(title='Площадка с лучшей ценой (на Маркете)')
    best_price_im: float | None = Field(title='Цена площадки (на Маркете)')
    minimum_group_price: float = Field(title='Минимальная цена в группе')

    current_price: float | None = Field(title='Текущая цена')
    target_price: float | None = Field(title='Целевая цена')

    # User additional fields
    note_1: str | None = Field(None, title='Примечание 1')
    note_2: str | None = Field(None, title='Примечание 2')
    note_3: str | None = Field(None, title='Примечание 3')

    use_manual_min_price: bool = Field(True, title='Использовать ручную мин. цену') # использовать ли автоматический расчет нижней планки цены
    auto_min_price: float = Field(title='Авто мин. цена %') # в процентах
    manual_min_price: float | None = Field(None, title='Ручная мин. цена')

    auto_price_control: bool = Field(False, title='Авто контроль цен')

    class Config:
        orm_mode = True


class OfferChange(BaseModel):
    sku: str
    name_of_shop: str
    dollar_cost_price: float
    total_price_min_additional: float
    total_price_coeff: float

    note_1: str | None = None
    note_2: str | None = None
    note_3: str | None = None

    use_manual_min_price: bool = True # использовать ли автоматический расчет нижней планки цены
    auto_min_price: float # в процентах
    manual_min_price: float | None = None
    auto_price_control: bool = False # ручное управление ценами


class OfferDelete(BaseModel):
    sku: str



