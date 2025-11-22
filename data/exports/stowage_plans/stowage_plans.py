"""
Stowage Plan Export Utilities
Generates various export formats for stowage plans and optimization results.
"""

import json
import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import xlsxwriter
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False


@dataclass
class ExportMetadata:
    """Metadata for export files."""
    export_id: str
    created_at: str
    created_by: Optional[str]
    version: str = "1.0.0"
    source: str = "CargoOpt"


class StowagePlanExporter:
    """
    Export stowage plans to various formats.
    """
    
    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for export files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_json(
        self,
        stowage_plan: Dict,
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> str:
        """
        Export stowage plan to JSON format.
        
        Args:
            stowage_plan: Stowage plan data
            filename: Output filename
            pretty: Pretty print JSON
            
        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"stowage_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        export_data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format_version": "1.0.0",
                "source": "CargoOpt"
            },
            "stowage_plan": stowage_plan
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(export_data, f, indent=2, default=str)
            else:
                json.dump(export_data, f, default=str)
        
        return str(filepath)
    
    def export_to_csv(
        self,
        stowage_plan: Dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Export stowage plan positions to CSV format.
        
        Args:
            stowage_plan: Stowage plan data
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"stowage_positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.output_dir / filename
        positions = stowage_plan.get('positions', [])
        
        if not positions:
            positions = stowage_plan.get('placements', [])
        
        fieldnames = [
            'container_id', 'bay', 'row', 'tier', 'is_above_deck',
            'position_x', 'position_y', 'position_z',
            'length', 'width', 'height', 'weight_kg',
            'is_reefer', 'hazard_class', 'destination'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for pos in positions:
                row = self._flatten_position(pos)
                writer.writerow(row)
        
        return str(filepath)
    
    def _flatten_position(self, position: Any) -> Dict:
        """Flatten position object to dictionary."""
        if hasattr(position, '__dict__'):
            return {
                'container_id': getattr(position, 'container_id', getattr(position, 'item_index', '')),
                'bay': getattr(position, 'bay', ''),
                'row': getattr(position, 'row', ''),
                'tier': getattr(position, 'tier', ''),
                'is_above_deck': getattr(position, 'is_above_deck', ''),
                'position_x': getattr(position, 'x', getattr(position, 'position_x', '')),
                'position_y': getattr(position, 'y', getattr(position, 'position_y', '')),
                'position_z': getattr(position, 'z', getattr(position, 'position_z', '')),
                'length': getattr(position, 'length', ''),
                'width': getattr(position, 'width', ''),
                'height': getattr(position, 'height', ''),
                'weight_kg': getattr(position, 'weight', getattr(position, 'weight_kg', '')),
                'is_reefer': getattr(position, 'is_reefer', False),
                'hazard_class': getattr(position, 'hazard_class', ''),
                'destination': getattr(position, 'destination', '')
            }
        elif isinstance(position, dict):
            return position
        return {}
    
    def export_to_xlsx(
        self,
        stowage_plan: Dict,
        filename: Optional[str] = None,
        include_summary: bool = True,
        include_charts: bool = True
    ) -> str:
        """
        Export stowage plan to Excel format with multiple sheets.
        
        Args:
            stowage_plan: Stowage plan data
            filename: Output filename
            include_summary: Include summary sheet
            include_charts: Include charts
            
        Returns:
            Path to exported file
        """
        if not XLSX_AVAILABLE:
            raise ImportError("xlsxwriter not available. Install with: pip install xlsxwriter")
        
        if not filename:
            filename = f"stowage_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.output_dir / filename
        
        workbook = xlsxwriter.Workbook(str(filepath))
        
        # Formats
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1})
        cell_fmt = workbook.add_format({'border': 1})
        number_fmt = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        percent_fmt = workbook.add_format({'border': 1, 'num_format': '0.0%'})
        
        # Summary Sheet
        if include_summary:
            self._write_summary_sheet(workbook, stowage_plan, header_fmt, cell_fmt, number_fmt, percent_fmt)
        
        # Positions Sheet
        self._write_positions_sheet(workbook, stowage_plan, header_fmt, cell_fmt, number_fmt)
        
        # Statistics Sheet
        self._write_statistics_sheet(workbook, stowage_plan, header_fmt, cell_fmt, number_fmt, percent_fmt)
        
        # Bay Plan Sheet
        self._write_bay_plan_sheet(workbook, stowage_plan, header_fmt, cell_fmt)
        
        workbook.close()
        return str(filepath)
    
    def _write_summary_sheet(self, workbook, plan, header_fmt, cell_fmt, number_fmt, percent_fmt):
        """Write summary sheet to Excel workbook."""
        ws = workbook.add_worksheet('Summary')
        ws.set_column('A:A', 30)
        ws.set_column('B:B', 25)
        
        # Title
        title_fmt = workbook.add_format({'bold': True, 'font_size': 16})
        ws.write('A1', 'Stowage Plan Summary', title_fmt)
        ws.write('A2', f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        row = 4
        summary_data = [
            ('Plan ID', plan.get('plan_id', plan.get('optimization_id', 'N/A'))),
            ('Vessel/Container', plan.get('vessel_id', plan.get('container', {}).get('container_id', 'N/A'))),
            ('Total Containers', len(plan.get('positions', plan.get('placements', [])))),
            ('Space Utilization', f"{plan.get('utilization', 0):.1f}%"),
            ('Total Weight (kg)', plan.get('total_weight', 0)),
            ('Computation Time (s)', plan.get('computation_time', 0)),
            ('Algorithm', plan.get('algorithm', 'N/A')),
            ('Status', plan.get('status', 'N/A'))
        ]
        
        for label, value in summary_data:
            ws.write(row, 0, label, header_fmt)
            ws.write(row, 1, value, cell_fmt)
            row += 1
    
    def _write_positions_sheet(self, workbook, plan, header_fmt, cell_fmt, number_fmt):
        """Write positions sheet to Excel workbook."""
        ws = workbook.add_worksheet('Positions')
        
        headers = ['#', 'Container/Item', 'Position X', 'Position Y', 'Position Z', 
                   'Length', 'Width', 'Height', 'Weight (kg)', 'Rotation']
        
        for col, header in enumerate(headers):
            ws.write(0, col, header, header_fmt)
            ws.set_column(col, col, 15)
        
        positions = plan.get('positions', plan.get('placements', []))
        
        for row, pos in enumerate(positions, start=1):
            flat = self._flatten_position(pos)
            ws.write(row, 0, row, cell_fmt)
            ws.write(row, 1, flat.get('container_id', ''), cell_fmt)
            ws.write(row, 2, flat.get('position_x', ''), number_fmt)
            ws.write(row, 3, flat.get('position_y', ''), number_fmt)
            ws.write(row, 4, flat.get('position_z', ''), number_fmt)
            ws.write(row, 5, flat.get('length', ''), number_fmt)
            ws.write(row, 6, flat.get('width', ''), number_fmt)
            ws.write(row, 7, flat.get('height', ''), number_fmt)
            ws.write(row, 8, flat.get('weight_kg', ''), number_fmt)
            ws.write(row, 9, getattr(pos, 'rotation', 0) if hasattr(pos, 'rotation') else pos.get('rotation', 0), cell_fmt)
    
    def _write_statistics_sheet(self, workbook, plan, header_fmt, cell_fmt, number_fmt, percent_fmt):
        """Write statistics sheet to Excel workbook."""
        ws = workbook.add_worksheet('Statistics')
        ws.set_column('A:A', 25)
        ws.set_column('B:B', 20)
        
        positions = plan.get('positions', plan.get('placements', []))
        
        if not positions:
            ws.write('A1', 'No position data available')
            return
        
        # Calculate statistics
        weights = [self._flatten_position(p).get('weight_kg', 0) or 0 for p in positions]
        total_weight = sum(weights)
        avg_weight = total_weight / len(weights) if weights else 0
        max_weight = max(weights) if weights else 0
        min_weight = min(weights) if weights else 0
        
        stats = [
            ('Total Positions', len(positions)),
            ('Total Weight (kg)', total_weight),
            ('Average Weight (kg)', avg_weight),
            ('Max Weight (kg)', max_weight),
            ('Min Weight (kg)', min_weight),
            ('Space Utilization', plan.get('utilization', 0) / 100),
        ]
        
        ws.write('A1', 'Statistic', header_fmt)
        ws.write('B1', 'Value', header_fmt)
        
        for row, (label, value) in enumerate(stats, start=1):
            ws.write(row, 0, label, cell_fmt)
            if isinstance(value, float) and value < 1:
                ws.write(row, 1, value, percent_fmt)
            else:
                ws.write(row, 1, value, number_fmt if isinstance(value, (int, float)) else cell_fmt)
    
    def _write_bay_plan_sheet(self, workbook, plan, header_fmt, cell_fmt):
        """Write bay plan visualization sheet."""
        ws = workbook.add_worksheet('Bay Plan')
        ws.write('A1', 'Bay Plan Visualization', header_fmt)
        ws.write('A3', 'See Positions sheet for detailed placement data')
    
    def export_to_pdf(
        self,
        stowage_plan: Dict,
        filename: Optional[str] = None,
        include_graphics: bool = True,
        page_size: str = 'A4'
    ) -> str:
        """
        Export stowage plan to PDF format.
        
        Args:
            stowage_plan: Stowage plan data
            filename: Output filename
            include_graphics: Include graphical visualizations
            page_size: Page size ('A4' or 'letter')
            
        Returns:
            Path to exported file
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab not available. Install with: pip install reportlab")
        
        if not filename:
            filename = f"stowage_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = self.output_dir / filename
        
        page = A4 if page_size.upper() == 'A4' else letter
        doc = SimpleDocTemplate(str(filepath), pagesize=page, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=10)
        
        elements = []
        
        # Title
        elements.append(Paragraph("Stowage Plan Report", title_style))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Summary
        elements.append(Paragraph("Summary", heading_style))
        summary_data = [
            ['Plan ID', str(stowage_plan.get('plan_id', stowage_plan.get('optimization_id', 'N/A')))],
            ['Total Items', str(len(stowage_plan.get('positions', stowage_plan.get('placements', []))))],
            ['Utilization', f"{stowage_plan.get('utilization', 0):.1f}%"],
            ['Status', str(stowage_plan.get('status', 'N/A'))],
        ]
        
        summary_table = Table(summary_data, colWidths=[80*mm, 80*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Positions Table
        elements.append(Paragraph("Placement Details", heading_style))
        
        positions = stowage_plan.get('positions', stowage_plan.get('placements', []))
        if positions:
            table_data = [['#', 'Item', 'X', 'Y', 'Z', 'Weight']]
            for i, pos in enumerate(positions[:50], 1):  # Limit to 50 for PDF
                flat = self._flatten_position(pos)
                table_data.append([
                    str(i),
                    str(flat.get('container_id', ''))[:15],
                    str(flat.get('position_x', '')),
                    str(flat.get('position_y', '')),
                    str(flat.get('position_z', '')),
                    str(flat.get('weight_kg', ''))
                ])
            
            pos_table = Table(table_data, colWidths=[15*mm, 40*mm, 25*mm, 25*mm, 25*mm, 30*mm])
            pos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ]))
            elements.append(pos_table)
            
            if len(positions) > 50:
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"... and {len(positions) - 50} more items (see full export)", styles['Italic']))
        
        doc.build(elements)
        return str(filepath)
    
    def export_baplie(
        self,
        stowage_plan: Dict,
        filename: Optional[str] = None
    ) -> str:
        """
        Export stowage plan to BAPLIE (EDI) format.
        
        BAPLIE is the standard EDI format for container stowage plans.
        
        Args:
            stowage_plan: Stowage plan data
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"stowage_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.edi"
        
        filepath = self.output_dir / filename
        
        lines = []
        timestamp = datetime.now().strftime('%y%m%d:%H%M')
        
        # UNB - Interchange header
        lines.append(f"UNB+UNOA:2+CARGOOPT+RECEIVER+{timestamp}+1'")
        
        # UNH - Message header
        lines.append("UNH+1+BAPLIE:D:95B:UN'")
        
        # BGM - Beginning of message
        lines.append(f"BGM+45+{stowage_plan.get('plan_id', 'PLAN001')}+9'")
        
        # DTM - Date/time
        lines.append(f"DTM+137:{datetime.now().strftime('%Y%m%d%H%M')}:203'")
        
        # TDT - Transport details
        vessel_id = stowage_plan.get('vessel_id', 'VESSEL001')
        lines.append(f"TDT+20+{stowage_plan.get('voyage', 'VOY001')}+++{vessel_id}'")
        
        # LOC - Locations
        lines.append(f"LOC+5+{stowage_plan.get('port_of_loading', 'XXXXX')}:139:6'")
        lines.append(f"LOC+61+{stowage_plan.get('port_of_discharge', 'YYYYY')}:139:6'")
        
        # Container details
        positions = stowage_plan.get('positions', stowage_plan.get('placements', []))
        for pos in positions:
            flat = self._flatten_position(pos)
            container_id = flat.get('container_id', 'XXXX0000000')
            
            # LOC - Stowage position
            bay = flat.get('bay', 1)
            row = flat.get('row', 1)
            tier = flat.get('tier', 1)
            lines.append(f"LOC+147+{bay:02d}{row:02d}{tier:02d}::5'")
            
            # EQD - Equipment details
            lines.append(f"EQD+CN+{container_id}+22G1:102:5'")
            
            # MEA - Measurements (weight)
            weight = flat.get('weight_kg', 0)
            lines.append(f"MEA+AAE+G+KGM:{weight}'")
        
        # UNT - Message trailer
        lines.append(f"UNT+{len(lines) + 1}+1'")
        
        # UNZ - Interchange trailer
        lines.append("UNZ+1+1'")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)


class OptimizationResultExporter:
    """
    Export container optimization results.
    """
    
    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stowage_exporter = StowagePlanExporter(output_dir)
    
    def export(
        self,
        result: Dict,
        format: str = 'json',
        filename: Optional[str] = None
    ) -> str:
        """
        Export optimization result in specified format.
        
        Args:
            result: Optimization result
            format: Export format ('json', 'csv', 'xlsx', 'pdf')
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        format_lower = format.lower()
        
        if format_lower == 'json':
            return self.stowage_exporter.export_to_json(result, filename)
        elif format_lower == 'csv':
            return self.stowage_exporter.export_to_csv(result, filename)
        elif format_lower == 'xlsx':
            return self.stowage_exporter.export_to_xlsx(result, filename)
        elif format_lower == 'pdf':
            return self.stowage_exporter.export_to_pdf(result, filename)
        elif format_lower == 'baplie' or format_lower == 'edi':
            return self.stowage_exporter.export_baplie(result, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_all_formats(self, result: Dict, base_filename: str = None) -> Dict[str, str]:
        """
        Export to all available formats.
        
        Args:
            result: Optimization result
            base_filename: Base filename without extension
            
        Returns:
            Dictionary of format -> filepath
        """
        if not base_filename:
            base_filename = f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        exports = {}
        
        exports['json'] = self.export(result, 'json', f"{base_filename}.json")
        exports['csv'] = self.export(result, 'csv', f"{base_filename}.csv")
        
        if XLSX_AVAILABLE:
            exports['xlsx'] = self.export(result, 'xlsx', f"{base_filename}.xlsx")
        
        if REPORTLAB_AVAILABLE:
            exports['pdf'] = self.export(result, 'pdf', f"{base_filename}.pdf")
        
        return exports


# Utility functions
def export_optimization_result(result: Dict, format: str = 'json', output_dir: str = "data/exports") -> str:
    """
    Convenience function to export optimization result.
    
    Args:
        result: Optimization result dictionary
        format: Export format
        output_dir: Output directory
        
    Returns:
        Path to exported file
    """
    exporter = OptimizationResultExporter(output_dir)
    return exporter.export(result, format)


def export_stowage_plan(plan: Dict, format: str = 'json', output_dir: str = "data/exports") -> str:
    """
    Convenience function to export stowage plan.
    
    Args:
        plan: Stowage plan dictionary
        format: Export format
        output_dir: Output directory
        
    Returns:
        Path to exported file
    """
    exporter = StowagePlanExporter(output_dir)
    
    if format.lower() == 'json':
        return exporter.export_to_json(plan)
    elif format.lower() == 'csv':
        return exporter.export_to_csv(plan)
    elif format.lower() == 'xlsx':
        return exporter.export_to_xlsx(plan)
    elif format.lower() == 'pdf':
        return exporter.export_to_pdf(plan)
    elif format.lower() in ('baplie', 'edi'):
        return exporter.export_baplie(plan)
    else:
        raise ValueError(f"Unsupported format: {format}")


if __name__ == "__main__":
    # Example usage
    sample_result = {
        "optimization_id": "OPT-2025-001",
        "status": "completed",
        "utilization": 85.5,
        "computation_time": 12.34,
        "algorithm": "genetic",
        "placements": [
            {"item_index": 0, "x": 0, "y": 0, "z": 0, "length": 1000, "width": 800, "height": 600, "weight": 50},
            {"item_index": 1, "x": 1000, "y": 0, "z": 0, "length": 800, "width": 600, "height": 400, "weight": 30},
        ]
    }
    
    exporter = OptimizationResultExporter()
    
    # Export to JSON
    json_path = exporter.export(sample_result, 'json')
    print(f"Exported to JSON: {json_path}")
    
    # Export to CSV
    csv_path = exporter.export(sample_result, 'csv')
    print(f"Exported to CSV: {csv_path}")