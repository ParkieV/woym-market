from datetime import datetime
from pydantic import BaseModel


class LogsOut(BaseModel):
    updated_at: datetime | None
