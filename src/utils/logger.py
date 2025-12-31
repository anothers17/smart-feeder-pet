"""Logging utility for Smart Pet Feeder.

Provides centralized logging configuration for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from config.constants import Constants


# Global logger cache
_loggers = {}


def get_logger(name: str, log_file: Optional[str] = None, log_level: str = 'INFO') -> logging.Logger:
    """Get or create a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Optional log file path. If None, logs to console only.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Return cached logger if exists
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        Constants.LOG_FORMAT,
        datefmt=Constants.LOG_DATE_FORMAT
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    # Cache logger
    _loggers[name] = logger
    
    return logger


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """Setup root logger configuration.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=Constants.LOG_FORMAT,
        datefmt=Constants.LOG_DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(
                logging.Formatter(Constants.LOG_FORMAT, datefmt=Constants.LOG_DATE_FORMAT)
            )
            logging.getLogger().addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Could not create log file {log_file}: {e}")
