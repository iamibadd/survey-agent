import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

from models.base import Base


# ============================================================
# Load environment variables (from .env file)
# ============================================================
load_dotenv()

# Read database connection string from environment variable
DB_CONNECTION_STRING = os.getenv("DATABASE_URL")


# ============================================================
# Create a SQLAlchemy Engine
# ============================================================
# The engine is the starting point for any SQLAlchemy application.
# It manages connections to the database and handles SQL execution.
engine = create_engine(
    DB_CONNECTION_STRING,
    # Required for SQLite thread safety
    connect_args={"check_same_thread": False},
    pool_size=10,         # Maintain up to 10 persistent DB connections
    max_overflow=20,      # Allow up to 20 additional temporary connections if pool is full
    pool_timeout=60       # Wait up to 60 seconds before raising a timeout error
)


# ============================================================
# Dependency: Get a new DB session for each request
# ============================================================
def get_db():
    """
    Creates a scoped session for database operations.
    Automatically closes the connection after each request.
    """
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    db = SessionLocal()

    try:
        yield db  # Provide session to the request handler
    finally:
        db.close()  # Ensure session is closed even if an error occurs


# ============================================================
# Initialize database tables (called during app startup)
# ============================================================
def init_db():
    """
    Creates all tables defined in SQLAlchemy models (via Base.metadata).
    Should be run once at application startup.
    """
    Base.metadata.create_all(bind=engine)
