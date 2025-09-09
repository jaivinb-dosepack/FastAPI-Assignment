from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ProductBase(BaseModel):
    id: Optional[str] = None
    status :str
    userId :str
    lat: float
    lon: float
    price: float
    price :float
    description :str

class ProductUpdate(BaseModel):
    status: Optional[str] = None
    userId: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    price: Optional[float] = None
    description: Optional[str] = None
    
class UserBase(BaseModel):
 
    name: str
    email: str
    password: str
    is_active: bool = True


class ShowUser(BaseModel):
    name: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True