#!/usr/bin/env python3
"""
Comprehensive test runner for the markdown to PDF converter
"""

import os
import sys
import logging
import subprocess
import time
import argparse
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from dialog_handler import DialogHandler, accept_dialog

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test categories
TEST_CATEGORIES = {
    "core": ["test_core_functionality.py"],
    "page_preview": ["test_page_preview_breaks.py", "test_page_preview_comprehensive.py", "test_js_syntax_and_page_numbers.py", "test_page_navigation_and_export.py"],
    "mdz": ["test_mdz_export_integration.py", "test_mdz_comprehensive.py"],
    "js": ["test_js_syntax_and_page_numbers.py"],
    "navigation": ["test_page_navigation_and_export.py"],
    "export": ["test_page_navigation_and_export.py"],
    "test_mode": ["test_test_mode.py"],
    "all": []  # Will be populated with all tests
}

# Populate the "all" category
for category, tests in TEST_CATEGORIES.items():
    if category != "all":
        TEST_CATEGORIES["all"].extend(tests)

def run_test(test_file, timeout=120):
    """Run a single test file with timeout"""
    logger.info(f"Running test: {test_file}")
    start_time = time.time()

    try:
        # Set environment variable to indicate test mode
        env = os.environ.copy()
        env["MARKDOWN_PDF_TEST_MODE"] = "1"
        env["MARKDOWN_PDF_DIALOG_TIMEOUT"] = str(10)  # 10 seconds timeout for dialogs

        # Run the test with timeout
        result = subprocess.run(
            ["python", test_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )

        # Calculate execution time
        execution_time = time.time() - start_time

        # Check if the test passed
        if result.returncode == 0:
            logger.info(f"✅ PASS: {test_file} (Time: {execution_time:.2f}s)")
            return True, result.stdout, result.stderr, execution_time
        else:
            logger.error(f"❌ FAIL: {test_file} (Time: {execution_time:.2f}s)")
            logger.error(f"Error output: {result.stderr}")
            return False, result.stdout, result.stderr, execution_time

    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ TIMEOUT: {test_file} (Timeout: {timeout}s)")
        return False, "", f"Test timed out after {timeout} seconds", timeout

    except Exception as e:
        logger.error(f"⚠️ ERROR: {test_file} - {str(e)}")
        return False, "", str(e), time.time() - start_time

def run_tests(category="all", timeout=120):
    """Run all tests in the specified category"""
    if category not in TEST_CATEGORIES:
        logger.error(f"Unknown test category: {category}")
        return False

    tests = TEST_CATEGORIES[category]
    if not tests:
        logger.error(f"No tests found in category: {category}")
        return False

    logger.info(f"Running {len(tests)} tests in category: {category}")

    # Create results directory if it doesn't exist
    results_dir = "test_results"
    os.makedirs(results_dir, exist_ok=True)

    # Create a timestamp for the test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a results file
    results_file = os.path.join(results_dir, f"test_results_{category}_{timestamp}.txt")

    # Initialize counters
    passed = 0
    failed = 0
    total = len(tests)

    # Run each test
    with open(results_file, "w") as f:
        f.write(f"Test Results for Category: {category}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {total}\n\n")

        for i, test_file in enumerate(tests):
            logger.info(f"Running test {i+1}/{total}: {test_file}")
            f.write(f"Test {i+1}/{total}: {test_file}\n")

            # Run the test
            success, stdout, stderr, execution_time = run_test(test_file, timeout)

            # Update counters
            if success:
                passed += 1
            else:
                failed += 1

            # Write results to file
            f.write(f"Status: {'PASS' if success else 'FAIL'}\n")
            f.write(f"Execution Time: {execution_time:.2f}s\n")
            f.write("Standard Output:\n")
            f.write(stdout)
            f.write("\nStandard Error:\n")
            f.write(stderr)
            f.write("\n" + "-" * 80 + "\n\n")

        # Write summary
        f.write(f"\nSummary:\n")
        f.write(f"Passed: {passed}/{total} ({passed/total*100:.2f}%)\n")
        f.write(f"Failed: {failed}/{total} ({failed/total*100:.2f}%)\n")

    logger.info(f"Test results written to: {results_file}")
    logger.info(f"Summary: Passed {passed}/{total} tests ({passed/total*100:.2f}%)")

    return passed == total

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for the markdown to PDF converter")
    parser.add_argument("--category", choices=TEST_CATEGORIES.keys(), default="all",
                        help="Test category to run")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout for each test in seconds")
    args = parser.parse_args()

    success = run_tests(args.category, args.timeout)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
