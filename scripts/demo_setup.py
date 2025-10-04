#!/usr/bin/env python3
"""
CargoOpt Demo Setup Script

This script sets up a complete demo environment with sample data
for testing and demonstration purposes.
"""

import os
import sys
import json
import shutil
import sqlite3
import argparse
from pathlib import Path
import requests
from datetime import datetime, timedelta
import random

class DemoSetup:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.data_dir = self.base_dir / "backend" / "data"
        self.sample_dir = self.data_dir / "sample"
        self.export_dir = self.base_dir / "backend" / "data" / "exports" / "stowage_plans"
        
        # Demo data
        self.demo_scenarios = []
        self.demo_containers = []
        self.demo_vehicles = []
        
        # Colors for console output
        self.colors = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m'
        }
    
    def print_header(self, message):
        """Print formatted header message"""
        print(f"\n{self.colors['HEADER']}{'='*60}{self.colors['ENDC']}")
        print(f"{self.colors['BOLD']}{message}{self.colors['ENDC']}")
        print(f"{self.colors['HEADER']}{'='*60}{self.colors['ENDC']}\n")
    
    def print_success(self, message):
        """Print success message"""
        print(f"{self.colors['OKGREEN']}✅ {message}{self.colors['ENDC']}")
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"{self.colors['WARNING']}⚠️  {message}{self.colors['ENDC']}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"{self.colors['FAIL']}❌ {message}{self.colors['ENDC']}")
    
    def print_info(self, message):
        """Print info message"""
        print(f"{self.colors['OKBLUE']}ℹ️  {message}{self.colors['ENDC']}")
    
    def check_environment(self):
        """Check if required directories and files exist"""
        self.print_header("Checking Environment")
        
        required_dirs = [
            self.base_dir,
            self.data_dir,
            self.sample_dir,
            self.export_dir
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                self.print_warning(f"Creating directory: {directory}")
                directory.mkdir(parents=True, exist_ok=True)
            else:
                self.print_success(f"Directory exists: {directory}")
        
        # Check for required files
        required_files = [
            self.sample_dir / "test_scenarios.json",
            self.data_dir / "reference" / "imdg_codes.json",
            self.data_dir / "reference" / "stability_rules.json"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.print_warning(f"Missing file: {file_path}")
                if "reference" in str(file_path):
                    self.create_reference_files()
                elif "test_scenarios" in str(file_path):
                    self.create_sample_scenarios()
            else:
                self.print_success(f"File exists: {file_path}")
    
    def create_reference_files(self):
        """Create reference data files if they don't exist"""
        self.print_info("Creating reference data files...")
        
        # IMDG Codes
        imdg_data = {
            "imdg_classes": [
                {
                    "class": "1",
                    "name": "Explosives",
                    "description": "Substances and articles which have a mass explosion hazard",
                    "segregation_group": "A",
                    "storage_requirements": ["On deck only", "Away from living quarters"],
                    "emergency_procedures": "Use copious amounts of water"
                },
                {
                    "class": "3",
                    "name": "Flammable Liquids",
                    "description": "Liquids which give off flammable vapors at or below 60°C",
                    "segregation_group": "C",
                    "storage_requirements": ["Cool, ventilated areas", "Away from ignition sources"],
                    "emergency_procedures": "Use foam, CO2, or dry chemical extinguishers"
                }
            ]
        }
        
        imdg_file = self.data_dir / "reference" / "imdg_codes.json"
        imdg_file.parent.mkdir(parents=True, exist_ok=True)
        with open(imdg_file, 'w') as f:
            json.dump(imdg_data, f, indent=2)
        self.print_success(f"Created: {imdg_file}")
    
    def create_sample_scenarios(self):
        """Create comprehensive sample scenarios"""
        self.print_info("Creating sample scenarios...")
        
        scenarios = {
            "scenarios": [
                {
                    "id": "demo_urban_delivery",
                    "name": "Urban Delivery Demo",
                    "description": "Small package delivery in urban area with mixed containers",
                    "containers": [
                        {
                            "id": "urb_001",
                            "name": "Small Electronics Box",
                            "length": 1.2,
                            "width": 0.8,
                            "height": 0.8,
                            "weight": 150,
                            "type": "box"
                        },
                        {
                            "id": "urb_002", 
                            "name": "Medium Furniture Crate",
                            "length": 1.5,
                            "width": 1.0,
                            "height": 1.0,
                            "weight": 300,
                            "type": "crate"
                        },
                        {
                            "id": "urb_003",
                            "name": "Office Supplies Pallet",
                            "length": 1.2,
                            "width": 0.8,
                            "height": 1.5,
                            "weight": 450,
                            "type": "pallet"
                        },
                        {
                            "id": "urb_004",
                            "name": "Document Archive Box",
                            "length": 0.8,
                            "width": 0.6,
                            "height": 0.6,
                            "weight": 80,
                            "type": "box"
                        }
                    ],
                    "vehicles": [
                        {
                            "id": "urb_van_01",
                            "type": "van",
                            "max_weight": 800,
                            "length": 2.5,
                            "width": 1.8,
                            "height": 1.8,
                            "emission_factor": 0.00015
                        },
                        {
                            "id": "urb_truck_01",
                            "type": "small_truck", 
                            "max_weight": 1000,
                            "length": 3.0,
                            "width": 2.0,
                            "height": 2.0,
                            "emission_factor": 0.00012
                        }
                    ],
                    "distance_km": 50,
                    "tags": ["urban", "small-scale", "demo"]
                },
                {
                    "id": "demo_logistics_operation", 
                    "name": "Logistics Operation Demo",
                    "description": "Large scale logistics with multiple vehicle types",
                    "containers": [
                        {
                            "id": "log_001",
                            "name": "Heavy Machinery Pallet",
                            "length": 2.4,
                            "width": 1.2,
                            "height": 1.2,
                            "weight": 800,
                            "type": "pallet"
                        },
                        {
                            "id": "log_002",
                            "name": "Industrial Parts Crate", 
                            "length": 1.8,
                            "width": 1.2,
                            "height": 1.0,
                            "weight": 600,
                            "type": "crate"
                        },
                        {
                            "id": "log_003",
                            "name": "Bulk Material Box",
                            "length": 1.0,
                            "width": 1.0,
                            "height": 1.0,
                            "weight": 200,
                            "type": "box"
                        },
                        {
                            "id": "log_004",
                            "name": "Hazardous Chemicals Drum",
                            "length": 1.0,
                            "width": 1.0,
                            "height": 1.2,
                            "weight": 300,
                            "type": "hazardous",
                            "hazard_class": "3"
                        },
                        {
                            "id": "log_005",
                            "name": "Refrigerated Food Container",
                            "length": 1.5,
                            "width": 1.0,
                            "height": 1.0,
                            "weight": 400,
                            "type": "refrigerated"
                        }
                    ],
                    "vehicles": [
                        {
                            "id": "log_truck_large",
                            "type": "large_truck",
                            "max_weight": 2000,
                            "length": 5.0,
                            "width": 2.5, 
                            "height": 2.5,
                            "emission_factor": 0.00008
                        },
                        {
                            "id": "log_truck_medium",
                            "type": "medium_truck",
                            "max_weight": 1500,
                            "length": 4.0,
                            "width": 2.2,
                            "height": 2.2,
                            "emission_factor": 0.00010
                        },
                        {
                            "id": "log_truck_hazmat",
                            "type": "hazmat_truck", 
                            "max_weight": 1200,
                            "length": 4.0,
                            "width": 2.2,
                            "height": 2.2,
                            "emission_factor": 0.00010,
                            "can_carry_hazardous": True
                        },
                        {
                            "id": "log_truck_reefer",
                            "type": "refrigerated_truck",
                            "max_weight": 1000,
                            "length": 3.5,
                            "width": 2.0,
                            "height": 2.0,
                            "emission_factor": 0.00012,
                            "has_refrigeration": True
                        }
                    ],
                    "distance_km": 200,
                    "tags": ["logistics", "large-scale", "hazardous", "demo"]
                },
                {
                    "id": "demo_port_operations",
                    "name": "Port Operations Demo", 
                    "description": "Shipping container operations at port facility",
                    "containers": [
                        {
                            "id": "port_001",
                            "name": "20ft Standard Container",
                            "length": 6.1,
                            "width": 2.44,
                            "height": 2.59,
                            "weight": 2200,
                            "type": "standard"
                        },
                        {
                            "id": "port_002",
                            "name": "20ft Refrigerated Container",
                            "length": 6.1, 
                            "width": 2.44,
                            "height": 2.59,
                            "weight": 2800,
                            "type": "refrigerated"
                        },
                        {
                            "id": "port_003",
                            "name": "40ft High Cube Container",
                            "length": 12.2,
                            "width": 2.44,
                            "height": 2.9,
                            "weight": 3800, 
                            "type": "high_cube"
                        },
                        {
                            "id": "port_004",
                            "name": "Hazardous Materials Container",
                            "length": 6.1,
                            "width": 2.44,
                            "height": 2.59,
                            "weight": 2500,
                            "type": "hazardous",
                            "hazard_class": "5.1"
                        }
                    ],
                    "vehicles": [
                        {
                            "id": "port_truck_heavy",
                            "type": "heavy_duty_truck",
                            "max_weight": 25000,
                            "length": 16.0,
                            "width": 2.6,
                            "height": 2.9,
                            "emission_factor": 0.00006
                        },
                        {
                            "id": "port_truck_medium",
                            "type": "medium_duty_truck",
                            "max_weight": 15000,
                            "length": 12.0, 
                            "width": 2.5,
                            "height": 2.7,
                            "emission_factor": 0.00008
                        }
                    ],
                    "distance_km": 150,
                    "tags": ["port", "shipping", "heavy-duty", "demo"]
                }
            ]
        }
        
        scenarios_file = self.sample_dir / "test_scenarios.json"
        with open(scenarios_file, 'w') as f:
            json.dump(scenarios, f, indent=2)
        self.print_success(f"Created: {scenarios_file}")
        
        return scenarios["scenarios"]
    
    def generate_demo_data(self, num_optimizations=5):
        """Generate demo optimization results and exports"""
        self.print_header("Generating Demo Data")
        
        # Load sample scenarios
        scenarios_file = self.sample_dir / "test_scenarios.json"
        with open(scenarios_file, 'r') as f:
            scenarios_data = json.load(f)
        
        scenarios = scenarios_data["scenarios"]
        
        for i, scenario in enumerate(scenarios[:num_optimizations]):
            self.print_info(f"Generating demo optimization {i+1}/{num_optimizations}")
            
            # Create realistic optimization result
            optimization_result = self.create_demo_optimization_result(scenario)
            
            # Export in multiple formats
            self.export_demo_results(optimization_result, scenario, i+1)
        
        self.print_success(f"Generated {num_optimizations} demo optimizations")
    
    def create_demo_optimization_result(self, scenario):
        """Create realistic demo optimization result"""
        containers = scenario["containers"]
        vehicles = scenario["vehicles"]
        
        # Simple assignment logic for demo
        assignments = {}
        remaining_containers = containers.copy()
        
        for vehicle in vehicles:
            if not remaining_containers:
                break
                
            vehicle_containers = []
            current_weight = 0
            
            for container in remaining_containers[:]:
                if current_weight + container["weight"] <= vehicle["max_weight"]:
                    # Check special requirements
                    if container.get("hazard_class") and not vehicle.get("can_carry_hazardous", False):
                        continue
                    if container.get("type") == "refrigerated" and not vehicle.get("has_refrigeration", False):
                        continue
                    
                    vehicle_containers.append(container["id"])
                    current_weight += container["weight"]
                    remaining_containers.remove(container)
            
            if vehicle_containers:
                assignments[vehicle["id"]] = vehicle_containers
        
        # Calculate metrics
        total_weight = sum(c["weight"] for c in containers)
        assigned_weight = sum(c["weight"] for c in containers if any(c["id"] in v for v in assignments.values()))
        utilization = (assigned_weight / sum(v["max_weight"] for v in vehicles if v["id"] in assignments)) * 100
        
        # Calculate emissions
        total_emissions = 0
        for vehicle_id, container_ids in assignments.items():
            vehicle = next(v for v in vehicles if v["id"] == vehicle_id)
            vehicle_weight = sum(c["weight"] for c in containers if c["id"] in container_ids)
            total_emissions += vehicle_weight * vehicle["emission_factor"] * scenario["distance_km"]
        
        return {
            "assignments": assignments,
            "total_emissions": round(total_emissions, 2),
            "utilization": round(utilization, 1),
            "vehicle_count": len(assignments),
            "total_containers": len(containers),
            "status": "optimal",
            "execution_time": round(random.uniform(0.5, 3.0), 2),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
            "containers": containers,
            "vehicles": vehicles,
            "distance_km": scenario["distance_km"]
        }
    
    def export_demo_results(self, optimization_result, scenario, demo_number):
        """Export demo results in multiple formats"""
        try:
            # Import the exporter
            sys.path.append(str(self.base_dir / "backend"))
            from data.exports.stowage_plans.stowage_exporter import StowagePlanExporter
            
            exporter = StowagePlanExporter(str(self.export_dir))
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"demo_{scenario['id']}_{timestamp}"
            
            # Export JSON
            json_file = exporter.export_json(
                optimization_result,
                optimization_result["containers"],
                optimization_result["vehicles"],
                f"{base_filename}.json"
            )
            
            # Export CSV
            csv_file = exporter.export_csv(
                optimization_result,
                optimization_result["containers"], 
                optimization_result["vehicles"],
                f"{base_filename}.csv"
            )
            
            self.print_success(f"Demo {demo_number}: Exported {os.path.basename(json_file)}")
            self.print_success(f"Demo {demo_number}: Exported {os.path.basename(csv_file)}")
            
        except Exception as e:
            self.print_warning(f"Could not export demo results: {e}")
    
    def create_demo_database(self):
        """Create a demo SQLite database with sample data"""
        self.print_info("Creating demo database...")
        
        db_path = self.data_dir / "demo_cargoopt.db"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id TEXT,
                    scenario_name TEXT,
                    total_emissions REAL,
                    utilization REAL,
                    vehicle_count INTEGER,
                    container_count INTEGER,
                    status TEXT,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS containers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    container_id TEXT,
                    name TEXT,
                    length REAL,
                    width REAL,
                    height REAL,
                    weight REAL,
                    type TEXT,
                    hazard_class TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    type TEXT,
                    max_weight REAL,
                    length REAL,
                    width REAL,
                    height REAL,
                    emission_factor REAL,
                    can_carry_hazardous BOOLEAN DEFAULT 0
                )
            ''')
            
            # Insert sample data
            scenarios = [
                ("urban_demo", "Urban Delivery", 4.2, 85.5, 2, 4, "optimal", 1.2),
                ("logistics_demo", "Logistics Operation", 15.8, 78.3, 3, 5, "optimal", 2.1),
                ("port_demo", "Port Operations", 45.2, 92.1, 2, 4, "optimal", 3.5)
            ]
            
            cursor.executemany('''
                INSERT INTO optimizations 
                (scenario_id, scenario_name, total_emissions, utilization, vehicle_count, container_count, status, execution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', scenarios)
            
            conn.commit()
            conn.close()
            
            self.print_success(f"Demo database created: {db_path}")
            
        except Exception as e:
            self.print_error(f"Failed to create demo database: {e}")
    
    def setup_frontend_demo(self):
        """Setup frontend demo configuration"""
        self.print_info("Setting up frontend demo configuration...")
        
        frontend_dir = self.base_dir / "frontend"
        public_dir = frontend_dir / "public"
        src_dir = frontend_dir / "src"
        
        # Create demo configuration file
        demo_config = {
            "demo_mode": True,
            "demo_scenarios": ["demo_urban_delivery", "demo_logistics_operation", "demo_port_operations"],
            "features": {
                "optimization": True,
                "3d_visualization": True,
                "emission_tracking": True,
                "export": True
            },
            "limits": {
                "max_containers": 50,
                "max_vehicles": 10
            }
        }
        
        config_file = frontend_dir / "demo_config.json"
        with open(config_file, 'w') as f:
            json.dump(demo_config, f, indent=2)
        
        self.print_success(f"Frontend demo config created: {config_file}")
    
    def display_demo_info(self):
        """Display demo setup information"""
        self.print_header("Demo Setup Complete!")
        
        print(f"{self.colors['BOLD']}Demo Scenarios Created:{self.colors['ENDC']}")
        print("  1. 🏙️  Urban Delivery Demo")
        print("  2. 🚛 Logistics Operation Demo") 
        print("  3. 🚢 Port Operations Demo")
        print()
        
        print(f"{self.colors['BOLD']}Next Steps:{self.colors['ENDC']}")
        print("  1. Start the backend server:")
        print("     $ cd backend && python main.py")
        print()
        print("  2. Start the frontend development server:")
        print("     $ cd frontend && npm start")
        print("     Or run: scripts/start_frontend.bat (Windows)")
        print()
        print("  3. Access the application:")
        print("     Frontend: http://localhost:3000")
        print("     Backend API: http://localhost:8000")
        print()
        
        print(f"{self.colors['BOLD']}Demo Features:{self.colors['ENDC']}")
        print("  ✅ Sample data with realistic scenarios")
        print("  ✅ Pre-generated optimization results")
        print("  ✅ Multiple export formats")
        print("  ✅ 3D visualization ready")
        print("  ✅ Emission calculations")
        print()
        
        print(f"{self.colors['WARNING']}Note: This is a demo setup with sample data.")
        print("For production use, configure your actual data sources.{self.colors['ENDC']}")
    
    def run_complete_setup(self, num_demos=3):
        """Run the complete demo setup process"""
        try:
            self.print_header("CargoOpt Demo Setup")
            print(f"Base Directory: {self.base_dir}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Step 1: Check environment
            self.check_environment()
            
            # Step 2: Create sample data
            self.create_sample_scenarios()
            
            # Step 3: Generate demo optimizations
            self.generate_demo_data(num_demos)
            
            # Step 4: Create demo database
            self.create_demo_database()
            
            # Step 5: Setup frontend demo
            self.setup_frontend_demo()
            
            # Step 6: Display completion info
            self.display_demo_info()
            
            return True
            
        except Exception as e:
            self.print_error(f"Demo setup failed: {e}")
            return False

def main():
    """Main function to run the demo setup"""
    parser = argparse.ArgumentParser(description="CargoOpt Demo Setup Script")
    parser.add_argument(
        "--dir", 
        type=str, 
        help="Base directory of CargoOpt project (default: parent of scripts directory)"
    )
    parser.add_argument(
        "--demos", 
        type=int, 
        default=3,
        help="Number of demo optimizations to generate (default: 3)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing demo data before setup"
    )
    
    args = parser.parse_args()
    
    # Initialize demo setup
    demo = DemoSetup(args.dir)
    
    # Clean if requested
    if args.clean:
        demo.print_warning("Cleaning existing demo data...")
        # Implementation for cleaning would go here
    
    # Run setup
    success = demo.run_complete_setup(args.demos)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()