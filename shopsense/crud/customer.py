from sqlalchemy.orm import Session
from models import Customer, Product, Transaction
from schemas.customer import CustomerCreate, OrderCreate
from fastapi import HTTPException, status
from datetime import datetime

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if db_customer:
        return db_customer # Return existing if already registered
        
    new_customer = Customer(
        name=customer.name,
        email=customer.email
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

def get_customers(db: Session):
    return db.query(Customer).all()

def place_order(db: Session, order: OrderCreate):
    # Get product to check stock and price
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.stock_quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available")
        
    # Calculate total
    total_amount = product.price * order.quantity
    
    # Create transaction
    transaction = Transaction(
        product_id=product.id,
        vendor_id=product.vendor_id,
        customer_id=order.customer_id,
        quantity=order.quantity,
        total_amount=total_amount,
        timestamp=datetime.utcnow()
    )
    
    # Update stock
    product.stock_quantity -= order.quantity
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction
