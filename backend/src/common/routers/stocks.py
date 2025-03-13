from pydantic import BaseModel, Field

from src.domain.stocks import FboStock


class UpdateFboStocksRequest(BaseModel):
    stocks: list[FboStock] = Field(default_factory=list)