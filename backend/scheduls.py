import asyncio
import multiprocessing
from typing import Sequence

from logs import get_logger
from src.api.gateway_template import get_api_session
from src.database.db import get_db_session
from src.database.utils import duplicate_offers_to_catalog
from src.services.offer_service import update_offers
from src.services.orders_services import setup_orders
from src.services.stocks_service import update_warehouses_and_stocks

logger = get_logger(__name__)


async def update_data(user_ids: Sequence[int]):
    logger.info('Start updating data!')

    try:
        # Получение карточек товаров из магазина
        await update_offers(get_db_session, get_api_session, user_ids)
        # Добавление новых карточек в каталог только sku
        await duplicate_offers_to_catalog(get_db_session)
    except Exception as e:
        logger.error('Error in update offers', exc_info=e)

    try:
        # Получение информации о остатках на складах
        await update_warehouses_and_stocks(get_api_session, get_db_session)
    except Exception as e:
        logger.error("Error in update warehouses and stocks", exc_info=e)

    try:
        await setup_orders(get_api_session, get_db_session)
    except Exception as e:
        logger.error('Error in update orders data', exc_info=e)

    logger.error('Scheduler finished successful!')


async def start_worker(async_func, *args, **kwargs):
    def run_async():
        asyncio.run(async_func(*args, **kwargs))
    print('Worker started!')
    process = multiprocessing.Process(target=run_async)
    process.start()
    process.join()
    print('Worker finished!')

if __name__ == '__main__':
    asyncio.run(update_data([3, 4]))