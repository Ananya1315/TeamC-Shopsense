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
async def place_order(order: schema.OrderCreate, db: Session = Depends(get_db)):
    transaction = crud.place_order(db, order)
    try:
        from models import Product
        from routers.websocket import manager

        prod_name = db.query(Product.name).filter(Product.id == transaction.product_id).scalar() or "Product"
        await manager.broadcast_new_sale({
            "transaction_id": transaction.id,
            "product_id": transaction.product_id,
            "product_name": prod_name,
            "vendor_id": transaction.vendor_id,
            "customer_id": transaction.customer_id,
            "quantity": transaction.quantity,
            "total_amount": round(float(transaction.total_amount), 2),
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else ""
        })
    except Exception as e:
        import logging
        logging.getLogger("shopsense.websocket").error(f"WebSocket broadcast failed safely: {e}")

    return transaction
