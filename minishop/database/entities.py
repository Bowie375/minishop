from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, Text,
                        DECIMAL, DATETIME, func, ForeignKey,
                        CheckConstraint, PrimaryKeyConstraint,)
from decimal import Decimal
from datetime import datetime

# Define the base class for ORM models
Base = declarative_base()

class SerializerMixin:
    def to_dict(self):
        ret = {}
        for c in self.__table__.columns:
            if isinstance(getattr(self, c.name), datetime):
                ret[c.name] = getattr(self, c.name).strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(getattr(self, c.name), Decimal):
                ret[c.name] = float(getattr(self, c.name))
            else:
                ret[c.name] = getattr(self, c.name)
        return ret

# Define the ORM model
class User(Base, SerializerMixin):
    __tablename__ = 'User'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    address = Column(Text, nullable=True)
    registration_date = Column(String(20), nullable=False, default=func.now())
    user_type = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "user_type IN ('customer', 'merchant')",
            name='check_user_type'
        ),
    )

class Store(Base, SerializerMixin):
    __tablename__ = 'Store'
    
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    store_description = Column(Text, nullable=True)
    store_status = Column(Text, nullable=False, default='active')
    registration_date = Column(DATETIME, nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint(
            "store_status IN ('active', 'inactive')",
            name='check_store_status'
        ),
    )

class Product(Base, SerializerMixin):
    __tablename__ = 'Product'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('Store.store_id'), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    created_at = Column(DATETIME, nullable=False, default=func.now())
    status = Column(Text, nullable=False, default='active')

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name='check_product_status'
        ),
    )

class Order_Table(Base, SerializerMixin):
    __tablename__ = 'Order_Table'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    payer_id = Column(Integer, ForeignKey('User.user_id'), nullable=True)
    payment_method = Column(Text, nullable=True)
    payment_status = Column(Text, nullable=True)
    payment_time = Column(DATETIME, nullable=True, default=None)
    order_status = Column(Text, nullable=False, default='pending')
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DATETIME, nullable=False, default=func.now())

    __table_args__ = (
        CheckConstraint(
            "payment_method is NULL or payment_method IN ('credit_card', 'wechat', 'alipay')",
            name='check_payment_method'
        ),
        CheckConstraint(
            "payment_status is NULL or payment_status IN ('pending', 'success', 'failed')",
            name='check_payment_status'
        ),
        CheckConstraint(
            "order_status IN ('pending', 'paid', 'shipped', 'completed', 'canceled')",
            name='check_order_status'
        ),
    )

class Order_Item(Base, SerializerMixin):
    __tablename__ = 'Order_Item'

    order_id = Column(Integer, ForeignKey('Order_Table.order_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('Product.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'product_id'),
    )

class Review(Base, SerializerMixin):
    __tablename__ = 'Review'

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('User.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('Product.product_id'), nullable=False)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)
    comment_time = Column(DATETIME, nullable=False, default=func.now())
    reply = Column(Text, nullable=True)
    reply_time = Column(DATETIME, nullable=True, default=None)

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name='check_rating'
        ),
    )

class Category(Base, SerializerMixin):
    __tablename__ = 'Category'

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    parent_category_id = Column(Integer, ForeignKey('Category.category_id'), nullable=True)

class Product_Tag(Base, SerializerMixin):
    __tablename__ = 'Product_Tag'

    product_id = Column(Integer, ForeignKey('Product.product_id'), nullable=False)
    category_id = Column(Integer, ForeignKey('Category.category_id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('product_id', 'category_id'),
    )

class Shipping(Base, SerializerMixin):
    __tablename__ = 'Shipping'

    shipping_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('Order_Table.order_id'), nullable=False)
    tracking_number = Column(String(50), unique=True, nullable=False)
    carrier = Column(String(50), nullable=False)
    shipping_status = Column(Text, nullable=False, default='pending')
    estimated_arrival = Column(DATETIME, nullable=True, default=None)
    actual_arrival = Column(DATETIME, nullable=True, default=None)
    recipient_name = Column(String(50), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    shipping_address = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "shipping_status IN ('pending', 'shipped', 'in_transit', 'delivered')",
            name='check_shipping_status'
        ),
    )

class Shipping_Track(Base, SerializerMixin):
    __tablename__ = 'Shipping_Track'

    shipping_id = Column(Integer, ForeignKey('Shipping.shipping_id'), nullable=False)
    track_id = Column(Integer, nullable=False)
    status = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    timestamp = Column(DATETIME, nullable=False, default=func.now())

    __table_args__ = (
        PrimaryKeyConstraint('shipping_id', 'track_id'),
        CheckConstraint(
            "status IN ('sorting', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered')",
            name='check_shipping_track_status'
        ),
    )
