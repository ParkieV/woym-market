import os
import shutil
from collections.abc import Iterable, Callable
from datetime import datetime
from decimal import Decimal
from os.path import exists
from pathlib import Path
from typing import Sequence, Literal, Any
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, Field, constr, field_validator, computed_field

from logs import backend_logger
from src.common.infra.mapper import AbstractMapper, AbstractMutableMapper
from src.common.infra.uow import AbstractUoW
from src.database.db import get_db_session
from src.infra.base_mapper import MapperAggregator
from src.infra.uow import SQLAlchemyUnitOfWork


class DeliverSupply(BaseModel):
    sku: int = Field(title="SKU")
    title: str = Field(title="Наименование")
    number_of_delivery: int = Field(title="Кол-во")
    weight: float = Field(title="Вес(одного)")
    volume: float | None = Field(title="Объем(одного)")
    cost_price: Decimal | None = Field(title="Себестоимость(одного)")

    @field_validator("cost_price", mode="after")
    @classmethod
    def validate_cost_price(cls, price: Decimal):
        if price is not None:
            return price.quantize(Decimal("0.00"))
        return price

    @computed_field(title="Вес кг")
    def deliver_weight(self) -> float | None:
        return self.weight * self.number_of_delivery

    @computed_field(title="Объем л")
    def deliver_volume(self) -> float | None:
        if self.volume is not None:
            return self.volume * self.number_of_delivery
        else:
            return None

    @computed_field(title="Себестоимость")
    def deliver_cost_price(self) -> Decimal | None:
        if self.cost_price is not None:
            return self.cost_price * self.number_of_delivery
        else:
            return None

class WarehouseDeliverSupply(BaseModel, frozen=True):
    sku: int = Field(title="артикул")
    title: str | None = Field(title="имя (необязательно)")
    number_of_delivery: int = Field(title="количество")

class SupplyWarehouse(BaseModel, frozen=True):
    id: int = Field(title="Идентификатор склада")
    warehouse_name: str = Field(title="Название склада")
    to_deliver_number: int = Field(title="Количество товара к поставке")

class DeliverOrder(BaseModel, frozen=True):
    sku: str = Field(title="СКУ товара")
    marketplace_name: str = Field(title="Название маркетплейса")
    shop_name: str = Field(title="Название магазина")
    weight: float = Field(title="Вес товара")
    volume: float = Field(title="Объём товара")
    cost_price: float = Field(title="Себестоимость товара")
    goods_name: str = Field(title="Наименование товара")
    to_deliver_number: int = Field(title="Количество товара к поставке")
    warehouses: Sequence[SupplyWarehouse] | None = Field(title="Информация об интересующих складах")

    def offer_info(self) -> tuple:
        return self.sku, self.marketplace_name, self.shop_name

    @field_validator("cost_price", mode="after")
    @classmethod
    def validate_cost_price(cls, price: Decimal | None):
        if price is not None:
            if isinstance(price, float):
                price = Decimal(price)
            return price.quantize(Decimal("0.00"))
        return price


class ExportDeliverInteractor:

    def __init__(
            self,
            uow: AbstractUoW,
            db_session_fabric
    ):
        self._uow = uow
        self._db_session_fabric = db_session_fabric

    @staticmethod
    def _generate_supplies_excel(
            filepath: Path,
            supplies: Sequence[WarehouseDeliverSupply] | Sequence[DeliverSupply],
    ) -> Path:
        match supplies[0]:
            case x if isinstance(x, WarehouseDeliverSupply):
                supplies_df = pd.DataFrame((supply.model_dump() for supply in supplies), columns=[
                    "sku",
                    "title",
                    "number_of_delivery",
                ])
                excel_headers = [
                    "артикул",
                    "имя (необязательно)",
                    "количество"
                ]
            case x if isinstance(x, DeliverSupply):
                supplies_df = pd.DataFrame((supply.model_dump() for supply in supplies), columns=[
                    "sku",
                    "title",
                    "number_of_delivery",
                    "weight",
                    "deliver_weight",
                    "volume",
                    "deliver_volume",
                    "cost_price",
                    "deliver_cost_price"
                ])
                total_row = {}
                for col in supplies_df.columns:
                    if col == 'deliver_weight' or col == 'deliver_volume' or col == 'deliver_cost_price':
                        total_row[col] = supplies_df[col].sum()
                    elif col == 'title':
                        total_row[col] = 'Итого'
                    else:
                        total_row[col] = None

                total_df = pd.DataFrame([total_row], columns=supplies_df.columns)

                supplies_df = pd.concat([total_df, supplies_df], ignore_index=True)

                excel_headers = [
                    "SKU",
                    "Наименование",
                    "Кол-во",
                    "Вес(одного)",
                    "Вес кг",
                    "Объем(одного)",
                    "Объем л",
                    "Себестоимость(одного)",
                    "Себестоимость"
                ]
            case _:
                raise AssertionError()

        filepath.parent.mkdir(parents=True, exist_ok=True)
        backend_logger.debug(f'header length: {len(supplies[0].model_fields.values()) + len(supplies[0].__class__.__pydantic_computed_fields__.keys())}')
        supplies_df.to_excel(filepath, index=False, header=excel_headers)

        return filepath

    @staticmethod
    def _generate_supplies_archive(
            archive_name: str,
            base_dir: Path,
            encoding: Literal['zip'] = 'zip'
    ) -> Path:
        if exists(base_dir):
            shutil.make_archive(archive_name, encoding, base_dir=base_dir)
            return Path(archive_name+'.zip')
        else:
            raise FileNotFoundError

    @staticmethod
    def _remove_directory(filepath: Path | None) -> None:
        if filepath is not None and filepath.exists():
            shutil.rmtree(filepath, ignore_errors=True)

    @staticmethod
    def _remove_archive(filepath: Path) -> None:
        if filepath.exists():
            os.remove(filepath)

    @staticmethod
    async def _generate_supply_data(orders: Sequence[DeliverOrder]) -> dict[str, Any]:
        all_data_list = []
        supply_data = {"all_data": all_data_list}

        for order in orders:
            fl = False
            for data in all_data_list:
                if order.sku == str(data.sku):
                    fl = True
                    backend_logger.debug(order.warehouses)
                    data.number_of_delivery += sum(map(lambda x: x.to_deliver_number, order.warehouses))
                    break
            if not fl:
                all_data_list.append(
                    DeliverSupply(
                        sku=order.sku,
                        title=order.goods_name,
                        number_of_delivery=sum(map(lambda x: x.to_deliver_number, order.warehouses)),
                        weight=order.weight,
                        volume=order.volume,
                        cost_price=order.cost_price,
                    )
                )
            if order.marketplace_name not in supply_data:
                supply_data[order.marketplace_name] = {}
            market_supply_data = supply_data[order.marketplace_name]

            if order.shop_name not in supply_data[order.marketplace_name]:
                market_supply_data[order.shop_name] = {}
            shop_supply_data = market_supply_data[order.shop_name]

            for warehouse in order.warehouses:
                if warehouse.warehouse_name not in shop_supply_data:
                    shop_supply_data[warehouse.warehouse_name] = [
                        WarehouseDeliverSupply(
                            sku=order.sku,
                            title=order.goods_name,
                            number_of_delivery=next(
                                filter(
                                    lambda x: x.id == warehouse.id,
                                    order.warehouses)
                            ).to_deliver_number,
                        )
                    ]
                else:
                    shop_supply_data[warehouse.warehouse_name].append(
                        WarehouseDeliverSupply(
                            sku=order.sku,
                            title=order.goods_name,
                            number_of_delivery=next(
                                filter(
                                    lambda x: x.id == warehouse.id,
                                    order.warehouses)
                            ).to_deliver_number,
                        )
                    )
        return supply_data

    async def _generate_dir(self, order_data: dict[str, Any], base_dir: Path) -> Path:
        self._generate_supplies_excel(
            base_dir / f'Заказ, {datetime.now().strftime("%Y.%m.%d, %H:%M")}.xlsx',
            list(order_data.get("all_data", []))
        )
        order_data.pop("all_data")
        for market in order_data:
            for shop in order_data.get(market, []):
                for warehouse in order_data[market].get(shop, []):
                    self._generate_supplies_excel(
                        filepath=base_dir / market / shop / f"{warehouse}, {datetime.now().strftime('%Y.%m.%d, %H:%M')}.xlsx",
                        supplies=order_data[market][shop].get(warehouse, [])
                    )
        return base_dir

    async def generate_supplies(self, orders: Sequence[DeliverOrder], session_id: UUID) -> Path:
        base_dir = Path(f'Поставка_{datetime.now().strftime("%Y.%m.%d, %H:%M")}')
        dir_path = None

        try:
            supply_data = await self._generate_supply_data(orders)
            backend_logger.debug(supply_data)
            dir_path = await self._generate_dir(supply_data, base_dir)
            archive_path = self._generate_supplies_archive(
                archive_name=f"supply_{datetime.now().strftime('%Y.%m.%d_%H:%M')}.{session_id}",
                base_dir=dir_path,
            )
        except Exception as e:
            raise e
        else:
            return archive_path
        finally:
            self._remove_directory(dir_path)
            self._remove_archive(Path(f"supply_{datetime.now().strftime('%Y.%m.%d_%H:%M')}.{session_id}"))

def create_deliver_interactor(
        mappers: Sequence[type[AbstractMapper] | type[AbstractMutableMapper]]
    ) -> Callable[[], ExportDeliverInteractor]:
    def func() -> ExportDeliverInteractor:
        return ExportDeliverInteractor(
            uow=SQLAlchemyUnitOfWork(
                mappers,
                MapperAggregator,
            ),
            db_session_fabric=get_db_session
        )

    return func