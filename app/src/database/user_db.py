from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.schemas import user_schemas as schema
from .db import async_session
from .utils import row_list_to_dict_list, row_to_dict
from .models.models import Users, Settings


async def reg_user(login: str, password: str) -> Users | None:
    session: AsyncSession
    async with async_session() as session:
        check = await session.execute(
            select(
                Users.login
            ).where(
                Users.login == login
            )
        )
        check = check.scalar_one_or_none()
        if check is not None:
            raise HTTPException(
                detail='login already exist',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        new_user = Users(
            login=login,
            password=password
        )
        session.add(new_user)
        await session.commit()

        return new_user  # <src.database.models.models.Users object at 0x108972f50>


async def get_user_by_id(id_user: int):
    session: AsyncSession
    async with async_session() as session:
        user = await session.execute(
            select(
                Users
            ).where(
                Users.id == int(id_user)
            )
        )
        user = user.scalar_one_or_none()
        return user


async def get_user_by_login(login: str):
    session: AsyncSession
    async with async_session() as session:
        user = await session.execute(
            select(
                Users
            ).where(
                Users.login == login
            )
        )
        user = user.scalar_one_or_none()
        return user


async def create_user_settings(session: AsyncSession, user_id: int) -> Settings:
    settings_db = Settings(user_id=user_id)
    session.add(settings_db)
    await session.commit()
    await session.refresh(settings_db)
    return settings_db


async def get_user_settings(session: AsyncSession, user_id: int) -> Settings | None:
    query = select(Settings).where(Settings.user_id == user_id)
    res = await session.execute(query)
    return res.scalar_one_or_none()


async def update_user_settings(session: AsyncSession, user_id: int, settings_update: schema.SettingsUpdate):
    query = update(Settings).where(Settings.user_id == user_id).values(**dict(settings_update))
    await session.execute(query)
    await session.commit()

# async def update_user(id_user: int, new_data: NewUserData):
#     session: AsyncSession
#     async with async_session() as session:
#         user = await session.execute(
#             select(
#                 Users
#             ).where(
#                 Users.id == id_user
#             )
#         ) # .scalar_one()
#         user = user.scalar_one_or_none()
#         if user is None:
#             raise HTTPException(
#                 detail=f'id={id_user} does not exist in users table',
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         data_dict = {key: val for key, val in new_data if val is not None and key not in 'competence_list'}
#         await user.update(**data_dict)
#         await session.commit()
