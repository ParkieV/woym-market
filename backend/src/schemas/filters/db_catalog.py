from collections.abc import Sequence

from sqlalchemy import TextClause, text

from src.schemas.filters.filter_schemas import BaseFilter


class OfferDataFilter(BaseFilter[str]):
    """ Filter offer that synchronize with current Catalog item """

    def __call__(self, query):
        query += "FROM offers\nWHERE catalog_items.reverse_sync_offer_id = offers.id"
        return query


class SkuInArrayFilter(BaseFilter[str]):

    def __init__(self, skus: Sequence[str] | None = None):
        self._skus = skus

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
        query += f" AND catalog_items.sku IN {str_skus}"
        return query

