from collections.abc import Sequence

from src.database.interfaces import IAsyncReverseSyncUnitOfWork
from src.services.interfaces import IDBMetadataService


class ReverseSynchronizationInteractor:
    """
    Выполнение обратной синхронизации между карточками и каталогом.
    """
    exclude_fields = {'id', 'sku'}

    def __init__(self,
                 metadata_service: IDBMetadataService,
                 uow: IAsyncReverseSyncUnitOfWork):
        self.metadata_service = metadata_service
        self.uow = uow


    async def __call__(self,
                 skus: Sequence[str],
                 exclude_fields: Sequence[str] | None = None):
        if exclude_fields:
            self.exclude_fields.update(exclude_fields)

        offer_columns = set(self.metadata_service.get_columns('Offer'))
        catalog_columns = set(self.metadata_service.get_columns('CatalogItem'))

        # Колонки, значения которых будут обновлены
        updating_columns = (offer_columns & catalog_columns) - self.exclude_fields

        async with self.uow:
            await self.uow.reverse_sync_service(updating_columns, skus)
