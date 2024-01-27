from src.database import settings_db as db
from src.database.db import async_session
from src.schemas.settings_schemas import SettingsUpdate, ColumnUpdate, ColumnDataType, ColumnCreate

columns_info = [
    ColumnCreate(
        index=0,
        key='sku',
        name='SKU',
        data_type=ColumnDataType.STRING,
        editable=False,
        pinned=True,
    ),
    ColumnCreate(
        index=0,
        key='name',
        name='Название',
        data_type=ColumnDataType.STRING,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='self_weight',
        name='Вес',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='self_length',
        name='Длина',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='self_width',
        name='Ширина',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='self_height',
        name='Высота',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='yandex_weight',
        name='Вес с маркета',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='yandex_length',
        name='Длина с маркета',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='yandex_width',
        name='Ширина с маркета',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='yandex_height',
        name='Высота с маркета',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='volume',
        name='Объём',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Длинна * ширина * высота / 1000'
    ),
    ColumnCreate(
        index=0,
        key='yandex_volume',
        name='Объём с яндекса',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Длинна * ширина * высота / 1000'
    ),
    ColumnCreate(
        index=0,
        key='volume_difference',
        name='Разница объемов',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='photo',
        name='Фото',
        data_type=ColumnDataType.IMAGE,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='name_of_shop',
        name='Название магазина',
        data_type=ColumnDataType.STRING,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='market',
        name='Площадка',
        data_type=ColumnDataType.STRING,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='remaining_stock',
        name='Остатки на складах',
        data_type=ColumnDataType.INTEGER,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='dollar_cost_price',
        name='Закупка у. е.',
        data_type=ColumnDataType.USD,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='total_price_coeff',
        name='Коэффициент расчетной цены',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='cost_price',
        name='Себестоимость',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Закупка у. е. * курс'
    ),
    ColumnCreate(
        index=0,
        key='total_price_min_additional',
        name='Мин. наценка на расчетную цену',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='total_price',
        name='Расчетная цена',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Закупка * коэф. ?+ мин. наценка'
    ),
    ColumnCreate(
        index=0,
        key='discount_base_price',
        name='Цена до скидки',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Цена + 20%'
    ),
    ColumnCreate(
        index=0,
        key='profit',
        name='Прибыль',
        data_type=ColumnDataType.FLOAT,
        editable=False,
        tooltip='Цена - закупка - FBY'
    ),
    ColumnCreate(
        index=0,
        key='margin',
        name='Окупаемость',
        data_type=ColumnDataType.PERCENT,
        editable=False,
        tooltip='Прибыль / закупка * 100'
    ),
    ColumnCreate(
        index=0,
        key='fby',
        name='Цена за FBY',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='attractive_price_threshold',
        name='Порог для привлекательной цены',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='moderately_attractive_price_threshold',
        name='Порог для умеренно привлекательной цены',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='best_place_wm',
        name='Площадка с лучшей ценой (без учета Маркета)',
        data_type=ColumnDataType.STRING,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='best_price_wm',
        name='Цена площадки (без учета Маркета)',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='best_place_im',
        name='Площадка с лучшей ценой (на Маркете)',
        data_type=ColumnDataType.STRING,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='best_price_im',
        name='Цена площадки (на Маркете)',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='minimum_group_price',
        name='Минимальная цена в группе',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='current_price',
        name='Текущая цена',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='target_price',
        name='Целевая цена',
        data_type=ColumnDataType.FLOAT,
        editable=False,
    ),
    ColumnCreate(
        index=0,
        key='note_1',
        name='Примечание 1',
        data_type=ColumnDataType.STRING,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='note_2',
        name='Примечание 2',
        data_type=ColumnDataType.STRING,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='note_3',
        name='Примечание 3',
        data_type=ColumnDataType.STRING,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='use_manual_min_price',
        name='Использовать ручную мин. цену',
        data_type=ColumnDataType.BOOLEAN,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='auto_min_price',
        name='Авто мин. цена %',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='manual_min_price',
        name='Ручная мин. цена',
        data_type=ColumnDataType.FLOAT,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='auto_price_control',
        name='Авто контроль цен',
        data_type=ColumnDataType.BOOLEAN,
        editable=True,
    ),
    ColumnCreate(
        index=0,
        key='hidden',
        name='Скрыт',
        data_type=ColumnDataType.BOOLEAN,
        editable=True,
    )
]

for i, column in enumerate(columns_info):
    column.index = i


async def get_logs(user_id: int):
    async with async_session() as session:
        return await db.get_logs_by_user_id(session, user_id)


async def create_logs(user_id: int):
    async with async_session() as session:
        return await db.create_logs(session, user_id)


async def update_logs(user_id: int, data: dict):
    async with async_session() as session:
        return await db.update_logs(session, user_id, data)


async def create_settings(user_id: int):
    async with async_session() as session:
        settings = await db.create_user_settings(session, user_id)
        await db.create_columns(session, settings, columns_info)
        return settings


async def get_settings(user_id: int):
    async with async_session() as session:
        return await db.get_user_settings(session, user_id)


async def update_settings(user_id: int, data: SettingsUpdate):
    async with async_session() as session:
        return await db.update_user_settings(session, user_id, data)


async def update_columns(user_id: int, data: list[ColumnUpdate]):
    async with async_session() as session:
        settings = await db.get_user_settings(session, user_id)

        return await db.update_columns(session, settings.id, data)
