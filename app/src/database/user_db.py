from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .db import async_session
from .models.models import Users
from src.schemas.user_schemas import UserCreate


async def reg_user(login: str, password: str, is_staff: bool) -> Users | None:
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
            password=password,
            is_staff=is_staff
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




async def update_user(id_user: int, new_data: UserCreate):
    session: AsyncSession
    async with async_session() as session:
        user = await session.execute(
            select(
                Users
            ).where(
                Users.id == id_user
            )
        )
        user = user.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                detail=f'id={id_user} does not exist in users table',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        await session.execute(
            update(
                Users
            ).where(
                Users.id == id_user
            ).values(
                **new_data.model_dump
            )
        )

        await session.commit()
