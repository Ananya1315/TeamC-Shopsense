from sqlalchemy.orm import Session
from models import Product
from schemas.product import ProductCreate, ProductUpdate

def create_product(db: Session, product: ProductCreate, vendor_id: int):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category=product.category,
        tags=product.tags,
        image_url=product.image_url,
        vendor_id=vendor_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def get_products_by_vendor(db: Session, vendor_id: int):
    return db.query(Product).filter(Product.vendor_id == vendor_id).order_by(Product.id.desc()).all()

def get_all_products(db: Session):
    return db.query(Product).order_by(Product.id.desc()).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return None
    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return False
    db.delete(db_product)
    db.commit()
    return True
