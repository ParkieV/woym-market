import asyncio
from typing import Sequence

from logs import get_logger
from src.database.db import get_session
from src.database.utils import duplicate_offers_to_catalog
from src.services.offer_service import update_offers
from src.services.orders_services import setup_orders
from src.services.stocks_service import update_warehouses_and_stocks

logger = get_logger(__name__)


async def update_data(user_ids: Sequence[int]):
    logger.info('Start updating data!')

    try:
        # Получение карточек товаров из магазина
        await update_offers(get_session(), user_ids)
        # Добавление новых карточек в каталог только sku
        await duplicate_offers_to_catalog(get_session())
    except Exception as e:
        logger.error(f'Error in update offers', exc_info=e)

    try:
        # Получение информации о остатках на складах
        await update_warehouses_and_stocks()
    except Exception as e:
        logger.error(f"Error in update warehouses and stocks", exc_info=e)

    try:
        await setup_orders()
    except Exception as e:
        logger.error(f'Error in update orders data', exc_info=e)

    logger.info('Schedules updated completed')

if __name__ == '__main__':
    asyncio.run(update_data([3, 4]))