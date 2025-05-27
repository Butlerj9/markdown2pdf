#!/usr/bin/env python3
"""
Comprehensive test script for markdown to PDF converter
"""

import os
import sys
import time
import argparse
import subprocess
import json
import tempfile
from datetime import datetime

def check_dependencies():
    """Check for all required dependencies"""
    print("Checking dependencies...")

    # Check if Pandoc is installed
    pandoc_installed = False
    pandoc_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), "Pandoc", "pandoc.exe"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), "Pandoc", "pandoc.exe")
    ]

    for path in pandoc_paths:
        if os.path.exists(path):
            pandoc_installed = True
            print(f"✅ Pandoc is installed at {path}")
            break

    if not pandoc_installed:
        print("❌ Pandoc is not installed")
        print("Installing Pandoc...")
        try:
            # Download Pandoc installer
            subprocess.run(
                ["powershell", "-Command", "Invoke-WebRequest -Uri https://github.com/jgm/pandoc/releases/download/3.1.12.1/pandoc-3.1.12.1-windows-x86_64.msi -OutFile pandoc-installer.msi"],
                check=True
            )

            # Install Pandoc
            subprocess.run(
                ["msiexec", "/i", "pandoc-installer.msi", "/quiet", "/norestart"],
                check=True
            )

            print("Pandoc installed successfully")
            pandoc_installed = True
        except subprocess.CalledProcessError as e:
            print(f"Error installing Pandoc: {e}")

    # Check for Python packages
    required_packages = {
        "PyQt6": "PyQt6",
        "PyPDF2": "PyPDF2",
        "beautifulsoup4": "bs4",
        "lxml": "lxml",
        "ebooklib": "ebooklib",
        "python-docx": "docx"
    }

    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ Python package {package_name} is installed")
        except ImportError:
            print(f"❌ Python package {package_name} is not installed")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"Installing missing Python packages: {', '.join(missing_packages)}")
        try:
            subprocess.run(
                ["pip", "install"] + missing_packages,
                check=True
            )
            print("Python packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing Python packages: {e}")

    # Final check
    all_installed = pandoc_installed

    if all_installed:
        print("All critical dependencies are installed")
        return True
    else:
        print("Some critical dependencies are still missing")
        return False

def fix_pandoc_path():
    """Fix the Pandoc path in the application"""
    print("Fixing Pandoc path...")

    # Find Pandoc executable
    pandoc_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), "Pandoc", "pandoc.exe"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), "Pandoc", "pandoc.exe")
    ]

    pandoc_path = None
    for path in pandoc_paths:
        if os.path.exists(path):
            pandoc_path = path
            break

    if not pandoc_path:
        print("Error: Pandoc executable not found")
        return False

    print(f"Found Pandoc at: {pandoc_path}")

    # Update the Pandoc path in the application files
    files_to_update = [
        "markdown_to_pdf_converter.py",
        "markdown_to_pdf_export.py",
        "render_utils.py"
    ]

    for file_path in files_to_update:
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace 'pandoc' with the full path
        content = content.replace("['pandoc',", f"[r'{pandoc_path}',")
        content = content.replace("'pandoc',", f"r'{pandoc_path}',")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Updated Pandoc path in {file_path}")

    return True

def run_tests(formats=None, timeout=600):
    """Run the tests with concise output"""
    if formats is None:
        formats = ["pdf", "html", "epub", "docx"]

    print(f"Running tests for formats: {', '.join(formats)}")

    all_passed = True
    for format_type in formats:
        print(f"\nTesting {format_type.upper()} format...")

        cmd = ["python", "run_concise_tests.py", f"--format={format_type}", f"--timeout={timeout}"]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stdout)

        if "FAIL" in result.stdout or result.returncode != 0:
            all_passed = False

    return all_passed

def verify_output_files():
    """Verify that the output files match the expected settings"""
    print("\nVerifying output files...")

    # Find the latest test results directory
    temp_dirs = []
    for root, dirs, files in os.walk(tempfile.gettempdir()):
        for dir_name in dirs:
            if dir_name.startswith("tmp") and os.path.exists(os.path.join(root, dir_name, "test_results.json")):
                temp_dirs.append(os.path.join(root, dir_name))

    if not temp_dirs:
        print("No test results found")
        return False

    # Get the most recent directory
    latest_dir = max(temp_dirs, key=os.path.getmtime)
    print(f"Using test results from: {latest_dir}")

    # Load the test results
    with open(os.path.join(latest_dir, "test_results.json"), 'r', encoding='utf-8') as f:
        results = json.load(f)

    # Check if there were any failures
    total_success = sum(format_results["success"] for format_results in results["results"].values())
    total_failure = sum(format_results["failure"] for format_results in results["results"].values())

    print(f"Total tests: {results['completed_tests']}/{results['total_tests']}")
    print(f"Successful: {total_success}")
    print(f"Failed: {total_failure}")

    if total_failure > 0:
        print("Some tests failed. Check the test results for details.")
        return False

    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for markdown to PDF converter")
    parser.add_argument("--format", choices=["pdf", "html", "epub", "docx", "all"], default="all",
                      help="Format to test (default: all)")
    parser.add_argument("--timeout", type=int, default=600,
                      help="Timeout in seconds for the entire test suite (default: 600)")
    parser.add_argument("--skip-dependency-check", action="store_true",
                      help="Skip dependency checking")
    args = parser.parse_args()

    formats_to_test = ["pdf", "html", "epub", "docx"] if args.format == "all" else [args.format]

    print("=" * 80)
    print("Markdown to PDF Converter - Comprehensive Test Suite")
    print("=" * 80)

    # Step 1: Check dependencies
    if not args.skip_dependency_check:
        if not check_dependencies():
            print("Failed to install all required dependencies")
            return 1

        # Fix Pandoc path
        if not fix_pandoc_path():
            print("Failed to fix Pandoc path")
            return 1

    # Step 2: Run tests
    if not run_tests(formats_to_test, args.timeout):
        print("Some tests failed")
        return 1

    # Step 3: Verify output files
    if not verify_output_files():
        print("Failed to verify output files")
        return 1

    print("\n" + "=" * 80)
    print("All tests passed successfully!")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
