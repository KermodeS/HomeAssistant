#!/usr/bin/env python3
"""
Unified logging module for Home Assistant automation scripts
"""
import os
import datetime
import logging
from .config_manager import config_manager


class Logger:
    """Unified logger for automation scripts with file and console output"""
    
    def __init__(self, module_name, log_dir="/config/www/logs"):
        """
        Initialize the logger
        
        Args:
            module_name: Name of the module using this logger
            log_dir: Directory to store log files
        """
        self.module_name = module_name
        self.log_dir = log_dir
        self.verbose = config_manager.is_enabled('debug.verbose_logging')
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                print(f"Error creating log directory {log_dir}: {str(e)}")
        
        # Set up file path
        self.log_file = f"{log_dir}/{module_name}.log"
        
        # Set up Python logger
        self.logger = logging.getLogger(module_name)
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Add file handler
        try:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error setting up log file {self.log_file}: {str(e)}")
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def section(self, title):
        """Create a section divider in the log"""
        self.logger.info(f"===== {title} =====")


def get_logger(module_name):
    """Get a logger for the specified module"""
    return Logger(module_name)


if __name__ == "__main__":
    # Test the logger
    test_logger = get_logger("test")
    test_logger.section("Testing Logger")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")