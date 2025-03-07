from typing import Sequence

from sqlalchemy import values, column, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from logs import backend_logger
from src.common.export import Supply
from src.common.infra.supply import AbstractSupplyRepository
from src.database.models.models import Offer, Warehouse, OfferStock
from src.domain.export import DeliverOrder


class SupplyRepository(AbstractSupplyRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_object_by_id(self, object_id: str) -> Supply:
        raise NotImplementedError

    async def read_list(self) -> Sequence[Supply]:
        raise NotImplementedError

    async def read_list_by_delivery_order(self, orders: Sequence[DeliverOrder]) -> list[Supply]:
        supplies: list[Supply] = []

        criteria_values = values(
            column("sku", String),
            column("market", String),
            column("shop", String),
            name="criteries"
        )
        for i in range(len(orders) // 5000 + 1):
            cte_values = criteria_values.data(
                [
                    (
                        orders[j].sku,
                        orders[j].marketplace_name,
                        orders[j].shop_name
                    ) for j in range(i * 5000, min(len(orders), (i + 1) * 5000))
                ]
            )
            criteries_cte = select(cte_values).cte("criteries_cte")

            query = (
                select(
                    Offer,
                    OfferStock.current_stock,
                    Warehouse.id,
                    Warehouse.name,
                )
                .join(
                    OfferStock,
                    OfferStock.offer_id == Offer.id,
                )
                .join(
                    Warehouse,
                    Warehouse.id == OfferStock.warehouse_id,
                )
                .join(
                    criteries_cte,
                    (Offer.sku == criteries_cte.c.sku) &
                    (Offer.market == criteries_cte.c.market) &
                    (Offer.name_of_shop == criteries_cte.c.shop)
                )
                .where(
                    Warehouse.warehouse_type == 'warehouse'
                )
            )
            result = await self._session.execute(query)

            supplies.extend(map(lambda row: Supply(
                sku=row[0].sku,
                title=row[0].name,
                marketplace_name=row[0].market,
                shop_name=row[0].name_of_shop,
                number_of_delivery=row[1],
                weight=row[0].self_weight,
                volume=row[0].volume,
                cost_price=row[0].cost_price
            ), result.all()))

        backend_logger.debug(f"supplies: {supplies}")
        return supplies
