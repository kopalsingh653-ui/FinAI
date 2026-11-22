import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

DATABASE_DIR = os.path.join(BASE_DIR, "data", "database")

os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'finai.db')}"

# --------------------------------------------------
# SQLALCHEMY ENGINE
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# --------------------------------------------------
# DATABASE SESSION
# --------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# BASE MODEL
# --------------------------------------------------

Base = declarative_base()

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():
    """
    Initialize all database tables.
    Import models before creating tables.
    """

    from app.database import models

    Base.metadata.create_all(bind=engine)

    print("FinAI database initialized successfully!")


# --------------------------------------------------
# DATABASE DEPENDENCY
# --------------------------------------------------

def get_db():
    """
    Create and manage database sessions.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# --------------------------------------------------
# DATABASE HEALTH CHECK
# --------------------------------------------------

def check_database():
    """
    Check whether the database connection is active.
    """

    try:
        from sqlalchemy import text

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
