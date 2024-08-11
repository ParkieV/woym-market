from pydantic import BaseModel, Field


class SynchronizationOffer(BaseModel):
    sku: str = Field(title='SKU товара')
    id: int = Field(title='ID товара')
    market: str = Field(title='Площадка')
    name_of_shop: str = Field(title='Название магазина')
    synchronization: bool = Field(title='Синхронихирован ли товара с каталогом')
    # is_blocked: bool = Field(title='Доступно ли изменение синхронизации', description='Если поле false, то товар на данной площадке не представлен')


class SynchronizationOfferUpdate(BaseModel):
    sku: str = Field('SKU товара')
    id: int
    synchronization: bool


class BaseCatalogItem(BaseModel):
    sku: str = Field(title='sku')


class CatalogItemUpdate(BaseCatalogItem):
    name: str | None = Field(title='Название', default=None)
    annotation: str | None = Field(title='Аннотация', default=None)
    search_words: str | None = Field(title='Поисковые слова', default=None)
    barcodes: str | None = Field(title='Штрихкоды', default=None)

    self_weight: float | None = Field(title='Вес', default=None)
    self_length: float | None = Field(title='Длина', default=None)
    self_width: float | None = Field(title='Ширина', default=None)
    self_height: float | None = Field(title='Высота', default=None)
    self_volume: float | None = Field(title='Объем', default=None)
    note: str | None = Field(title='Примечание', default=None)
    use_promotion_price: bool = Field(title='Акция', default=False)
    wholesale_dollar_cost_price: float | None = Field(title='ОПТ закупка у. е.', default=None)


class CatalogItemCreate(CatalogItemUpdate):
    pass


class CatalogItem(CatalogItemUpdate):
    # supplier_available: bool = Field(title='Наличие у поставщика')

    synchronization: list[SynchronizationOffer] = Field(title='Связанные товары', default_factory=list)







