from datetime import datetime
from enum import Enum

from pydantic import BaseModel

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

    default_auto_min_price: float
    default_auto_price_control: bool
    default_total_price_coeff: float
    default_total_price_min_additional: float
    default_auto_participation_in_promotions: bool
    default_pricing_scheme: str | None


class MarketUpdate(BaseModel):
    tax: float = 0
    discount_purchase: float
    long_term_storage_cost: float | None = None
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

    default_auto_min_price: float
    default_auto_price_control: bool
    default_total_price_coeff: float
    default_total_price_min_additional: float
    default_auto_participation_in_promotions: bool
    default_pricing_scheme: str


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

