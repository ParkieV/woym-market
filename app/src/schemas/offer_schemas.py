from pydantic import BaseModel, Field
from abc import ABC
from enum import Enum


class BasePricingScheme(BaseModel):
    name: str
    use_total_price: bool = False
    use_attractive_price_threshold: bool = False
    use_moderately_attractive_price_threshold: bool = False
    use_your_price_for_buyers: bool = False
    use_min_price_without_market: bool = False
    use_min_price_in_market: bool = False
    use_min_general_markets_price: bool = False
    n: float = 1
    m: float = 0

    @staticmethod
    def active_fields(dump: dict):
        return [k.replace('use_', '', 1) for k, v in dump.items() if k.startswith('use_') and v == True]


class PricingSchemeCreate(BasePricingScheme):
    pass


class PricingSchemeOut(BasePricingScheme):
    id: int


class PricingSchemeChange(PricingSchemeOut):
    pass


class BaseModelFields(ABC):
    _skip_fields = [
        'group_sellers_amount',
        'pricing_scheme',
        'business_id',
        'id',
    ]

    @classmethod
    def fields(cls):
        return {name: field.title for name, field in cls.model_fields.items() if name not in cls._skip_fields}

    @classmethod
    def reverse_fields(cls):
        return {field.title: name for name, field in cls.model_fields.items() if name not in cls._skip_fields}


class BaseOffer(BaseModel, BaseModelFields):
    sku: str = Field(title='sku')
    name_of_shop: str = Field(title='Название магазина')

    market: str = Field(title='Площадка')


class OfferChange(BaseOffer):
    self_weight: float | None = Field(title='Вес')
    self_length: float | None = Field(title='Длина')
    self_width: float | None = Field(title='Ширина')
    self_height: float | None = Field(title='Высота')

    dollar_cost_price: float | None = Field(title='Закупка у. е.', default=0)
    total_price_min_additional: float = Field(title='Мин. наценка на расчетную цену', default=200)
    total_price_coeff: float = Field(title='Коэфициент расчетной цены', default=2.4)

    note_1: str = Field('', title='Примечание 1')
    note_2: str = Field('', title='Примечание 2')
    note_3: str = Field('', title='Примечание 3')

    use_manual_min_price: bool = Field(True, title='Использовать ручную мин. цену')
    auto_min_price: float = Field(title='Авто мин. цена %')  # в процентах
    manual_min_price: float | None = Field(None, title='Ручная мин. цена')
    auto_price_control: bool = Field(False, title='Авто контроль цен')
    pricing_scheme_id: int = Field(title='Id схемы ценообразования')

    hidden: bool = Field(False, title='Скрыт')


class OfferOut(OfferChange):
    # from yandex api
    id: int = Field(title='id')
    name: str = Field(title='Название')

    yandex_weight: float | None = Field(title='Вес с маркета', default=0)
    yandex_length: float | None = Field(title='Длинна с маркета', default=0)
    yandex_width: float | None = Field(title='Ширина с маркета', default=0)
    yandex_height: float | None = Field(title='Высота с маркета', default=0)

    volume: float | None = Field(title='Объём (Длинна * ширина * высота / 1000)')
    yandex_volume: float | None = Field(title='Объём с яндекса')
    volume_difference: float | None = Field(title='Разница объемов', default=None)

    photo: str | None = Field(title='Фото')
    remaining_stock: int = Field(title='Остатки на складах')
    group_sellers_amount: int = Field(title='Количество продавцов в группе')
    business_id: int = Field(title='id бизнесса')

    # countable/editable values
    cost_price: float | None = Field(title='Себестоимость (Закупка у. е. * курс)')
    total_price: float | None = Field(title='Расчетная цена (Закупка * коэф. ?+ мин. наценка)')
    discount_base_price: float | None = Field(title='Цена до скидки (Текущая цена + 20%)')
    profit: float | None = Field(title='Прибыль (Текущая цена - закупка - FBY)')
    margin: float | None = Field(title='Окупаемость (Прибыль / закупка * 100)')
    fby: float | None = Field(title='Цена за FBY')

    attractive_price_threshold: float | None = Field(title='Порог для привлекательной цены')
    moderately_attractive_price_threshold: float | None = Field(title='Порог для умеренно привлекательной цены')
    best_place_wm: str | None = Field(title='Площадка с лучшей ценой (без учета Маркета)')
    min_price_without_market: float | None = Field(title='Цена площадки (без учета Маркета)')
    best_place_im: str | None = Field(title='Площадка с лучшей ценой (на Маркете)')
    min_price_in_market: float | None = Field(title='Цена площадки (на Маркете)')
    your_price_for_buyers: float | None = Field(title='Ваша цена для покупателей')
    min_general_markets_price: float | None = Field(title='Лучшая цена среди всех площадок')

    current_price: float | None = Field(title='Текущая цена')
    target_price: float | None = Field(title='Целевая цена')

    class Config:
        orm_mode = True




class OfferOutWithPriceScheme(OfferOut):
    pricing_scheme: PricingSchemeOut | None = None


class OfferDelete(BaseModel):
    sku: str
    name_of_shop: str
    market: str


class Market(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'
    ALL = 'all'


class ImportType(str, Enum):
    PRICES = 'prices'
    SIZES = 'sizes'
    TABLE = 'table'
    MATRIX_STOCKS = 'matrix-stocks'


class ExportType(str, Enum):
    TABLE = 'table'
    MATRIX_STOCKS = 'matrix-stocks'
    MATRIX_OFFERS = 'matrix-offers'

