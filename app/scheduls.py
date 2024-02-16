from src.services.offer_service import update_offers
from src.services.stocks_service import update_warehouses_and_stocks


async def update_data(user_id: int):
    try:
        await update_offers(user_id)
        await update_warehouses_and_stocks()
    except Exception as e:
        print(f"Error in update warehouses and stocks or update offers: {e}")
