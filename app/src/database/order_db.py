from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models import Order
from src.schemas.orders_scemas import OrderCreate, OrderOut


async def create_orders(session: AsyncSession, orders: list[OrderCreate]) -> None:
    new_order = [Order(**order.model_dump()) for order in orders]
    session.add_all(new_order)
    await session.commit()


async def get_orders(session: AsyncSession) -> list[OrderOut]:
    query = select(Order)
    result = (await session.execute(query)).scalars()
    return [OrderOut.model_validate(i, from_attributes=True) for i in result]




