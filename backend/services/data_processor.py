"""
Data Processing Service
Handles data transformation, preprocessing, and format conversions.
"""

import json
import csv
import io
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

from backend.config.settings import Config
from backend.utils.logger import get_logger
from backend.utils.file_utils import FileHandler

logger = get_logger(__name__)


class DataTransformer:
    """
    Handles data transformation and normalization operations.
    """
    
    @staticmethod
    def normalize_dimensions(item: Dict, unit: str = 'mm') -> Dict:
        """
        Normalize item dimensions to standard unit (millimeters).
        
        Args:
            item: Item dictionary with dimensions
            unit: Current unit of measurement
            
        Returns:
            Item with normalized dimensions
        """
        conversion_factors = {
            'mm': 1,
            'cm': 10,
            'm': 1000,
            'in': 25.4,
            'ft': 304.8
        }
        
        factor = conversion_factors.get(unit.lower(), 1)
        
        normalized = item.copy()
        
        if 'length' in item:
            normalized['length'] = int(item['length'] * factor)
        if 'width' in item:
            normalized['width'] = int(item['width'] * factor)
        if 'height' in item:
            normalized['height'] = int(item['height'] * factor)
            
        return normalized
    
    @staticmethod
    def normalize_weight(item: Dict, unit: str = 'kg') -> Dict:
        """
        Normalize item weight to standard unit (kilograms).
        
        Args:
            item: Item dictionary with weight
            unit: Current unit of measurement
            
        Returns:
            Item with normalized weight
        """
        conversion_factors = {
            'kg': 1,
            'g': 0.001,
            'lb': 0.453592,
            'oz': 0.0283495,
            'ton': 1000,
            'tonne': 1000
        }
        
        factor = conversion_factors.get(unit.lower(), 1)
        
        normalized = item.copy()
        
        if 'weight' in item:
            normalized['weight'] = float(item['weight'] * factor)
            
        return normalized
    
    @staticmethod
    def expand_quantities(items: List[Dict]) -> List[Dict]:
        """
        Expand items with quantities > 1 into individual items.
        
        Args:
            items: List of items with quantity field
            
        Returns:
            Expanded list of individual items
        """
        expanded = []
        
        for idx, item in enumerate(items):
            quantity = item.get('quantity', 1)
            
            for i in range(quantity):
                expanded_item = item.copy()
                expanded_item['original_index'] = idx
                expanded_item['instance'] = i + 1
                expanded_item['item_id'] = f"{item.get('item_id', f'item_{idx}')}_{i+1}"
                expanded_item.pop('quantity', None)
                expanded.append(expanded_item)
        
        return expanded
    
    @staticmethod
    def calculate_volume(item: Dict) -> float:
        """
        Calculate item volume in cubic meters.
        
        Args:
            item: Item with length, width, height in mm
            
        Returns:
            Volume in m³
        """
        length = item.get('length', 0)
        width = item.get('width', 0)
        height = item.get('height', 0)
        
        return (length * width * height) / 1e9  # mm³ to m³
    
    @staticmethod
    def calculate_density(item: Dict) -> float:
        """
        Calculate item density in kg/m³.
        
        Args:
            item: Item with weight and dimensions
            
        Returns:
            Density in kg/m³
        """
        volume = DataTransformer.calculate_volume(item)
        weight = item.get('weight', 0)
        
        if volume > 0:
            return weight / volume
        return 0
    
    @staticmethod
    def sort_items_by_priority(items: List[Dict], strategy: str = 'default') -> List[Dict]:
        """
        Sort items based on packing priority strategy.
        
        Args:
            items: List of items
            strategy: Sorting strategy ('default', 'volume', 'weight', 'priority')
            
        Returns:
            Sorted list of items
        """
        if strategy == 'volume':
            # Largest volume first
            return sorted(
                items,
                key=lambda x: x['length'] * x['width'] * x['height'],
                reverse=True
            )
        elif strategy == 'weight':
            # Heaviest first
            return sorted(items, key=lambda x: x.get('weight', 0), reverse=True)
        elif strategy == 'priority':
            # By explicit priority field (lower number = higher priority)
            return sorted(items, key=lambda x: x.get('priority', 5))
        else:
            # Default: priority, then volume, then weight
            return sorted(
                items,
                key=lambda x: (
                    x.get('priority', 5),
                    -(x['length'] * x['width'] * x['height']),
                    -x.get('weight', 0)
                )
            )
    
    @staticmethod
    def add_color_coding(items: List[Dict]) -> List[Dict]:
        """
        Add color codes to items for visualization.
        
        Args:
            items: List of items
            
        Returns:
            Items with color field added
        """
        # Color schemes for different item types
        type_colors = {
            'glass': '#87CEEB',      # Sky blue
            'wood': '#8B4513',       # Saddle brown
            'metal': '#708090',      # Slate gray
            'plastic': '#FFB6C1',    # Light pink
            'electronics': '#4169E1', # Royal blue
            'textiles': '#DDA0DD',   # Plum
            'food': '#FFA500',       # Orange
            'chemicals': '#FF4500',  # Orange red
            'other': '#A9A9A9'       # Dark gray
        }
        
        # Hazmat colors (priority over type)
        hazmat_colors = {
            '1': '#FF0000',   # Explosives - Red
            '2.1': '#FF6B6B', # Flammable gas - Light red
            '2.2': '#90EE90', # Non-flammable gas - Light green
            '2.3': '#8B008B', # Toxic gas - Dark magenta
            '3': '#FFA500',   # Flammable liquid - Orange
            '4.1': '#FFD700', # Flammable solid - Gold
            '4.2': '#FF4500', # Spontaneous combustion - Orange red
            '4.3': '#4169E1', # Dangerous when wet - Royal blue
            '5.1': '#FFFF00', # Oxidizer - Yellow
            '5.2': '#FF8C00', # Organic peroxide - Dark orange
            '6.1': '#800080', # Toxic - Purple
            '6.2': '#DC143C', # Infectious - Crimson
            '7': '#FFFF00',   # Radioactive - Yellow
            '8': '#000000',   # Corrosive - Black
            '9': '#808080'    # Miscellaneous - Gray
        }
        
        for item in items:
            if not item.get('color'):
                # Check if hazardous
                hazard_class = item.get('hazard_class')
                if hazard_class and hazard_class in hazmat_colors:
                    item['color'] = hazmat_colors[hazard_class]
                else:
                    # Use type color
                    item_type = item.get('item_type', 'other')
                    item['color'] = type_colors.get(item_type, type_colors['other'])
        
        return items


class DataProcessor:
    """
    Main data processing service for handling various data operations.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize data processor.
        
        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.transformer = DataTransformer()
        self.file_handler = FileHandler()
        
        logger.info("DataProcessor initialized")
    
    def process_optimization_input(
        self,
        container_data: Dict,
        items_data: List[Dict],
        normalize: bool = True
    ) -> Tuple[Dict, List[Dict]]:
        """
        Process and validate optimization input data.
        
        Args:
            container_data: Container specifications
            items_data: List of items to pack
            normalize: Whether to normalize units
            
        Returns:
            Tuple of (processed_container, processed_items)
        """
        logger.info(f"Processing optimization input: 1 container, {len(items_data)} items")
        
        # Process container
        container = self._process_container(container_data, normalize)
        
        # Process items
        items = self._process_items(items_data, normalize)
        
        logger.info(f"Processing complete: {len(items)} items after expansion")
        
        return container, items
    
    def _process_container(self, container: Dict, normalize: bool = True) -> Dict:
        """
        Process container data.
        
        Args:
            container: Container dictionary
            normalize: Whether to normalize units
            
        Returns:
            Processed container
        """
        processed = container.copy()
        
        # Normalize dimensions if requested
        if normalize:
            unit = container.get('dimension_unit', 'mm')
            processed = self.transformer.normalize_dimensions(processed, unit)
            
            weight_unit = container.get('weight_unit', 'kg')
            processed = self.transformer.normalize_weight(processed, weight_unit)
        
        # Calculate volume
        processed['volume'] = self.transformer.calculate_volume(processed)
        
        # Add defaults
        if 'container_id' not in processed:
            processed['container_id'] = f"container_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if 'max_weight' not in processed:
            processed['max_weight'] = 100000  # Default 100 tons
        
        if 'container_type' not in processed:
            processed['container_type'] = 'standard'
        
        return processed
    
    def _process_items(self, items: List[Dict], normalize: bool = True) -> List[Dict]:
        """
        Process items data.
        
        Args:
            items: List of items
            normalize: Whether to normalize units
            
        Returns:
            Processed items list
        """
        processed = []
        
        for idx, item in enumerate(items):
            item_copy = item.copy()
            
            # Add ID if missing
            if 'item_id' not in item_copy:
                item_copy['item_id'] = f"item_{idx + 1}"
            
            # Normalize dimensions and weight
            if normalize:
                unit = item.get('dimension_unit', 'mm')
                item_copy = self.transformer.normalize_dimensions(item_copy, unit)
                
                weight_unit = item.get('weight_unit', 'kg')
                item_copy = self.transformer.normalize_weight(item_copy, weight_unit)
            
            # Calculate derived properties
            item_copy['volume'] = self.transformer.calculate_volume(item_copy)
            item_copy['density'] = self.transformer.calculate_density(item_copy)
            
            # Add defaults
            if 'quantity' not in item_copy:
                item_copy['quantity'] = 1
            
            if 'item_type' not in item_copy:
                item_copy['item_type'] = 'other'
            
            if 'fragile' not in item_copy:
                item_copy['fragile'] = False
            
            if 'stackable' not in item_copy:
                item_copy['stackable'] = True
            
            if 'rotation_allowed' not in item_copy:
                item_copy['rotation_allowed'] = True
            
            if 'priority' not in item_copy:
                item_copy['priority'] = 5
            
            processed.append(item_copy)
        
        # Expand quantities
        expanded = self.transformer.expand_quantities(processed)
        
        # Add color coding
        expanded = self.transformer.add_color_coding(expanded)
        
        # Sort by priority
        expanded = self.transformer.sort_items_by_priority(expanded)
        
        return expanded
    
    def import_from_json(self, file_path: str) -> Dict[str, Any]:
        """
        Import data from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with container and items data
        """
        logger.info(f"Importing data from JSON: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            container = data.get('container', {})
            items = data.get('items', [])
            
            logger.info(f"Imported {len(items)} items from JSON")
            
            return {
                'container': container,
                'items': items,
                'metadata': data.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error importing JSON: {e}")
            raise
    
    def import_from_csv(self, file_path: str, is_container: bool = False) -> Union[Dict, List[Dict]]:
        """
        Import data from CSV file.
        
        Args:
            file_path: Path to CSV file
            is_container: Whether file contains container data (vs items)
            
        Returns:
            Container dict or list of items
        """
        logger.info(f"Importing data from CSV: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            
            if is_container:
                # First row is container data
                container = df.iloc[0].to_dict()
                logger.info("Imported container from CSV")
                return container
            else:
                # All rows are items
                items = df.to_dict('records')
                logger.info(f"Imported {len(items)} items from CSV")
                return items
                
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            raise
    
    def import_from_excel(self, file_path: str) -> Dict[str, Any]:
        """
        Import data from Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with container and items data
        """
        logger.info(f"Importing data from Excel: {file_path}")
        
        try:
            # Read container sheet
            container_df = pd.read_excel(file_path, sheet_name='Container')
            container = container_df.iloc[0].to_dict()
            
            # Read items sheet
            items_df = pd.read_excel(file_path, sheet_name='Items')
            items = items_df.to_dict('records')
            
            logger.info(f"Imported container and {len(items)} items from Excel")
            
            return {
                'container': container,
                'items': items
            }
            
        except Exception as e:
            logger.error(f"Error importing Excel: {e}")
            raise
    
    def export_to_json(self, data: Dict, file_path: str) -> str:
        """
        Export data to JSON file.
        
        Args:
            data: Data to export
            file_path: Output file path
            
        Returns:
            Path to created file
        """
        logger.info(f"Exporting data to JSON: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Data exported successfully to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            raise
    
    def export_to_csv(
        self,
        items: List[Dict],
        file_path: str,
        columns: Optional[List[str]] = None
    ) -> str:
        """
        Export items to CSV file.
        
        Args:
            items: List of items to export
            file_path: Output file path
            columns: Columns to include (None = all)
            
        Returns:
            Path to created file
        """
        logger.info(f"Exporting {len(items)} items to CSV: {file_path}")
        
        try:
            df = pd.DataFrame(items)
            
            if columns:
                df = df[columns]
            
            df.to_csv(file_path, index=False)
            
            logger.info(f"Items exported successfully to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise
    
    def export_to_excel(
        self,
        data: Dict[str, Any],
        file_path: str
    ) -> str:
        """
        Export data to Excel file with multiple sheets.
        
        Args:
            data: Dictionary with data to export
            file_path: Output file path
            
        Returns:
            Path to created file
        """
        logger.info(f"Exporting data to Excel: {file_path}")
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export each key as a separate sheet
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, list):
                        df = pd.DataFrame(sheet_data)
                    elif isinstance(sheet_data, dict):
                        df = pd.DataFrame([sheet_data])
                    else:
                        continue
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Data exported successfully to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}")
            raise
    
    def generate_statistics(self, items: List[Dict]) -> Dict[str, Any]:
        """
        Generate statistical summary of items.
        
        Args:
            items: List of items
            
        Returns:
            Dictionary with statistics
        """
        if not items:
            return {}
        
        df = pd.DataFrame(items)
        
        stats = {
            'total_items': len(items),
            'total_weight': float(df['weight'].sum()) if 'weight' in df else 0,
            'total_volume': sum(self.transformer.calculate_volume(item) for item in items),
            'dimensions': {
                'length': {
                    'min': float(df['length'].min()) if 'length' in df else 0,
                    'max': float(df['length'].max()) if 'length' in df else 0,
                    'mean': float(df['length'].mean()) if 'length' in df else 0
                },
                'width': {
                    'min': float(df['width'].min()) if 'width' in df else 0,
                    'max': float(df['width'].max()) if 'width' in df else 0,
                    'mean': float(df['width'].mean()) if 'width' in df else 0
                },
                'height': {
                    'min': float(df['height'].min()) if 'height' in df else 0,
                    'max': float(df['height'].max()) if 'height' in df else 0,
                    'mean': float(df['height'].mean()) if 'height' in df else 0
                }
            },
            'weight': {
                'min': float(df['weight'].min()) if 'weight' in df else 0,
                'max': float(df['weight'].max()) if 'weight' in df else 0,
                'mean': float(df['weight'].mean()) if 'weight' in df else 0
            }
        }
        
        # Count by type
        if 'item_type' in df:
            stats['by_type'] = df['item_type'].value_counts().to_dict()
        
        # Count hazardous
        if 'hazard_class' in df:
            hazmat_count = df['hazard_class'].notna().sum()
            stats['hazardous_items'] = int(hazmat_count)
        
        # Count fragile
        if 'fragile' in df:
            stats['fragile_items'] = int(df['fragile'].sum())
        
        return stats
    
    def validate_data_consistency(
        self,
        container: Dict,
        items: List[Dict]
    ) -> Tuple[bool, List[str]]:
        """
        Validate data consistency and feasibility.
        
        Args:
            container: Container data
            items: List of items
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check if total volume exceeds container
        container_volume = self.transformer.calculate_volume(container)
        total_item_volume = sum(
            self.transformer.calculate_volume(item) for item in items
        )
        
        if total_item_volume > container_volume:
            issues.append(
                f"Total item volume ({total_item_volume:.2f} m³) exceeds "
                f"container volume ({container_volume:.2f} m³)"
            )
        
        # Check if total weight exceeds capacity
        total_weight = sum(item.get('weight', 0) for item in items)
        max_weight = container.get('max_weight', float('inf'))
        
        if total_weight > max_weight:
            issues.append(
                f"Total item weight ({total_weight:.2f} kg) exceeds "
                f"container capacity ({max_weight:.2f} kg)"
            )
        
        # Check if any item is larger than container
        for idx, item in enumerate(items):
            dims = sorted([item['length'], item['width'], item['height']])
            container_dims = sorted([
                container['length'],
                container['width'],
                container['height']
            ])
            
            if (dims[0] > container_dims[0] or
                dims[1] > container_dims[1] or
                dims[2] > container_dims[2]):
                issues.append(
                    f"Item {idx + 1} ({item.get('item_id', 'unknown')}) is too large "
                    f"for container in at least one dimension"
                )
        
        is_valid = len(issues) == 0
        
        return is_valid, issues