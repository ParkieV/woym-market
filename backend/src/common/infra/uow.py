from abc import ABC, abstractmethod

from src.common.infra.mapper import AbstractMapperAggregator



class AbstractUoW(ABC):
    mappers: AbstractMapperAggregator

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError