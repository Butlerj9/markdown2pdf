#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter - Logging Configuration
----------------------------------------------------------
File: src--logging_config.py
Sets up an enhanced logging system for the Markdown to PDF Converter
application to facilitate debugging and troubleshooting.
"""

import os
import sys
import logging
import traceback
from datetime import datetime

class EnhancedLogger:
    """Provides enhanced logging capabilities for the application."""
    
    _instance = None
    logger = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance of the logger"""
        if cls._instance is None:
            cls._instance = EnhancedLogger()
        return cls._instance
    
    def __init__(self):
        """Initialize the enhanced logger configuration"""
        if self.logger is not None:
            return
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.expanduser("~"), ".markdown_pdf_logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create timestamped log file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"markdown_pdf_debug_{timestamp}.log")
        
        # Store the log file path
        self.log_file_path = log_file
        
        # Create a custom logger
        self.logger = logging.getLogger('MarkdownToPDF')
        
        # Clear any existing handlers to prevent duplication
        while self.logger.handlers:
            self.logger.removeHandler(self.logger.handlers[0])
        
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters
        file_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        
        # Only add console handler if not in quiet mode
        if not os.environ.get('MARKDOWN_PDF_QUIET', False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logging to file: {log_file}")
    
    def get_logger(self):
        """Get the configured logger"""
        return self.logger
    
    def get_log_file_path(self):
        """Get the current log file path"""
        return self.log_file_path
    
    @staticmethod
    def log_exception(logger, e):
        """Log exception with full traceback"""
        logger.error(f"Exception: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
    
    @staticmethod
    def log_function_entry(logger, func_name, *args, **kwargs):
        """Log function entry with arguments"""
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        params = f"{args_str}{', ' if args_str and kwargs_str else ''}{kwargs_str}"
        logger.debug(f"Entering function: {func_name}({params})")
    
    @staticmethod
    def log_function_exit(logger, func_name, result=None):
        """Log function exit with optional result"""
        if result is not None:
            result_str = str(result)
            if len(result_str) > 1000:
                result_str = result_str[:1000] + "... [truncated]"
            logger.debug(f"Exiting function: {func_name} with result: {result_str}")
        else:
            logger.debug(f"Exiting function: {func_name}")
    
    @staticmethod
    def log_ui_action(logger, action, details=None):
        """Log user interface action"""
        if details:
            logger.info(f"UI Action: {action} - {details}")
        else:
            logger.info(f"UI Action: {action}")
    
    @staticmethod
    def log_command(logger, command):
        """Log executable command"""
        logger.debug(f"Running command: {' '.join(command)}")

def initialize_logger():
    """Initialize and return the enhanced logger"""
    logger_instance = EnhancedLogger.get_instance()
    logger = logger_instance.get_logger()
    
    # Ensure we're not adding duplicate exception hooks
    # Remove existing exception hook if it's already set
    if hasattr(sys, 'excepthook') and sys.excepthook.__name__ == 'exception_hook':
        # Restore the original exception hook
        if hasattr(sys, '__excepthook__'):
            sys.excepthook = sys.__excepthook__
    
    # Log system information
    logger.info("Initializing Advanced Markdown to PDF Converter")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    # Add exception hook to log unhandled exceptions
    def exception_hook(exc_type, exc_value, exc_traceback):
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # Store the function name to check for duplicates later
    exception_hook.__name__ = 'exception_hook'
    sys.excepthook = exception_hook
    
    return logger

# Convenience function to get logger
def get_logger():
    """Get the application logger"""
    return EnhancedLogger.get_instance().get_logger()