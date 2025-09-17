"""
Database Connection Management for Campaign Data Foundation

This module provides:
1. SQLAlchemy engine and session management
2. Database URL configuration for different environments
3. Connection pooling for performance
4. Test database isolation support

Educational Focus: Shows proper database connection patterns for FastAPI
applications with PostgreSQL production and SQLite testing support.
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/ppv_system_health"
)

# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_campaign_data.db"
)

# Determine if we're in testing mode
TESTING = os.getenv("TESTING", "0") == "1"

# Use appropriate database URL based on environment
if TESTING:
    DATABASE_URL = TEST_DATABASE_URL
    logger.info(f"Using test database: {DATABASE_URL}")
else:
    logger.info(f"Using production database: {DATABASE_URL}")

# Engine configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for testing
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,  # Connection pool size
        max_overflow=30,  # Additional connections beyond pool_size
        echo=False  # Set to True for SQL debugging
    )

# Session configuration
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Used by FastAPI dependency injection system.
    Ensures proper session cleanup after request completion.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.

    Used during application startup and testing setup.
    Only creates tables that don't already exist.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.

    Used primarily for testing cleanup.
    DANGER: This will destroy all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


# Database event listeners for enhanced functionality
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set SQLite pragmas for better performance and foreign key support.

    Only applies to SQLite databases (testing).
    """
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")
        # Enable Write-Ahead Logging for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode for better performance in testing
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


# Connection health check
def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is working, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


# Database initialization for applications
def init_db():
    """
    Initialize database with tables and basic setup.

    Used during application startup.
    """
    logger.info("Initializing database...")

    # Check connection first
    if not check_database_connection():
        raise ConnectionError("Cannot connect to database")

    # Create tables
    create_tables()

    logger.info("Database initialization completed")


# Clean shutdown
def close_db():
    """
    Clean database shutdown.

    Used during application shutdown to properly close connections.
    """
    logger.info("Closing database connections...")
    engine.dispose()
    logger.info("Database connections closed")