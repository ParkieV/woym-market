from datetime import datetime

from pydantic import BaseModel


class VersionInfo(BaseModel):
    object_hash: str | None
    object_type: str
    date: datetime
    author: str | None
    branch: str | None

