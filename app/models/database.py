"""
Database Models - Simplified
File: app/models/database.py

Simplified database models without async requirements.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger(__name__, "database")

# Create declarative base
Base = declarative_base()

# Simple SQLite engine (synchronous)
DATABASE_URL = "sqlite:///data/trading_bot.db"

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("[OK] Database models initialized")
    
except Exception as e:
    logger.error(f"[ERROR] Database initialization failed: {e}")
    # Create dummy objects so imports don't fail
    engine = None
    SessionLocal = None


def get_db_session():
    """Get database session."""
    if SessionLocal:
        return SessionLocal()
    return None


def create_tables():
    """Create database tables."""
    try:
        if engine:
            Base.metadata.create_all(bind=engine)
            logger.info("[OK] Database tables created")
            return True
        else:
            logger.warning("[WARN] No engine available for table creation")
            return False
    except Exception as e:
        logger.error(f"[ERROR] Table creation failed: {e}")
        return False
