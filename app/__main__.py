import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.routers.user_router import user_router
from src.routers.auth_router import auth_router
from src.routers.offer_router import offer_router
from src.routers.settings_router import settings_router
from src.database.db import db_create
import aioschedule
from src.services.offer_service import update_offers
from src.params.confing import config


app: FastAPI = FastAPI(default_response_class=ORJSONResponse)


async def scheduler():
    aioschedule.every(60).minutes.do(update_offers, 1)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def to_startup():
    if config.schedule_update:
        asyncio.create_task(scheduler())


@app.on_event('startup')
async def startup():
    db_create()
    await to_startup()


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
app.include_router(offer_router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
