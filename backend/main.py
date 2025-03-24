import asyncio
from contextlib import asynccontextmanager

# import sentry_sdk
import aioschedule
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse

from logs import backend_logger
from scheduls import update_data
from src.routers import api_router, api_router_v2
from src.database.db import db_create
from src.params.config import config
from src.shared.exceptions import InitializationError


# if config.use_sentry:
#     sentry_sdk.init(
#         dsn=config.sentry_sdk_dsn,
#         # Set traces_sample_rate to 1.0 to capture 100%
#         # of transactions for tracing.
#         traces_sample_rate=1.0,
#         # Set profiles_sample_rate to 1.0 to profile 100%
#         # of sampled transactions.
#         # We recommend adjusting this value in production.
#         profiles_sample_rate=1.0,
#     )


async def scheduler():
    aioschedule.every(60).minutes.do(update_data, (3, 4))

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
    backend_logger.info('Worker start!')
    yield


app: FastAPI = FastAPI(
    default_response_class=ORJSONResponse,
    root_path='/backend',
    lifespan=startup,
    docs_url=None if config.is_prod else '/docs',
    redoc_url=None if config.is_prod else '/redoc'
)

if config.is_prod:
    origins = ['https://woym-market.ru']
elif config.is_dev:
    origins = ['https://dev.woym-market.ru']
elif config.is_local:
    origins = ['*']
else:
    raise InitializationError('Не получилось определить контур развертывания')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(api_router)
app.include_router(api_router_v2)


@app.exception_handler(500)
async def pull_response_headers(request, exc):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
        'detail': 'Произошла ошибка сервера'
    })


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
