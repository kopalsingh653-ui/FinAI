from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# INITIALISE DATABASE
# ============================================================

def init_db():

    from app.database import models

    Base.metadata.create_all(bind=engine)

    print("FinAI database initialised successfully.")