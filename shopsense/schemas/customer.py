from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CustomerCreate(BaseModel):
    name: str
    email: str

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    product_id: int
    vendor_id: int
    customer_id: int
    quantity: int
    total_amount: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
