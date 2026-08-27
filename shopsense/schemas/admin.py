from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse

class AdminDashboardMetrics(BaseModel):
    total_vendors: int
    active_vendors: int
    inactive_vendors: int
    total_products: int
    low_stock_products: int
    pending_products: int
    total_revenue: float
    today_revenue: float
    stock_value: float

class AdminVendorView(BaseModel):
    id: int
    name: str # Store Name
    owner_name: str # Owner Name
    email: EmailStr
    phone: str
    products_count: int
    products_sold: int = 0
    is_active: bool = True
    status: str = "Active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminProductView(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    price: float
    stock_quantity: int
    category: str
    tags: Optional[str] = ""
    image_url: Optional[str] = ""
    is_approved: bool = True
    vendor_id: int
    vendor_name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
