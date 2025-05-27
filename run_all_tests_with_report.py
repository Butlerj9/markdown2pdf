#!/usr/bin/env python3
"""
Run all tests and generate a comprehensive report
"""

import os
import sys
import time
import argparse
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define test categories from run_all_tests.py
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
        for test in tests:
            if test not in TEST_CATEGORIES["all"]:
                TEST_CATEGORIES["all"].append(test)

def run_test(test_file, timeout=120):
    """Run a single test and return the result"""
    logger.info(f"Running test: {test_file}")
    start_time = time.time()
    
    try:
        # Set environment variable to indicate test mode
        env = os.environ.copy()
        env["MARKDOWN_PDF_TEST_MODE"] = "1"
        env["MARKDOWN_PDF_DIALOG_TIMEOUT"] = str(10)  # 10 seconds timeout for dialogs
        
        # Run the test with timeout
        result = subprocess.run(
            ["python", test_file, "--test-mode"],
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
            return {
                "status": "PASS",
                "file": test_file,
                "time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        else:
            logger.error(f"❌ FAIL: {test_file} (Time: {execution_time:.2f}s)")
            logger.error(f"Error output: {result.stderr}")
            return {
                "status": "FAIL",
                "file": test_file,
                "time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        logger.error(f"⏱️ TIMEOUT: {test_file} (Time: {execution_time:.2f}s)")
        return {
            "status": "TIMEOUT",
            "file": test_file,
            "time": execution_time,
            "stdout": "",
            "stderr": f"Test timed out after {timeout} seconds",
            "returncode": -1
        }
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"⚠️ ERROR: {test_file} (Time: {execution_time:.2f}s)")
        logger.error(f"Exception: {str(e)}")
        return {
            "status": "ERROR",
            "file": test_file,
            "time": execution_time,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def run_tests(category="all", timeout=120):
    """Run all tests in the specified category"""
    if category not in TEST_CATEGORIES:
        logger.error(f"Invalid category: {category}")
        return False
    
    test_files = TEST_CATEGORIES[category]
    logger.info(f"Running {len(test_files)} tests in category: {category}")
    
    results = []
    for i, test_file in enumerate(test_files, 1):
        logger.info(f"Running test {i}/{len(test_files)}: {test_file}")
        result = run_test(test_file, timeout)
        results.append(result)
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{category}_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write(f"Test Report - Category: {category} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        timeout = sum(1 for r in results if r["status"] == "TIMEOUT")
        error = sum(1 for r in results if r["status"] == "ERROR")
        
        f.write(f"Summary:\n")
        f.write(f"  Passed:  {passed}/{len(results)} ({passed/len(results)*100:.2f}%)\n")
        f.write(f"  Failed:  {failed}/{len(results)} ({failed/len(results)*100:.2f}%)\n")
        f.write(f"  Timeout: {timeout}/{len(results)} ({timeout/len(results)*100:.2f}%)\n")
        f.write(f"  Error:   {error}/{len(results)} ({error/len(results)*100:.2f}%)\n\n")
        
        # Detailed results
        f.write("Detailed Results:\n")
        f.write("-" * 80 + "\n")
        
        for result in results:
            f.write(f"Test: {result['file']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Time: {result['time']:.2f}s\n")
            f.write(f"Return Code: {result['returncode']}\n")
            
            if result["status"] != "PASS":
                f.write("\nStandard Output:\n")
                f.write(result["stdout"] + "\n")
                
                f.write("\nStandard Error:\n")
                f.write(result["stderr"] + "\n")
            
            f.write("-" * 80 + "\n")
        
        # Error checklist
        if failed > 0 or timeout > 0 or error > 0:
            f.write("\nError Checklist:\n")
            for result in results:
                if result["status"] != "PASS":
                    f.write(f"[ ] {result['file']} - {result['status']}\n")
                    
                    # Extract specific errors
                    if "JavaScript Error" in result["stderr"]:
                        for line in result["stderr"].split("\n"):
                            if "JavaScript Error" in line:
                                f.write(f"    - {line.strip()}\n")
                    
                    # Extract dialog issues
                    if "dialog" in result["stderr"].lower():
                        for line in result["stderr"].split("\n"):
                            if "dialog" in line.lower():
                                f.write(f"    - {line.strip()}\n")
            
            f.write("\n")
    
    logger.info(f"Test results written to: {report_file}")
    
    # Return True if all tests passed
    return passed == len(results), report_file

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for the markdown to PDF converter")
    parser.add_argument("--category", choices=TEST_CATEGORIES.keys(), default="all",
                        help="Test category to run")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout for each test in seconds")
    args = parser.parse_args()
    
    success, report_file = run_tests(args.category, args.timeout)
    
    # Print report file content
    with open(report_file, "r") as f:
        print(f.read())
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
