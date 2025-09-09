from sqlalchemy import Column, String, Float, Boolean,Integer
from app.core.database import Base  # Use centralized Base
from sqlalchemy.orm import declarative_base




class Product(Base):
    __tablename__ = "Product"

    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    userId = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    price = Column(Float)
    description = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
