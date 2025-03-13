# from src.routers.user_router import user_router
from fastapi import APIRouter

from src.routers.media_router import router as media_router
from src.routers.catalog_router import router as catalog_router
from src.routers.core_router import router as core_router
from src.routers.offers.base_router import router as data_router
from src.routers.auth_router import auth_router
from src.routers.settings_router import settings_router
from src.routers.debug_router import debug_router
from src.routers.user_router import user_router
from src.routers.stocks import router as stocks_router
from src.routers.export import router as export_router


api_router = APIRouter()

api_router.include_router(media_router)
api_router.include_router(catalog_router)
api_router.include_router(core_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(settings_router)
api_router.include_router(data_router)
api_router.include_router(stocks_router)
api_router.include_router(debug_router)
api_router.include_router(export_router)