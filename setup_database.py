"""
Database Setup Script for CargoOpt
Handles database initialization, reset, and testing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging

logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database with all tables"""
    print("\nCreating database...")
    try:
        from backend.main import create_app
        from backend.models.base import Base
        
        # Import all models to register them with Base
        from backend.models.db_models import (
            ContainerDB, ItemDB, VesselDB, StowagePlanDB, 
            StowagePositionDB, UserDB, OptimizationRunDB
        )
        
        app = create_app()
        with app.app_context():
            # Get database manager from app
            db_manager = app.config.get('db_manager') or app.extensions.get('db_manager')
            
            if not db_manager:
                # Fallback: create engine directly
                from backend.config.database import DatabaseManager
                db_manager = DatabaseManager()
            
            # Create all tables using SQLAlchemy Base metadata
            engine = db_manager.engine
            Base.metadata.create_all(bind=engine)
            
            print("✓ Database tables created successfully!")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n✓ Created {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")
                
            return True
            
    except Exception as e:
        print(f"✗ Error during database setup: {e}")
        import traceback
        traceback.print_exc()
        return False


def reset_database():
    """Drop all tables and recreate them (WARNING: Deletes all data)"""
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != 'YES':
        print("Reset cancelled.")
        return False
    
    print("\nResetting database...")
    try:
        from backend.main import create_app
        from backend.models.base import Base
        
        # Import all models
        from backend.models.db_models import (
            ContainerDB, ItemDB, VesselDB, StowagePlanDB, 
            StowagePositionDB, UserDB, OptimizationRunDB
        )
        
        app = create_app()
        with app.app_context():
            # Get database manager
            db_manager = app.config.get('db_manager') or app.extensions.get('db_manager')
            
            if not db_manager:
                from backend.config.database import DatabaseManager
                db_manager = DatabaseManager()
            
            engine = db_manager.engine
            
            # Drop all tables
            Base.metadata.drop_all(bind=engine)
            print("✓ Dropped all existing tables")
            
            # Recreate all tables
            Base.metadata.create_all(bind=engine)
            print("✓ Recreated all tables")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n✓ Database reset complete. {len(tables)} tables created:")
            for table in sorted(tables):
                print(f"  - {table}")
                
            return True
            
    except Exception as e:
        print(f"✗ Error during database reset: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from backend.main import create_app
        
        app = create_app()
        with app.app_context():
            # Get database manager
            db_manager = app.config.get('db_manager') or app.extensions.get('db_manager')
            
            if not db_manager:
                from backend.config.database import DatabaseManager
                db_manager = DatabaseManager()
            
            # Try a simple query
            with db_manager.get_session() as session:
                result = session.execute("SELECT 1")
                result.fetchone()
                
            print("✓ Database connection successful!")
            
            # Show database info
            from sqlalchemy import inspect
            inspector = inspect(db_manager.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n✓ Found {len(tables)} existing tables:")
                for table in sorted(tables):
                    # Get row count
                    with db_manager.get_session() as session:
                        try:
                            count = session.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                            print(f"  - {table} ({count} rows)")
                        except:
                            print(f"  - {table}")
            else:
                print("\n⚠️  No tables found. Run option 1 to initialize the database.")
                
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def seed_sample_data():
    """Add sample data for testing"""
    print("\nAdding sample data...")
    try:
        from backend.main import create_app
        from backend.models.db_models import (
            ContainerDB, VesselDB, ContainerTypeEnum, VesselTypeEnum
        )
        
        app = create_app()
        with app.app_context():
            # Get database manager
            db_manager = app.config.get('db_manager') or app.extensions.get('db_manager')
            
            if not db_manager:
                from backend.config.database import DatabaseManager
                db_manager = DatabaseManager()
            
            with db_manager.get_session() as session:
                # Check if data already exists
                existing_containers = session.query(ContainerDB).count()
                if existing_containers > 0:
                    print(f"⚠️  Database already has {existing_containers} containers.")
                    confirm = input("Add more sample data anyway? (yes/no): ")
                    if confirm.lower() != 'yes':
                        print("Cancelled.")
                        return False
                
                # Add sample containers
                containers = [
                    ContainerDB(
                        container_id="CNT-001",
                        name="20ft Standard Container",
                        container_type=ContainerTypeEnum.STANDARD_20,
                        length=5898, width=2352, height=2393,
                        max_weight=28180, tare_weight=2300
                    ),
                    ContainerDB(
                        container_id="CNT-002",
                        name="40ft High Cube",
                        container_type=ContainerTypeEnum.HIGH_CUBE_40,
                        length=12032, width=2352, height=2698,
                        max_weight=26560, tare_weight=3920
                    )
                ]
                
                # Add sample vessel
                vessel = VesselDB(
                    vessel_id="VSL-001",
                    name="MV Cargo Express",
                    vessel_type=VesselTypeEnum.FEEDER,
                    teu_capacity=2500,
                    max_weight_tons=30000,
                    length_m=185.0, width_m=28.0, draft_m=10.5,
                    bays=14, rows=7, tiers_above_deck=5, tiers_below_deck=6,
                    reefer_plugs=200
                )
                
                session.add_all(containers)
                session.add(vessel)
                session.commit()
                
                print(f"✓ Added {len(containers)} sample containers")
                print(f"✓ Added 1 sample vessel")
                
            return True
            
    except Exception as e:
        print(f"✗ Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main menu for database setup"""
    print("=" * 50)
    print("CargoOpt - Database Setup")
    print("=" * 50)
    
    print("\nSelect an option:")
    print("1. Initialize database (first time setup)")
    print("2. Reset database (WARNING: Deletes all data)")
    print("3. Test database connection")
    print("4. Add sample data")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        success = init_database()
    elif choice == '2':
        success = reset_database()
    elif choice == '3':
        success = test_connection()
    elif choice == '4':
        success = seed_sample_data()
    else:
        print("Invalid choice. Please run the script again.")
        return
    
    if success:
        print("\n✓ Operation completed successfully!")
    else:
        print("\n✗ Operation failed. Check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()