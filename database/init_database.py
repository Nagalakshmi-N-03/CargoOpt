"""
CargoOpt Database Initialization Script
Initializes the PostgreSQL database with schema and sample data.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from pathlib import Path
from typing import Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles database initialization and setup."""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 5432,
        database: str = 'cargoopt',
        user: str = 'postgres',
        password: str = '',
        admin_database: str = 'postgres'
    ):
        """
        Initialize database initializer.
        
        Args:
            host: Database host
            port: Database port
            database: Target database name
            user: Database user
            password: Database password
            admin_database: Admin database for creating new database
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.admin_database = admin_database
        
        # Get script directory
        self.script_dir = Path(__file__).parent
        self.schema_file = self.script_dir / 'schema.sql'
        self.sample_data_file = self.script_dir / 'sample_data.sql'
    
    def get_connection_params(self, database: Optional[str] = None) -> dict:
        """Get connection parameters dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'database': database or self.database,
            'user': self.user,
            'password': self.password
        }
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing database connection...")
            conn = psycopg2.connect(**self.get_connection_params(self.admin_database))
            conn.close()
            logger.info("✓ Database connection successful")
            return True
        except psycopg2.Error as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
    
    def database_exists(self) -> bool:
        """
        Check if target database exists.
        
        Returns:
            True if database exists
        """
        try:
            conn = psycopg2.connect(**self.get_connection_params(self.admin_database))
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database,)
            )
            
            exists = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            
            return exists
        except psycopg2.Error as e:
            logger.error(f"Error checking database existence: {e}")
            return False
    
    def create_database(self) -> bool:
        """
        Create the target database.
        
        Returns:
            True if database created successfully
        """
        try:
            logger.info(f"Creating database '{self.database}'...")
            
            conn = psycopg2.connect(**self.get_connection_params(self.admin_database))
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database))
            )
            
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Database '{self.database}' created successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"✗ Failed to create database: {e}")
            return False
    
    def drop_database(self) -> bool:
        """
        Drop the target database.
        
        Returns:
            True if database dropped successfully
        """
        try:
            logger.warning(f"Dropping database '{self.database}'...")
            
            conn = psycopg2.connect(**self.get_connection_params(self.admin_database))
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Terminate existing connections
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{self.database}'
                AND pid <> pg_backend_pid()
            """)
            
            # Drop database
            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(self.database))
            )
            
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Database '{self.database}' dropped successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"✗ Failed to drop database: {e}")
            return False
    
    def run_sql_file(self, filepath: Path) -> bool:
        """
        Execute SQL file.
        
        Args:
            filepath: Path to SQL file
            
        Returns:
            True if executed successfully
        """
        if not filepath.exists():
            logger.error(f"✗ SQL file not found: {filepath}")
            return False
        
        try:
            logger.info(f"Executing SQL file: {filepath.name}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            conn = psycopg2.connect(**self.get_connection_params())
            cursor = conn.cursor()
            
            # Execute SQL
            cursor.execute(sql_content)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✓ SQL file executed successfully: {filepath.name}")
            return True
        except psycopg2.Error as e:
            logger.error(f"✗ Failed to execute SQL file: {e}")
            return False
    
    def create_schema(self) -> bool:
        """
        Create database schema.
        
        Returns:
            True if schema created successfully
        """
        logger.info("Creating database schema...")
        return self.run_sql_file(self.schema_file)
    
    def load_sample_data(self) -> bool:
        """
        Load sample data into database.
        
        Returns:
            True if data loaded successfully
        """
        logger.info("Loading sample data...")
        return self.run_sql_file(self.sample_data_file)
    
    def verify_installation(self) -> bool:
        """
        Verify database installation.
        
        Returns:
            True if verification successful
        """
        try:
            logger.info("Verifying database installation...")
            
            conn = psycopg2.connect(**self.get_connection_params())
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'users', 'containers', 'items', 'optimizations', 'placements',
                'vessels', 'vessel_compartments', 'stowage_plans', 'stowage_positions',
                'configurations', 'audit_logs'
            ]
            
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                logger.warning(f"Missing tables: {', '.join(missing_tables)}")
            else:
                logger.info("✓ All expected tables present")
            
            # Check row counts
            logger.info("\nTable row counts:")
            for table in sorted(tables):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"  {table}: {count} rows")
            
            cursor.close()
            conn.close()
            
            logger.info("\n✓ Database verification complete")
            return True
        except psycopg2.Error as e:
            logger.error(f"✗ Verification failed: {e}")
            return False
    
    def initialize(
        self,
        drop_existing: bool = False,
        load_sample: bool = True,
        verify: bool = True
    ) -> bool:
        """
        Complete database initialization.
        
        Args:
            drop_existing: Drop existing database if it exists
            load_sample: Load sample data
            verify: Verify installation after setup
            
        Returns:
            True if initialization successful
        """
        logger.info("=" * 70)
        logger.info("CargoOpt Database Initialization")
        logger.info("=" * 70)
        
        # Test connection
        if not self.test_connection():
            return False
        
        # Check if database exists
        db_exists = self.database_exists()
        
        if db_exists:
            if drop_existing:
                logger.warning(f"Database '{self.database}' already exists and will be dropped!")
                if not self.drop_database():
                    return False
            else:
                logger.error(f"Database '{self.database}' already exists. Use --drop to drop it first.")
                return False
        
        # Create database
        if not self.create_database():
            return False
        
        # Create schema
        if not self.create_schema():
            return False
        
        # Load sample data
        if load_sample:
            if not self.load_sample_data():
                logger.warning("Failed to load sample data, but schema is created")
        
        # Verify installation
        if verify:
            if not self.verify_installation():
                logger.warning("Verification failed, but database may still be usable")
        
        logger.info("\n" + "=" * 70)
        logger.info("Database initialization complete!")
        logger.info("=" * 70)
        logger.info(f"\nDatabase: {self.database}")
        logger.info(f"Host: {self.host}:{self.port}")
        logger.info(f"User: {self.user}")
        logger.info("\nYou can now start the application.")
        
        return True


def main():
    """Main entry point for database initialization."""
    parser = argparse.ArgumentParser(
        description='Initialize CargoOpt PostgreSQL database'
    )
    
    parser.add_argument(
        '--host',
        default=os.getenv('DB_HOST', 'localhost'),
        help='Database host (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=int(os.getenv('DB_PORT', 5432)),
        help='Database port (default: 5432)'
    )
    
    parser.add_argument(
        '--database',
        default=os.getenv('DB_NAME', 'cargoopt'),
        help='Database name (default: cargoopt)'
    )
    
    parser.add_argument(
        '--user',
        default=os.getenv('DB_USER', 'postgres'),
        help='Database user (default: postgres)'
    )
    
    parser.add_argument(
        '--password',
        default=os.getenv('DB_PASSWORD', ''),
        help='Database password'
    )
    
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Drop existing database if it exists'
    )
    
    parser.add_argument(
        '--no-sample-data',
        action='store_true',
        help='Do not load sample data'
    )
    
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip verification after setup'
    )
    
    args = parser.parse_args()
    
    # Check for password
    if not args.password:
        logger.warning("No database password provided. Using empty password.")
        logger.warning("Set DB_PASSWORD environment variable or use --password flag.")
    
    # Initialize database
    initializer = DatabaseInitializer(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )
    
    success = initializer.initialize(
        drop_existing=args.drop,
        load_sample=not args.no_sample_data,
        verify=not args.no_verify
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()