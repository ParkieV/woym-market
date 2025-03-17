from pathlib import Path

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from logs import backend_logger
from ..common.routers.export import DeliverRequest
from ..dependencies.users import get_current_user
from ..domain.export import ExportDeliverInteractor, create_deliver_interactor
from ..infra.delivery import SupplyMapper

router = APIRouter(prefix="/export", tags=["Экспорт"])


@router.post("/deliver", dependencies=[Depends(get_current_user)])
async def export_deliver_archive(
        body: DeliverRequest | None,
        deliver_interactor: ExportDeliverInteractor = Depends(
            create_deliver_interactor([SupplyMapper])
        ),
):
    backend_logger.debug(f"Request body: {body}")
    archive_path = await deliver_interactor.generate_supplies(
        orders=body.orders,
        session_id=body.session_id,
    )

    async def file_generator(filepath: Path):
        with open(filepath, "rb") as file:
            while chunk := file.read(1024 * 1024):
                yield chunk

    return StreamingResponse(
        file_generator(archive_path),
        media_type="application/octet-stream",  # Указываем двоичный тип
        headers={
            "Content-Disposition": f'attachment; filename="{archive_path.name}"'
        }
    )