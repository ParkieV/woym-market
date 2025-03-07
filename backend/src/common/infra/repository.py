from abc import abstractmethod, ABC
from collections.abc import Sequence, Iterable, Iterator
from typing import Protocol, TypeVar, Any

Model = TypeVar("Model")
ID = TypeVar("ID")

class AbstractRepository(Protocol[Model, ID]):

    @abstractmethod
    async def read_object_by_id(self, object_id: ID) -> Model: ...

    @abstractmethod
    async def read_list(self) -> Sequence[Model]: ...

class AbstractMutableRepository(Protocol[Model, ID]):

    @abstractmethod
    async def create_object(self, object: Model) -> None: ...

    @abstractmethod
    async def update_object(self, new_object: Model, object_id: ID) -> None: ...

    @abstractmethod
    async def delete_object(self, object_id: ID) -> None: ...


class AbstractRepositoryAggregator(ABC):
    
    #: Сессия подключения к БД
    _session = None
    
    #: Кэшированные репозитории
    _repos: dict[str, type]
    
    #: Зарегистрированные репозитории
    _registry: dict[str, type]

    def __init__(self, repository_classes: Iterable[type[AbstractRepository] | type[AbstractMutableRepository]]):
        self._repos: dict[str, type] = {}
        self._registry: dict[str, type] = {}
        for repo_class in repository_classes:
            repo_name = self._camel_to_snake(repo_class.__name__)
            self._registry[repo_name] = repo_class

    @property
    def session(self) -> None:
        if self._session is None:
            raise ValueError("Session has not set")
        return self._session
    
    @session.setter
    def session(self, session: Any) -> None:
        self._session = session
    
    @abstractmethod
    def __getattr__(self, item: str):
        raise NotImplementedError

    def __iter__(self) -> Iterator[type]:
        return iter(self._registry.values())