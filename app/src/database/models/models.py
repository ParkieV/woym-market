from sqlalchemy import (
    Column,
    ForeignKey,
    Integer, 
    String,
    Boolean,
    TIMESTAMP,
    Float,
DateTime
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
    discount = Column(Float, default=20)
    discount_promotional = Column(Float, default=0)
    discount_purchase = Column(Float, default=20)
    rate = Column(Float, default=10)

    columns = relationship('ColumnInfo', back_populates='settings', lazy='subquery')


class Offer(Base):
    __tablename__ = 'offers'
    # from yandex api
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    sku = Column(String, index=True) # same as id
    name = Column(String)

    self_weight = Column(Float, default=0)
    self_length = Column(Float, default=0)
    self_width = Column(Float, default=0)
    self_height = Column(Float, default=0)

    yandex_weight = Column(Float)
    yandex_length = Column(Float)
    yandex_width = Column(Float)
    yandex_height = Column(Float)

    volume = Column(Float, default=0)
    yandex_volume = Column(Float)
    volume_difference = Column(Float, nullable=True, default=None)

    photo = Column(String, nullable=True)
    remaining_stock = Column(Integer)
    name_of_shop = Column(String, index=True)
    market = Column(String)
    group_sellers_amount = Column(Integer)
    business_id = Column(Integer)

    # countable/editable values
    dollar_cost_price = Column(Float)
    cost_price = Column(Float)
    total_price_coeff = Column(Float)
    total_price_min_additional = Column(Float)
    total_price = Column(Float)
    discount_base_price = Column(Float)
    profit = Column(Float)
    margin = Column(Float)
    fby = Column(Float)

    attractive_price_threshold = Column(Float)
    moderately_attractive_price_threshold = Column(Float)
    best_place_wm = Column(String)
    best_price_wm = Column(Float)
    best_place_im = Column(String)
    best_price_im = Column(Float)
    minimum_group_price = Column(Float)

    current_price = Column(Float, nullable=True)
    target_price = Column(Float, nullable=True, default=None)

    # User additional fields
    note_1 = Column(String, default='')
    note_2 = Column(String, default='')
    note_3 = Column(String, default='')

    use_manual_min_price = Column(Boolean, default=True)
    auto_min_price = Column(Float)
    manual_min_price = Column(Float, nullable=True, default=None)

    auto_price_control = Column(Boolean, default=False)


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
    key = Column(String)
    data_type = Column(String)
    index = Column(Integer)
    width = Column(Float, default=0)
    editable = Column(Float, default=True)
    is_visible = Column(Float, default=True)


