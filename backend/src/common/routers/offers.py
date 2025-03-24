from collections.abc import Sequence

from pydantic import BaseModel

from src.common.fbo_stocks import FboOffer


class FboStocksOffers(BaseModel, frozen=True):
    offers: Sequence[FboOffer]