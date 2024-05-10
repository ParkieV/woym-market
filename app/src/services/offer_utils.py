import pandas as pd
import numpy as np
from io import BytesIO
from fastapi import HTTPException, status
from src.database.offer_db import get_pricing_schemes
from src.database.db import async_session
from src.database.settings_db import get_markets


def count_fbo(data: pd.DataFrame, settings) -> pd.Series:
    data = data.copy()
    # 19% - коммисия за продажу (дача, сад и огород, содовый инвентарь)
    # 1% - перевод денежных средств магазину
    # если dimensions_sum < 150 и вес < 25 кг, то 3% (20 <= x <= 60), иначе 350 - доставка внутри округа
    # если dimensions_sum < 150 и вес < 25 кг, то 3% (20 <= x <= 60), иначе 350 - доставка внутри округа

    dimensions_sum = data['yandex_length'] + data['yandex_width'] + data['yandex_height']
    dimensions_sum.fillna(0, inplace=True)

    delivery_and_warehouse_processing_price = np.where(
        (dimensions_sum < 150) | (data['yandex_weight'] < 25),
        data['current_price'] * 0.06,
        350 * 2
    )

    data['fbo'] = np.where(
        data['market'] == 'ozon',
        data['fbo'],
        data['current_price'] * (settings.fbo_sales_commission / 100) + delivery_and_warehouse_processing_price + data['current_price'] * 0.01
    )
    return data['fbo']


async def calculate_offers_values(data: pd.DataFrame, settings) -> pd.DataFrame:
    data = data.copy()

    data['fbo'] = count_fbo(data, settings)
    data['yandex_volume'] = data['yandex_length'] * data['yandex_width'] * data['yandex_height'] / 1000
    data['volume'] = data['self_length'] * data['self_width'] * data['self_height'] / 1000
    data['volume_difference'] = data['yandex_volume'] / data['volume']
    data['cost_price'] = data['dollar_cost_price'] * settings.rate
    data['total_price'] = data['cost_price'] * data['total_price_coeff'] + data['total_price_min_additional']

    data = await calculate_price(data)

    data['market_discount_in_percent'] = 100 - data['your_price_for_buyers'] * 100 / data['current_price']

    data['profit'] = np.nan
    data['days_to_zero_profit'] = np.nan

    data['temp_profit_base'] = np.where(
        data['your_price_for_buyers'].isna() | data['your_price_for_buyers'] is None,
        data['current_price'],
        data['your_price_for_buyers']
    )

    async with async_session() as session:
        for market in await get_markets(session):
            data['profit'] = np.where(
                ((data['market'] == market.type) & (data['name_of_shop'] == market.name)),
                data['temp_profit_base'] * (1 - market.tax / 100) - data['fbo'] - data['cost_price'],
                data['profit']
            )
            data['days_to_zero_profit'] = np.where(
                ((data['market'] == market.type) & (data['name_of_shop'] == market.name)),
                data['profit'] / (market.long_term_storage_cost or np.nan),
                data['days_to_zero_profit']
            )

    data.drop('temp_profit_base', axis=1, inplace=True)

    data['margin'] = data['profit'] / data['cost_price'] * 100

    data['volume_profitability_ratio'] = np.where(
        data['volume'] == 0,
        0,
        data['profit'] / data['volume']
    )

    data = round_values(data)

    return data


async def calculate_price(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data['min_level'] = np.nan

    async with async_session() as session:
        for price_scheme in await get_pricing_schemes(session):
            sum_fields = price_scheme.active_fields()
            n = price_scheme.n
            m = price_scheme.m

            data['min_level'] = np.where(
                data['pricing_scheme_name'] == price_scheme.name,
                (data[sum_fields].sum(axis=1, skipna=False) / n) + (data[sum_fields].sum(axis=1, skipna=False) / n) * (m / 100),
                data['min_level']
            )

    data['min_price_in_market'] = data['min_price_in_market'].replace({None: np.nan})

    data['min_level'] = np.where(
        (data['min_level'] < data['min_price_in_market']) | (np.isnan(data['min_level'])),
        data['min_price_in_market'],
        data['min_level']
    )
    data['min_level'] = data['min_level'].replace(0, np.nan)

    # используем ручную мин планку
    sub_data_2 = data[data['use_manual_min_price'] == True]
    sub_data_2.loc[:, 'target_price'] = np.where(
        (sub_data_2['current_price'] >= sub_data_2['min_price_in_market']),
        sub_data_2[['min_level', 'manual_min_price']].max(axis=1),
        sub_data_2[['total_price', 'min_level']].min(axis=1)
    )
    # total_price = верхняя планка
    #  используем автоматическую мин планку
    sub_data_3 = data[data['use_manual_min_price'] == False]
    sub_data_3['temp_auto_min_price'] = sub_data_3['total_price'] * sub_data_3['auto_min_price'] / 100
    sub_data_3.loc[:, 'target_price'] = np.where(
        sub_data_3['current_price'] >= sub_data_3['min_price_in_market'],
        sub_data_3[['min_level', 'temp_auto_min_price']].max(axis=1),
        sub_data_3[['total_price', 'min_level']].min(axis=1)
    )
    sub_data_3.drop('temp_auto_min_price', axis=1, inplace=True)

    df = pd.concat([sub_data_2, sub_data_3])
    df.reset_index(drop=True, inplace=True)
    df.drop('min_level', axis=1, inplace=True)

    # прибовляем 5% если магазин с лучшей ценой это текущий магазин
    df[['target_price', 'min_price_in_market']] = df[['target_price', 'min_price_in_market']].astype(float)

    df['target_price'] = np.where(
        (df['best_place_im'] == df['name_of_shop']) & (df['min_price_in_market'].round() == df['target_price'].round()),
        (df['target_price'] * 1.05).round(),
        df['target_price'].round()
    )
    return df


async def build_offers_data(data: pd.DataFrame, settings, total_price_coeff: float = 2.4, total_price_min_additional: float = 200, setup_mode: bool = False, default_price_scheme_id: int = 1) -> pd.DataFrame:
    data = data.copy()

    if data.empty:
        return data

    if setup_mode:
        data['dollar_cost_price'] = np.nan  # закупка
        data[['self_weight', 'self_length', 'self_width', 'self_height']] = np.nan
        # data['pricing_scheme_name'] = 'Y0' if data['market'] == 'yandex' else 'O0'
        data['pricing_scheme_name'] = np.where(
            data['market'] == 'yandex',
            'Y0',
            'O0'
        )

    data['total_price_coeff'] = total_price_coeff
    data['total_price_min_additional'] = total_price_min_additional

    data['auto_min_price'] = 100
    data['manual_min_price'] = 100
    data['target_price'] = np.nan

    data['use_manual_min_price'] = False
    data['auto_price_control'] = True

    data = await calculate_offers_values(data, settings)
    data['auto_price_control'] = False
    data[['photo', 'name_of_shop', 'market', 'best_place_wm', 'best_place_im', 'price_index']] = data[['photo', 'name_of_shop', 'market', 'best_place_wm', 'best_place_im', 'price_index']].astype('string')

    return data


def bytes_to_data_frame(data: bytes, sheet_name: str | int = 0, file_extension: str = 'xlsx') -> pd.DataFrame:
    io = BytesIO(data)
    pd_engine = {
        '.xlsx': 'openpyxl',
        '.xls': 'xlrd'
    }
    if file_extension not in pd_engine.keys():
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f'Файлы с расширением "{file_extension}" не поддерживаются')

    return pd.read_excel(io, engine=pd_engine[file_extension], sheet_name=sheet_name)


def round_values(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()

    df[['current_price', 'target_price', 'cost_price', 'total_price', 'discount_base_price', 'profit', 'margin', 'fbo']] = df[['current_price', 'target_price', 'cost_price', 'total_price', 'discount_base_price', 'profit', 'margin', 'fbo']].round()

    return df
