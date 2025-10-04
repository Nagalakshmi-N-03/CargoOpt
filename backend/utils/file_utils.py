import logging
import json
import csv
import pandas as pd
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)

class FileUtils:
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory_path}: {str(e)}")
            return False
    
    @staticmethod
    def save_json(data: Dict, filepath: str, indent: int = 2) -> bool:
        """Save data to JSON file"""
        try:
            FileUtils.ensure_directory(Path(filepath).parent)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info(f"Data saved to JSON: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON to {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Optional[Dict]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON from {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def save_csv(data: List[Dict], filepath: str) -> bool:
        """Save data to CSV file"""
        try:
            if not data:
                logger.warning("No data to save to CSV")
                return False
            
            FileUtils.ensure_directory(Path(filepath).parent)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Data saved to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save CSV to {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_csv(filepath: str) -> Optional[List[Dict]]:
        """Load data from CSV file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"Failed to load CSV from {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def export_optimization_result(result: Dict, export_format: str = 'excel') -> str:
        """Export optimization result to various formats"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == 'excel':
                filename = f"optimization_result_{timestamp}.xlsx"
                return FileUtils._export_to_excel(result, filename)
            elif export_format == 'json':
                filename = f"optimization_result_{timestamp}.json"
                return FileUtils._export_to_json(result, filename)
            elif export_format == 'csv':
                filename = f"optimization_result_{timestamp}.csv"
                return FileUtils._export_to_csv(result, filename)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            raise
    
    @staticmethod
    def _export_to_excel(result: Dict, filename: str) -> str:
        """Export result to Excel file"""
        try:
            filepath = Path("exports") / filename
            FileUtils.ensure_directory("exports")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Export placements
                placements = result.get('placements', [])
                if placements:
                    placements_df = pd.DataFrame([
                        {
                            'item_id': p['item_id'],
                            'x_position': p['position'][0],
                            'y_position': p['position'][1],
                            'z_position': p['position'][2],
                            'length': p['dimensions'][0],
                            'width': p['dimensions'][1],
                            'height': p['dimensions'][2],
                            'rotated': p.get('rotated', False),
                            'volume': p['dimensions'][0] * p['dimensions'][1] * p['dimensions'][2]
                        }
                        for p in placements
                    ])
                    placements_df.to_excel(writer, sheet_name='Placements', index=False)
                
                # Export metrics
                metrics = result.get('metrics', {})
                if metrics:
                    metrics_data = []
                    
                    # Flatten metrics
                    for key, value in metrics.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                metrics_data.append({
                                    'category': key,
                                    'metric': subkey,
                                    'value': subvalue
                                })
                        else:
                            metrics_data.append({
                                'category': 'general',
                                'metric': key,
                                'value': value
                            })
                    
                    metrics_df = pd.DataFrame(metrics_data)
                    metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
                
                # Export summary
                summary_data = [{
                    'algorithm': result.get('algorithm', 'unknown'),
                    'execution_time': result.get('execution_time', 0),
                    'total_items': len(placements),
                    'timestamp': datetime.now().isoformat()
                }]
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise
    
    @staticmethod
    def _export_to_json(result: Dict, filename: str) -> str:
        """Export result to JSON file"""
        try:
            filepath = Path("exports") / filename
            FileUtils.ensure_directory("exports")
            
            # Add export metadata
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'export_format': 'json',
                'data': result
            }
            
            FileUtils.save_json(export_data, filepath)
            return str(filepath)
            
        except Exception as e:
            logger.error(f"JSON export failed: {str(e)}")
            raise
    
    @staticmethod
    def _export_to_csv(result: Dict, filename: str) -> str:
        """Export result to CSV file"""
        try:
            filepath = Path("exports") / filename
            FileUtils.ensure_directory("exports")
            
            placements = result.get('placements', [])
            if placements:
                csv_data = []
                for placement in placements:
                    csv_data.append({
                        'item_id': placement['item_id'],
                        'x_position': placement['position'][0],
                        'y_position': placement['position'][1],
                        'z_position': placement['position'][2],
                        'length': placement['dimensions'][0],
                        'width': placement['dimensions'][1],
                        'height': placement['dimensions'][2],
                        'rotated': placement.get('rotated', False),
                        'volume': placement['dimensions'][0] * placement['dimensions'][1] * placement['dimensions'][2]
                    })
                
                FileUtils.save_csv(csv_data, filepath)
                return str(filepath)
            else:
                raise ValueError("No placement data to export")
                
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            raise
    
    @staticmethod
    def generate_report(optimization_results: List[Dict], report_type: str = 'summary') -> str:
        """Generate comprehensive optimization report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimization_report_{report_type}_{timestamp}.xlsx"
            filepath = Path("reports") / filename
            FileUtils.ensure_directory("reports")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if report_type == 'summary':
                    FileUtils._generate_summary_report(writer, optimization_results)
                elif report_type == 'detailed':
                    FileUtils._generate_detailed_report(writer, optimization_results)
                elif report_type == 'comparison':
                    FileUtils._generate_comparison_report(writer, optimization_results)
                else:
                    raise ValueError(f"Unknown report type: {report_type}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise
    
    @staticmethod
    def _generate_summary_report(writer, results: List[Dict]):
        """Generate summary report"""
        summary_data = []
        
        for result in results:
            metrics = result.get('metrics', {})
            volume_metrics = metrics.get('volume_metrics', {})
            
            summary_data.append({
                'algorithm': result.get('algorithm', 'unknown'),
                'utilization_rate': volume_metrics.get('utilization_rate', metrics.get('utilization_rate', 0)),
                'total_items_packed': metrics.get('total_items_packed', 0),
                'total_volume_used': volume_metrics.get('used_volume', metrics.get('total_volume_used', 0)),
                'execution_time': result.get('execution_time', 0),
                'efficiency_score': metrics.get('efficiency_score', 0),
                'stability_score': metrics.get('stability_score', 0)
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    @staticmethod
    def _generate_detailed_report(writer, results: List[Dict]):
        """Generate detailed report"""
        FileUtils._generate_summary_report(writer, results)
        
        # Add additional sheets for detailed analysis
        for i, result in enumerate(results):
            algorithm = result.get('algorithm', f'result_{i}')
            
            # Placements sheet
            placements = result.get('placements', [])
            if placements:
                placements_df = pd.DataFrame([
                    {
                        'item_id': p['item_id'],
                        'position_x': p['position'][0],
                        'position_y': p['position'][1],
                        'position_z': p['position'][2],
                        'length': p['dimensions'][0],
                        'width': p['dimensions'][1],
                        'height': p['dimensions'][2],
                        'volume': p['dimensions'][0] * p['dimensions'][1] * p['dimensions'][2]
                    }
                    for p in placements
                ])
                placements_df.to_excel(writer, sheet_name=f'{algorithm}_Placements', index=False)
    
    @staticmethod
    def _generate_comparison_report(writer, results: List[Dict]):
        """Generate algorithm comparison report"""
        comparison_data = []
        
        for result in results:
            metrics = result.get('metrics', {})
            volume_metrics = metrics.get('volume_metrics', {})
            
            comparison_data.append({
                'algorithm': result.get('algorithm', 'unknown'),
                'volume_utilization': volume_metrics.get('utilization_rate', 0),
                'weight_utilization': metrics.get('weight_metrics', {}).get('utilization_rate', 0),
                'items_packed': metrics.get('total_items_packed', 0),
                'execution_time': result.get('execution_time', 0),
                'efficiency_score': metrics.get('efficiency_score', 0),
                'stability_score': metrics.get('stability_score', 0),
                'space_efficiency': metrics.get('space_efficiency', 0)
            })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df.to_excel(writer, sheet_name='Algorithm Comparison', index=False)
            
            # Add ranking
            comparison_df['overall_rank'] = comparison_df['efficiency_score'].rank(ascending=False)
            comparison_df['speed_rank'] = comparison_df['execution_time'].rank(ascending=True)
            comparison_df.to_excel(writer, sheet_name='Rankings', index=False)
    
    @staticmethod
    def load_config(config_file: str) -> Optional[Dict]:
        """Load configuration from file"""
        try:
            config_path = Path("config") / config_file
            if config_path.exists():
                return FileUtils.load_json(config_path)
            else:
                logger.warning(f"Config file not found: {config_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            return None
    
    @staticmethod
    def save_config(config: Dict, config_file: str) -> bool:
        """Save configuration to file"""
        try:
            FileUtils.ensure_directory("config")
            config_path = Path("config") / config_file
            return FileUtils.save_json(config, config_path)
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            return False
    
    @staticmethod
    def get_file_size(filepath: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return Path(filepath).stat().st_size
        except Exception as e:
            logger.error(f"Failed to get file size for {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def list_exports() -> List[Dict]:
        """List all export files"""
        try:
            exports_dir = Path("exports")
            if not exports_dir.exists():
                return []
            
            export_files = []
            for file_path in exports_dir.glob("*.*"):
                export_files.append({
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size_bytes': file_path.stat().st_size,
                    'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
            
            return sorted(export_files, key=lambda x: x['modified_time'], reverse=True)
        except Exception as e:
            logger.error(f"Failed to list exports: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_days: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in directory_path.glob("*.*"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {file_path}")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup files in {directory}: {str(e)}")
            return 0