from collections.abc import Sequence, Iterable

from sqlalchemy import TextClause, text

from src.database.models.models import Offer, CatalogItem
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

class ReverseSyncUpdatingColumnFilter(BaseFilter[str]):
    def __init__(self, updating_columns: Iterable[str]):
        self.updating_columns = updating_columns

    def __call__(self, query):
        tracking_columns = {getattr(CatalogItem, f'{column}_changed').name if (getattr(CatalogItem, f'{column}_changed', None) and getattr(Offer, f'{column}_changed', None)) else None for column in self.updating_columns}
        tracking_columns.remove(None)

        updating_values = {col: f'catalog_items.{col}' for col in self.updating_columns}

        changed_detected_updating_values = {col[:col.find('_changed')]: f"COALESCE(offers.{col[:col.find('_changed')]}, catalog_items.{col[:col.find('_changed')]})"
            for col in tracking_columns}

        detect_changes_values = {
            column: f"""
                catalog_items.{column} OR
                CONCAT(catalog_items.{column}, '') != CONCAT(
                    COALESCE(offers.{column}, catalog_items.{column}), '')"""
            for column in tracking_columns
        }


        # track_changes = {
        #     f'{col}_changed': or_(
        #         getattr(CatalogItem, f'{col}_changed'),
        #         func.concat(getattr(CatalogItem, col), '') != func.concat(
        #             func.coalesce(getattr(Offer, col), getattr(CatalogItem, col)), '')
        #     )
        #     for col in common_columns if all((getattr(CatalogItem, f'{col}_changed', None),
        #                                       getattr(CatalogItem, col, None), getattr(Offer, col, None)))
        # }

        updating_values.update(changed_detected_updating_values)
        updating_values.update(detect_changes_values)

        for k, v in updating_values.items():
            query += f"{k} = {v},\n\t"
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

        # Формируем словарь значений для проверки, что поле было изменено
        tracking_columns = {getattr(Offer, f'{column}_changed').name if getattr(Offer, f'{column}_changed', None) else None for column in self.updating_columns}
        tracking_columns.remove(None)

        detect_changes_values = {
            column: f"""offers.{column} OR
                CONCAT(offers.{column}, '') != CONCAT(
                    COALESCE(catalog_items.{column}, offers.{column}), '')"""
            for column in tracking_columns
        }

        # detect_changes_values = {
        #     getattr(Offer, f'{col}_changed'): or_(
        #         getattr(Offer, f'{col}_changed'),
        #         func.concat(getattr(Offer, col), '') != func.concat(
        #             func.coalesce(getattr(CatalogItem, col), getattr(Offer, col)), '')
        #     )
        #     for col in common_columns if
        #     all((getattr(Offer, f'{col}_changed', None), getattr(CatalogItem, col, None), getattr(Offer, col, None)))
        # }

        detect_search_words_changes_for_ozon = {
            'search_words_changed': f"""CASE
                    WHEN offers.market = 'ozon' THEN (offers.search_words_changed OR CONCAT(offers.search_words, '') != CONCAT(
                        COALESCE(catalog_items.search_words, offers.search_words ), '')
                    )
                    ELSE offers.search_words_changed
                END"""
        }

        # Поисковые слова изменяемые только для озона, поэтому тречим изменения только у него
        # detect_search_words_changes_for_ozon = {
        #     'search_words_changed': case(
        #         (Offer.market == 'ozon', or_(
        #             Offer.search_words_changed,
        #             func.concat(Offer.search_words, '') != func.concat(
        #                 func.coalesce(CatalogItem.search_words, Offer.search_words), '')
        #         )),
        #         else_=Offer.search_words_changed)
        # }

        detect_barcodes_changes_for_yandex = {
            'barcodes_changed': f"""CASE
                    WHEN offers.market = 'yandex' THEN (offers.barcodes_changed OR CONCAT(offers.barcodes, '') != CONCAT(
                        COALESCE(catalog_items.barcodes, offers.barcodes ), '')
                    )
                    ELSE offers.barcodes_changed
                END"""
        }
        # Штрихкоды изменяемые только для яндекса, поэтому тречим изменения только у него
        # detect_barcodes_changes_for_yandex = {
        #     'barcodes_changed': case(
        #         (Offer.market == 'yandex', or_(
        #             Offer.barcodes_changed,
        #             func.concat(Offer.barcodes, '') != func.concat(func.coalesce(CatalogItem.barcodes, Offer.barcodes),
        #                                                            '')
        #
        #         )),
        #         else_=Offer.barcodes_changed)
        # }

        updating_values.update(update_search_words)
        updating_values.update(update_barcodes)
        updating_values.update(detect_barcodes_changes_for_yandex)
        updating_values.update(detect_changes_values)
        updating_values.update(detect_search_words_changes_for_ozon)

        for k, v in updating_values.items():
            query += f"{k} = {v},\n\t"
        return query

class CatalogDataFilter(BaseFilter[str]):
    """ Filter offer that synchronize with current offer """

    def __call__(self, query):
        query += "FROM catalog_items\n\tWHERE offers.synchronization = true AND offers.sku = catalog_items.sku"
        return query
