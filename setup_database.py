"""
Database setup script for CargoOpt
Creates all database tables and initializes the system
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import create_app
from backend.config.database import db_manager


def init_database():
    """Initialize the database with tables"""
    print("\n" + "="*50)
    print("CargoOpt - Database Setup")
    print("="*50 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create database if it doesn't exist
            print("Creating database...")
            db_manager.create_database()
            print("✓ Database created/verified successfully!")
            
            # Initialize tables
            print("\nInitializing database tables...")
            db_manager.init_database()
            print("✓ Database tables created successfully!")
            
            print("\n" + "="*50)
            print("Database setup complete!")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during database setup: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def reset_database():
    """Drop all tables and recreate them (WARNING: Deletes all data)"""
    print("\n" + "="*50)
    print("CargoOpt - Database Reset")
    print("="*50 + "\n")
    
    confirm = input("⚠️  WARNING: This will delete ALL data. Type 'YES' to confirm: ")
    
    if confirm == 'YES':
        app = create_app()
        
        with app.app_context():
            try:
                print("\nResetting database...")
                db_manager.reset_database()
                print("✓ Database reset complete!")
                
                print("\nInitializing fresh tables...")
                db_manager.init_database()
                print("✓ Database reinitialized successfully!")
                
            except Exception as e:
                print(f"\n✗ Error during database reset: {str(e)}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    else:
        print("Database reset cancelled.")


def test_connection():
    """Test database connection"""
    print("\n" + "="*50)
    print("CargoOpt - Database Connection Test")
    print("="*50 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            if db_manager.test_connection():
                print("✓ Database connection successful!")
            else:
                print("✗ Database connection failed!")
        except Exception as e:
            print(f"✗ Error testing connection: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("\nSelect an option:")
    print("1. Initialize database (first time setup)")
    print("2. Reset database (WARNING: Deletes all data)")
    print("3. Test database connection")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        init_database()
    elif choice == '2':
        reset_database()
    elif choice == '3':
        test_connection()
    else:
        print("Invalid choice. Exiting...")