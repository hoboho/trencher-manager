import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    """Set up a logger with both file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # File handler with rotation
    log_file = os.path.join(log_dir, f'{name}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters and add them to the handlers
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_action(logger, action_type, details, user=None):
    """Log a user action with details."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_info = f" by user '{user}'" if user else ""
    logger.info(f"{action_type}{user_info}: {details}")

def log_error(logger, error_type, error_message, user=None):
    """Log an error with details."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_info = f" by user '{user}'" if user else ""
    logger.error(f"{error_type}{user_info}: {error_message}")

def log_warning(logger, warning_type, warning_message, user=None):
    """Log a warning with details."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_info = f" by user '{user}'" if user else ""
    logger.warning(f"{warning_type}{user_info}: {warning_message}") 