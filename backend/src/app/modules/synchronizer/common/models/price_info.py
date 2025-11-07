from dataclasses import field
from decimal import Decimal

from attr import dataclass

from app.modules.synchronizer.common.models.enums import DecimalPlaces, Currency, PriceIndex
from app.modules.synchronizer.common.models.percent import Percent
from app.modules.synchronizer.common.models.price import Price


@dataclass(slots=True)
class PriceInfo:
    """Информация о ценовой политике товара"""
    auto_min_price: Percent # 'Авто мин. цена (в %)'
    pricing_scheme_name: str # 'Id схемы ценообразования'
    seller_discount: Percent | None # 'Скидка продавца (в %)'
    old_seller_discount: Percent | None # Старая скидка продавца (в %)
    wholesale_price: Price | None # Оптовая цена
    current_price: Price | None # Текущая цена
    target_price: Price | None # Целевая цена
    _price_index: str | None # Индекс цены
    your_price_for_buyers: Price | None # Ваша цена по акции
    your_promotion_price: Price | None # Ваша цена для покупателей
    attractive_price_threshold: Price | None # Порог для привлекательной цены
    moderately_attractive_price_threshold: Price | None # Порог для умеренно привлекательной цены
    recommended_retail_price: Price | None # РРЦ
    stop_price: Price | None # Стоп цена
    logistic_price: Price | None # Стоимость дополнительной логистики 1 литра
    total_price_min_additional: Price = field(
        default=Price(
            currency=Currency.RUBLE, value=Decimal(200)
        )
    ) # 'Мин. наценка на расчетную цену'
    manual_min_price: Price | None = field(
        default=None,
        metadata={"precision": DecimalPlaces.TWO.value},
    ) # 'Ручная мин. цена'
    total_price_coeff: Decimal = field(
        default=Decimal(2.4),
        metadata={"precision": DecimalPlaces.TWO.value},
    ) # 'Коэффициент расчетной цены'
    purchase_price: Price = field(
        default=Price(currency=Currency.DOLLAR, value=Decimal(0)),
    ) # Цена закупки

    @property
    def discount_base_price(self) -> Price:
        return self.current_price * 1.2

    @property
    def price_index(self) -> str | None:
        match self._price_index:
            case PriceIndex.WITHOUT_INDEX.value:
                return PriceIndex.WITHOUT_INDEX.value
            case PriceIndex.PROFIT.value:
                return PriceIndex.PROFIT.value
            case PriceIndex.AVG_PROFIT.value:
                return PriceIndex.AVG_PROFIT.value
            case PriceIndex.NON_PROFIT.value:
                return PriceIndex.NON_PROFIT.value
            case _:
                return None

    @property
    def market_discount_in_percent(self) -> Percent:
        return Percent(
            100 - self.your_price_for_buyers * 100 / self.your_promotion_price
        )
