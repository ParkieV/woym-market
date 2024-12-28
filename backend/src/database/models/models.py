from datetime import datetime
from typing import Any

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    Float,
    DateTime,
    select, func, BigInteger
)
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase

from src.schemas.base_api_schemas import WarehouseType

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    first_name = mapped_column(String)
    last_name = mapped_column(String)
    login = mapped_column(String, unique=True)
    password = mapped_column(String)
    created_at = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_staff = mapped_column(Boolean, default=False)


class Settings(Base):
    __tablename__ = 'settings'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'))


class Offer(Base):
    __tablename__ = 'offers'
    # from yandex api
    id = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)

    sku = mapped_column(String, index=True, nullable=False) # same as id

    name = mapped_column(String, nullable=True)
    name_changed = mapped_column(Boolean, nullable=False, default=False)

    description = mapped_column(String, nullable=True, default=None, server_default=None)
    description_changed = mapped_column(Boolean, nullable=False, default=False)

    self_weight = mapped_column(Float, default=None, nullable=True)
    self_length = mapped_column(Float, default=None, nullable=True)
    self_width = mapped_column(Float, default=None, nullable=True)
    self_height = mapped_column(Float, default=None, nullable=True)

    yandex_weight = mapped_column(Float, nullable=True)
    yandex_length = mapped_column(Float, nullable=True)
    yandex_width = mapped_column(Float, nullable=True)
    yandex_height = mapped_column(Float, nullable=True)

    photo = mapped_column(String, nullable=True)
    name_of_shop = mapped_column(String, index=True)
    market = mapped_column(String)
    group_sellers_amount = mapped_column(Integer)
    business_id = mapped_column(Integer)

    # countable/editable values
    dollar_cost_price = mapped_column(Float, nullable=True)
    dollar_cost_price_updated_at = mapped_column(DateTime, nullable=True, default=None)
    cost_price = mapped_column(Float, nullable=True)
    total_price_coeff = mapped_column(Float)
    total_price_min_additional = mapped_column(Float)
    total_price = mapped_column(Float, nullable=True)
    discount_base_price = mapped_column(Float, nullable=True)
    profit = mapped_column(Float, nullable=True)
    margin = mapped_column(Float, nullable=True)
    fbo = mapped_column(Float, nullable=True)

    content_rating = mapped_column(Float, nullable=True)
    price_index = mapped_column(String, nullable=True)
    supplier_available = mapped_column(Boolean, default=False)
    volume_profitability_ratio = mapped_column(Float, nullable=True, default=None)
    days_to_zero_profit = mapped_column(Float, nullable=True, default=None)
    market_discount_in_percent = mapped_column(Float, nullable=True, default=None)
    auto_participation_in_promotions = mapped_column(Boolean, default=False)
    recommended_retail_price = mapped_column(Float, nullable=True, default=None)
    stop_price = mapped_column(Float, nullable=True, default=None)

    attractive_price_threshold = mapped_column(Float, nullable=True)
    moderately_attractive_price_threshold = mapped_column(Float, nullable=True)
    best_place_wm = mapped_column(String, nullable=True)
    min_price_without_market = mapped_column(Float, nullable=True)
    best_place_im = mapped_column(String, nullable=True)
    best_place_im_link = mapped_column(String, nullable=True, default=None)
    min_price_in_market = mapped_column(Float, nullable=True)
    your_price_for_buyers = mapped_column(Float, nullable=True)
    min_general_markets_price = mapped_column(Float, nullable=True)
    logistic_price = mapped_column(Float, default=0)
    your_promotion_price = mapped_column(Float, nullable=True, default=None)

    current_price = mapped_column(Float, nullable=True)
    target_price = mapped_column(Float, nullable=True, default=None)

    catalog_note = mapped_column(String, nullable=False, default='', server_default=text("''"))

    # User additional fields
    note_1 = mapped_column(String, default='', nullable=False)
    note_2 = mapped_column(String, default='', nullable=False)
    note_3 = mapped_column(String, default='', nullable=False)

    use_manual_min_price = mapped_column(Boolean, default=True, nullable=False)
    auto_min_price = mapped_column(Float, nullable=False)
    manual_min_price = mapped_column(Float, default=None, nullable=True)
    auto_price_control = mapped_column(Boolean, default=False, nullable=False)

    hidden = mapped_column(Boolean, default=False, nullable=False)

    pricing_scheme_name = mapped_column(String, ForeignKey('pricing_schemes.name', ondelete='RESTRICT'), nullable=False)
    pricing_scheme = relationship('PricingScheme', back_populates='offers', lazy='immediate', uselist=False)

    barcodes = mapped_column(String, nullable=True, default=None)
    barcodes_changed = mapped_column(Boolean, nullable=False, default=False)

    use_promotion_price = mapped_column(Boolean, default=False)
    wholesale_dollar_cost_price = mapped_column(Float, nullable=True)
    vendor_code = mapped_column(BigInteger, nullable=True, default=None)
    search_words = mapped_column(String, nullable=True, default=None)
    search_words_changed = mapped_column(Boolean, default=False, nullable=False)

    synchronization = mapped_column(Boolean, default=False, nullable=False)

    stocks = relationship('OfferStock')

    @classmethod
    def columns(cls, use_catalog: bool = False, exclude: list | None = None, exclude_from_catalog: list | None = None):
        _exclude = exclude or []

        if not use_catalog:
            return [i for i in cls.__table__.columns if i.name not in _exclude]

        _exclude_from_catalog = ['id', 'sku']
        if exclude_from_catalog:
            _exclude_from_catalog.extend(exclude_from_catalog)

        catalog_columns = {i.name: i for i in CatalogItem.__table__.columns if i.name not in _exclude_from_catalog}

        result = []

        for column in cls.__table__.columns:
            if column.name in _exclude:
                continue

            if column.name in catalog_columns:
                result.append(catalog_columns[column.name])
            else:
                result.append(column)

        return result

class Logs(Base):
    __tablename__ = 'logs'
    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'))

    updated_at = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class TableInfo(Base):
    __tablename__ = 'tables'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)

    name = mapped_column(String, unique=True)
    updated_at = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    data = mapped_column(String, nullable=True, default=None)


# class PricingScheme(Base):
#     __tablename__ = 'pricing_schemes'
#
#     id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
#     name = mapped_column(String, nullable=False)
#
#     use_total_price = mapped_column(Boolean, default=False, nullable=False)
#     use_attractive_price_threshold = mapped_column(Boolean, default=False, nullable=False)
#     use_moderately_attractive_price_threshold = mapped_column(Boolean, default=False, nullable=False)
#     use_your_price_for_buyers = mapped_column(Boolean, default=False, nullable=False)
#     use_min_price_without_market = mapped_column(Boolean, default=False, nullable=False)
#     use_min_price_in_market = mapped_column(Boolean, default=False, nullable=False)
#     use_min_general_markets_price = mapped_column(Boolean, default=False, nullable=False)
#
#     n = mapped_column(Float, default=1, nullable=False)
#     m = mapped_column(Float, default=0, nullable=False)
#
#     offers = relationship(Offer, back_populates='pricing_scheme')


class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    name = mapped_column(String)
    market = mapped_column(String)
    parent_warehouse_id = mapped_column(Integer, ForeignKey('warehouses.id', ondelete='SET NULL'), nullable=True, default=None)
    related_warehouses = relationship('Warehouse', uselist=True)
    warehouse_type = mapped_column(String, default=WarehouseType.WAREHOUSE)
    from_file_updated_at = mapped_column(DateTime(timezone=True), nullable=True, default=None)


class OfferStock(Base):
    __tablename__ = 'offers_stocks'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    offer_id = mapped_column(Integer, ForeignKey('offers.id', ondelete='CASCADE'), index=True)
    warehouse_id = mapped_column(Integer, ForeignKey('warehouses.id', ondelete='CASCADE'), index=True)
    warehouse = relationship(Warehouse, uselist=False)
    can_be_delivered = mapped_column(Boolean, default=False)
    advice_from_the_store = mapped_column(String, default='')
    current_stock = mapped_column(Integer, default=0)
    in_box = mapped_column(Integer, default=1)
    is_deliver_in_boxes = mapped_column(Boolean, default=False)
    min_stock = mapped_column(Integer, default=0)
    for_delivery = mapped_column(Integer, default=0)


class Market(Base):
    __tablename__ = 'markets'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = mapped_column(String, index=True)

    token = mapped_column(String)
    entity_id = mapped_column(Integer, nullable=True, default=None)
    type = mapped_column(String, nullable=False, index=True)
    discount_purchase = mapped_column(Float, default=20)

    tax = mapped_column(Float, default=0)
    long_term_storage_cost = mapped_column(Float, nullable=True, default=None)
    rate = mapped_column(Float, default=10)
    fbo_sales_commission = mapped_column(Float, default=19)
    first_variable_for_recommended_retail_price = mapped_column(Float, default=10)
    second_variable_for_recommended_retail_price = mapped_column(Float, default=10)
    first_variable_for_stop_price = mapped_column(Float, default=10)
    second_variable_for_stop_price = mapped_column(Float, default=10)
    price_before_discount = mapped_column(Float, default=20)
    volume_threshold_for_additional_logistics = mapped_column(Float, default=10)
    cost_of_additional_logistics_per_liter = mapped_column(Float, default=100)

    a_variable_for_smart_delivery = mapped_column(Float, default=0, nullable=False)
    b_variable_for_smart_delivery = mapped_column(Float, default=0, nullable=False)
    c_variable_for_smart_delivery = mapped_column(Float, default=0, nullable=False)
    d_variable_for_smart_delivery = mapped_column(Float, default=0, nullable=False)
    e_variable_for_smart_delivery = mapped_column(Float, default=0, nullable=False)


class OwnStorage(Base):
    __tablename__ = 'own_storage'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    sku = mapped_column(String, index=True, nullable=False)
    storage_place_id = mapped_column(Integer, ForeignKey('own_storage_place.id', ondelete='RESTRICT'), nullable=True, default=None)
    storage_place = relationship('OwnStoragePlace', uselist=False)
    value = mapped_column(Integer, default=0, nullable=False)


class PricingScheme(Base):
    __tablename__ = 'pricing_schemes'

    name = mapped_column(String, unique=True, index=True, nullable=False, primary_key=True)
    market = mapped_column(String, nullable=False)
    m = mapped_column(Float, default=0)
    n = mapped_column(Float, default=1)
    fields = relationship('PricingSchemeField', back_populates='pricing_scheme', order_by='PricingSchemeField.name.asc()')
    offers = relationship(Offer, back_populates='pricing_scheme')


class PricingSchemeField(Base):
    __tablename__ = 'pricing_scheme_fields'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    key = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    value = mapped_column(Boolean, nullable=False, default=False)

    pricing_scheme_name = mapped_column(String, ForeignKey("pricing_schemes.name", ondelete='CASCADE'))
    pricing_scheme = relationship(PricingScheme, uselist=False, back_populates='fields')


class OwnStoragePlace(Base):
    __tablename__ = 'own_storage_place'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = mapped_column(String, unique=True, nullable=False)


class CatalogItem(Base):
    __tablename__ = 'catalog_items'

    sku = mapped_column(String, index=True, nullable=False, primary_key=True)

    self_weight = mapped_column(Float, nullable=True, default=None)
    self_length = mapped_column(Float, nullable=True, default=None)
    self_width = mapped_column(Float, nullable=True, default=None)
    self_height = mapped_column(Float, nullable=True, default=None)
    volume = mapped_column(Float, nullable=True, default=None)
    catalog_note = mapped_column(String, nullable=True, server_default=text("'Новый товар'"))
    use_promotion_price = mapped_column(Boolean, nullable=False, default=False)
    wholesale_dollar_cost_price = mapped_column(Float, nullable=True, default=None)
    supplier_available = mapped_column(Boolean, nullable=False, default=False)
    dollar_cost_price_updated_at = mapped_column(DateTime, nullable=True, default=None)
    description = mapped_column(String, nullable=True, default=None, server_default=None)
    search_words = mapped_column(String, nullable=True, default=None, server_default=None)
    search_words_changed = mapped_column(Boolean, nullable=False, default=False)
    name = mapped_column(String, nullable=True, default=None, server_default=None)
    barcodes = mapped_column(String, nullable=True, default=None, server_default=None)

    synchronization = relationship('Offer', uselist=True, primaryjoin='foreign(Offer.sku) == CatalogItem.sku')


class Order(Base):
    __tablename__ = 'orders'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    internal_order_id = mapped_column(String, nullable=False)

    offer_id = mapped_column(Integer, ForeignKey('offers.id', ondelete='CASCADE'), nullable=False)
    sku = mapped_column(String, nullable=False, index=True)
    name_of_shop = mapped_column(String, nullable=False, index=True)
    market = mapped_column(String, nullable=False, index=True)

    quantity = mapped_column(Integer, nullable=False)
    price = mapped_column(Float, nullable=True)
    warehouse_id = mapped_column(Integer, ForeignKey('warehouses.id', ondelete='SET NULL'), index=True, nullable=True)
    warehouse = relationship(Warehouse, uselist=False)

    created_at = mapped_column(DateTime(), nullable=False)
    updated_at = mapped_column(DateTime, nullable=True, default=None)


remaining_stocks_subuery = (
    select(
        OfferStock.offer_id,
        func.sum(func.coalesce(OfferStock.current_stock, 0)).label('remaining_stock')
    )
    .join(Warehouse, Warehouse.id == OfferStock.warehouse_id)
    .where(Warehouse.warehouse_type == 'warehouse')
    .group_by(
        OfferStock.offer_id).subquery())
