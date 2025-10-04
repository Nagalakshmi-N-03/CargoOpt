#!/usr/bin/env python3
"""
CargoOpt - Database Setup Script
Initializes the database with required tables and sample data
"""

import os
import sys
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.db_name = os.getenv('DATABASE_NAME', 'cargoopt')
        self.db_user = os.getenv('DATABASE_USER', 'cargoopt_user')
        self.db_password = os.getenv('DATABASE_PASSWORD')
        self.db_host = os.getenv('DATABASE_HOST', 'localhost')
        self.db_port = os.getenv('DATABASE_PORT', '5432')
        
    def get_connection(self, database=None):
        """Get database connection"""
        try:
            if database:
                conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password,
                    database=database
                )
            else:
                conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password
                )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def check_postgres_connection(self):
        """Check if PostgreSQL is running and accessible"""
        try:
            conn = self.get_connection('postgres')
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"Connected to PostgreSQL: {version[0]}")
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Cannot connect to PostgreSQL: {str(e)}")
            return False

    def database_exists(self):
        """Check if database already exists"""
        try:
            conn = self.get_connection(self.db_name)
            conn.close()
            return True
        except psycopg2.OperationalError:
            return False

    def create_database(self):
        """Create the database if it doesn't exist"""
        if self.database_exists():
            logger.info(f"Database '{self.db_name}' already exists")
            return True
            
        try:
            conn = self.get_connection('postgres')
            cur = conn.cursor()
            
            # Check if user exists, create if not
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (self.db_user,))
            if not cur.fetchone():
                logger.info(f"Creating database user '{self.db_user}'")
                cur.execute(f"CREATE USER {self.db_user} WITH PASSWORD '{self.db_password}'")
            
            # Create database
            logger.info(f"Creating database '{self.db_name}'")
            cur.execute(f"CREATE DATABASE {self.db_name} OWNER {self.db_user}")
            
            # Grant privileges
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_name} TO {self.db_user}")
            
            cur.close()
            conn.close()
            logger.info("Database created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {str(e)}")
            return False

    def run_schema_sql(self):
        """Execute the schema SQL file"""
        try:
            schema_file = os.path.join('database', 'schema.sql')
            if not os.path.exists(schema_file):
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            conn = self.get_connection(self.db_name)
            cur = conn.cursor()
            
            logger.info("Creating database tables...")
            cur.execute(schema_sql)
            
            cur.close()
            conn.close()
            logger.info("Database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create schema: {str(e)}")
            return False

    def load_sample_data(self):
        """Load sample data into the database"""
        try:
            sample_data_file = os.path.join('database', 'sample_data.sql')
            if not os.path.exists(sample_data_file):
                logger.warning(f"Sample data file not found: {sample_data_file}")
                return True
            
            with open(sample_data_file, 'r') as f:
                sample_sql = f.read()
            
            conn = self.get_connection(self.db_name)
            cur = conn.cursor()
            
            logger.info("Loading sample data...")
            cur.execute(sample_sql)
            
            cur.close()
            conn.close()
            logger.info("Sample data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load sample data: {str(e)}")
            return False

    def setup_database(self):
        """Main database setup procedure"""
        logger.info("Starting database setup...")
        
        # Check PostgreSQL connection
        if not self.check_postgres_connection():
            return False
        
        # Create database
        if not self.create_database():
            return False
        
        # Run schema
        if not self.run_schema_sql():
            return False
        
        # Load sample data
        if not self.load_sample_data():
            return False
        
        logger.info("Database setup completed successfully!")
        return True

def main():
    """Main function for database setup"""
    try:
        setup = DatabaseSetup()
        
        if setup.setup_database():
            logger.info("CargoOpt database is ready!")
            print("\n" + "="*50)
            print("✅ DATABASE SETUP COMPLETED SUCCESSFULLY!")
            print("="*50)
            print(f"Database: {setup.db_name}")
            print(f"Host: {setup.db_host}:{setup.db_port}")
            print(f"User: {setup.db_user}")
            print("You can now run the application with: python run.py")
            print("="*50)
        else:
            logger.error("Database setup failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()