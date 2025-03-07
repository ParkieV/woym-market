from abc import ABC, abstractmethod

from src.common.infra.repository import AbstractRepositoryAggregator



class AbstractUoW(ABC):
    repositories: AbstractRepositoryAggregator

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError