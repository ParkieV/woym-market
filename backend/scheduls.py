import asyncio
import concurrent.futures
from collections.abc import Callable
from typing import Sequence

from logs import parser_logger
from src.api.gateway_template import get_api_session
from src.database.db import get_db_session
from src.database.utils import duplicate_offers_to_catalog
from src.services.offer_service import update_offers
from src.services.orders_services import setup_orders
from src.services.stocks_service import update_warehouses_and_stocks


async def update_data(user_ids: Sequence[int]):
    parser_logger.info('Start updating data!')

    try:
        # Получение карточек товаров из магазина
        await update_offers(get_db_session, get_api_session, user_ids)
        # Добавление новых карточек в каталог только sku
        await duplicate_offers_to_catalog(get_db_session)
    except Exception as e:
        parser_logger.error(f'Error in update offers: {str(e)}', exc_info=e)

    try:
        # Получение информации о остатках на складах
        await update_warehouses_and_stocks(get_api_session, get_db_session)
    except Exception as e:
        parser_logger.error(f"Error in update warehouses and stocks: {str(e)}", exc_info=e)

    parser_logger.info('Update data finished successful!')

def run_async(async_func, *args):
    asyncio.run(async_func(*args))

async def start_worker(async_func: Callable, *args):
    parser_logger.debug(f'Worker args: {async_func}, {args}')

    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        parser_logger.info('Start worker!')
        result = await loop.run_in_executor(executor, run_async, async_func, *args)
        parser_logger.info(f'Finish worker! Result: {result}')

if __name__ == '__main__':
    asyncio.run(update_data([3, 4]))