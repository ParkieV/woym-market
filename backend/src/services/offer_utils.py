
import pandas as pd
import numpy as np

from src.api.interfaces import ApiTypes
from src.database.offer import get_pricing_schemes
from src.database.db import async_session
from src.schemas.settings_schemas import MarketOut
from src.schemas.offer_schemas import PricingSchemeOut


async def calculate_offers_values(data: pd.DataFrame, market_settings: MarketOut, pricing_schemes: dict[str, PricingSchemeOut] | None = None) -> pd.DataFrame:
    """
    Расчёт вычисляемых значений в карточках

    data - список карточек в виде таблицы
    market_settings - настройки магазинов для вычисления значений
    pricing_schemes - схемы ценообразования

    Список карточек с обновленными вычисляемыми значениями
    """
    if pricing_schemes is None:
        async with async_session() as session:
            pricing_schemes = await get_pricing_schemes(session)

    data = data.copy()

    # Расчет объёма
    data.loc[:, 'volume'] = data['self_width'] * data['self_height'] * data['self_length'] / 1000

    # Расчет стоимости поставки в долларах
    data.loc[:, 'dollar_cost_price'] = np.where(
        data['wholesale_dollar_cost_price'].isna(),
        data['dollar_cost_price'],
        np.where(
            data['use_promotion_price'],
            data['wholesale_dollar_cost_price'],
            data['wholesale_dollar_cost_price'] * (1 - market_settings.discount_purchase / 100)
        )
    )
    # Расчет стоимости
    data.loc[:, 'cost_price'] = (
        data['dollar_cost_price'] * market_settings.rate +
        (np.ceil(data['volume']) - market_settings.volume_threshold_for_additional_logistics) *
        market_settings.cost_of_additional_logistics_per_liter
    )
    data.loc[:, 'total_price'] = (
        data['cost_price'] * data['total_price_coeff'] + data['total_price_min_additional']
    )
    data.loc[:, 'recommended_retail_price'] = (
        market_settings.first_variable_for_recommended_retail_price +
        (data['wholesale_dollar_cost_price'] * market_settings.rate) +
        (market_settings.second_variable_for_recommended_retail_price / 100 *
         data['wholesale_dollar_cost_price'] * market_settings.rate)
    )
    data.loc[:, 'stop_price'] = (
        market_settings.first_variable_for_stop_price +
        (data['wholesale_dollar_cost_price'] * market_settings.rate) +
        (market_settings.second_variable_for_stop_price / 100 *
         data['wholesale_dollar_cost_price'] * market_settings.rate)
    )

    data = await calculate_price(data, market_settings, pricing_schemes)

    data.loc[:, 'logistic_price'] = np.where(
        data['volume'] > market_settings.volume_threshold_for_additional_logistics,
        np.ceil(data['volume'] - market_settings.volume_threshold_for_additional_logistics) *
        market_settings.cost_of_additional_logistics_per_liter,
        0
    )
    data['logistic_price'].fillna(0, inplace=True)
    data.loc[:, 'fbo'] = (
        data['current_price'] * (market_settings.fbo_sales_commission / 100)
    ) + data['logistic_price']

    
    data.loc[:, 'market_discount_in_percent'] = np.where(
        data['your_promotion_price'] > 0,
        100 - data['your_price_for_buyers'] * 100 / data['your_promotion_price'],
        0
    )

    data.loc[:, 'profit'] = np.nan
    data.loc[:, 'days_to_zero_profit'] = np.nan

    data.loc[:, 'profit'] = (
        data['your_promotion_price'] * (1 - market_settings.tax / 100)
        - data['fbo'] - data['cost_price']
    )
    
    
    data.loc[:, 'days_to_zero_profit'] = np.where(
        (market_settings.long_term_storage_cost or 0) > 0,
        data['profit'] / market_settings.long_term_storage_cost,
        np.nan
    )

    
    data.loc[:, 'margin'] = np.where(
        data['cost_price'] > 0,
        data['profit'] / data['cost_price'] * 100,
        np.nan
    )

    data.loc[:, 'volume_profitability_ratio'] = np.where(
        data['volume'] == 0,
        0,
        data['profit'] / data['volume']
    )
    data.drop(columns=['volume'], inplace=True)

    data.loc[:, 'discount_base_price'] = data['current_price'] * (1.0 + market_settings.price_before_discount / 100)

    data = round_values(data)

    return data


async def calculate_price(data: pd.DataFrame, market_settings: MarketOut, pricing_schemes: dict[str, PricingSchemeOut]) -> pd.DataFrame:
    data = data.copy()
    data['min_level'] = np.nan

    for price_scheme in pricing_schemes.values():
        sum_fields = price_scheme.active_fields()
        n = price_scheme.n
        m = price_scheme.m

        data['min_level'] = np.where(
            data['pricing_scheme_name'] == price_scheme.name,
            (data[sum_fields].sum(axis=1, skipna=False) / n) + (data[sum_fields].sum(axis=1, skipna=False) / n) * (m / 100),
            data['min_level']
        )

    data['min_level'] = data['min_level'].replace(0, np.nan)

    data['final_min_price'] = np.nan
    
    # используем ручную мин планку
    manual_mask = data['use_manual_min_price'] == True
    data.loc[manual_mask, 'final_min_price'] = data.loc[manual_mask, 'min_level']
    
    #  используем автоматическую мин планку
    auto_mask = data['use_manual_min_price'] == False
    data.loc[auto_mask, 'final_min_price'] = (
        data.loc[auto_mask, 'total_price'] * data.loc[auto_mask, 'auto_min_price'] / 100
    )

    data['target_price'] = data[['total_price', 'final_min_price']].max(axis=1)
    
    data['target_price'] = data['target_price'].fillna(data['total_price'])

    data.drop(columns=['min_level'], inplace=True)

    return data


async def build_offers_data(data: pd.DataFrame, market, total_price_coeff: float = 2.4, total_price_min_additional: float = 200, setup_mode: bool = False, default_price_scheme_id: int = 1) -> pd.DataFrame:
    data = data.copy()

    if data.empty:
        return data

    data['dollar_cost_price'] = np.nan  # закупка
    data[['self_weight', 'self_length', 'self_width', 'self_height']] = np.nan
    data['pricing_scheme_name'] = None

    data['pricing_scheme_name'] = np.where(
        data['market'] == ApiTypes.OZON,
        'O0',
        data['pricing_scheme_name']
    )
    data['pricing_scheme_name'] = np.where(
        data['market'] == ApiTypes.YANDEX,
        'Y0',
        data['pricing_scheme_name']
    )
    data['pricing_scheme_name'] = np.where(
        data['market'] == ApiTypes.WILDBERRIES,
        'W0',
        data['pricing_scheme_name']
    )

    data['wholesale_dollar_cost_price'] = np.nan
    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['auto_min_price'] = 100
    data['manual_min_price'] = 100
    data['target_price'] = np.nan

    data['use_manual_min_price'] = False
    data['auto_price_control'] = False
    data['use_promotion_price'] = False
    data['yandex_length'] = np.nan
    data['yandex_width'] = np.nan
    data['yandex_height'] = np.nan
    data['yandex_weight'] = np.nan

    data = await calculate_offers_values(data, market)
    data[['photo', 'name_of_shop', 'market', 'best_place_wm', 'best_place_im', 'price_index']] = data[['photo', 'name_of_shop', 'market', 'best_place_wm', 'best_place_im', 'price_index']].astype('string')

    return data


def round_values(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    df[['current_price', 'target_price', 'cost_price', 'total_price', 'discount_base_price', 'profit', 'margin', 'fbo']] = df[['current_price', 'target_price', 'cost_price', 'total_price', 'discount_base_price', 'profit', 'margin', 'fbo']].round()

    return df
