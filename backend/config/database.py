"""
CargoOpt Database Manager
Handles database connections, connection pooling, and database operations.
"""

import os
import psycopg2
from psycopg2 import pool, extras, sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
import threading
from functools import wraps

from backend.config.settings import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database connection manager with connection pooling.
    Provides thread-safe database operations.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for database manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database manager."""
        if self._initialized:
            return
            
        self._pool = None
        self._config = None
        self._initialized = True
    
    def init_app(self, app):
        """
        Initialize database manager with Flask app.
        
        Args:
            app: Flask application instance
        """
        self._config = app.config
        self._create_pool()
    
    def _create_pool(self):
        """Create the connection pool."""
        try:
            self._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self._config.get('DB_POOL_SIZE', Config.DB_POOL_SIZE),
                host=self._config.get('DB_HOST', Config.DB_HOST),
                port=self._config.get('DB_PORT', Config.DB_PORT),
                database=self._config.get('DB_NAME', Config.DB_NAME),
                user=self._config.get('DB_USER', Config.DB_USER),
                password=self._config.get('DB_PASSWORD', Config.DB_PASSWORD),
                cursor_factory=extras.RealDictCursor
            )
            logger.info("Database connection pool created successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a database connection from the pool.
        
        Yields:
            psycopg2 connection object
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """
        Context manager for getting a database cursor.
        
        Args:
            commit: Whether to commit the transaction automatically
            
        Yields:
            psycopg2 cursor object
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """
        Test if the database connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def check_tables_exist(self) -> bool:
        """
        Check if required tables exist in the database.
        
        Returns:
            True if all required tables exist
        """
        required_tables = [
            'users', 'containers', 'items', 'optimizations',
            'placements', 'configurations'
        ]
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                existing = {row['table_name'] for row in cursor.fetchall()}
                return all(t in existing for t in required_tables)
        except Exception as e:
            logger.error(f"Table check failed: {e}")
            return False
    
    def execute(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return None
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """
        Execute a query and return single result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Result dictionary or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchone()
            return None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of rows affected
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def insert(self, table: str, data: Dict[str, Any], returning: str = 'id') -> Any:
        """
        Insert a row into a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs
            returning: Column to return after insert
            
        Returns:
            Value of returning column
        """
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['%s'] * len(values))
        cols = ', '.join(columns)
        
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        if returning:
            query += f" RETURNING {returning}"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            if returning:
                result = cursor.fetchone()
                return result[returning] if result else None
            return cursor.rowcount
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, where_params: tuple) -> int:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs to update
            where: WHERE clause (without 'WHERE')
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of rows affected
        """
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + list(where_params)
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount
    
    def delete(self, table: str, where: str, where_params: tuple) -> int:
        """
        Delete rows from a table.
        
        Args:
            table: Table name
            where: WHERE clause (without 'WHERE')
            where_params: Parameters for WHERE clause
            
        Returns:
            Number of rows affected
        """
        query = f"DELETE FROM {table} WHERE {where}"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, where_params)
            return cursor.rowcount
    
    def find_by_id(self, table: str, id_value: Any, id_column: str = 'id') -> Optional[Dict]:
        """
        Find a row by its ID.
        
        Args:
            table: Table name
            id_value: ID value to search for
            id_column: Name of ID column
            
        Returns:
            Result dictionary or None
        """
        query = f"SELECT * FROM {table} WHERE {id_column} = %s"
        return self.execute_one(query, (id_value,))
    
    def find_all(self, table: str, where: str = None, 
                 where_params: tuple = None, order_by: str = None,
                 limit: int = None, offset: int = None) -> List[Dict]:
        """
        Find all rows matching criteria.
        
        Args:
            table: Table name
            where: Optional WHERE clause
            where_params: Parameters for WHERE clause
            order_by: Optional ORDER BY clause
            limit: Optional LIMIT
            offset: Optional OFFSET
            
        Returns:
            List of result dictionaries
        """
        query = f"SELECT * FROM {table}"
        params = []
        
        if where:
            query += f" WHERE {where}"
            params.extend(where_params or [])
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if offset:
            query += f" OFFSET {offset}"
        
        return self.execute(query, tuple(params)) or []
    
    def count(self, table: str, where: str = None, where_params: tuple = None) -> int:
        """
        Count rows in a table.
        
        Args:
            table: Table name
            where: Optional WHERE clause
            where_params: Parameters for WHERE clause
            
        Returns:
            Row count
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        
        if where:
            query += f" WHERE {where}"
        
        result = self.execute_one(query, where_params)
        return result['count'] if result else 0
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status.
        
        Returns:
            Dictionary with pool statistics
        """
        if not self._pool:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'active',
            'min_connections': self._pool.minconn,
            'max_connections': self._pool.maxconn
        }


class Transaction:
    """
    Context manager for handling database transactions.
    Provides automatic commit/rollback functionality.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize transaction.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """Begin transaction."""
        self.conn = self.db_manager._pool.getconn()
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End transaction with commit or rollback."""
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                logger.error(f"Transaction rolled back: {exc_val}")
        finally:
            self.cursor.close()
            self.db_manager._pool.putconn(self.conn)
        
        return False  # Don't suppress exceptions
    
    def execute(self, query: str, params: tuple = None):
        """Execute query within transaction."""
        self.cursor.execute(query, params)
        return self.cursor
    
    def fetchone(self):
        """Fetch one result."""
        return self.cursor.fetchone()
    
    def fetchall(self):
        """Fetch all results."""
        return self.cursor.fetchall()


def with_transaction(func):
    """
    Decorator for wrapping a function in a database transaction.
    
    Usage:
        @with_transaction
        def my_function(transaction, ...):
            transaction.execute("INSERT INTO ...")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Transaction(db_manager) as transaction:
            return func(transaction, *args, **kwargs)
    return wrapper


# Global database manager instance
db_manager = DatabaseManager()