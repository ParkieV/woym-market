from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    Float,
    DateTime,
    Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from datetime import datetime
from .base import Base
from ...api.factory import APITypes


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    login = Column(String, unique=True)
    password = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_staff = Column(Boolean, default=False)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    discount_purchase = Column(Float, default=20)
    fbo_sales_commission = Column(Float, default=19)
    rate = Column(Float, default=10)


class Offer(Base):
    __tablename__ = 'offers'
    # from yandex api
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    sku = Column(String, index=True, nullable=False) # same as id
    name = Column(String, nullable=False)

    self_weight = Column(Float, default=None, nullable=True)
    self_length = Column(Float, default=None, nullable=True)
    self_width = Column(Float, default=None, nullable=True)
    self_height = Column(Float, default=None, nullable=True)

    yandex_weight = Column(Float, nullable=True)
    yandex_length = Column(Float, nullable=True)
    yandex_width = Column(Float, nullable=True)
    yandex_height = Column(Float, nullable=True)

    volume = Column(Float, default=None, nullable=True)
    yandex_volume = Column(Float, nullable=True)
    volume_difference = Column(Float, nullable=True, default=None)

    photo = Column(String, nullable=True)
    remaining_stock = Column(Integer)
    name_of_shop = Column(String, index=True)
    market = Column(String)
    group_sellers_amount = Column(Integer)
    business_id = Column(Integer)

    # countable/editable values
    dollar_cost_price = Column(Float, nullable=True)
    dollar_cost_price_updated_at = Column(DateTime, nullable=True, default=None)
    cost_price = Column(Float, nullable=True)
    total_price_coeff = Column(Float)
    total_price_min_additional = Column(Float)
    total_price = Column(Float, nullable=True)
    discount_base_price = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    margin = Column(Float, nullable=True)
    fbo = Column(Float, nullable=True)

    content_rating = Column(Float, nullable=True)
    price_index = Column(String, nullable=True)
    supplier_available = Column(Boolean, default=False)
    volume_profitability_ratio = Column(Float, nullable=True, default=None)
    days_to_zero_profit = Column(Float, nullable=True, default=None)
    market_discount_in_percent = Column(Float, nullable=True, default=None)

    attractive_price_threshold = Column(Float, nullable=True)
    moderately_attractive_price_threshold = Column(Float, nullable=True)
    best_place_wm = Column(String, nullable=True)
    min_price_without_market = Column(Float, nullable=True)
    best_place_im = Column(String, nullable=True)
    min_price_in_market = Column(Float, nullable=True)
    your_price_for_buyers = Column(Float, nullable=True)
    min_general_markets_price = Column(Float, nullable=True)

    current_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True, default=None)

    # User additional fields
    note_1 = Column(String, default='', nullable=False)
    note_2 = Column(String, default='', nullable=False)
    note_3 = Column(String, default='', nullable=False)

    use_manual_min_price = Column(Boolean, default=True, nullable=False)
    auto_min_price = Column(Float, nullable=False)
    manual_min_price = Column(Float, default=None, nullable=True)
    auto_price_control = Column(Boolean, default=False, nullable=False)

    hidden = Column(Boolean, default=False, nullable=False)

    pricing_scheme_name = Column(String, ForeignKey('pricing_schemes.name', ondelete='RESTRICT'), nullable=False)
    pricing_scheme = relationship('PricingScheme', back_populates='offers', lazy='immediate', uselist=False)

    stocks = relationship('OfferStock')


class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)


class TableInfo(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    name = Column(String, unique=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    data = Column(String, nullable=True, default=None)


# class PricingScheme(Base):
#     __tablename__ = 'pricing_schemes'
#
#     id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
#     name = Column(String, nullable=False)
#
#     use_total_price = Column(Boolean, default=False, nullable=False)
#     use_attractive_price_threshold = Column(Boolean, default=False, nullable=False)
#     use_moderately_attractive_price_threshold = Column(Boolean, default=False, nullable=False)
#     use_your_price_for_buyers = Column(Boolean, default=False, nullable=False)
#     use_min_price_without_market = Column(Boolean, default=False, nullable=False)
#     use_min_price_in_market = Column(Boolean, default=False, nullable=False)
#     use_min_general_markets_price = Column(Boolean, default=False, nullable=False)
#
#     n = Column(Float, default=1, nullable=False)
#     m = Column(Float, default=0, nullable=False)
#
#     offers = relationship(Offer, back_populates='pricing_scheme')


class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    name = Column(String)
    market = Column(String)


class OfferStock(Base):
    __tablename__ = 'offers_stocks'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    offer_id = Column(Integer, ForeignKey('offers.id', ondelete='CASCADE'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id', ondelete='CASCADE'))
    warehouse = relationship(Warehouse, uselist=False)
    current_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    for_delivery = Column(Integer, default=0)


class Market(Base):
    __tablename__ = 'markets'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String)

    token = Column(String)
    entity_id = Column(Integer, nullable=True, default=None)
    type = Column(Enum(APITypes))

    tax = Column(Float, default=0)
    long_term_storage_cost = Column(Float, nullable=True, default=None)


class OwnStorage(Base):
    __tablename__ = 'own_storage'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)

    value = Column(Integer, default=0, nullable=False)


class PricingScheme(Base):
    __tablename__ = 'pricing_schemes'

    name = Column(String, unique=True, index=True, nullable=False, primary_key=True)
    market = Column(Enum(APITypes))
    m = Column(Float, default=0)
    n = Column(Float, default=1)
    fields = relationship('PricingSchemeField', back_populates='pricing_scheme')
    offers = relationship(Offer, back_populates='pricing_scheme')


class PricingSchemeField(Base):
    __tablename__ = 'pricing_scheme_fields'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    value = Column(Boolean, nullable=False, default=False)

    pricing_scheme_name = Column(String, ForeignKey("pricing_schemes.name", ondelete='CASCADE'))
    pricing_scheme = relationship(PricingScheme, uselist=False, back_populates='fields')



