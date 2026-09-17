from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import text
import os

from database import engine
from models import Base
from routers.vendor import router as vendor_router
from routers.admin import router as admin_router
from routers.product import router as product_router
from routers.analytics import router as analytics_router
from routers.customer import router as customer_router
from routers.websocket import router as websocket_router
from routers.ai import router as ai_router

Base.metadata.create_all(bind=engine)

# Auto-migrate missing columns for existing PostgreSQL tables if needed
with engine.connect() as conn:
    try:
        if conn.dialect.name == "postgresql":
            conn.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS password_hash VARCHAR DEFAULT '';"))
            conn.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS owner_name VARCHAR DEFAULT '';"))
            conn.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("ALTER TABLE vendors ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("CREATE TABLE IF NOT EXISTS customers (id SERIAL PRIMARY KEY, name VARCHAR, email VARCHAR UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"))
            conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS customer_id INTEGER REFERENCES customers(id);"))
            conn.commit()
    except Exception as e:
        print(f"Table auto-migration note: {e}")

app = FastAPI(title="ShopSense Multi-Vendor Commerce & Analytics Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vendor_router)
app.include_router(admin_router)
app.include_router(product_router)
app.include_router(analytics_router)
app.include_router(customer_router)
app.include_router(websocket_router)
app.include_router(ai_router)

# Mount frontend static directory
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir, exist_ok=True)

app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/")
def home():
    login_path = os.path.join(frontend_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return RedirectResponse(url="/frontend/login.html")