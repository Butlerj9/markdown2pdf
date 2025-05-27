#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter - Main Entry Point with MDZ Support
----------------------------------------------------
This script launches the Markdown to PDF converter application with MDZ format support.
File: main_with_mdz.py
"""

import sys
import os
import logging
import time
from typing import Dict, List, Optional, Tuple, Set
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings, Qt
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import initialize_logger, get_logger

os.environ["PATH"] += os.pathsep + r"C:\Users\joshd\AppData\Roaming\npm"

# Configure logger
logger = initialize_logger()

# Track start time for performance monitoring
start_time = time.time()

# Create a message tracker to detect duplicate messages
class MessageTracker:
    def __init__(self):
        self.message_counts = {}

    def track(self, message):
        if message in self.message_counts:
            self.message_counts[message] += 1
        else:
            self.message_counts[message] = 1

    def get_duplicate_summary(self):
        duplicates = {msg: count for msg, count in self.message_counts.items() if count > 1}
        if duplicates:
            return f"Duplicate messages detected: {duplicates}"
        else:
            return "No duplicate messages detected"

# Create a message tracker instance
message_tracker = MessageTracker()

def check_dependencies():
    """Check for critical dependencies like Pandoc"""
    logger.info("Checking application dependencies...")

    # Check for Pandoc
    from shutil import which
    import subprocess

    pandoc_path = which('pandoc')
    if pandoc_path:
        try:
            result = subprocess.run(['pandoc', '--version'], shell=True,
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

    # Check for Node.js (for Mermaid)
    node_path = which('node') or which('nodejs')
    if node_path:
        try:
            result = subprocess.run(['node', '--version'], shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            node_version = result.stdout.strip()
            logger.info(f"Node.js found: {node_version}")
        except Exception as e:
            logger.warning(f"Node.js found at {node_path} but version check failed: {str(e)}")
    else:
        logger.warning("Node.js not found. Using fallback rendering for Mermaid diagrams.")

    # Check for Mermaid CLI
    mmdc_path = which('mmdc')
    if mmdc_path:
        try:
            result = subprocess.run(['mmdc', '--version'], shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            mmdc_version = result.stdout.strip() if result.stdout else "Unknown version"
            logger.info(f"Mermaid CLI found: {mmdc_version}")
        except Exception as e:
            logger.warning(f"Mermaid CLI found at {mmdc_path} but version check failed: {str(e)}")
    else:
        current_path = os.environ.get("PATH", "")
        print("Current PATH:")
        print(current_path)
        print("-" * 80)
        for p in os.environ["PATH"].split(os.pathsep):
            candidate = os.path.join(p, "mmdc.cmd")
            print(candidate)
            if os.path.isfile(candidate):
                path = candidate
                logger.info(f"Found Mermaid CLI at {path}")
                break
            else:
                logger.warning("Mermaid CLI not found. Using fallback rendering for Mermaid diagrams.")

    # Check for MDZ dependencies
    try:
        import zstandard
        logger.info("Zstandard library found for MDZ support")
    except ImportError:
        logger.warning("Zstandard library not found. MDZ format support will be limited.")
        return False, "Zstandard library not found. MDZ format support will be limited."

    return True, None

def setup_mermaid():
    """Set up Mermaid resources"""
    logger.info("Setting up Mermaid resources...")

    # Try to import the local fallback module
    try:
        from mermaid_local_fallback import find_mermaid_js, copy_mermaid_to_resources, create_resources_directory

        # Create resources directory if needed
        resources_dir = create_resources_directory()
        if resources_dir:
            # Check if mermaid.min.js already exists in resources
            js_path = os.path.join(resources_dir, "mermaid.min.js")
            if os.path.exists(js_path):
                file_size = os.path.getsize(js_path)
                if file_size > 100000:  # Reasonable size for mermaid.min.js
                    logger.info(f"Found existing Mermaid.js in resources: {js_path}")
                    return True
                else:
                    logger.warning(f"Existing Mermaid.js is too small ({file_size} bytes), will attempt to replace")

            # Try to copy from system
            local_path = find_mermaid_js()
            if local_path:
                # Copy to resources
                try:
                    import shutil
                    shutil.copy2(local_path, js_path)
                    logger.info(f"Copied Mermaid.js from {local_path} to {js_path}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to copy Mermaid.js: {str(e)}")
            else:
                # Try direct copy function
                copied_path = copy_mermaid_to_resources()
                if copied_path:
                    logger.info(f"Successfully copied Mermaid.js to resources: {copied_path}")
                    return True
                else:
                    logger.warning("Could not find Mermaid.js to copy to resources. Will use fallback rendering.")
        else:
            logger.error("Failed to create resources directory")
    except Exception as e:
        logger.error(f"Error in Mermaid setup: {str(e)}")

    # If we get here, we weren't able to set up Mermaid resources
    return False

def download_mermaid_from_cdn():
    """Download a known-compatible version of mermaid.min.js from CDN
    Set up Mermaid resources with enhanced error handling and recovery mechanisms.
    Add this to your main.py file's initialization sequence.
    """
    logger.info("Setting up Mermaid resources...")

    # Import our local mermaid modules
    from mermaid_local_fallback import download_compatible_mermaid_js

    # Create resources directory and download compatible Mermaid.js
    mermaid_js_path = download_compatible_mermaid_js()

    if mermaid_js_path and os.path.exists(mermaid_js_path):
        logger.info(f"Mermaid.js successfully set up at: {mermaid_js_path}")
        return True
    else:
        logger.warning("Failed to set up local Mermaid.js, application will use CDN fallback")
        return False

def setup_mdz_support(window):
    """Set up MDZ format support"""
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
    """Main entry point for the application"""
    logger.info("Starting Advanced Markdown to PDF Converter with MDZ support")

    # Check dependencies
    deps_ok, error_msg = check_dependencies()
    if not deps_ok:
        # Show a warning but continue anyway
        QMessageBox.warning(None, "Missing Dependencies",
                          error_msg or "Some required dependencies are missing.")

    # Set up Mermaid resources
    setup_mermaid()

    # Import PyQt6.QtWebEngineWidgets before creating QApplication
    # This is required to avoid issues with duplicate page preview instances
    try:
        from PyQt6 import QtWebEngineWidgets
        from PyQt6.QtCore import QCoreApplication, Qt
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

    # Enter the application event loop
    result = app.exec()

    # Log application exit and duplicate message summary
    logger.info(f"Application exited with code: {result}")
    logger.info(message_tracker.get_duplicate_summary())

    # Calculate and log total execution time
    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

    return result

if __name__ == "__main__":
    sys.exit(main())
