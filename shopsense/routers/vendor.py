from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud.vendor as crud
import schemas.vendor as schema
from database import SessionLocal

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema.VendorResponse)
def create_vendor(vendor: schema.VendorCreate, db: Session = Depends(get_db)):
    existing = crud.get_vendor_by_email(db, vendor.email)
    if existing:
        return existing
    return crud.create_vendor(db, vendor)

@router.post("/register", response_model=schema.VendorResponse)
def register_vendor(vendor: schema.VendorCreate, db: Session = Depends(get_db)):
    existing = crud.get_vendor_by_email(db, vendor.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_vendor(db, vendor)

@router.post("/login", response_model=schema.TokenResponse)
def login_vendor(login_data: schema.VendorLogin, db: Session = Depends(get_db)):
    clean_email = login_data.email.lower().strip()
    
    # 1. Check if vendor email exists
    vendor = crud.get_vendor_by_email(db, clean_email)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    # 2. Check password verification
    authenticated = crud.authenticate_vendor(db, login_data)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )

    return {
        "access_token": f"vendor_token_{vendor.id}",
        "token_type": "bearer",
        "vendor": vendor
    }

@router.get("/", response_model=list[schema.VendorResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    return crud.get_vendors(db)