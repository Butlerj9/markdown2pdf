#!/usr/bin/env python3
"""
MDZ Format Integration Script
---------------------------
This script integrates the MDZ format into the main application.

File: integrate_mdz_format.py
"""

import os
import sys
import logging
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    Check if all required dependencies are installed
    
    Returns:
        Tuple of (success, missing_dependencies)
    """
    required_packages = [
        "zstandard",
        "markdown",
        "PyQt6",
        "pyyaml"
    ]
    
    optional_packages = [
        "pymdownx",  # For GitHub Flavored Markdown
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_required.append(package)
    
    # Check optional packages
    for package in optional_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_optional.append(package)
    
    return (len(missing_required) == 0, missing_required, missing_optional)

def install_dependencies(packages):
    """
    Install missing dependencies
    
    Args:
        packages: List of packages to install
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import subprocess
        for package in packages:
            logger.info(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False

def integrate_mdz_format():
    """
    Integrate MDZ format into the main application
    
    Returns:
        True if successful, False otherwise
    """
    # Check dependencies
    deps_ok, missing_required, missing_optional = check_dependencies()
    
    if not deps_ok:
        logger.warning(f"Missing required dependencies: {', '.join(missing_required)}")
        print(f"Missing required dependencies: {', '.join(missing_required)}")
        
        # Ask to install missing dependencies
        install = input("Would you like to install the missing dependencies? (y/n): ")
        if install.lower() == 'y':
            if install_dependencies(missing_required):
                logger.info("Successfully installed required dependencies")
                print("Successfully installed required dependencies")
            else:
                logger.error("Failed to install required dependencies")
                print("Failed to install required dependencies")
                return False
        else:
            logger.warning("Required dependencies not installed")
            print("Required dependencies not installed")
            return False
    
    if missing_optional:
        logger.warning(f"Missing optional dependencies: {', '.join(missing_optional)}")
        print(f"Missing optional dependencies: {', '.join(missing_optional)}")
        
        # Ask to install missing optional dependencies
        install = input("Would you like to install the optional dependencies for enhanced features? (y/n): ")
        if install.lower() == 'y':
            if install_dependencies(missing_optional):
                logger.info("Successfully installed optional dependencies")
                print("Successfully installed optional dependencies")
            else:
                logger.warning("Failed to install optional dependencies")
                print("Failed to install optional dependencies")
    
    # Check if the main application is already running
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            logger.warning("No running application found")
            print("No running application found. Please run the main application first.")
            return False
    except Exception as e:
        logger.error(f"Error checking application: {str(e)}")
        print(f"Error checking application: {str(e)}")
        return False
    
    # Find the main window
    main_window = None
    for widget in app.topLevelWidgets():
        if widget.__class__.__name__ == "AdvancedMarkdownToPDF":
            main_window = widget
            break
    
    if main_window is None:
        logger.warning("Main window not found")
        print("Main window not found. Please run the main application first.")
        return False
    
    # Integrate MDZ format
    try:
        from mdz_integration import integrate_mdz
        mdz_integration = integrate_mdz(main_window)
        
        if mdz_integration is None:
            logger.error("Failed to integrate MDZ format")
            print("Failed to integrate MDZ format")
            return False
        
        logger.info("Successfully integrated MDZ format")
        print("Successfully integrated MDZ format")
        return True
    except Exception as e:
        logger.error(f"Error integrating MDZ format: {str(e)}")
        print(f"Error integrating MDZ format: {str(e)}")
        return False

def main():
    """
    Main function
    """
    print("MDZ Format Integration Script")
    print("-----------------------------")
    
    # Check if running as a script or imported as a module
    if __name__ != "__main__":
        logger.warning("This script should be run directly, not imported")
        return 1
    
    # Integrate MDZ format
    if integrate_mdz_format():
        print("\nMDZ format integration successful!")
        print("You can now open, save, and export MDZ files.")
        return 0
    else:
        print("\nMDZ format integration failed.")
        print("Please check the logs for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
