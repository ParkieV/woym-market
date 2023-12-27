from sqlalchemy import (
    Column,
    ForeignKey,
    Integer, 
    String,
    Boolean,
    TIMESTAMP,
    Float
)
from sqlalchemy.orm import relationship, backref
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


class Offer(Base):
    __tablename__ = 'offers'
    # from yandex api
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    sku = Column(String, unique=True, index=True) # same as id
    name = Column(String)
    weight = Column(Float)
    length = Column(Float)
    width = Column(Float)
    height = Column(Float)
    volume_from_yandex = Column(Float)
    photo = Column(String, nullable=True)
    remaining_stock = Column(Integer)
    minimum_group_price = Column(Float)
    name_of_shop = Column(String)
    group_sellers_amount = Column(Integer)

    # countable/editable values
    parches = Column(Float)
    settlement_price_factor = Column(Float)
    volume = Column(Float)
    cost_price = Column(Float)
    settlement_price_factor = Column(Float)
    minimum_markup = Column(Float)
    settlement_price = Column(Float)
    price_before_discount = Column(Float)
    profit = Column(Float)
    payback = Column(Float)
    fby = Column(Float)

    market_price = Column(Float,nullable=True)

    # User additional fields
    notation_1 = Column(String, nullable=True)
    notation_2 = Column(String, nullable=True)
    notation_3 = Column(String, nullable=True)

    automatic_price_management = Column(Boolean, default=True)
    manual_control_min_price = Column(Boolean, default=False)
