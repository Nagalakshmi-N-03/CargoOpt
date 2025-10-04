import json
import os
from pathlib import Path
from typing import Dict, List, Any

class StowagePlanExporter:
    def export_json(self, result: Dict[str, Any], containers: List[Dict[str, Any]], vehicles: List[Dict[str, Any]]) -> str:
        """Export optimization results to JSON"""
        filepath = "exports/stowage_plan.json"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        export_data = {
            "optimization_result": result,
            "containers": containers,
            "vehicles": vehicles,
            "metadata": {
                "exported_at": "2024-01-01T00:00:00Z",
                "format": "json",
                "version": "1.0"
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath
    
    def export_csv(self, result: Dict[str, Any], containers: List[Dict[str, Any]], vehicles: List[Dict[str, Any]]) -> str:
        """Export optimization results to CSV"""
        filepath = "exports/stowage_plan.csv"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            # Write header
            f.write("vehicle_id,container_ids,container_count,total_weight_kg,emissions_kg,utilization\n")
            
            # Write data
            assignments = result.get('assignments', {})
            for vehicle_id, container_list in assignments.items():
                container_ids = ','.join(container_list)
                container_count = len(container_list)
                f.write(f"{vehicle_id},{container_ids},{container_count},0,0,0\n")
        
        return filepath
    
    def export_xml(self, result: Dict[str, Any], containers: List[Dict[str, Any]], vehicles: List[Dict[str, Any]]) -> str:
        """Export optimization results to XML"""
        filepath = "exports/stowage_plan.xml"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        assignments = result.get('assignments', {})
        
        with open(filepath, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<stowage_plan>\n')
            f.write('  <metadata>\n')
            f.write('    <exported_at>2024-01-01T00:00:00Z</exported_at>\n')
            f.write('    <format>xml</format>\n')
            f.write('    <version>1.0</version>\n')
            f.write('  </metadata>\n')
            f.write('  <assignments>\n')
            
            for vehicle_id, container_list in assignments.items():
                f.write(f'    <vehicle id="{vehicle_id}">\n')
                for container_id in container_list:
                    f.write(f'      <container>{container_id}</container>\n')
                f.write('    </vehicle>\n')
            
            f.write('  </assignments>\n')
            f.write('</stowage_plan>\n')
        
        return filepath