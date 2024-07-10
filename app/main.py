import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
from scheduls import update_data
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.offer_router import data_router
from src.routers.debug_router import debug_router
from src.routers.stocks_router import stocks_router
from src.routers.settings_router import settings_router
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from src.database.db import db_create
import aioschedule
from src.params.confing import config


async def scheduler():
    aioschedule.every(60).minutes.do(update_data, 1)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def to_startup():
    if config.schedule_update:
        asyncio.create_task(scheduler())


@asynccontextmanager
async def startup(_: FastAPI):
    db_create()
    await to_startup()
    redis = aioredis.from_url('redis://redis:6379', decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app: FastAPI = FastAPI(default_response_class=ORJSONResponse, root_path='/backend', lifespan=startup)


origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:3000',
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(settings_router)
app.include_router(data_router)
app.include_router(stocks_router)
app.include_router(debug_router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
