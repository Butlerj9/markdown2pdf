#!/usr/bin/env python3
"""
Comprehensive Test Runner for Markdown to PDF Converter
------------------------------------------------------
Provides automated testing of all features without GUI dependencies.
This runner can execute unit tests, content processor tests, MDZ format tests,
and export functionality tests.
"""

import os
import sys
import json
import time
import logging
import argparse
import unittest
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
from logging_config import get_logger
logger = get_logger()

class TestResult:
    """Class to store test results"""
    def __init__(self, name: str, passed: bool, message: str = "",
                 details: str = "", execution_time: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
        self.timestamp = time.time()
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "execution_time": self.execution_time
        }

    def __str__(self) -> str:
        """String representation of the test result"""
        status = "PASS" if self.passed else "FAIL"
        return f"{self.name}: {status} ({self.execution_time:.2f}s) - {self.message}"

def run_process_with_timeout(cmd: List[str], timeout: int = 30,
                            cwd: Optional[str] = None,
                            env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Run a process with timeout handling"""
    start_time = time.time()

    try:
        # Set environment variable to indicate test mode
        if env is None:
            env = os.environ.copy()
        env["MARKDOWN_PDF_TEST_MODE"] = "1"
        env["MARKDOWN_PDF_DIALOG_TIMEOUT"] = str(10)  # 10 seconds timeout for dialogs

        # Run the process with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env
        )

        # Calculate execution time
        execution_time = time.time() - start_time

        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": execution_time,
            "timed_out": False
        }
    except subprocess.TimeoutExpired:
        # Process timed out
        execution_time = time.time() - start_time
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Process timed out after {timeout} seconds",
            "execution_time": execution_time,
            "timed_out": True
        }
    except Exception as e:
        # Other error occurred
        execution_time = time.time() - start_time
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "execution_time": execution_time,
            "timed_out": False
        }

def run_test(test_name: str, test_cmd: List[str], timeout: int = 30,
            cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None,
            category: str = "") -> TestResult:
    """Run a test with timeout handling"""
    logger.info(f"Running test: {test_name}")

    # Run the process
    result = run_process_with_timeout(test_cmd, timeout, cwd, env)

    # Check if the test passed
    passed = result["returncode"] == 0 and not result["timed_out"]

    # Create a message
    if passed:
        message = "Test passed"
    elif result["timed_out"]:
        message = f"Test timed out after {timeout} seconds"
    else:
        message = f"Test failed with return code {result['returncode']}"

    # Create details from stdout and stderr
    details = f"STDOUT:\n{result['stdout']}\n\nSTDERR:\n{result['stderr']}"

    # Create and return the test result
    return TestResult(
        name=test_name,
        passed=passed,
        message=message,
        details=details,
        execution_time=result["execution_time"]
    )

def run_unit_tests(timeout: int = 30) -> List[TestResult]:
    """Run unit tests"""
    logger.info("Running unit tests")

    # Import unit tests
    try:
        from unit_tests import run_tests

        # Create a temporary file for test results
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_path = temp_file.name

        # Run the tests with timeout
        cmd = [sys.executable, "unit_tests.py", "--output", temp_path]
        result = run_process_with_timeout(cmd, timeout)

        # Check if the tests ran successfully
        if result["returncode"] == 0 and not result["timed_out"]:
            # Read the test results
            try:
                with open(temp_path, 'r') as f:
                    test_results = json.load(f)

                # Convert to TestResult objects
                results = []
                for test_result in test_results:
                    results.append(TestResult(
                        name=test_result["name"],
                        passed=test_result["passed"],
                        message=test_result["message"],
                        details=test_result.get("details", ""),
                        execution_time=test_result.get("execution_time", 0.0)
                    ))

                return results
            except Exception as e:
                logger.error(f"Error reading unit test results: {str(e)}")
                return [TestResult("UnitTests", False, f"Error reading test results: {str(e)}")]
        else:
            # Tests failed to run
            return [TestResult("UnitTests", False,
                              f"Unit tests failed to run: {result['stderr']}",
                              execution_time=result["execution_time"])]
    except ImportError:
        logger.error("Unit tests module not found")
        return [TestResult("UnitTests", False, "Unit tests module not found")]

def run_content_processor_tests(timeout: int = 30) -> List[TestResult]:
    """Run content processor tests"""
    logger.info("Running content processor tests")

    results = []

    # Test each content processor
    processor_types = [
        "mermaid", "math", "image", "code", "media", "visualization"
    ]

    for processor_type in processor_types:
        test_name = f"ContentProcessor.{processor_type}"

        # Create a test file for this processor
        test_content = create_test_content_for_processor(processor_type)
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            test_file = temp_file.name

        # Run the test
        cmd = [sys.executable, "test_content_processing.py", test_file, "--format", "preview"]
        result = run_test(test_name, cmd, timeout)
        results.append(result)

    return results

def create_test_content_for_processor(processor_type: str) -> str:
    """Create test content for a specific processor type"""
    if processor_type == "mermaid":
        return """# Mermaid Test

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
"""
    elif processor_type == "math":
        return """# Math Test

Inline math: $E = mc^2$

Block math:

$$
\\frac{d}{dx}\\left( \\int_{0}^{x} f(u)\\,du\\right)=f(x)
$$
"""
    elif processor_type == "image":
        return """# Image Test

![Test Image](test_image.png)

<img src="test_image.png" alt="HTML Image" width="300" />
"""
    elif processor_type == "code":
        return """# Code Test

```python
def hello_world():
    print("Hello, world!")
```

```javascript
function helloWorld() {
    console.log("Hello, world!");
}
```
"""
    elif processor_type == "media":
        return """# Media Test

<video src="test_video.mp4" controls></video>

<audio src="test_audio.mp3" controls></audio>
"""
    elif processor_type == "visualization":
        return """# Visualization Test

```plotly
{
    "data": [
        {
            "x": [1, 2, 3, 4],
            "y": [10, 15, 13, 17],
            "type": "scatter"
        }
    ],
    "layout": {
        "title": "Test Plot"
    }
}
```
"""
    else:
        return f"# {processor_type.capitalize()} Test\n\nTest content for {processor_type} processor."

def run_mdz_tests(timeout: int = 30) -> List[TestResult]:
    """Run MDZ format tests"""
    logger.info("Running MDZ format tests")

    results = []

    # Test MDZ basic functionality
    cmd = [sys.executable, "test_mdz_basic.py"]
    result = run_test("MDZ.Basic", cmd, timeout)
    results.append(result)

    # Test MDZ export
    cmd = [sys.executable, "test_mdz_export.py"]
    result = run_test("MDZ.Export", cmd, timeout)
    results.append(result)

    # Test MDZ comprehensive
    cmd = [sys.executable, "test_mdz_comprehensive.py"]
    result = run_test("MDZ.Comprehensive", cmd, timeout)
    results.append(result)

    return results

def run_export_tests(timeout: int = 30) -> List[TestResult]:
    """Run export functionality tests"""
    logger.info("Running export functionality tests")

    results = []

    # Test PDF export
    cmd = [sys.executable, "test_pdf_export.py"]
    result = run_test("Export.PDF", cmd, timeout)
    results.append(result)

    # Test HTML export
    cmd = [sys.executable, "test_html_export.py"]
    result = run_test("Export.HTML", cmd, timeout)
    results.append(result)

    # Test DOCX export
    cmd = [sys.executable, "test_docx_export.py"]
    result = run_test("Export.DOCX", cmd, timeout)
    results.append(result)

    # Test EPUB export
    cmd = [sys.executable, "test_epub_export.py"]
    result = run_test("Export.EPUB", cmd, timeout)
    results.append(result)

    return results

def run_zoom_fix_tests(timeout: int = 30) -> List[TestResult]:
    """Run zoom fix tests"""
    logger.info("Running zoom fix tests")

    results = []

    # Test zoom fix functionality
    cmd = [sys.executable, "test_zoom_fix_automated.py", "--test-mode"]
    result = run_test("ZoomFix.Automated", cmd, timeout)
    results.append(result)

    return results

def run_all_tests(timeout: int = 30) -> List[TestResult]:
    """Run all tests"""
    logger.info("Running all tests")

    results = []

    # Run unit tests
    unit_results = run_unit_tests(timeout)
    results.extend(unit_results)

    # Run content processor tests
    processor_results = run_content_processor_tests(timeout)
    results.extend(processor_results)

    # Run MDZ tests
    mdz_results = run_mdz_tests(timeout)
    results.extend(mdz_results)

    # Run export tests
    export_results = run_export_tests(timeout)
    results.extend(export_results)

    # Run zoom fix tests
    zoom_fix_results = run_zoom_fix_tests(timeout)
    results.extend(zoom_fix_results)

    return results

def generate_report(results: List[TestResult], output_file: str) -> None:
    """Generate a comprehensive test report"""
    logger.info(f"Generating test report: {output_file}")

    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    # Calculate total execution time
    total_time = sum(r.execution_time for r in results)

    # Group results by category
    categories = {}
    for result in results:
        category = result.name.split('.')[0] if '.' in result.name else "Other"
        if category not in categories:
            categories[category] = []
        categories[category].append(result)

    # Generate the report
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Markdown to PDF Converter Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Write summary
        f.write("## Summary\n\n")
        f.write(f"- Total Tests: {total_tests}\n")
        f.write(f"- Passed: {passed_tests}\n")
        f.write(f"- Failed: {failed_tests}\n")
        f.write(f"- Pass Rate: {pass_rate:.2f}%\n")
        f.write(f"- Total Execution Time: {total_time:.2f} seconds\n\n")

        # Write results by category
        f.write("## Results by Category\n\n")
        for category, category_results in categories.items():
            category_total = len(category_results)
            category_passed = sum(1 for r in category_results if r.passed)
            category_rate = (category_passed / category_total) * 100

            f.write(f"### {category}\n\n")
            f.write(f"- Tests: {category_total}\n")
            f.write(f"- Passed: {category_passed}\n")
            f.write(f"- Pass Rate: {category_rate:.2f}%\n\n")

            # Write table of results
            f.write("| Test | Status | Time (s) | Message |\n")
            f.write("|------|--------|----------|--------|\n")
            for result in category_results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                test_name = result.name.split('.')[-1] if '.' in result.name else result.name
                f.write(f"| {test_name} | {status} | {result.execution_time:.2f} | {result.message} |\n")

            f.write("\n")

        # Write failed tests section
        if failed_tests > 0:
            f.write("## Failed Tests\n\n")
            for result in results:
                if not result.passed:
                    f.write(f"### {result.name}\n\n")
                    f.write(f"- Message: {result.message}\n")
                    f.write(f"- Execution Time: {result.execution_time:.2f} seconds\n\n")
                    f.write("#### Details\n\n")
                    f.write("```\n")
                    f.write(result.details)
                    f.write("\n```\n\n")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive Test Runner for Markdown to PDF Converter")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--processors", action="store_true", help="Run content processor tests")
    parser.add_argument("--mdz", action="store_true", help="Run MDZ format tests")
    parser.add_argument("--export", action="store_true", help="Run export functionality tests")
    parser.add_argument("--zoom-fix", action="store_true", help="Run zoom fix tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--timeout", type=int, default=30, help="Test timeout in seconds")
    parser.add_argument("--output", type=str, default="test_report.md", help="Output report file")
    args = parser.parse_args()

    # If no specific tests are selected, run all tests
    if not (args.unit or args.processors or args.mdz or args.export or args.zoom_fix or args.all):
        args.all = True

    # Run the selected tests
    results = []

    if args.unit or args.all:
        results.extend(run_unit_tests(args.timeout))

    if args.processors or args.all:
        results.extend(run_content_processor_tests(args.timeout))

    if args.mdz or args.all:
        results.extend(run_mdz_tests(args.timeout))

    if args.export or args.all:
        results.extend(run_export_tests(args.timeout))

    if args.zoom_fix or args.all:
        results.extend(run_zoom_fix_tests(args.timeout))

    # Generate the report
    generate_report(results, args.output)

    # Print summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\nTest Summary:")
    print(f"- Total Tests: {total_tests}")
    print(f"- Passed: {passed_tests}")
    print(f"- Failed: {failed_tests}")
    print(f"- Pass Rate: {pass_rate:.2f}%")
    print(f"\nReport saved to: {args.output}")

    # Return success if all tests passed
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
