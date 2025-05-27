#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter - Main Entry Point
----------------------------------------------------
This script launches the Markdown to PDF converter application with MDZ format support.
File: main.py
"""

import sys
import os
import logging
import time
from typing import Dict, List, Optional, Tuple, Set
from PyQt6.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt6.QtCore import QSettings, Qt
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import initialize_logger, get_logger

# Configure logger
logger = initialize_logger()

# Message tracking for duplicate detection
class MessageTracker:
    """Tracks messages to detect duplicates in the terminal output"""

    def __init__(self):
        self.messages: Set[str] = set()
        self.duplicates: Dict[str, int] = {}

    def track(self, message: str) -> bool:
        """
        Track a message and detect if it's a duplicate

        Args:
            message: The message to track

        Returns:
            True if the message is a duplicate, False otherwise
        """
        # Normalize the message to ignore case and whitespace
        normalized = ' '.join(message.lower().split())

        if normalized in self.messages:
            if normalized in self.duplicates:
                self.duplicates[normalized] += 1
            else:
                self.duplicates[normalized] = 1
            return True

        self.messages.add(normalized)
        return False

    def get_duplicate_count(self) -> int:
        """Get the total number of duplicate messages"""
        return sum(self.duplicates.values())

    def get_duplicate_summary(self) -> str:
        """Get a summary of duplicate messages"""
        if not self.duplicates:
            return "No duplicate messages detected."

        summary = f"Found {len(self.duplicates)} unique messages duplicated {self.get_duplicate_count()} times:\n"
        for message, count in sorted(self.duplicates.items(), key=lambda x: x[1], reverse=True):
            # Truncate long messages
            display_message = message[:50] + "..." if len(message) > 50 else message
            summary += f"- '{display_message}' repeated {count} times\n"

        return summary

# Create a global message tracker
message_tracker = MessageTracker()

# Custom logger handler to track messages
class DuplicateDetectionHandler(logging.Handler):
    """Logging handler that detects duplicate messages"""

    def emit(self, record):
        message = self.format(record)
        is_duplicate = message_tracker.track(message)
        if is_duplicate:
            # Add a note about the duplicate
            print(f"DUPLICATE: {message}")

def check_dependencies() -> Tuple[bool, Optional[str]]:
    """
    Check for critical dependencies like Pandoc

    Returns:
        Tuple of (success, error_message)
    """
    logger.info("Checking application dependencies...")

    # Check for Pandoc
    from shutil import which
    import subprocess

    pandoc_path = which('pandoc')
    if pandoc_path:
        try:
            result = subprocess.run(['pandoc', '--version'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            pandoc_version = result.stdout.splitlines()[0] if result.stdout else "Unknown version"
            logger.info(f"Pandoc found: {pandoc_version}")
        except Exception as e:
            logger.warning(f"Pandoc found at {pandoc_path} but version check failed: {str(e)}")
    else:
        logger.warning("Pandoc not found. PDF export functionality may be limited.")
        return False, "Pandoc not found. PDF export functionality may be limited."

    # Check for MDZ dependencies
    try:
        import zstandard
        logger.info("Zstandard library found for MDZ support")
    except ImportError:
        logger.warning("Zstandard library not found. MDZ format support will be limited.")
        return False, "Zstandard library not found. MDZ format support will be limited."

    return True, None

def setup_mdz_support(window) -> bool:
    """
    Set up MDZ format support

    Args:
        window: The main application window

    Returns:
        True if MDZ support was enabled, False otherwise
    """
    logger.info("Setting up MDZ format support...")

    # Add the current directory to the Python path if not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        logger.info(f"Added current directory to Python path: {current_dir}")

    try:
        # Check if the MDZ integration module is available
        try:
            from mdz_integration import integrate_mdz
            logger.info("MDZ integration module found")
        except ImportError:
            # Try to find the module in the current directory
            module_path = os.path.join(current_dir, 'mdz_integration.py')
            if os.path.exists(module_path):
                logger.info(f"Found mdz_integration.py at {module_path}")
                # Use importlib to import the module
                import importlib.util
                spec = importlib.util.spec_from_file_location("mdz_integration", module_path)
                mdz_integration_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mdz_integration_module)
                integrate_mdz = mdz_integration_module.integrate_mdz
                logger.info("Successfully imported mdz_integration module using importlib")
            else:
                logger.warning(f"mdz_integration.py not found in {current_dir}")
                raise ImportError("MDZ integration module not found")

        # Integrate MDZ format
        mdz_integration = integrate_mdz(window)

        if mdz_integration:
            logger.info("MDZ format support enabled")
            return True
        else:
            logger.warning("Failed to enable MDZ format support")
            return False
    except ImportError as e:
        logger.warning(f"MDZ integration module not found. MDZ format support will not be available. Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error setting up MDZ format support: {str(e)}")
        return False

def main():
    """
    Main entry point for the application

    Returns:
        Application exit code
    """
    # Add duplicate detection handler to the logger
    duplicate_handler = DuplicateDetectionHandler()
    duplicate_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    duplicate_handler.setFormatter(formatter)
    logging.getLogger().addHandler(duplicate_handler)

    logger.info("Starting Advanced Markdown to PDF Converter")
    start_time = time.time()

    # Check dependencies
    deps_ok, error_msg = check_dependencies()
    if not deps_ok:
        # Show a warning but continue anyway
        QMessageBox.warning(None, "Missing Dependencies",
                          error_msg or "Some required dependencies are missing.")

    # Import PyQt6.QtWebEngineWidgets before creating QApplication
    # This is required to avoid issues with duplicate page preview instances
    try:
        from PyQt6 import QtWebEngineWidgets
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        logger.info("Successfully imported QtWebEngineWidgets before creating QApplication")
    except ImportError as e:
        logger.warning(f"Failed to import QtWebEngineWidgets: {str(e)}")

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced Markdown to PDF Converter")
    app.setOrganizationName("MarkdownToPDF")

    # Create and show the main window
    window = AdvancedMarkdownToPDF()

    # Restore window geometry if available
    settings = QSettings("MarkdownToPDF", "AdvancedConverter")
    if settings.contains("window_geometry"):
        window.restoreGeometry(settings.value("window_geometry"))

    # Save settings before exit
    app.aboutToQuit.connect(window.save_settings)

    # Set up MDZ format support
    mdz_support = setup_mdz_support(window)
    if mdz_support:
        window.setWindowTitle(window.windowTitle() + " (with MDZ support)")

    # Show the window
    window.show()

    # Log startup time
    elapsed_time = time.time() - start_time
    logger.info(f"Application startup completed in {elapsed_time:.2f} seconds")

    # Enter the application event loop
    result = app.exec()

    # Log application exit and duplicate message summary
    logger.info(f"Application exited with code: {result}")
    logger.info(message_tracker.get_duplicate_summary())

    return result

if __name__ == "__main__":
    sys.exit(main())
