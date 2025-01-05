from collections.abc import Sequence, Iterable

from sqlalchemy import TextClause, text

from src.schemas.filters.filter_schemas import BaseFilter


class OfferDataFilter(BaseFilter[str]):
    """ Filter offer that synchronize with current Catalog item """

    def __call__(self, query):
        query += "FROM offers\nWHERE catalog_items.reverse_sync_offer_id = offers.id"
        return query

class SkuInArrayFilter(BaseFilter[str]):

    def __init__(self,
                 table_name: str,
                 *,
                 skus: Sequence[str] | None = None):
        self._skus = skus
        self.table_name = table_name

    @property
    def skus(self):
        if self._skus is None:
            raise ValueError("Skus are not initialized")

        return self._skus

    @skus.setter
    def skus(self, skus: Sequence[str]):
        self._skus = skus

    def __call__(self, query):
        str_skus = "('" + '\', \''.join(self.skus) + "')"
        # Bad way, because of works correctly only in one specific case
        query += f" AND {self.table_name}.sku IN {str_skus}"
        return query

class SyncUpdatingColumnFilter(BaseFilter[str]):

    def __init__(self, updating_columns: Iterable[str]):
        self.updating_columns = updating_columns

    def __call__(self, query):
        updating_values = {col: f'catalog_items.{col}' for col in self.updating_columns}

        # Поисковые слова изменяются только для озона
        update_search_words = {'search_words': f"""CASE
            WHEN offers.market = 'ozon' THEN catalog_items.search_words
            ELSE offers.search_words
            END"""}

        # Штрихкоды изменяются только у яндекса
        update_barcodes = {'barcodes': f"""CASE
            WHEN offers.market = 'yandex' THEN catalog_items.barcodes
            ELSE offers.barcodes
            END"""}

        updating_values.update(update_search_words)
        updating_values.update(update_barcodes)


        for k, v in updating_values.items():
            query += f"{k} = {v},\n\t"
        return query

class CatalogDataFilter(BaseFilter[str]):
    """ Filter offer that synchronize with current offer """

    def __call__(self, query):
        query += "FROM catalog_items\n\tWHERE offers.synchronization = true AND offers.sku = catalog_items.sku"
        return query
