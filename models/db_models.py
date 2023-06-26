from __future__ import annotations
from typing import Optional, List
from typing import Annotated
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric,
    Date, DateTime, create_engine,
    inspect, ForeignKey, func,
    )
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship,
    )

import datetime


###################################################################################
# Pre-defined annotations
###################################################################################

intpk = Annotated[int, mapped_column(primary_key=True)]
def_timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, default=datetime.datetime.now()),
]
upd_timestamp = Annotated[
    datetime.datetime,
    mapped_column(nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now()),
]
required_name = Annotated[str, mapped_column(String(30), nullable=False)]
std_value = Annotated[Decimal,12, mapped_column(Numeric(12,2), nullable = True)]

class Base(DeclarativeBase):
    pass


class Products(Base):
    __tablename__ = 'products'

    id: Mapped[intpk]

    name: Mapped[required_name]
    price: Mapped[std_value]
    description: Mapped[str]

    transactions: Mapped['ProductTransactions'] = relationship(back_populates='product')

    created: Mapped[def_timestamp]
    updated: Mapped[upd_timestamp]

    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description
        }

class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[intpk]

    order_client: Mapped[required_name]

    products: Mapped[List['ProductTransactions']] = relationship(back_populates='order')

    created: Mapped[def_timestamp]
    updated: Mapped[upd_timestamp]

    def __init__(self, order_client):
        self.order_client = order_client

class ProductTransactions(Base):
    __tablename__ = 'product_transactions'

    id: Mapped[intpk]
    
    # trans_type: Mapped[int] = mapped_column(nullable = False, default = 1)

    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable = False, default = 1)
    price: Mapped[std_value]

    order: Mapped['Orders'] = relationship(back_populates='products')
    product: Mapped['Products'] = relationship(back_populates='transactions')

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
