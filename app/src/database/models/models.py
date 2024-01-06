from sqlalchemy import (
    Column,
    ForeignKey,
    Integer, 
    String,
    Boolean,
    TIMESTAMP,
    Float
)
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

    rate = Column(Float, default=10)


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
    volume_yandex = Column(Float)
    photo = Column(String, nullable=True)
    remaining_stock = Column(Integer)
    minimum_group_price = Column(Float)
    name_of_shop = Column(String)
    group_sellers_amount = Column(Integer)
    business_id = Column(Integer)

    # countable/editable values
    dollar_cost_price = Column(Float)
    volume = Column(Float)
    cost_price = Column(Float)
    total_price_coeff = Column(Float)
    total_price_min_additional = Column(Float)
    total_price = Column(Float)
    discount_base_price = Column(Float)
    profit = Column(Float)
    margin = Column(Float)
    fby = Column(Float)

    current_price = Column(Float, nullable=True)

    # User additional fields
    note_1 = Column(String, nullable=True)
    note_2 = Column(String, nullable=True)
    note_3 = Column(String, nullable=True)

    use_manual_min_price = Column(Boolean, default=True)
    auto_min_price = Column(Float)
    manual_min_price = Column(Float, nullable=True, default=None)

    auto_price_control = Column(Boolean, default=False)
