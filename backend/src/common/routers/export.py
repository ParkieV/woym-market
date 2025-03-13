from collections.abc import Sequence
from uuid import UUID

from pydantic import BaseModel

from src.domain.export import DeliverOrder


class DeliverRequest(BaseModel):
    session_id: UUID
    orders: Sequence[DeliverOrder] | None
