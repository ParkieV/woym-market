from datetime import datetime
import math
from pydantic import BaseModel, Field, computed_field
from abc import ABC
from enum import Enum
from urllib.parse import urlparse
from urllib.parse import parse_qs


class PricingSchemeFieldCreate(BaseModel):
    key: str
    name: str
    pricing_scheme_name: str


class PricingSchemeFieldOut(BaseModel):
    id: int
    key: str
    name: str
    value: bool
    pricing_scheme_name: str


class PricingSchemeFieldChange(BaseModel):
    id: int
    value: bool


class PricingSchemeCreate(BaseModel):
    name: str
    market: str
    fields: list[PricingSchemeFieldCreate]


class PricingSchemeOut(BaseModel):
    name: str
    market: str
    n: float
    m: float
    fields: list[PricingSchemeFieldOut]

    def active_fields(self) -> list[str]:
        return [i.key for i in self.fields if i.value]


class PricingSchemeChange(BaseModel):
    name: str
    n: float
    m: float
    fields: list[PricingSchemeFieldChange]


class BaseModelFields(ABC):
    _skip_fields = [
        'group_sellers_amount',
        'pricing_scheme',
        'business_id',
        'id',
        'remaining_stock'
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


class OfferChange(BaseModel, BaseModelFields):
    id: int | None = Field(default=None, title='id')

    sku: str | None = Field(default=None, title='sku')
    name_of_shop: str = Field(default=None, title='Название магазина')
    market: str = Field(default=None, title='Площадка')

    name: str | None = Field(default=None, title='Название')
    description: str | None = Field(default=None, title='Описание')

    self_weight: float | None = Field(default=None, title='Вес')
    self_length: float | None = Field(default=None, title='Длина')
    self_width: float | None = Field(default=None, title='Ширина')
    self_height: float | None = Field(default=None, title='Высота')

    yandex_weight: float | None = Field(default=None, title='Вес c листа', description='Параметр редактируется только для Яндекс Мвркета')
    yandex_length: float | None = Field(default=None, title='Длинна с листа', description='Параметр редактируется только для Яндекс Мвркета')
    yandex_width: float | None = Field(default=None, title='Ширина с листа', description='Параметр редактируется только для Яндекс Мвркета')
    yandex_height: float | None = Field(default=None, title='Высота с листа', description='Параметр редактируется только для Яндекс Мвркета')

    wholesale_dollar_cost_price: float | None = Field(default=None, title='ОПТ закупка у. е.')

    auto_participation_in_promotions: bool | None = Field(default=None, title='Автоучастие в акциях')

    total_price_min_additional: float | None = Field(default=None, title='Мин. наценка на расчетную цену')
    total_price_coeff: float | None = Field(default=None, title='Коэфициент расчетной цены')

    note_1: str | None = Field('', title='Примечание 1')
    note_2: str | None = Field('', title='Примечание 2')
    note_3: str | None = Field('', title='Примечание 3')

    use_manual_min_price: bool | None = Field(default=None, title='Использовать ручную мин. цену')
    auto_min_price: float | None = Field(default=None, title='Авто мин. цена %')  # в процентах
    manual_min_price: float | None = Field(default=None, title='Ручная мин. цена')
    auto_price_control: bool | None = Field(default=None, title='Авто контроль цен')
    pricing_scheme_name: str | None = Field(default=None, title='Id схемы ценообразования')
    supplier_available: bool | None = Field(default=None, title='Наличие у поставщика')
    search_words: str | None = Field(default=None, title='Поисковые слова', max_length=255)
    use_promotion_price: bool | None = Field(default=None, title='Акция')
    barcodes: str | None = Field(default=None, title='Штрихкоды')

    synchronization: bool | None = Field(default=None, title='Синхронизация с каталогом')

    hidden: bool | None = Field(default=None, title='Скрыт')


class OfferOut(BaseModel, BaseModelFields):
    # from yandex api
    id: int = Field(title='id')

    sku: str = Field(title='sku')
    name_of_shop: str = Field(title='Название магазина')
    market: str = Field(title='Площадка')

    name: str | None = Field(title='Название')
    description: str | None = Field(title='Описание')

    self_weight: float | None = Field(title='Вес')
    self_weight_changed: bool = Field(title='Вес был изменен пользователем')

    self_length: float | None = Field(title='Длина')
    self_length_changed: bool = Field(title='Длина была изменена пользователем')

    self_width: float | None = Field(title='Ширина')
    self_width_changed: bool = Field(title='Ширина была изменена пользователем')

    self_height: float | None = Field(title='Высота')
    self_height_changed: bool = Field(title='Высота была изменена пользователем')

    wholesale_dollar_cost_price: float | None = Field(title='ОПТ закупка у. е.')

    auto_participation_in_promotions: bool = Field(title='Автоучастие в акциях')

    total_price_min_additional: float = Field(title='Мин. наценка на расчетную цену', default=200)
    total_price_coeff: float = Field(title='Коэфициент расчетной цены', default=2.4)

    note_1: str = Field('', title='Примечание 1')
    note_2: str = Field('', title='Примечание 2')
    note_3: str = Field('', title='Примечание 3')

    use_manual_min_price: bool = Field(True, title='Использовать ручную мин. цену')
    auto_min_price: float = Field(title='Авто мин. цена %')  # в процентах
    manual_min_price: float | None = Field(None, title='Ручная мин. цена')
    auto_price_control: bool = Field(False, title='Авто контроль цен')
    pricing_scheme_name: str = Field(title='Id схемы ценообразования')
    supplier_available: bool = Field(title='Наличие у поставщика')
    search_words: str | None = Field(title='Поисковые слова', max_length=255)
    use_promotion_price: bool = Field(title='Акция')
    barcodes: str | None = Field(title='Штрихкоды')

    synchronization: bool = Field(title='Синхронизация с каталогом')

    hidden: bool = Field(False, title='Скрыт')

    yandex_weight: float | None = Field(title='Вес с маркета', default=0)
    yandex_length: float | None = Field(title='Длинна с маркета', default=0)
    yandex_width: float | None = Field(title='Ширина с маркета', default=0)
    yandex_height: float | None = Field(title='Высота с маркета', default=0)

    volume: float | None = Field(title='Объём (Длинна * ширина * высота / 1000)')
    yandex_volume: float | None = Field(title='Объём с яндекса')
    volume_difference: float | None = Field(title='Разница объемов', default=None)

    photo: str | None = Field(title='Фото')
    group_sellers_amount: int | None = Field(title='Количество продавцов в группе')
    business_id: int | None = Field(title='id бизнесса')

    dollar_cost_price: float | None = Field(title='Закупка у. е.', default=0)

    catalog_note: str = Field(title='Примечание (Каталог)')

    # countable/editable values
    cost_price: float | None = Field(title='Себестоимость (Закупка у. е. * курс)')
    dollar_cost_price_updated_at: datetime | None = Field(title='Дата изменения стоимости закупки в y. e.')
    total_price: float | None = Field(title='Расчетная цена (Закупка * коэф. + мин. наценка)')
    discount_base_price: float | None = Field(title='Цена до скидки (Текущая цена + 20%)')
    profit: float | None = Field(title='Прибыль (Текущая цена - закупка - FBY)')
    margin: float | None = Field(title='Окупаемость (Прибыль / закупка * 100)')
    fbo: float | None = Field(title='Цена за FBO')

    content_rating: float | None = Field(title='Контент рейтинг')
    price_index: str | None = Field(title='Индекс цены')
    volume_profitability_ratio: float | None = Field(title=r'Коэффициент прибыльности от объёма (Прибыль \ объём)')
    days_to_zero_profit: float | None = Field(title='Дней до нулевой прибыли')
    market_discount_in_percent: float | None = Field(title=r'Скидка маркета в % (100-"цена для покупателей" * 100 \ "текущая цена")')

    attractive_price_threshold: float | None = Field(title='Порог для привлекательной цены')
    moderately_attractive_price_threshold: float | None = Field(title='Порог для умеренно привлекательной цены')
    best_place_wm: str | None = Field(title='Площадка с лучшей ценой (без учета Маркета)')
    min_price_without_market: float | None = Field(title='Цена площадки (без учета Маркета)')
    best_place_im: str | None = Field(title='Площадка с лучшей ценой (на Маркете)')
    min_price_in_market: float | None = Field(title='Цена площадки (на Маркете)')
    best_place_im_link: str | None = Field(title='Ссылка на магазин с лучшей ценой', exclude=True)
    your_price_for_buyers: float | None = Field(title='Ваша цена для покупателей')
    min_general_markets_price: float | None = Field(title='Лучшая цена среди всех площадок')
    vendor_code: int | None = Field(title='Артикул')
    recommended_retail_price: float | None = Field(title='РРЦ')
    stop_price: float | None = Field(title='Стоп цена')
    logistic_price: float | None = Field(title='Стоимость дополнительной логистики 1 литра')
    your_promotion_price: float | None = Field(title='Ваша цена по акции')
    search_words_changed: bool = Field(title='Поисковое слово изменено пользователем')

    current_price: float | None = Field(title='Текущая цена')
    target_price: float | None = Field(title='Целевая цена')

    name_changed: bool = Field(title='Название изменено пользователем')
    description_changed: bool = Field(title='Описание изменено')
    barcodes_changed: bool = Field(title='Штрихкоды изменены')

    @computed_field(title='Разница с РРЦ')
    @property
    def difference_from_recommended_retail_price(self) -> float | None:
        if all((self.recommended_retail_price, self.your_promotion_price)):
            return self.your_promotion_price - self.recommended_retail_price
        return None

    @property
    def violator_sku(self) -> str:
        if not self.best_place_im_link:
            return 'Не найдено'

        parsed_url = urlparse(self.best_place_im_link)
        captured = parse_qs(parsed_url.query)

        if 'sku' in captured:
            return ', '.join(captured['sku'])
        return 'Не найден'

    @computed_field()
    @property
    def violator(self) -> str:
        if not all((self.recommended_retail_price, self.min_price_in_market)):
            return ''

        if self.recommended_retail_price > self.min_price_in_market:
            return f'SKU: {self.violator_sku}, Маркетплейс: {self.market}, Магазин: {self.best_place_im}, Цена: {round(self.min_price_in_market)}, РРЦ: {round(self.recommended_retail_price)}'

        return ''


class OfferOutWithPriceScheme(OfferOut):
    pricing_scheme: PricingSchemeOut | None = None


class OfferDelete(BaseModel):
    sku: str
    name_of_shop: str
    market: str


class Market(str, Enum):
    OZON = 'ozon'
    YANDEX = 'yandex'
    WILDBERRIES = 'wildberries'


class ImportType(str, Enum):
    PRICES = 'prices'
    SIZES = 'sizes'
    TABLE = 'table'


class ExportType(str, Enum):
    TABLE = 'table'


class ViolatorDTO(BaseModel):
    market: str
    name_of_shop: str
    price: float
    recommended_retail_price: float
    link: str

    @computed_field()
    @property
    def sku(self) -> str:
        parsed_url = urlparse(self.link)
        captured = parse_qs(parsed_url.query)
        if 'sku' in captured:
            return ', '.join(captured['sku'])
        return 'Не найден'