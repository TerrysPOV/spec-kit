"""
Database Connection and Session Management

Async SQLAlchemy setup with connection pooling, session management, and utilities.
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_resume"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    # AsyncPG specific options
    pool_size=10,  # Number of persistent connections
    max_overflow=20,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL query logging in development
    future=True,  # Use SQLAlchemy 2.0 style
    # Connection arguments for asyncpg
    connect_args={
        "server_settings": {
            "jit": "off"  # Disable JIT for better async performance
        }
    } if DATABASE_URL.startswith("postgresql") else {}
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent lazy loading after commit
    autoflush=False,  # Manual control over when to flush
)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session

    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session without auto-commit (for read operations)

    Usage for read-only operations where you don't want auto-commit
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            # Import models to ensure they are registered
            from .models import Base
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

async def drop_tables():
    """Drop all database tables (for testing)"""
    try:
        async with engine.begin() as conn:
            from .models import Base
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

async def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        async with async_session_factory() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            await result.fetchone()
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Health check function for FastAPI
async def database_health_check() -> dict:
    """Database health check for monitoring"""
    is_connected = await check_database_connection()

    return {
        "database": {
            "connected": is_connected,
            "url": DATABASE_URL.replace(
                DATABASE_URL.split("@")[0].split("//")[1].split(":")[1] if "@" in DATABASE_URL else "postgres",
                "***"
            ) if is_connected else "disconnected"
        }
    }

# Utility functions for common database operations
async def get_or_create(session: AsyncSession, model, **kwargs):
    """Get existing record or create new one"""
    instance = await session.get(model, kwargs.get('id'))
    if instance:
        return instance

    instance = model(**kwargs)
    session.add(instance)
    await session.flush()  # Get the ID without committing
    return instance

async def safe_commit(session: AsyncSession) -> bool:
    """Safely commit session with error handling"""
    try:
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to commit session: {e}")
        await session.rollback()
        return False

# Cleanup function
async def close_database_connection():
    """Close database connection pool"""
    try:
        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

# Development helper
async def reset_database():
    """Reset database (drop and recreate all tables)"""
    logger.warning("Resetting database - this will delete all data!")
    await drop_tables()
    await create_tables()
    logger.info("Database reset complete")