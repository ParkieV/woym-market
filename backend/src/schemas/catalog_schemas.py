from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ValidationError, computed_field, ConfigDict


class SynchronizationOffer(BaseModel):
    sku: str = Field(title='SKU товара')
    id: int = Field(title='ID товара')
    market: str = Field(title='Площадка')
    name_of_shop: str = Field(title='Название магазина')
    synchronization: bool = Field(title='Синхронизация товара с каталогом')
    # is_blocked: bool = Field(title='Доступно ли изменение синхронизации', description='Если поле false, то товар на данной площадке не представлен')


class BaseCatalogItem(BaseModel):
    sku: str = Field(title='sku')


class CatalogItemUpdate(BaseCatalogItem):
    name: str | None = Field(title='Название', default=None)
    description: str | None = Field(title='Аннотация', default=None)
    search_words: str | None = Field(title='Поисковые слова', default=None)
    barcodes: str | None = Field(title='Штрихкоды', default=None)

    self_weight: float | None = Field(title='Вес', default=None)
    self_length: float | None = Field(title='Длина', default=None)
    self_width: float | None = Field(title='Ширина', default=None)
    self_height: float | None = Field(title='Высота', default=None)
    catalog_note: str | None = Field(title='Примечание', default='Новый товар')
    use_promotion_price: bool = Field(title='Акция', default=False)
    wholesale_dollar_cost_price: float | None = Field(title='ОПТ закупка у. е.', default=None)
    supplier_available: bool = Field(title='Наличие у поставщика', default=False)
    synchronization: list[SynchronizationOffer] = Field(title='Связанные товары', default_factory=list)
    reverse_sync_offer_id: int | None = Field(default=None, title='ID карточки товара для обратной синхронизации')


class CatalogItemCreate(CatalogItemUpdate):
    dollar_cost_price_updated_at: datetime | None = Field(title='Дата обновления ОПТ У.Е.', default=None)


class CatalogItem(CatalogItemCreate):

    @computed_field(title='Объем', description='Ширина * Высота * Длина / 1000')
    @property
    def volume(self) -> float | None:
        if not all((self.self_width, self.self_height, self.self_length)):
            return None

        return self.self_width * self.self_height * self.self_length / 1000








