from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'shopsense.db')}"
elif not (DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("sqlite")):
    raise ValueError(
        "DATABASE_URL must be a valid PostgreSQL or SQLite connection string. "
        "Example: postgresql://... or sqlite:///./shopsense.db"
    )

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()