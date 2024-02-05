from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    Float,
    DateTime, JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from .base import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    login = Column(String, unique=True)
    password = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    discount_purchase = Column(Float, default=20)
    fby_sales_commission = Column(Float, default=19)
    rate = Column(Float, default=10)

    columns = relationship('ColumnInfo', back_populates='settings', lazy='subquery')


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
    cost_price = Column(Float, nullable=True)
    total_price_coeff = Column(Float)
    total_price_min_additional = Column(Float)
    total_price = Column(Float, nullable=True)
    discount_base_price = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    margin = Column(Float, nullable=True)
    fby = Column(Float, nullable=True)

    attractive_price_threshold = Column(Float, nullable=True)
    moderately_attractive_price_threshold = Column(Float, nullable=True)
    best_place_wm = Column(String, nullable=True)
    best_price_wm = Column(Float, nullable=True)
    best_place_im = Column(String, nullable=True)
    best_price_im = Column(Float, nullable=True)
    your_price_for_buyers = Column(Float, nullable=True)
    minimum_group_price = Column(Float, nullable=True)

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

    pricing_scheme_id = Column(Integer, ForeignKey('pricing_schemes.id'), nullable=True, default=None)
    pricing_scheme = relationship('PricingScheme', back_populates='offers', lazy='immediate', uselist=False)


class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)


class ColumnInfo(Base):
    __tablename__ = 'columns'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    settings_id = Column(Integer, ForeignKey('settings.id', ondelete='CASCADE'))
    settings = relationship("Settings", back_populates='columns')

    name = Column(String)
    key = Column(String, unique=True, index=True)
    edit_key = Column(String, nullable=True, default=None)
    data_type = Column(String)
    index = Column(Integer)
    width = Column(Float, default=100)
    editable = Column(Boolean)
    is_visible = Column(Boolean, default=True)
    pinned = Column(Boolean, default=False)
    tooltip = Column(String, default='')
    options = Column(JSON, nullable=True, default=None)


class PricingScheme(Base):
    __tablename__ = 'pricing_schemes'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False)

    use_total_price = Column(Boolean, default=False, nullable=False)
    use_attractive_price_threshold = Column(Boolean, default=False, nullable=False)
    use_moderately_attractive_price_threshold = Column(Boolean, default=False, nullable=False)
    use_your_price_for_buyers = Column(Boolean, default=False, nullable=False)
    use_best_price_wm = Column(Boolean, default=False, nullable=False)
    use_best_price_im = Column(Boolean, default=False, nullable=False)
    use_minimum_group_price = Column(Boolean, default=False, nullable=False)

    n = Column(Float, default=1, nullable=False)
    m = Column(Float, default=0, nullable=False)

    offers = relationship(Offer, back_populates='pricing_scheme')


class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    name = Column(String)
    warehouse_id = Column(Integer)
    market = Column(String)


class OfferStock(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)

    offer_id = Column(Integer, ForeignKey('offers.id', ondelete='CASCADE'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id', ondelete='CASCADE'))
    in_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    for_delivery = Column(Integer, default=0)

