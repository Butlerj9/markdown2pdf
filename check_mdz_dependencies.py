#!/usr/bin/env python3
"""
MDZ Dependencies Checker
-----------------------
This script checks for all required dependencies for the MDZ format
and offers to install missing dependencies.

File: check_mdz_dependencies.py
"""

import sys
import subprocess
import importlib.util
import logging
import os
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define required and optional dependencies
REQUIRED_DEPENDENCIES = {
    "zstandard": "zstandard",
    "yaml": "pyyaml"
}

# At least one of these Markdown parsers is required
MARKDOWN_PARSERS = {
    "markdown_it": "markdown-it-py",
    "markdown": "markdown",
    "mistune": "mistune"
}

OPTIONAL_DEPENDENCIES = {
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "pymdownx": "pymdown-extensions",
    "mdit_py_plugins": "mdit-py-plugins"
}

# External tools
EXTERNAL_TOOLS = [
    "pandoc",
    "mmdc"  # Mermaid CLI
]

def check_python_package(package_name: str, import_name: str) -> bool:
    """
    Check if a Python package is installed
    
    Args:
        package_name: Name of the package (for pip)
        import_name: Name of the module to import
        
    Returns:
        True if the package is installed, False otherwise
    """
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            logger.warning(f"Python package {package_name} is not installed")
            return False
        
        # Try to import the module to make sure it works
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown version")
        logger.info(f"Python package {package_name} is installed (version: {version})")
        return True
    except ImportError:
        logger.warning(f"Python package {package_name} is not installed")
        return False
    except Exception as e:
        logger.warning(f"Error checking Python package {package_name}: {str(e)}")
        return False

def check_external_tool(tool_name: str) -> bool:
    """
    Check if an external tool is installed
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        True if the tool is installed, False otherwise
    """
    try:
        # Try to run the tool with --version
        result = subprocess.run([tool_name, "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode == 0:
            version = result.stdout.strip() if result.stdout else "unknown version"
            logger.info(f"External tool {tool_name} is installed (version: {version})")
            return True
        else:
            logger.warning(f"External tool {tool_name} is not installed or not working")
            return False
    except FileNotFoundError:
        logger.warning(f"External tool {tool_name} is not installed")
        return False
    except Exception as e:
        logger.warning(f"Error checking external tool {tool_name}: {str(e)}")
        return False

def install_python_package(package_name: str) -> bool:
    """
    Install a Python package using pip
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        True if the installation was successful, False otherwise
    """
    try:
        logger.info(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        logger.error(f"Failed to install {package_name}")
        return False
    except Exception as e:
        logger.error(f"Error installing {package_name}: {str(e)}")
        return False

def install_external_tool(tool_name: str) -> bool:
    """
    Provide instructions for installing external tools
    
    Args:
        tool_name: Name of the tool to install
        
    Returns:
        True if the user confirms installation, False otherwise
    """
    if tool_name == "pandoc":
        print("\nPandoc Installation Instructions:")
        print("--------------------------------")
        print("1. Visit https://pandoc.org/installing.html")
        print("2. Download and install the appropriate version for your system")
        print("3. Restart your terminal/command prompt after installation")
        print("4. Run 'pandoc --version' to verify the installation")
    elif tool_name == "mmdc":
        print("\nMermaid CLI Installation Instructions:")
        print("------------------------------------")
        print("1. Make sure Node.js is installed (https://nodejs.org/)")
        print("2. Run 'npm install -g @mermaid-js/mermaid-cli'")
        print("3. Run 'mmdc --version' to verify the installation")
    
    install = input(f"\nWould you like to attempt automatic installation of {tool_name}? (y/n): ")
    if install.lower() == 'y':
        if tool_name == "pandoc":
            if sys.platform == "win32":
                # Windows installation
                try:
                    print("Downloading Pandoc installer...")
                    subprocess.run(["powershell", "-Command", 
                                   "Invoke-WebRequest -Uri https://github.com/jgm/pandoc/releases/download/3.1.12.1/pandoc-3.1.12.1-windows-x86_64.msi -OutFile pandoc-installer.msi"], 
                                  check=True)
                    print("Installing Pandoc...")
                    subprocess.run(["msiexec", "/i", "pandoc-installer.msi", "/quiet", "/norestart"], 
                                  check=True)
                    print("Pandoc installed successfully")
                    return True
                except Exception as e:
                    print(f"Error installing Pandoc: {str(e)}")
                    return False
            elif sys.platform == "darwin":
                # macOS installation
                try:
                    print("Installing Pandoc using Homebrew...")
                    subprocess.run(["brew", "install", "pandoc"], check=True)
                    print("Pandoc installed successfully")
                    return True
                except Exception as e:
                    print(f"Error installing Pandoc: {str(e)}")
                    return False
            else:
                # Linux installation
                try:
                    print("Installing Pandoc using apt...")
                    subprocess.run(["sudo", "apt", "install", "pandoc"], check=True)
                    print("Pandoc installed successfully")
                    return True
                except Exception as e:
                    print(f"Error installing Pandoc: {str(e)}")
                    return False
        elif tool_name == "mmdc":
            try:
                print("Installing Mermaid CLI...")
                subprocess.run(["npm", "install", "-g", "@mermaid-js/mermaid-cli"], check=True)
                print("Mermaid CLI installed successfully")
                return True
            except Exception as e:
                print(f"Error installing Mermaid CLI: {str(e)}")
                return False
    
    return False

def check_dependencies() -> Tuple[bool, List[str], List[str], List[str]]:
    """
    Check all dependencies
    
    Returns:
        Tuple of (all_required_installed, missing_required, missing_markdown_parsers, missing_optional)
    """
    missing_required = []
    missing_markdown_parsers = []
    missing_optional = []
    
    # Check required dependencies
    for import_name, package_name in REQUIRED_DEPENDENCIES.items():
        if not check_python_package(package_name, import_name):
            missing_required.append(package_name)
    
    # Check Markdown parsers
    markdown_parser_installed = False
    for import_name, package_name in MARKDOWN_PARSERS.items():
        if check_python_package(package_name, import_name):
            markdown_parser_installed = True
            break
    
    if not markdown_parser_installed:
        # Add the preferred Markdown parser to the missing list
        missing_markdown_parsers = ["markdown-it-py", "mdit-py-plugins"]
    
    # Check optional dependencies
    for import_name, package_name in OPTIONAL_DEPENDENCIES.items():
        if not check_python_package(package_name, import_name):
            missing_optional.append(package_name)
    
    # Check external tools
    for tool_name in EXTERNAL_TOOLS:
        check_external_tool(tool_name)
    
    # Return the results
    all_required_installed = len(missing_required) == 0 and markdown_parser_installed
    return (all_required_installed, missing_required, missing_markdown_parsers, missing_optional)

def main():
    """Main function"""
    print("MDZ Dependencies Checker")
    print("=======================")
    
    # Check dependencies
    all_required_installed, missing_required, missing_markdown_parsers, missing_optional = check_dependencies()
    
    if all_required_installed:
        print("\nAll required dependencies are installed!")
    else:
        print("\nSome required dependencies are missing.")
        
        # Ask to install missing required dependencies
        if missing_required:
            print(f"\nMissing required dependencies: {', '.join(missing_required)}")
            install = input("Would you like to install the missing required dependencies? (y/n): ")
            if install.lower() == 'y':
                for package in missing_required:
                    install_python_package(package)
        
        # Ask to install a Markdown parser if none is installed
        if missing_markdown_parsers:
            print("\nNo Markdown parser is installed. At least one is required.")
            install = input("Would you like to install the recommended Markdown parser (markdown-it-py)? (y/n): ")
            if install.lower() == 'y':
                for package in missing_markdown_parsers:
                    install_python_package(package)
    
    # Ask to install missing optional dependencies
    if missing_optional:
        print(f"\nMissing optional dependencies: {', '.join(missing_optional)}")
        install = input("Would you like to install the missing optional dependencies? (y/n): ")
        if install.lower() == 'y':
            for package in missing_optional:
                install_python_package(package)
    
    # Check external tools again
    print("\nChecking external tools...")
    for tool_name in EXTERNAL_TOOLS:
        if not check_external_tool(tool_name):
            install = input(f"Would you like to install {tool_name}? (y/n): ")
            if install.lower() == 'y':
                install_external_tool(tool_name)
    
    print("\nDependency check completed.")

if __name__ == "__main__":
    main()
