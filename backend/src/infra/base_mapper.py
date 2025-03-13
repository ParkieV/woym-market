import re

from src.common.infra.mapper import AbstractMapperAggregator

class MapperAggregator(AbstractMapperAggregator):

    def _camel_to_snake(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def __getattr__(self, item: str):
        if item in self._registry:
            if item not in self._repos:
                repo_class = self._registry[item]
                self._repos[item] = repo_class(self.session)
            return self._repos[item]
        raise AttributeError(f"Not found repository '{item}'")
