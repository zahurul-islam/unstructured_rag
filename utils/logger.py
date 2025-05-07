"""
Logging configuration module.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys

from app.config import config


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    log_to_console: bool = True,
    log_to_file: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
    """
    # Get log level from config if not specified
    log_level = log_level or config.app.log_level
    
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Set default log file if not specified
        if log_file is None:
            log_file = os.path.join(log_dir, "rag.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if log_to_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log configuration
    logging.info(f"Logging configured with level: {log_level}")
    if log_to_file:
        logging.info(f"Logging to file: {log_file}")


# Set up logging when module is imported
try:
    setup_logging()
except:
    # In case config is not available yet
    pass
