from fastapi import APIRouter
from src.schemas.core_schemas import VersionInfo
from src.services import core_service as service


router = APIRouter(
    tags=['Core']
)


@router.get('/version', response_model=VersionInfo | None)
async def get_version_info():
    return service.get_latest_commit_info()

