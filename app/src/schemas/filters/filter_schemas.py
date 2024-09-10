from pydantic import BaseModel


class BaseFilter(BaseModel):
    def filter(self, query):
        raise NotImplementedError('Needs to implement filter method')

    def __call__(self, query, *args, **kwargs):
        raise NotImplementedError('Needs to implement filter method')

class PagingFilter(BaseFilter):
    limit: int | None = None
    offset: int | None = None

    def __call__(self, query,  *args, **kwargs):
        if self.offset:
            query = query.offset(self.offset)

        if self.limit:
            query = query.limit(self.limit)

        return query
