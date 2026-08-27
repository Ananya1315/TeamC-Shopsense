from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud.admin as crud
import schemas.admin as schema
from database import SessionLocal

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=schema.AdminTokenResponse)
def login_admin(login_data: schema.AdminLogin, db: Session = Depends(get_db)):
    admin = crud.authenticate_admin(db, login_data)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )
    return {
        "access_token": f"admin_token_{admin.id}",
        "token_type": "bearer",
        "admin": admin
    }

@router.get("/dashboard", response_model=schema.AdminDashboardMetrics)
def get_admin_dashboard(db: Session = Depends(get_db)):
    return crud.get_admin_dashboard_metrics(db)

@router.get("/vendors", response_model=List[schema.AdminVendorView])
def get_admin_vendors(db: Session = Depends(get_db)):
    return crud.get_all_vendors_admin(db)

@router.put("/vendors/{vendor_id}/status")
def update_vendor_status(vendor_id: int, is_active: bool, db: Session = Depends(get_db)):
    vendor = crud.toggle_vendor_status(db, vendor_id, is_active)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor status updated", "is_active": vendor.is_active}

@router.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    success = crud.delete_vendor_admin(db, vendor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}

@router.get("/products", response_model=List[schema.AdminProductView])
def get_admin_products(db: Session = Depends(get_db)):
    return crud.get_all_products_admin(db)
