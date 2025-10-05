#!/usr/bin/env python3
"""
Database setup script for CargoOpt
Creates and initializes the database with sample data
"""

import os
import sys
import sqlite3
from pathlib import Path

def setup_sqlite_database():
    """Setup SQLite database for development"""
    print("🛢️  Setting up SQLite database...")
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    
    # Create database connection
    conn = sqlite3.connect('cargoopt.db')
    cursor = conn.cursor()
    
    # Create tables
    print("📊 Creating database tables...")
    
    # Vessels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vessels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            length REAL,
            width REAL,
            height REAL,
            max_weight REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Containers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            container_id TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            length REAL NOT NULL,
            width REAL NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            destination TEXT,
            hazardous BOOLEAN DEFAULT FALSE,
            imdg_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Stowage plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stowage_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT NOT NULL,
            vessel_id INTEGER,
            container_data TEXT,
            optimization_metrics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vessel_id) REFERENCES vessels (id)
        )
    ''')
    
    # Insert sample data
    print("📝 Inserting sample data...")
    
    # Sample vessels
    vessels = [
        ('Container Ship A', 'Container', 300.0, 40.0, 25.0, 50000.0),
        ('Bulk Carrier B', 'Bulk', 250.0, 32.0, 18.0, 35000.0),
        ('Tanker C', 'Tanker', 280.0, 45.0, 22.0, 60000.0)
    ]
    
    cursor.executemany(
        'INSERT INTO vessels (name, type, length, width, height, max_weight) VALUES (?, ?, ?, ?, ?, ?)',
        vessels
    )
    
    # Sample containers
    containers = [
        ('CONT001', 'Standard', 20.0, 8.0, 8.5, 20000.0, 'Port A', False, None),
        ('CONT002', 'Refrigerated', 20.0, 8.0, 8.5, 18000.0, 'Port B', False, None),
        ('CONT003', 'Hazardous', 20.0, 8.0, 8.5, 15000.0, 'Port C', True, 'IMDG 3.1'),
        ('CONT004', 'Standard', 40.0, 8.0, 9.5, 30000.0, 'Port A', False, None),
        ('CONT005', 'Tank', 20.0, 8.0, 8.5, 12000.0, 'Port B', False, None)
    ]
    
    cursor.executemany(
        'INSERT INTO containers (container_id, type, length, width, height, weight, destination, hazardous, imdg_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        containers
    )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("✅ Database setup completed successfully!")
    print("📁 Database file: cargoopt.db")

def main():
    """Main setup function"""
    print("🚀 Starting CargoOpt Database Setup...")
    print("=" * 50)
    
    try:
        # Setup SQLite database
        setup_sqlite_database()
        
        print("=" * 50)
        print("🎉 Database setup completed!")
        print("\n📋 Next steps:")
        print("   1. Run: python run.py (to start backend)")
        print("   2. Run: cd frontend && npm run dev (to start frontend)")
        print("   3. Open: http://localhost:3000 in your browser")
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()