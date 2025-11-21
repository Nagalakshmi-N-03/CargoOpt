"""
Logging Utilities
Centralized logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.config.settings import Config


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    log_format: str = None
) -> None:
    """
    Setup application-wide logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_format: Log message format
    """
    config = Config()
    
    level = log_level or config.LOG_LEVEL
    file_path = log_file or config.LOG_FILE
    format_str = log_format or config.LOG_FORMAT
    
    # Create logs directory if needed
    if file_path:
        log_dir = Path(file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(file_path) if file_path else logging.NullHandler()
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter with additional context."""
    
    def process(self, msg, kwargs):
        """Add context information to log messages."""
        context = self.extra.get('context', {})
        if context:
            context_str = ' '.join(f'{k}={v}' for k, v in context.items())
            msg = f"[{context_str}] {msg}"
        return msg, kwargs


def get_request_logger(
    name: str,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> LoggerAdapter:
    """
    Get a logger with request context.
    
    Args:
        name: Logger name
        request_id: Request ID
        user_id: User ID
        
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    context = {}
    
    if request_id:
        context['request_id'] = request_id
    if user_id:
        context['user_id'] = user_id
    
    return LoggerAdapter(logger, {'context': context})


class PerformanceLogger:
    """Context manager for logging execution time."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} ({duration:.3f}s)")
        else:
            self.logger.error(
                f"Failed: {self.operation} ({duration:.3f}s) - {exc_val}"
            )
        
        return False  # Don't suppress exceptions


# Initialize logging on module import
setup_logging()