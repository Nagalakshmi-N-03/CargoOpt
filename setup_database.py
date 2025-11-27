"""
CargoOpt Database Setup Script
Initialize, reset, and manage the database.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50)


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def init_database():
    """Initialize the database for the first time."""
    try:
        print("Creating database...")
        
        # Import after adding to path
        from sqlalchemy import create_engine
        from backend.config import get_database_url
        from backend.models.base import Base
        
        # Import all models to register them with Base
        from backend.models.db_models import (
            ContainerDB,
            ItemDB,
            VesselDB,
            StowagePlanDB,
            StowagePositionDB,
            UserDB,
            OptimizationRunDB
        )
        
        # Create engine
        db_url = get_database_url()
        engine = create_engine(db_url, echo=True)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print_success("Database initialized successfully!")
        print(f"Database location: {db_url}")
        
        return True
        
    except Exception as e:
        print_error(f"Error during database setup: {e}")
        import traceback
        traceback.print_exc()
        return False


def reset_database():
    """Reset the database (WARNING: Deletes all data)."""
    try:
        response = input("⚠️  WARNING: This will delete ALL data. Type 'YES' to confirm: ")
        if response != 'YES':
            print("Operation cancelled.")
            return False
        
        print("Resetting database...")
        
        from sqlalchemy import create_engine
        from backend.config import get_database_url
        from backend.models.base import Base
        
        # Import all models
        from backend.models.db_models import (
            ContainerDB,
            ItemDB,
            VesselDB,
            StowagePlanDB,
            StowagePositionDB,
            UserDB,
            OptimizationRunDB
        )
        
        db_url = get_database_url()
        engine = create_engine(db_url, echo=True)
        
        # Drop all tables
        Base.metadata.drop_all(engine)
        print_success("All tables dropped")
        
        # Recreate all tables
        Base.metadata.create_all(engine)
        print_success("All tables recreated")
        
        print_success("Database reset complete!")
        return True
        
    except Exception as e:
        print_error(f"Error during reset: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_connection():
    """Test database connection."""
    try:
        print("Testing database connection...")
        
        from sqlalchemy import create_engine, text
        from backend.config import get_database_url
        
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        # Try to connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print_success("Database connection successful!")
        print(f"Database: {db_url}")
        
        return True
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


def add_sample_data():
    """Add sample data to the database."""
    try:
        print("Adding sample data...")
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.config import get_database_url
        from backend.models.db_models import (
            ContainerDB,
            ItemDB,
            VesselDB,
            ContainerTypeEnum,
            ItemTypeEnum,
            VesselTypeEnum
        )
        from datetime import datetime
        
        db_url = get_database_url()
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Add sample containers
            containers = [
                ContainerDB(
                    container_id="CONT-001",
                    name="20ft Standard Container #1",
                    container_type=ContainerTypeEnum.STANDARD_20,
                    length=5898,
                    width=2352,
                    height=2393,
                    max_weight=28180,
                    tare_weight=2300,
                    is_active=True
                ),
                ContainerDB(
                    container_id="CONT-002",
                    name="40ft High Cube Container #1",
                    container_type=ContainerTypeEnum.HIGH_CUBE_40,
                    length=12032,
                    width=2352,
                    height=2698,
                    max_weight=26560,
                    tare_weight=3920,
                    is_active=True
                ),
                ContainerDB(
                    container_id="CONT-003",
                    name="20ft Refrigerated Container #1",
                    container_type=ContainerTypeEnum.REFRIGERATED_20,
                    length=5444,
                    width=2294,
                    height=2276,
                    max_weight=27400,
                    tare_weight=3080,
                    temperature_controlled=True,
                    min_temperature=-25.0,
                    max_temperature=25.0,
                    is_active=True
                )
            ]
            
            for container in containers:
                session.add(container)
            print_success(f"Added {len(containers)} sample containers")
            
            # Add sample items
            items = [
                ItemDB(
                    item_id="ITEM-001",
                    name="Standard Pallet",
                    item_type=ItemTypeEnum.STANDARD,
                    length=1200,
                    width=1000,
                    height=1500,
                    weight=500.0,
                    is_stackable=True
                ),
                ItemDB(
                    item_id="ITEM-002",
                    name="Fragile Electronics Box",
                    item_type=ItemTypeEnum.FRAGILE,
                    length=800,
                    width=600,
                    height=400,
                    weight=50.0,
                    is_fragile=True,
                    is_stackable=False
                ),
                ItemDB(
                    item_id="ITEM-003",
                    name="Perishable Food Crate",
                    item_type=ItemTypeEnum.PERISHABLE,
                    length=600,
                    width=400,
                    height=300,
                    weight=100.0,
                    is_stackable=True
                )
            ]
            
            for item in items:
                session.add(item)
            print_success(f"Added {len(items)} sample items")
            
            # Add sample vessels
            vessels = [
                VesselDB(
                    vessel_id="VESSEL-001",
                    name="MV Cargo Express",
                    vessel_type=VesselTypeEnum.FEEDER,
                    teu_capacity=1000,
                    max_weight_tons=12000,
                    length_m=135.0,
                    width_m=20.0,
                    draft_m=8.0,
                    bays=8,
                    rows=6,
                    tiers_above_deck=3,
                    tiers_below_deck=5,
                    reefer_plugs=50,
                    max_speed_knots=18.0,
                    is_active=True
                ),
                VesselDB(
                    vessel_id="VESSEL-002",
                    name="MV Pacific Star",
                    vessel_type=VesselTypeEnum.PANAMAX,
                    teu_capacity=4500,
                    max_weight_tons=52000,
                    length_m=294.0,
                    width_m=32.2,
                    draft_m=12.0,
                    bays=17,
                    rows=13,
                    tiers_above_deck=5,
                    tiers_below_deck=7,
                    reefer_plugs=300,
                    max_speed_knots=22.0,
                    is_active=True
                )
            ]
            
            for vessel in vessels:
                session.add(vessel)
            print_success(f"Added {len(vessels)} sample vessels")
            
            # Commit all changes
            session.commit()
            print_success("Sample data added successfully!")
            
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    except Exception as e:
        print_error(f"Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    print_header("CargoOpt - Database Setup")
    
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
        success = add_sample_data()
    else:
        print_error("Invalid choice!")
        return
    
    if success:
        print_success("\nOperation completed successfully!")
    else:
        print_error("\nOperation failed. Check the errors above.")


if __name__ == "__main__":
    main()