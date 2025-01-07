from collections.abc import Sequence, Iterable

import pandas as pd
from sqlalchemy import text

from logs import get_logger
from src.database.db import ISessionFabric
from src.schemas.query_builders.update_offer import CreateTempTable, UpdateOfferWithTempTable, InsertTempTable
from src.services.interfaces import IDBMetadataService


logger = get_logger(__name__)

class UpdateOfferFromApi:
    exclude_fields = {'id'}

    def __init__(self,
                 metadata_service: IDBMetadataService,
                 session_fabric: ISessionFabric):
        self.metadata_service = metadata_service
        self.session_fabric = session_fabric

    async def __call__(self,
                 data: pd.DataFrame,
                 skus: Sequence[str],
                 exclude_fields: Iterable[str] | None = None):
        if exclude_fields:
            self.exclude_fields.update(exclude_fields)

        offer_columns = set(self.metadata_service.get_columns('Offer'))
        catalog_columns = set(self.metadata_service.get_columns('CatalogItem'))

        # Колонки, обновляемые синхронизациями
        unupdated_columns = (offer_columns & catalog_columns) - self.exclude_fields
        unupdated_columns.remove('sku')
        updated_columns = offer_columns - unupdated_columns

        if len(skus) > 0:
            data = data[data['sku'].isin(skus)]

        data = data.fillna(0.0).map(lambda x: 'NULL' if x is None else x)

        temp_table_builder = CreateTempTable(data.to_dict('records'), updated_columns)
        insert_temp_table_builder = InsertTempTable(data.to_dict('records'), updated_columns)
        query_builder = UpdateOfferWithTempTable(set(data.columns.tolist()) & updated_columns)

        query_create = temp_table_builder('')
        query_insert = insert_temp_table_builder('')
        query_update = query_builder("UPDATE offers\n\tSET ")

        async with self.session_fabric() as session:
            await session.execute(text(query_create))
            await session.execute(text(query_insert))
            await session.execute(text(query_update))

        logger.info(f'Updated db offers: {len(data)}')

