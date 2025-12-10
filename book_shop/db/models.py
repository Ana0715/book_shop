from flask_login import UserMixin

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_verified = Column(Boolean, default=False)

    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')



    def __repr__(self):
        return f"<User {self.username}>"


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    genre = Column(String(100), nullable=False)
    cover = Column(String(500))
    description = Column(Text)
    rating = Column(Float)
    year = Column(Integer)

    reviews = relationship('Review', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Book {self.title}>"


class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    book = relationship('Book', back_populates='reviews')
    user = relationship('User', back_populates='reviews')

    def __repr__(self):
        return f"<Review {self.id} for Book {self.book_id} by User {self.user_id}>"
    

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    user = relationship('User', back_populates='cart_items')
    book = relationship('Book')

    def __repr__(self):
        return f"<CartItem {self.id}: {self.quantity} × Book {self.book_id}>"

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    status = Column(String(20), default='оформлен', nullable=False)
    delivery_type = Column(String(20), nullable=False)
    address = Column(String(255))
    total_price = Column(Float, nullable=False)

    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Order {self.id}: {self.status} ({self.total_price}₽)>"


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship('Order', back_populates='items')
    book = relationship('Book')

    def __repr__(self):
        return f"<OrderItem {self.id}: {self.quantity} × Book {self.book_id}>"


