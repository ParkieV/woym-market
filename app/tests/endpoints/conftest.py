import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from starlette import status

from __main__ import app
from src.database.db import Base
from src.params.confing import config

engine_test = create_async_engine(config.db_url)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    assert config.mode == 'TEST'

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print('Database created')
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print('Databse dropped')


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac

#
#
# async def test_register_user(async_client: AsyncClient):
#     response = await async_client.post("/registration", json={'login': 'admin', 'password': 'admin', 'is_staff': True})
#     assert response.status_code == status.HTTP_201_CREATED, response.text
#     response_data = response.json()


@pytest.fixture
async def auth_token(async_client: AsyncClient) -> AsyncGenerator[str, None]:
    response = await async_client.post('/login', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == status.HTTP_200_OK
    token = response.json()['access_token']
    return token
