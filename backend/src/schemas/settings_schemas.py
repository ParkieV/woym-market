from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator, field_validator

from src.api.factory import APITypes


class LogsOut(BaseModel):
    updated_at: datetime | None


class SettingsOut(BaseModel):
    id: int
    user_id: int


class SettingsUpdate(BaseModel):
    pass


class ColumnDataType(str, Enum):
    STRING = 'string'
    INTEGER = 'int'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    IMAGE = 'image'
    RUB = 'ruble'
    USD = 'dollar'
    PERCENT = 'percent'
    URL = 'url'
    COMBOBOX = 'combobox'


class Tables(str, Enum):
    OFFERS = 'offers'
    MATRIX_STOCKS = 'matrix_stocks'
    MATRIX_WAREHOUSES = 'matrix_warehouses'


class BaseTableInfo(BaseModel):
    data: str | None = None
    name: str


class TableInfoCreate(BaseTableInfo):
    pass


class TableInfoUpdate(BaseTableInfo):
    pass


class TableInfoOut(TableInfoUpdate):
    updated_at: datetime


class MarketOut(BaseModel):
    id: int
    name: str
    tax: float = 0
    type: APITypes
    discount_purchase: float
    long_term_storage_cost: float | None
    rate: float
    fbo_sales_commission: float
    first_variable_for_recommended_retail_price: float
    second_variable_for_recommended_retail_price: float
    first_variable_for_stop_price: float
    second_variable_for_stop_price: float
    price_before_discount: float
    volume_threshold_for_additional_logistics: float
    cost_of_additional_logistics_per_liter: float
    a_variable_for_smart_delivery: float
    b_variable_for_smart_delivery: float
    c_variable_for_smart_delivery: float
    d_variable_for_smart_delivery: float
    e_variable_for_smart_delivery: float

    default_auto_min_price: float | None = None
    default_auto_price_control: bool | None = None
    default_total_price_coeff: float | None = None
    default_total_price_min_additional: float | None = None
    default_auto_participation_in_promotions: bool | None = None
    default_pricing_scheme: str | None = None
    consider_logistic_cost: bool = Field(title='Учитывать в целевой цене товара стоимость дополнительной логистики', description='Если включено, то к «Целевая цена» прибавляем «Цена доп. логистики за 1 литр (₽)» * («объем» товара с маркетплейса, округленный до целого в большую сторону и минус 1)', default=False)

    @field_validator('a_variable_for_smart_delivery',
                        'b_variable_for_smart_delivery',
                        'c_variable_for_smart_delivery',
                        'd_variable_for_smart_delivery',
                        'e_variable_for_smart_delivery', mode='before')
    def validate_null(cls, value: float | None) -> float:
        if value is None:
            return 0
        return value


class MarketUpdate(BaseModel):
    tax: float = 0
    discount_purchase: float
    long_term_storage_cost: float | None = None
    rate: float = Field(title='Курс')
    fbo_sales_commission: float
    first_variable_for_recommended_retail_price: float
    second_variable_for_recommended_retail_price: float
    first_variable_for_stop_price: float
    second_variable_for_stop_price: float
    price_before_discount: float
    volume_threshold_for_additional_logistics: float = Field(title='Порог для расчета цены за доп логистики')
    cost_of_additional_logistics_per_liter: float = Field(title='Цена доп логистики за 1 литр')
    a_variable_for_smart_delivery: float = Field(title='Переменная A для расчета умной поставки', description='«заказы за 7 дней» * **A** + «заказы за 14 дней» * B + «заказы за 28 дней» * C + «заказы за 60 дней» * D + «заказы за 120 дней» * E')
    b_variable_for_smart_delivery: float = Field(title='Переменная B для расчета умной поставки', description='«заказы за 7 дней» * A + «заказы за 14 дней» * **B** + «заказы за 28 дней» * C + «заказы за 60 дней» * D + «заказы за 120 дней» * E')
    c_variable_for_smart_delivery: float = Field(title='Переменная C для расчета умной поставки', description='«заказы за 7 дней» * A + «заказы за 14 дней» * B + «заказы за 28 дней» * **C** + «заказы за 60 дней» * D + «заказы за 120 дней» * E')
    d_variable_for_smart_delivery: float = Field(title='Переменная D для расчета умной поставки', description='«заказы за 7 дней» * A + «заказы за 14 дней» * B + «заказы за 28 дней» * C + «заказы за 60 дней» * **D** + «заказы за 120 дней» * E')
    e_variable_for_smart_delivery: float = Field(title='Переменная E для расчета умной поставки', description='«заказы за 7 дней» * A + «заказы за 14 дней» * B + «заказы за 28 дней» * C + «заказы за 60 дней» * D + «заказы за 120 дней» * **E**')

    default_auto_min_price: float | None = Field(title='Значение авто мин цены по умолчанию для новых товаров')
    default_auto_price_control: bool | None = Field(title='Значение **автоконтроля цен** по умолчанию для новых товаров')
    default_total_price_coeff: float | None = Field(title='Значение **коэффициента расчетной цены** по умолчанию для новых товаров')
    default_total_price_min_additional: float | None = Field(title='Значение **мин наценки на расчетную цену** по умолчанию для новых товаров')
    default_auto_participation_in_promotions: bool | None = Field(title='Значения **автоучастия в акциях** по умолчанию для для новых товаров')
    default_pricing_scheme: str | None = Field(title='Схема ценообразования по умолчанию для новых товаров', description='Если не указана, то для новых товаров по умолчанию будет устанавливаться схема {MARKET}0')
    consider_logistic_cost: bool = Field(title='Учитывать в целевой цене товара стоимость дополнительной логистики', description='Если включено, то к «Целевая цена» прибавляем «Цена доп. логистики за 1 литр (₽)» * («объем» товара с маркетплейса, округленный до целого в большую сторону и минус 1). Т.е. расчет доп наценки идет начиная со второго литра и дальше')


class MarketFullOut(MarketOut):
    token: str
    entity_id: int | None


class MarketFullUpdate(MarketFullOut):
    pass


class MarketCreate(BaseModel):
    name: str
    tax: float = 0
    type: APITypes
    token: str
    entity_id: int | None

