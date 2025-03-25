from collections.abc import Sequence, Iterable

from src.database.catalog import CatalogRepository
from src.database.interfaces import IDbSessionFabric
from src.database.offer import OfferRepository
from src.services.interfaces import IDBMetadataService


class ReverseSynchronizationInteractor:
    """
    Выполнение обратной синхронизации между карточками и каталогом.
    """
    exclude_fields = {'id', 'sku'}

    def __init__(self,
                 metadata_service: IDBMetadataService,
                 session_fabric: IDbSessionFabric):
        self.metadata_service = metadata_service
        self.session_fabric = session_fabric

    async def __call__(self,
                 skus: Sequence[str],
                 exclude_fields: Iterable[str] | None = None):
        if exclude_fields:
            self.exclude_fields.update(exclude_fields)

        offer_columns = set(self.metadata_service.get_columns('Offer'))
        catalog_columns = set(self.metadata_service.get_columns('CatalogItem'))

        # Колонки, значения которых будут обновлены
        updating_columns = (offer_columns & catalog_columns) - self.exclude_fields

        catalog_repo = CatalogRepository()

        async with self.session_fabric() as session:
            catalog_repo.session = session
            await catalog_repo.synchronization_catalog_from_offer(updating_columns, skus)
            await session.commit()


class SynchronizationInteractor:
    """
    Выполнение обратной синхронизации между карточками и каталогом.
    """
    exclude_fields = {'id', 'sku'}

    def __init__(self,
                 metadata_service: IDBMetadataService,
                 session_fabric: IDbSessionFabric):
        self.metadata_service = metadata_service
        self.session_fabric = session_fabric

    async def __call__(self,
                 skus: Sequence[str],
                 exclude_fields: Iterable[str] | None = None):
        if exclude_fields:
            self.exclude_fields.update(exclude_fields)

        offer_columns = set(self.metadata_service.get_columns('Offer'))
        catalog_columns = set(self.metadata_service.get_columns('CatalogItem'))

        # Колонки, значения которых будут обновлены
        updating_columns = (offer_columns & catalog_columns) - self.exclude_fields

        offer_repository = OfferRepository()

        async with self.session_fabric() as session:
            offer_repository.session = session
            await offer_repository.synchronization_offer_from_catalog(updating_columns, skus)
            await session.commit()
