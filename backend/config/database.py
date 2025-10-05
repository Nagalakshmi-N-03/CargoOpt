"""
Database Configuration and Connection Management
Database setup for CargoOpt using SQLAlchemy and asyncpg
"""

import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import MetaData

from backend.config.settings import get_settings

# Get settings
settings = get_settings()

# Configure logging
logger = logging.getLogger(__name__)

# Create shared declarative base for all models - THIS IS THE KEY FIX
Base = declarative_base()

# Database configuration
class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = settings.database_url
        self.echo = settings.debug
        self.pool_size = 20
        self.max_overflow = 30
        
        # Convert postgresql:// to postgresql+asyncpg:// for async operations
        if self.database_url.startswith("postgresql://"):
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        else:
            self.async_database_url = self.database_url

# Create database config instance
db_config = DatabaseConfig()

# Create async engine
engine = create_async_engine(
    db_config.async_database_url,
    echo=db_config.echo,
    poolclass=NullPool,  # Use NullPool for better async performance
    future=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Database metadata
metadata = MetaData()

async def init_db():
    """
    Initialize database connection and create tables if needed
    """
    try:
        # Import models to ensure they are registered with SQLAlchemy
        from backend.api import models
        from backend.models import container, vessel, stowage_plan
        
        # Create all tables using Base metadata
        async with engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)  # Uncomment for development
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

async def get_db():
    """
    Dependency function to get database session
    Use with FastAPI Depends()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()

async def test_connection():
    """
    Test database connection
    """
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Database connection successful: {version}")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

async def close_connection():
    """
    Close database connection
    """
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")

# Database health check
async def check_database_health() -> dict:
    """
    Check database health and return status information
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Test basic query
            await session.execute(text("SELECT 1"))
            
            # Get database size and connection info
            result = await session.execute(text("""
                SELECT 
                    current_database() as database,
                    version() as version,
                    pg_database_size(current_database()) as size_bytes,
                    (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) as active_connections
            """))
            
            db_info = result.fetchone()
            
            return {
                "status": "healthy",
                "database": db_info[0],
                "version": db_info[1],
                "size_bytes": db_info[2],
                "active_connections": db_info[3],
                "timestamp": "now()"  # Would use actual timestamp in production
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }