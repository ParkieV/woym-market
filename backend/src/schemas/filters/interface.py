from abc import abstractmethod, ABC
from typing import Protocol, TypeVar

Query = TypeVar('Query')


class IBaseFilter(Protocol[Query]):

    @abstractmethod
    def __call__(self, query: Query) -> Query:
        raise NotImplementedError
