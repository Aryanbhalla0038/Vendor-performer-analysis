"""Logging configuration utility."""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_dir: Path, level=logging.INFO):
    """Set up logger with file and console handlers."""
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotates daily)
    log_file = log_dir / f"vendor_analysis_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger
