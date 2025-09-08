from sqlalchemy import Column, String, Float
from app.core.database import Base  # Use centralized Base
from sqlalchemy.orm import declarative_base




class Product(Base):
    __tablename__ = "Product"

    id = Column(String, primary_key=True, index=True)
    status = Column(String)
    userId = Column(String)
    loc = Column(String)
    price = Column(Float)
    description = Column(String)
