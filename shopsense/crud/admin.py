from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from models import Admin, Vendor, Product, Transaction, Review
from schemas.admin import AdminLogin

def get_admin_by_email(db: Session, email: str):
    return db.query(Admin).filter(Admin.email == email).first()

def authenticate_admin(db: Session, login_data: AdminLogin):
    # Only predefined/allowed admin email & password match
    admin = get_admin_by_email(db, login_data.email)
    
    if not admin:
        if login_data.email.lower() in ["admin@shopsense.com", "admin@gmail.com"]:
            admin = Admin(name="System Admin", email=login_data.email, password_hash=login_data.password)
            db.add(admin)
            db.commit()
            db.refresh(admin)
            return admin
        return None
        
    if admin.password_hash and admin.password_hash != login_data.password:
        return None
        
    return admin

def get_admin_dashboard_metrics(db: Session):
    total_vendors = db.query(Vendor).count()
    active_vendors = db.query(Vendor).filter(Vendor.is_active == True).count()
    inactive_vendors = db.query(Vendor).filter(Vendor.is_active == False).count()
    
    total_products = db.query(Product).count()
    low_stock_products = db.query(Product).filter(Product.stock_quantity <= 20).count()
    pending_products = db.query(Product).filter(Product.is_approved == False).count()
    
    total_orders = db.query(Transaction).count()
    total_revenue = db.query(func.sum(Transaction.total_amount)).scalar() or 0.0
    
    today = date.today()
    today_revenue = db.query(func.sum(Transaction.total_amount)).filter(func.date(Transaction.timestamp) == today).scalar() or 0.0
    
    # Calculate Total Stock Value (sum of price * stock_quantity)
    products = db.query(Product).all()
    stock_value = sum(p.price * p.stock_quantity for p in products) if products else 0.0
    
    return {
        "total_vendors": total_vendors,
        "active_vendors": active_vendors,
        "inactive_vendors": inactive_vendors,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "pending_products": pending_products,
        "total_revenue": round(float(total_revenue), 2),
        "today_revenue": round(float(today_revenue), 2),
        "stock_value": round(float(stock_value), 2)
    }

def get_all_vendors_admin(db: Session):
    vendors = db.query(Vendor).order_by(Vendor.id.asc()).all()
    result = []
    for v in vendors:
        p_count = db.query(Product).filter(Product.vendor_id == v.id).count()
        p_sold = db.query(func.sum(Transaction.quantity)).filter(Transaction.vendor_id == v.id).scalar() or 0
        
        result.append({
            "id": v.id,
            "name": v.name, # Store Name
            "owner_name": v.owner_name or v.name,
            "email": v.email,
            "phone": v.phone or "N/A",
            "products_count": p_count,
            "products_sold": int(p_sold),
            "is_active": v.is_active if v.is_active is not None else True,
            "status": "Active" if (v.is_active is not False) else "Disabled",
            "created_at": v.created_at
        })
    return result

def get_all_products_admin(db: Session):
    products = db.query(Product).order_by(Product.id.desc()).all()
    result = []
    for p in products:
        vname = p.vendor.name if p.vendor else f"Vendor #{p.vendor_id}"
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description or "",
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "category": p.category or "General",
            "tags": p.tags or "",
            "image_url": p.image_url or "",
            "is_approved": p.is_approved if p.is_approved is not None else True,
            "vendor_id": p.vendor_id,
            "vendor_name": vname,
            "created_at": p.created_at
        })
    return result

def toggle_vendor_status(db: Session, vendor_id: int, is_active: bool):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor:
        vendor.is_active = is_active
        db.commit()
        db.refresh(vendor)
    return vendor

def delete_vendor_admin(db: Session, vendor_id: int):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor:
        p_ids = [p.id for p in db.query(Product).filter(Product.vendor_id == vendor_id).all()]
        if p_ids:
            db.query(Review).filter(Review.product_id.in_(p_ids)).delete(synchronize_session=False)
            db.query(Transaction).filter(Transaction.product_id.in_(p_ids)).delete(synchronize_session=False)
            db.query(Product).filter(Product.vendor_id == vendor_id).delete(synchronize_session=False)
        db.delete(vendor)
        db.commit()
        return True
    return False
