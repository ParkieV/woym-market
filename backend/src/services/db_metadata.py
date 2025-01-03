from collections.abc import Mapping
from typing import Sequence, Type

from sqlalchemy.orm import DeclarativeBase

from src.services.interfaces import IDBMetadataService


class DBMetadataService(IDBMetadataService):
    def __init__(self, models: Mapping[str, Type[DeclarativeBase]]) -> None:
        self.models = models

    def get_columns(self, table_name: str) -> Sequence[str]:
        """ Получить наименование колонок в таблице """
        model = self.models.get(table_name)

        if model is None:
            raise ValueError(f"Table {table_name} not found.")

        return model.__table__.columns.keys()
