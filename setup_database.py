"""
Database setup script for the Real Estate Management System
Creates all database tables and optionally adds sample data
"""
import os
from app import create_app, db
from app.models import User, Property
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        # Create all database tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # Create default admin user
            print("\nCreating default admin user...")
            admin_user = User(
                username='admin',
                email='admin@realestate.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            
            try:
                db.session.commit()
                print("✓ Admin user created successfully!")
                print("\n" + "="*50)
                print("Default Admin Credentials:")
                print("Username: admin")
                print("Password: admin123")
                print("="*50)
                print("\n⚠️  IMPORTANT: Please change the admin password after first login!")
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error creating admin user: {str(e)}")
        else:
            print("\n✓ Admin user already exists.")
        
        # Ask if user wants to add sample data
        add_samples = input("\nDo you want to add sample properties? (y/n): ").strip().lower()
        
        if add_samples == 'y':
            add_sample_data()

def add_sample_data():
    """Add sample properties to the database"""
    app = create_app()
    
    with app.app_context():
        # Check if properties already exist
        if Property.query.count() > 0:
            print("Sample data already exists in the database.")
            return
        
        print("\nAdding sample properties...")
        
        sample_properties = [
            {
                'title': 'Luxury Downtown Apartment',
                'description': 'Beautiful modern apartment in the heart of downtown with stunning city views. Features include hardwood floors, stainless steel appliances, and floor-to-ceiling windows.',
                'price': 450000.00,
                'location': 'Downtown, City Center',
                'property_type': 'Apartment',
                'bedrooms': 2,
                'bathrooms': 2,
                'area': 1200,
                'is_available': True
            },
            {
                'title': 'Spacious Family Home',
                'description': 'Perfect family home with large backyard, modern kitchen, and great school district. Recently renovated with new roof and HVAC system.',
                'price': 650000.00,
                'location': 'Suburban Area, West Side',
                'property_type': 'House',
                'bedrooms': 4,
                'bathrooms': 3,
                'area': 2500,
                'is_available': True
            },
            {
                'title': 'Cozy Studio Apartment',
                'description': 'Affordable studio apartment perfect for young professionals. Close to public transportation, restaurants, and entertainment.',
                'price': 180000.00,
                'location': 'East End, Transit District',
                'property_type': 'Apartment',
                'bedrooms': 1,
                'bathrooms': 1,
                'area': 550,
                'is_available': True
            },
            {
                'title': 'Modern Commercial Office Space',
                'description': 'Prime commercial property in business district. Ideal for startups and small businesses. Includes parking and conference rooms.',
                'price': 850000.00,
                'location': 'Business District, North',
                'property_type': 'Commercial',
                'bedrooms': 0,
                'bathrooms': 4,
                'area': 3500,
                'is_available': True
            },
            {
                'title': 'Beachfront Condo',
                'description': 'Stunning beachfront condominium with panoramic ocean views. Resort-style amenities including pool, gym, and concierge service.',
                'price': 1200000.00,
                'location': 'Coastal Area, Beach Road',
                'property_type': 'Condo',
                'bedrooms': 3,
                'bathrooms': 2,
                'area': 1800,
                'is_available': True
            },
            {
                'title': 'Historic Victorian Home',
                'description': 'Beautifully restored Victorian home with original features. Large rooms, high ceilings, and period details throughout.',
                'price': 725000.00,
                'location': 'Historic District, Old Town',
                'property_type': 'House',
                'bedrooms': 5,
                'bathrooms': 3,
                'area': 3200,
                'is_available': False
            }
        ]
        
        for prop_data in sample_properties:
            property = Property(**prop_data)
            db.session.add(property)
        
        try:
            db.session.commit()
            print(f"✓ Successfully added {len(sample_properties)} sample properties!")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding sample data: {str(e)}")

def reset_database():
    """Drop all tables and recreate them (WARNING: Deletes all data)"""
    app = create_app()
    
    with app.app_context():
        confirm = input("\n⚠️  WARNING: This will delete ALL data in the database. Are you sure? (yes/no): ")
        
        if confirm.lower() == 'yes':
            print("\nDropping all tables...")
            db.drop_all()
            print("✓ All tables dropped.")
            
            print("\nRecreating tables...")
            db.create_all()
            print("✓ Database reset complete!")
            
            # Create admin user
            admin_user = User(
                username='admin',
                email='admin@realestate.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user recreated.")
        else:
            print("Database reset cancelled.")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Real Estate Management System - Database Setup")
    print("="*50 + "\n")
    
    print("Select an option:")
    print("1. Initialize database (first time setup)")
    print("2. Add sample data only")
    print("3. Reset database (WARNING: Deletes all data)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        init_database()
    elif choice == '2':
        add_sample_data()
    elif choice == '3':
        reset_database()
    else:
        print("Invalid choice. Exiting...")
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("="*50 + "\n")