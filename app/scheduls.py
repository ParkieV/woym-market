from src.services.offer_service import update_offers
from src.services.stocks_service import update_warehouses_and_stocks
from logs import get_logger

logger = get_logger(__name__)


async def update_data(user_id: int):
    try:
        await update_offers(user_id)
    except Exception as e:
        logger.error(f'Error in update offers', exc_info=True)

    try:
        await update_warehouses_and_stocks()
    except Exception as e:
        logger.error(f"Error in update warehouses and stocks", exc_info=True)

    logger.info('Schedules updated completed')
