from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import crud.customer as crud
import schemas.customer as schema
from database import SessionLocal

router = APIRouter(
    prefix="/customer",
    tags=["Customer"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schema.CustomerResponse)
def register_customer(customer: schema.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer)

@router.get("/list", response_model=List[schema.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return crud.get_customers(db)

@router.post("/order", response_model=schema.OrderResponse)
def place_order(order: schema.OrderCreate, db: Session = Depends(get_db)):
    return crud.place_order(db, order)
