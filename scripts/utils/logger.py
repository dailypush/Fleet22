"""Centralized logging configuration for Fleet22 scripts."""
import logging
from pathlib import Path
from .path_utils import LOGS_DIR

def setup_logger(name: str, log_file: str = "scraping.log", 
                 level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Log file name (default: scraping.log)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Ensure log directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / log_file
    
    # File handler
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
