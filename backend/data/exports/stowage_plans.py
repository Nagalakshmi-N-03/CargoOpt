# Stowage plans export package
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class StowagePlanExporter:
    def __init__(self, export_dir: str = "backend/data/exports/stowage_plans"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def export_json(self, optimization_result: Dict, containers: List[Dict], 
                   vehicles: List[Dict], filename: Optional[str] = None) -> str:
        """Export stowage plan in JSON format"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stowage_plan_{timestamp}.json"
            
            filepath = self.export_dir / filename
            
            stowage_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "system": "CargoOpt"
                },
                "summary": {
                    "total_containers": len(containers),
                    "total_vehicles": len(vehicles),
                    "total_emissions": optimization_result.get('total_emissions', 0),
                    "utilization_rate": optimization_result.get('utilization', 0),
                    "assignment_count": len(optimization_result.get('assignments', {}))
                },
                "assignments": optimization_result.get('assignments', {}),
                "containers": containers,
                "vehicles": vehicles,
                "emission_analysis": self._calculate_emission_analysis(optimization_result, containers, vehicles)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stowage_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON stowage plan exported: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON stowage plan: {e}")
            raise
    
    def export_csv(self, optimization_result: Dict, containers: List[Dict], 
                  vehicles: List[Dict], filename: Optional[str] = None) -> str:
        """Export stowage plan in CSV format"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stowage_plan_{timestamp}.csv"
            
            filepath = self.export_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['Vehicle_ID', 'Container_ID', 'Container_Name', 
                               'Weight', 'Length', 'Width', 'Height', 'Type'])
                
                # Write assignment data
                assignments = optimization_result.get('assignments', {})
                container_lookup = {c['id']: c for c in containers}
                
                for vehicle_id, container_ids in assignments.items():
                    for container_id in container_ids:
                        container = container_lookup.get(container_id, {})
                        writer.writerow([
                            vehicle_id,
                            container_id,
                            container.get('name', ''),
                            container.get('weight', 0),
                            container.get('length', 0),
                            container.get('width', 0),
                            container.get('height', 0),
                            container.get('type', '')
                        ])
            
            self.logger.info(f"CSV stowage plan exported: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV stowage plan: {e}")
            raise
    
    def export_xml(self, optimization_result: Dict, containers: List[Dict], 
                  vehicles: List[Dict], filename: Optional[str] = None) -> str:
        """Export stowage plan in XML format"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stowage_plan_{timestamp}.xml"
            
            filepath = self.export_dir / filename
            
            root = ET.Element("StowagePlan")
            
            # Metadata
            metadata = ET.SubElement(root, "Metadata")
            ET.SubElement(metadata, "ExportDate").text = datetime.now().isoformat()
            ET.SubElement(metadata, "System").text = "CargoOpt"
            ET.SubElement(metadata, "Version").text = "1.0"
            
            # Summary
            summary = ET.SubElement(root, "Summary")
            ET.SubElement(summary, "TotalContainers").text = str(len(containers))
            ET.SubElement(summary, "TotalVehicles").text = str(len(vehicles))
            ET.SubElement(summary, "TotalEmissions").text = str(optimization_result.get('total_emissions', 0))
            ET.SubElement(summary, "UtilizationRate").text = str(optimization_result.get('utilization', 0))
            
            # Assignments
            assignments_elem = ET.SubElement(root, "Assignments")
            assignments = optimization_result.get('assignments', {})
            container_lookup = {c['id']: c for c in containers}
            vehicle_lookup = {v['id']: v for v in vehicles}
            
            for vehicle_id, container_ids in assignments.items():
                vehicle_elem = ET.SubElement(assignments_elem, "Vehicle")
                ET.SubElement(vehicle_elem, "VehicleID").text = vehicle_id
                vehicle_data = vehicle_lookup.get(vehicle_id, {})
                ET.SubElement(vehicle_elem, "VehicleType").text = vehicle_data.get('type', '')
                
                containers_elem = ET.SubElement(vehicle_elem, "Containers")
                for container_id in container_ids:
                    container_elem = ET.SubElement(containers_elem, "Container")
                    container_data = container_lookup.get(container_id, {})
                    ET.SubElement(container_elem, "ContainerID").text = container_id
                    ET.SubElement(container_elem, "Name").text = container_data.get('name', '')
                    ET.SubElement(container_elem, "Weight").text = str(container_data.get('weight', 0))
                    ET.SubElement(container_elem, "Length").text = str(container_data.get('length', 0))
                    ET.SubElement(container_elem, "Width").text = str(container_data.get('width', 0))
                    ET.SubElement(container_elem, "Height").text = str(container_data.get('height', 0))
                    ET.SubElement(container_elem, "Type").text = container_data.get('type', '')
            
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"XML stowage plan exported: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting XML stowage plan: {e}")
            raise
    
    def export_comprehensive_report(self, optimization_result: Dict, containers: List[Dict], 
                                  vehicles: List[Dict], filename: Optional[str] = None) -> str:
        """Export comprehensive stowage plan report in multiple formats"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"comprehensive_stowage_plan_{timestamp}"
            else:
                base_filename = filename.rsplit('.', 1)[0]
            
            # Export all formats
            json_file = self.export_json(optimization_result, containers, vehicles, f"{base_filename}.json")
            csv_file = self.export_csv(optimization_result, containers, vehicles, f"{base_filename}.csv")
            xml_file = self.export_xml(optimization_result, containers, vehicles, f"{base_filename}.xml")
            
            # Create manifest
            manifest = {
                "export_date": datetime.now().isoformat(),
                "files": {
                    "json": json_file,
                    "csv": csv_file,
                    "xml": xml_file
                },
                "summary": {
                    "total_containers": len(containers),
                    "total_vehicles": len(vehicles),
                    "formats_exported": ["JSON", "CSV", "XML"]
                }
            }
            
            manifest_file = self.export_dir / f"{base_filename}_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Comprehensive stowage plan exported with manifest: {manifest_file}")
            return str(manifest_file)
            
        except Exception as e:
            self.logger.error(f"Error exporting comprehensive report: {e}")
            raise
    
    def _calculate_emission_analysis(self, optimization_result: Dict, 
                                   containers: List[Dict], vehicles: List[Dict]) -> Dict[str, Any]:
        """Calculate detailed emission analysis for the stowage plan"""
        assignments = optimization_result.get('assignments', {})
        container_lookup = {c['id']: c for c in containers}
        vehicle_lookup = {v['id']: v for v in vehicles}
        
        emission_analysis = {
            "total_emissions_kg": optimization_result.get('total_emissions', 0),
            "emissions_by_vehicle": {},
            "weight_distribution": {},
            "efficiency_metrics": {}
        }
        
        # Calculate emissions by vehicle
        for vehicle_id, container_ids in assignments.items():
            vehicle = vehicle_lookup.get(vehicle_id, {})
            vehicle_emissions = 0
            vehicle_weight = 0
            
            for container_id in container_ids:
                container = container_lookup.get(container_id, {})
                container_emissions = container.get('weight', 0) * vehicle.get('emission_factor', 0) * 100  # Assuming 100km distance
                vehicle_emissions += container_emissions
                vehicle_weight += container.get('weight', 0)
            
            emission_analysis["emissions_by_vehicle"][vehicle_id] = {
                "emissions_kg": round(vehicle_emissions, 2),
                "total_weight": vehicle_weight,
                "vehicle_type": vehicle.get('type', ''),
                "utilization_percentage": round((vehicle_weight / vehicle.get('max_weight', 1)) * 100, 1)
            }
        
        # Calculate overall efficiency metrics
        total_weight = sum(c.get('weight', 0) for c in containers)
        total_capacity = sum(v.get('max_weight', 0) for v in vehicles)
        
        emission_analysis["efficiency_metrics"] = {
            "overall_utilization": round((total_weight / total_capacity) * 100, 1) if total_capacity > 0 else 0,
            "containers_per_vehicle": round(len(containers) / len(assignments), 1) if assignments else 0,
            "average_vehicle_utilization": round(sum(
                v_data["utilization_percentage"] for v_data in emission_analysis["emissions_by_vehicle"].values()
            ) / len(emission_analysis["emissions_by_vehicle"]), 1) if emission_analysis["emissions_by_vehicle"] else 0
        }
        
        return emission_analysis
    
    def list_exported_plans(self) -> List[Dict[str, str]]:
        """List all exported stowage plans"""
        try:
            plans = []
            for file_path in self.export_dir.glob("*.json"):
                if "_manifest" not in file_path.name:
                    plans.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "size_kb": round(file_path.stat().st_size / 1024, 2),
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return sorted(plans, key=lambda x: x["modified"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error listing exported plans: {e}")
            return []