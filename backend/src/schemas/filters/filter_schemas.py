from abc import ABC, abstractmethod
from typing import Generic

from pydantic import BaseModel

from src.schemas.filters.interface import Query

# This class must match the interface IBaseFilter
class BaseFilter(ABC, Generic[Query]):

    @abstractmethod
    def __call__(self, query: Query) -> Query:
        raise NotImplementedError


class BasePydanticFilter(BaseModel, BaseFilter):

    @abstractmethod
    def __call__(self, query: Query) -> Query:
        raise NotImplementedError


class PagingFilter(BasePydanticFilter):
    limit: int | None = None
    offset: int | None = None

    def __call__(self, query):
        if self.offset:
            query = query.offset(self.offset)

        if self.limit:
            query = query.limit(self.limit)

        return query
