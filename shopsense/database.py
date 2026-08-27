from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
        engine = create_engine(DATABASE_URL)
        # Test connection
        with engine.connect() as conn:
            pass
    else:
        raise Exception("Use SQLite fallback")
except Exception as e:
    print(f"PostgreSQL connection unavailable ({e}). Falling back to SQLite database.")
    DATABASE_URL = "sqlite:///./shopsense.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()