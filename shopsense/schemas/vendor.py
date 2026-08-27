from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional
from datetime import datetime

class VendorCreate(BaseModel):
    name: str # Store Name
    owner_name: Optional[str] = "" # Owner Name
    email: EmailStr
    phone: str
    password: str
    confirm_password: Optional[str] = None

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.confirm_password and self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password do not match")
        return self


class VendorLogin(BaseModel):
    email: EmailStr
    password: str


class VendorResponse(BaseModel):
    id: int
    name: str
    owner_name: Optional[str] = ""
    email: EmailStr
    phone: str
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    vendor: VendorResponse