"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_safety.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and seed data if empty"""
    Base.metadata.create_all(bind=engine)
    
    # Check if database needs seeding
    db = SessionLocal()
    try:
        from app.models.transport import TransportRoute
        route_count = db.query(TransportRoute).count()
        if route_count == 0:
            print("Database is empty, seeding with initial data...")
            db.close()
            # Import and run seed function
            from app.seed_data import seed_database
            seed_database()
        else:
            db.close()
    except Exception as e:
        db.close()
        print(f"Note: Could not check/seed database: {e}")
