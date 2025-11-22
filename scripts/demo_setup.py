#!/usr/bin/env python3
"""
Demo Setup Script
=================
Sets up demo data and configurations for development/testing.
"""

import os
import sys
import json
import random
import string
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DemoSetup:
    """Handles demo environment setup and data seeding."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.project_root = PROJECT_ROOT
        self.demo_users = []
        self.demo_data = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with formatting."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def generate_password_hash(self, password: str) -> str:
        """Generate a simple password hash for demo purposes."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_random_string(self, length: int = 8) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def setup_environment(self):
        """Create or update .env file with demo configuration."""
        self.log("Setting up demo environment configuration...")
        
        env_path = self.project_root / ".env"
        env_demo_path = self.project_root / ".env.demo"
        
        demo_config = {
            "# Demo Environment Configuration": "",
            "ENVIRONMENT": "demo",
            "DEBUG": "true",
            "SECRET_KEY": self.generate_random_string(32),
            "": "",
            "# Database": "",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "demo_database",
            "DB_USER": "demo_user",
            "DB_PASSWORD": "demo_password",
            "DATABASE_URL": "postgresql://demo_user:demo_password@localhost:5432/demo_database",
            " ": "",
            "# Backend": "",
            "BACKEND_HOST": "0.0.0.0",
            "BACKEND_PORT": "8000",
            "CORS_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
            "  ": "",
            "# Frontend": "",
            "REACT_APP_API_URL": "http://localhost:8000",
            "REACT_APP_ENV": "demo",
            "   ": "",
            "# Demo Settings": "",
            "DEMO_MODE": "true",
            "DEMO_SEED_DATA": "true",
            "DEMO_USER_PASSWORD": "demo123",
        }
        
        with open(env_demo_path, "w") as f:
            for key, value in demo_config.items():
                if key.startswith("#") or key.strip() == "":
                    f.write(f"{key}\n")
                else:
                    f.write(f"{key}={value}\n")
        
        self.log(f"Created {env_demo_path}")
        
        # Copy to .env if it doesn't exist
        if not env_path.exists():
            import shutil
            shutil.copy(env_demo_path, env_path)
            self.log(f"Created {env_path} from demo configuration")
        
        return True
    
    def create_demo_users(self) -> list:
        """Generate demo user data."""
        self.log("Creating demo users...")
        
        demo_password = "demo123"
        password_hash = self.generate_password_hash(demo_password)
        
        users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@demo.local",
                "password_hash": password_hash,
                "role": "admin",
                "full_name": "Demo Administrator",
                "is_active": True,
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "username": "user",
                "email": "user@demo.local",
                "password_hash": password_hash,
                "role": "user",
                "full_name": "Demo User",
                "is_active": True,
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": 3,
                "username": "manager",
                "email": "manager@demo.local",
                "password_hash": password_hash,
                "role": "manager",
                "full_name": "Demo Manager",
                "is_active": True,
                "created_at": datetime.now().isoformat(),
            },
        ]
        
        # Add some random users
        for i in range(4, 10):
            users.append({
                "id": i,
                "username": f"testuser{i}",
                "email": f"testuser{i}@demo.local",
                "password_hash": password_hash,
                "role": "user",
                "full_name": f"Test User {i}",
                "is_active": random.choice([True, True, True, False]),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            })
        
        self.demo_users = users
        self.log(f"Created {len(users)} demo users")
        return users
    
    def create_demo_data(self) -> dict:
        """Generate sample application data."""
        self.log("Creating demo data...")
        
        categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
        statuses = ["pending", "processing", "completed", "cancelled"]
        
        # Sample products
        products = []
        for i in range(1, 21):
            products.append({
                "id": i,
                "name": f"Demo Product {i}",
                "description": f"This is a demo product description for item {i}.",
                "price": round(random.uniform(9.99, 299.99), 2),
                "category": random.choice(categories),
                "stock": random.randint(0, 100),
                "is_active": True,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
            })
        
        # Sample orders
        orders = []
        for i in range(1, 16):
            order_date = datetime.now() - timedelta(days=random.randint(0, 30))
            orders.append({
                "id": i,
                "user_id": random.randint(1, len(self.demo_users)),
                "status": random.choice(statuses),
                "total": round(random.uniform(19.99, 599.99), 2),
                "items_count": random.randint(1, 5),
                "created_at": order_date.isoformat(),
                "updated_at": (order_date + timedelta(hours=random.randint(1, 48))).isoformat(),
            })
        
        # Sample analytics
        analytics = {
            "total_users": len(self.demo_users),
            "total_products": len(products),
            "total_orders": len(orders),
            "revenue_today": round(random.uniform(500, 2000), 2),
            "revenue_month": round(random.uniform(10000, 50000), 2),
            "active_sessions": random.randint(5, 25),
        }
        
        self.demo_data = {
            "users": self.demo_users,
            "products": products,
            "orders": orders,
            "analytics": analytics,
        }
        
        self.log(f"Created {len(products)} products, {len(orders)} orders")
        return self.demo_data
    
    def save_demo_data(self):
        """Save demo data to JSON files."""
        self.log("Saving demo data to files...")
        
        data_dir = self.project_root / "data" / "demo"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        for name, data in self.demo_data.items():
            file_path = data_dir / f"{name}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            self.log(f"Saved {file_path}")
        
        return True
    
    def seed_database(self):
        """Seed the database with demo data."""
        self.log("Attempting to seed database...")
        
        try:
            from backend.database import get_db_session, init_db
            from backend.models import User, Product, Order
            
            init_db()
            session = get_db_session()
            
            # Seed users
            for user_data in self.demo_users:
                user = User(**{k: v for k, v in user_data.items() if k != 'id'})
                session.merge(user)
            
            session.commit()
            self.log("Database seeded successfully")
            return True
            
        except ImportError:
            self.log("Backend models not found. Skipping database seeding.", "WARNING")
            self.log("Demo data saved to JSON files instead.")
            return False
        except Exception as e:
            self.log(f"Database seeding failed: {e}", "ERROR")
            return False
    
    def create_demo_directories(self):
        """Create necessary directory structure."""
        self.log("Creating directory structure...")
        
        directories = [
            "data/demo",
            "data/uploads",
            "logs",
            "static/images",
            "backups",
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Created {full_path}")
        
        return True
    
    def run(self):
        """Run complete demo setup."""
        print("=" * 50)
        print("Demo Setup Script")
        print("=" * 50)
        print()
        
        steps = [
            ("Setting up environment", self.setup_environment),
            ("Creating directories", self.create_demo_directories),
            ("Creating demo users", self.create_demo_users),
            ("Creating demo data", self.create_demo_data),
            ("Saving demo data", self.save_demo_data),
            ("Seeding database", self.seed_database),
        ]
        
        for step_name, step_func in steps:
            self.log(f"Starting: {step_name}")
            try:
                step_func()
            except Exception as e:
                self.log(f"Error in {step_name}: {e}", "ERROR")
        
        print()
        print("=" * 50)
        print("Demo Setup Complete!")
        print("=" * 50)
        print()
        print("Demo Credentials:")
        print("  Admin:   admin@demo.local / demo123")
        print("  User:    user@demo.local / demo123")
        print("  Manager: manager@demo.local / demo123")
        print()
        print("Next Steps:")
        print("  1. Run start_backend.bat to start the API server")
        print("  2. Run start_frontend.bat to start the frontend")
        print("  3. Access the app at http://localhost:3000")
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo Setup Script")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    parser.add_argument("--no-seed", action="store_true", help="Skip database seeding")
    args = parser.parse_args()
    
    setup = DemoSetup(verbose=not args.quiet)
    setup.run()


if __name__ == "__main__":
    main()