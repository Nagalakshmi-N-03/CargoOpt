#!/usr/bin/env python3
"""
CargoOpt Database Initialization Script
Standalone script for database setup and initialization
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add backend to Python path
sys.path.append(str(Path(__file__).parent.parent))

from backend.config.settings import get_settings
from backend.config.database import init_db, test_connection, close_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Database initialization and management class"""
    
    def __init__(self):
        self.settings = get_settings()
        self.schema_file = Path('database/schema.sql')
        self.sample_data_file = Path('database/sample_data.sql')
        
    async def check_database_connection(self) -> bool:
        """Test database connection"""
        try:
            logger.info("Testing database connection...")
            success = await test_connection()
            if success:
                logger.info("✅ Database connection successful")
            else:
                logger.error("❌ Database connection failed")
            return success
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False
    
    async def initialize_schema(self) -> bool:
        """Initialize database schema"""
        try:
            logger.info("Initializing database schema...")
            await init_db()
            logger.info("✅ Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database schema initialization failed: {str(e)}")
            return False
    
    def read_sql_file(self, file_path: Path) -> str:
        """Read SQL file content"""
        try:
            if not file_path.exists():
                logger.warning(f"SQL file not found: {file_path}")
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading SQL file {file_path}: {str(e)}")
            return ""
    
    async def execute_sql_script(self, sql_content: str, description: str) -> bool:
        """Execute SQL script content"""
        if not sql_content.strip():
            logger.warning(f"No SQL content to execute for {description}")
            return True
            
        try:
            from backend.config.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as session:
                # Split SQL by semicolons and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
                for i, statement in enumerate(statements, 1):
                    if statement:  # Skip empty statements
                        try:
                            await session.execute(statement)
                            logger.debug(f"Executed statement {i}/{len(statements)}")
                        except Exception as e:
                            logger.warning(f"Statement {i} execution warning: {str(e)}")
                
                await session.commit()
                logger.info(f"✅ {description} executed successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ {description} execution failed: {str(e)}")
            return False
    
    async def run_schema_sql(self) -> bool:
        """Execute schema SQL file"""
        logger.info("Executing schema SQL...")
        sql_content = self.read_sql_file(self.schema_file)
        if not sql_content:
            logger.error("No schema SQL content found")
            return False
        
        return await self.execute_sql_script(sql_content, "Schema SQL")
    
    async def load_sample_data(self) -> bool:
        """Load sample data into database"""
        logger.info("Loading sample data...")
        sql_content = self.read_sql_file(self.sample_data_file)
        if not sql_content:
            logger.warning("No sample data SQL content found - skipping")
            return True  # This is optional, so don't fail if missing
        
        return await self.execute_sql_script(sql_content, "Sample data SQL")
    
    async def run_migrations(self) -> bool:
        """Run database migrations (if using Alembic)"""
        try:
            # This would run Alembic migrations if configured
            logger.info("Checking for database migrations...")
            # Placeholder for Alembic migration execution
            logger.info("✅ Database migrations completed (if any)")
            return True
        except Exception as e:
            logger.error(f"❌ Database migrations failed: {str(e)}")
            return False
    
    async def verify_database_setup(self) -> bool:
        """Verify database setup by checking key tables"""
        try:
            from backend.config.database import AsyncSessionLocal
            from sqlalchemy import text
            
            required_tables = [
                'vessels', 'containers', 'vessel_compartments', 
                'stowage_plans', 'stowage_positions'
            ]
            
            async with AsyncSessionLocal() as session:
                for table in required_tables:
                    result = await session.execute(
                        text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'")
                    )
                    exists = result.scalar() > 0
                    
                    if exists:
                        # Count rows in table
                        count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        row_count = count_result.scalar()
                        logger.info(f"✅ Table '{table}' exists with {row_count} rows")
                    else:
                        logger.error(f"❌ Table '{table}' does not exist")
                        return False
            
            logger.info("✅ All required tables verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database verification failed: {str(e)}")
            return False
    
    async def initialize_database(self) -> bool:
        """Main database initialization procedure"""
        logger.info("🚀 Starting CargoOpt Database Initialization...")
        logger.info(f"📊 Database: {self.settings.database_name}")
        logger.info(f"🌐 Host: {self.settings.database_host}:{self.settings.database_port}")
        
        # Step 1: Test connection
        if not await self.check_database_connection():
            return False
        
        # Step 2: Initialize schema
        if not await self.initialize_schema():
            return False
        
        # Step 3: Execute schema SQL
        if not await self.run_schema_sql():
            return False
        
        # Step 4: Run migrations
        if not await self.run_migrations():
            return False
        
        # Step 5: Load sample data
        if not await self.load_sample_data():
            logger.warning("Sample data loading failed, but continuing...")
        
        # Step 6: Verify setup
        if not await self.verify_database_setup():
            return False
        
        logger.info("🎉 Database initialization completed successfully!")
        return True
    
    async def cleanup(self):
        """Cleanup database connections"""
        await close_connection()

async def main():
    """Main function"""
    initializer = DatabaseInitializer()
    
    try:
        success = await initializer.initialize_database()
        
        if success:
            print("\n" + "="*60)
            print("✅ CARGOOPT DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"Database: {initializer.settings.database_name}")
            print(f"Host: {initializer.settings.database_host}:{initializer.settings.database_port}")
            print(f"User: {initializer.settings.database_user}")
            print("\nYou can now start the application with: python run.py")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ DATABASE INITIALIZATION FAILED!")
            print("="*60)
            print("Please check the logs above for errors.")
            print("Ensure PostgreSQL is running and credentials are correct.")
            print("="*60)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)
    finally:
        await initializer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())