from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Protocol
from abc import abstractmethod

from pydantic import BaseModel, Field, constr, field_validator


class Supply(BaseModel, frozen=True):
    sku: str = Field(title="СКУ товара")
    title: constr(min_length=1, max_length=60) = Field(title="Наименование товара")
    marketplace_name: str = Field("Название маркетплейса")
    shop_name: str = Field("Название магазина")
    number_of_delivery: int = Field(title="Количество товара к поставке")
    weight: float = Field(title="Вес товара")
    volume: float | None = Field(title="Объём товара")
    cost_price: Decimal | None = Field(title="Себестоимость")
    info_order_date: date = Field(
        default=datetime.now().date(),
        title="Дата формирования отчета",
        description="Дата формирования информации о поставке"
    )




class AbstractExportDeliverInteractor(Protocol):

    @abstractmethod
    def generate_supplies_excel(
            self,
            filename: str,
            shop_name: str,
            supplies: Sequence[int],
    ) -> Path: ...

    @abstractmethod
    def generate_supplies(self, skus: Sequence[int]) -> Path: ...

    @abstractmethod
    def generate_supplies_archive(
            self, archive_name: str, skus: Sequence[int]
    ) -> Path: ...
