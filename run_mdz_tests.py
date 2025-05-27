#!/usr/bin/env python3
"""
MDZ Format Test Runner
-------------------
This script runs all the MDZ format tests.

File: run_mdz_tests.py
"""

import os
import sys
import logging
import argparse
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    Check if all required dependencies are installed
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    try:
        # Run the dependency checker
        result = subprocess.run(
            [sys.executable, "check_mdz_dependencies.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if the script ran successfully
        if result.returncode != 0:
            logger.error(f"Error running dependency checker: {result.stderr}")
            return False
        
        # Check if all required dependencies are installed
        if "All required dependencies are installed" in result.stdout:
            logger.info("All required dependencies are installed")
            return True
        else:
            logger.warning("Some required dependencies are missing")
            print(result.stdout)
            
            # Ask to install missing dependencies
            install = input("Would you like to install the missing dependencies? (y/n): ")
            if install.lower() == 'y':
                # Run the dependency checker again with user interaction
                subprocess.run([sys.executable, "check_mdz_dependencies.py"])
                return True
            else:
                return False
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        return False

def run_test(test_script, args=None):
    """
    Run a test script
    
    Args:
        test_script: Path to the test script
        args: Optional arguments to pass to the script
        
    Returns:
        True if the test passed, False otherwise
    """
    try:
        # Build the command
        cmd = [sys.executable, test_script]
        if args:
            cmd.extend(args)
        
        # Run the test
        logger.info(f"Running {test_script}...")
        start_time = time.time()
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        # Check if the test passed
        if result.returncode == 0:
            logger.info(f"{test_script} passed in {elapsed_time:.2f} seconds")
            return True
        else:
            logger.error(f"{test_script} failed in {elapsed_time:.2f} seconds")
            logger.error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running {test_script}: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MDZ Format Test Runner")
    parser.add_argument("--basic", action="store_true", help="Run basic tests")
    parser.add_argument("--compression", action="store_true", help="Run compression tests")
    parser.add_argument("--export", action="store_true", help="Run export tests")
    parser.add_argument("--editor", action="store_true", help="Run editor integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip dependency check")
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all tests
    if not (args.basic or args.compression or args.export or args.editor or args.all):
        args.all = True
    
    # Check dependencies
    if not args.skip_dependencies:
        if not check_dependencies():
            logger.error("Dependency check failed")
            return 1
    
    # Run tests
    tests_passed = 0
    tests_failed = 0
    
    # Run basic tests
    if args.basic or args.all:
        if run_test("test_mdz_basic.py", ["--all"]):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Run compression tests
    if args.compression or args.all:
        if run_test("test_mdz_compression.py", ["--all"]):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Run export tests
    if args.export or args.all:
        if run_test("test_mdz_export.py", ["--html"]):  # Just test HTML export for now
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Run editor integration tests
    if args.editor or args.all:
        print("\nEditor integration tests require manual verification.")
        print("Please run the following command to test editor integration:")
        print(f"  {sys.executable} test_mdz_editor_integration.py --all")
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Passed: {tests_passed}")
    print(f"  Failed: {tests_failed}")
    print(f"  Total: {tests_passed + tests_failed}")
    
    # Return appropriate exit code
    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
