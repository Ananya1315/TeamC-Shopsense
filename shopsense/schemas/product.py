from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    stock_quantity: int = 0
    category: str
    tags: Optional[str] = ""
    image_url: Optional[str] = ""
    vendor_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    price: float
    stock_quantity: int
    category: str
    tags: Optional[str] = ""
    image_url: Optional[str] = ""
    vendor_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
