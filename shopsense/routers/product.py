from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud.product as crud
import schemas.product as schema
from database import SessionLocal

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema.ProductResponse)
def create_product(
    product: schema.ProductCreate,
    vendor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    # Default to vendor_id 1 if not passed in query or body
    vid = product.vendor_id or vendor_id or 1
    return crud.create_product(db, product, vendor_id=vid)

@router.get("/", response_model=List[schema.ProductResponse])
def get_products(
    vendor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    if vendor_id:
        return crud.get_products_by_vendor(db, vendor_id)
    return crud.get_all_products(db)

@router.get("/{product_id}", response_model=schema.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    prod = crud.get_product_by_id(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@router.put("/{product_id}", response_model=schema.ProductResponse)
def update_product(
    product_id: int,
    product_update: schema.ProductUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
