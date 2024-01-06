from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.models import Logs


async def create_logs(session: AsyncSession, user_id: int) -> Logs:
    logs_db = Logs(user_id=user_id)
    session.add(logs_db)
    await session.commit()
    await session.refresh(logs_db)
    return logs_db


async def get_logs_by_user_id(session: AsyncSession, user_id: int) -> Logs | None:
    query = select(Logs).where(Logs.user_id == user_id)
    rez = await session.execute(query)
    return rez.scalar_one_or_none()


async def update_logs(session: AsyncSession, user_id: int, data: dict):
    query = update(Logs).where(Logs.user_id == user_id).values(**data)
    await session.execute(query)
    await session.commit()

