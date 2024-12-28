from typing import Literal, TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from src.shared.exceptions import MappingError




def mapping_pydantic_models(pydantic_model: BaseModel, sqlalc_model: type[DeclarativeBase],  *, extra: Literal['allow'] | None = None):

    data = pydantic_model.model_dump()
    sqlalchemy_mapper = sqlalc_model.__mapper__
    if extra == 'allow':
        return {k: v for k, v in data.items() if k in sqlalchemy_mapper.columns}
    else:
        try:
            return {k: v for k, v in data.items() if sqlalchemy_mapper.columns[k]}
        except KeyError as key_err:
            MappingError(f"Не удалось представить объект {pydantic_model.__class__.__name__} в виде словаря: {sqlalc_model.__class__.__name__} не содержит атрибут '{key_err.args[0]}'")
