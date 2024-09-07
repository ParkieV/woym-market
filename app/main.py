import asyncio
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse

from scheduls import update_data
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.offer_router import data_router
from src.routers.debug_router import debug_router
from src.routers.stocks.stocks_router import router as stocks_router
from src.routers.settings_router import settings_router
from src.routers.core_router import router as core_router
from src.routers.catalog_router import router as catalog_router
from src.routers.media_router import router as media_router
from src.database.db import db_create
import aioschedule
from src.params.confing import config

if config.use_sentry:
    sentry_sdk.init(
        dsn=config.sentry_sdk_dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )


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
    yield


app: FastAPI = FastAPI(default_response_class=ORJSONResponse, root_path='' if config.is_local else '/backend', lifespan=startup)


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

app.include_router(media_router)
app.include_router(catalog_router)
app.include_router(core_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(settings_router)
app.include_router(data_router)
app.include_router(stocks_router)
app.include_router(debug_router)


@app.exception_handler(500)
async def pull_response_headers(request, exc):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
        'detail': 'Произошла ошибка сервера'
    })


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
