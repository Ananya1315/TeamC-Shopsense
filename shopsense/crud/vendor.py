from sqlalchemy.orm import Session
from sqlalchemy import func
import hashlib
from models import Vendor
from schemas.vendor import VendorCreate, VendorLogin

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    # Verify SHA-256 hash or exact match
    return hash_password(plain_password) == hashed_password or plain_password == hashed_password

def create_vendor(db: Session, vendor: VendorCreate):
    clean_email = vendor.email.lower().strip()
    pwd_hash = hash_password(vendor.password)
    
    new_vendor = Vendor(
        name=vendor.name.strip(), # Store Name
        owner_name=(vendor.owner_name or vendor.name).strip(), # Owner Name
        email=clean_email,
        phone=vendor.phone.strip(),
        password_hash=pwd_hash,
        is_active=True
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor

def get_vendors(db: Session):
    return db.query(Vendor).order_by(Vendor.id.asc()).all()

def get_vendor_by_email(db: Session, email: str):
    if not email:
        return None
    clean_email = email.lower().strip()
    return db.query(Vendor).filter(func.lower(Vendor.email) == clean_email).first()

def authenticate_vendor(db: Session, login_data: VendorLogin):
    clean_email = login_data.email.lower().strip()
    vendor = get_vendor_by_email(db, clean_email)
    if not vendor:
        return None

    if vendor.is_active is False:
        return None

    # Upgrade empty/default legacy passwords on first login
    if not vendor.password_hash or vendor.password_hash in ["", "password123"]:
        vendor.password_hash = hash_password(login_data.password)
        db.commit()
        db.refresh(vendor)
        return vendor

    # Verify password hash
    if not verify_password(login_data.password, vendor.password_hash):
        return None

    return vendor