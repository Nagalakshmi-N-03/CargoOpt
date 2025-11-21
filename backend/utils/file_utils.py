"""
File Utility Functions
File handling and directory management utilities.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import hashlib


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm
        
    Returns:
        Hex digest of file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """Format file size for display."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


class FileHandler:
    """Handles file operations for the application."""
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> str:
        """Save data to JSON file."""
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return file_path
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """Copy a file."""
        try:
            ensure_directory(os.path.dirname(destination))
            shutil.copy2(source, destination)
            return True
        except Exception:
            return False
    
    @staticmethod
    def list_files(
        directory: str,
        extension: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """List files in directory."""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return []
        
        if recursive:
            pattern = f'**/*{extension}' if extension else '**/*'
            files = dir_path.glob(pattern)
        else:
            pattern = f'*{extension}' if extension else '*'
            files = dir_path.glob(pattern)
        
        return [str(f) for f in files if f.is_file()]
    
    @staticmethod
    def cleanup_old_files(directory: str, days: int = 30) -> int:
        """Delete files older than specified days."""
        count = 0
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for file_path in FileHandler.list_files(directory, recursive=True):
            if os.path.getmtime(file_path) < cutoff:
                if FileHandler.delete_file(file_path):
                    count += 1
        
        return count