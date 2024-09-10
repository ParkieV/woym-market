from pydantic import BaseModel


class BaseFilter(BaseModel):
    def filter(self, query):
        raise NotImplementedError('Needs to implement filter method')