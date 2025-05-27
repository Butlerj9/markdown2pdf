#!/usr/bin/env python3
"""
Markdown to PDF Converter Test Runner
------------------------------------
Comprehensive test runner for the Markdown to PDF Converter.
Supports unit tests, integration tests, visual tests, performance tests,
and code coverage reporting.
"""

import os
import sys
import time
import json
import logging
import argparse
import subprocess
import threading
import signal
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

# Configure logging
log_filename = f"test_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define test categories
TEST_CATEGORIES = {
    "core": ["test_core_functionality.py"],
    "page_preview": ["test_page_preview_breaks.py", "test_page_preview_comprehensive.py", 
                    "test_js_syntax_and_page_numbers.py", "test_page_navigation_and_export.py"],
    "mdz": ["test_mdz_export_integration.py", "test_mdz_comprehensive.py"],
    "js": ["test_js_syntax_and_page_numbers.py", "test_js_errors.py"],
    "navigation": ["test_page_navigation_and_export.py"],
    "export": ["test_page_navigation_and_export.py", "test_export_fix.py", 
              "test_docx_export.py", "test_epub_export.py", "test_pdf_export.py"],
    "test_mode": ["test_test_mode.py"],
    "unit": ["unit_tests.py"],
    "content": ["test_content_processing.py"],
    "performance": ["test_performance.py"],
    "visual": ["visual_test.py"],
    "all": []  # Will be populated with all tests
}

# Populate the "all" category
for category, tests in TEST_CATEGORIES.items():
    if category != "all":
        for test in tests:
            if test not in TEST_CATEGORIES["all"]:
                TEST_CATEGORIES["all"].append(test)

# Test result class
class TestResult:
    """Class to store test results"""
    def __init__(self, name: str, passed: bool, message: str = "", 
                 details: str = "", duration: float = 0.0, 
                 category: str = "", performance_metrics: Dict[str, float] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
        self.duration = duration
        self.timestamp = datetime.now().isoformat()
        self.category = category
        self.performance_metrics = performance_metrics or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "duration": self.duration,
            "timestamp": self.timestamp,
            "category": self.category,
            "performance_metrics": self.performance_metrics
        }

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"{self.name}: {status} ({self.duration:.2f}s) - {self.message}"

# Test timeout handler
class TestTimeoutError(Exception):
    """Exception raised when a test times out"""
    pass

def run_process_with_timeout(cmd: List[str], timeout: int = 30, 
                            cwd: Optional[str] = None, 
                            env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Run a process with timeout"""
    logger.info(f"Running command: {cmd}")
    start_time = time.time()
    
    # Use environment variables if provided
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    # Start the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=process_env
    )
    
    # Wait for the process to complete or timeout
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        duration = time.time() - start_time
        return {
            "returncode": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration,
            "timed_out": False
        }
    except subprocess.TimeoutExpired:
        # Kill the process if it times out
        process.kill()
        stdout, stderr = process.communicate()
        duration = time.time() - start_time
        return {
            "returncode": -1,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration,
            "timed_out": True
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
    
    # Create details
    details = f"STDOUT:\n{result['stdout']}\n\nSTDERR:\n{result['stderr']}"
    
    # Extract performance metrics if available
    performance_metrics = {}
    if passed and "PERFORMANCE_METRICS:" in result["stdout"]:
        # Extract performance metrics from stdout
        metrics_section = result["stdout"].split("PERFORMANCE_METRICS:")[1].split("\n")[0]
        try:
            performance_metrics = json.loads(metrics_section)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse performance metrics: {metrics_section}")
    
    # Create a test result
    test_result = TestResult(
        name=test_name,
        passed=passed,
        message=message,
        details=details,
        duration=result["duration"],
        category=category,
        performance_metrics=performance_metrics
    )
    
    # Log the result
    logger.info(f"Test {test_name} completed in {result['duration']:.2f} seconds: {'PASS' if passed else 'FAIL'}")
    
    return test_result

def run_page_preview_test(test_name: str, timeout: int = 30) -> TestResult:
    """Run a page preview test"""
    # Construct the command
    cmd = ["python", "test_page_preview.py", "--debug"]
    
    # Run the test
    return run_test(f"PagePreview.{test_name}", cmd, timeout, category="page_preview")

def run_markdown_conversion_test(input_file: str, output_format: str = "pdf", 
                                timeout: int = 30) -> TestResult:
    """Run a markdown conversion test"""
    # Construct the command
    cmd = ["python", "markdown_to_pdf_converter.py", input_file, f"--format={output_format}"]
    
    # Run the test
    return run_test(f"Conversion.{Path(input_file).stem}.{output_format}", 
                   cmd, timeout, category="export")

def run_mdz_test(input_file: str, timeout: int = 30) -> TestResult:
    """Run an MDZ format test"""
    # Construct the command
    cmd = ["python", "markdown_to_pdf_converter.py", input_file, "--format=mdz"]
    
    # Run the test
    return run_test(f"MDZ.{Path(input_file).stem}", cmd, timeout, category="mdz")

def run_unit_tests(timeout: int = 30) -> List[TestResult]:
    """Run unit tests"""
    # Construct the command
    cmd = ["python", "unit_tests.py"]
    
    # Run the test
    result = run_test("UnitTests", cmd, timeout, category="unit")
    
    # Parse the unit test results
    unit_test_results = []
    if result.passed:
        # Extract individual test results from the output
        pattern = r"(test_\w+) \(([\w.]+)\) \.\.\. (ok|FAIL)"
        matches = re.findall(pattern, result.details)
        
        for match in matches:
            test_name, test_class, status = match
            unit_test_results.append(TestResult(
                name=f"UnitTest.{test_class}.{test_name}",
                passed=status == "ok",
                message=f"Unit test {'passed' if status == 'ok' else 'failed'}",
                details="",
                duration=0.0,  # We don't have individual durations
                category="unit"
            ))
    else:
        # If the unit test runner failed, add a single failed result
        unit_test_results.append(result)
    
    return unit_test_results

def run_performance_tests(timeout: int = 60) -> List[TestResult]:
    """Run performance tests"""
    # Check if performance test file exists
    if not os.path.exists("test_performance.py"):
        logger.warning("Performance test file not found. Creating a basic one.")
        create_performance_test_file()
    
    # Construct the command
    cmd = ["python", "test_performance.py"]
    
    # Run the test
    result = run_test("PerformanceTests", cmd, timeout, category="performance")
    
    # Parse the performance test results
    performance_results = []
    if result.passed:
        # Extract individual test results from the output
        pattern = r"Performance test: ([\w.]+) - Time: ([\d.]+)s"
        matches = re.findall(pattern, result.details)
        
        for match in matches:
            test_name, duration = match
            performance_results.append(TestResult(
                name=f"Performance.{test_name}",
                passed=True,
                message=f"Performance test completed in {duration}s",
                details="",
                duration=float(duration),
                category="performance",
                performance_metrics={"execution_time": float(duration)}
            ))
    else:
        # If the performance test runner failed, add a single failed result
        performance_results.append(result)
    
    return performance_results

def run_visual_tests(timeout: int = 60) -> List[TestResult]:
    """Run visual tests"""
    # Check if visual test file exists
    if not os.path.exists("visual_test.py"):
        logger.warning("Visual test file not found. Creating a basic one.")
        create_visual_test_file()
    
    # Construct the command
    cmd = ["python", "visual_test.py"]
    
    # Run the test
    result = run_test("VisualTests", cmd, timeout, category="visual")
    
    # Parse the visual test results
    visual_results = []
    if result.passed:
        # Extract individual test results from the output
        pattern = r"Visual test: ([\w.]+) - (PASS|FAIL)"
        matches = re.findall(pattern, result.details)
        
        for match in matches:
            test_name, status = match
            visual_results.append(TestResult(
                name=f"Visual.{test_name}",
                passed=status == "PASS",
                message=f"Visual test {'passed' if status == 'PASS' else 'failed'}",
                details="",
                duration=0.0,  # We don't have individual durations
                category="visual"
            ))
    else:
        # If the visual test runner failed, add a single failed result
        visual_results.append(result)
    
    return visual_results

def run_coverage_tests(timeout: int = 120, output_dir: str = "coverage") -> TestResult:
    """Run tests with coverage"""
    # Check if coverage is installed
    try:
        import coverage
    except ImportError:
        logger.error("Coverage package not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"])
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the command to run tests with coverage
    cmd = [
        sys.executable, "-m", "coverage", "run", "--source=.", 
        "--omit=*/test_*,*/flat/*,*/__pycache__/*", 
        "run_all_tests.py", "--category", "all"
    ]
    
    # Run the tests with coverage
    result = run_test("CoverageTests", cmd, timeout, category="coverage")
    
    if result.passed:
        # Generate coverage report
        report_cmd = [sys.executable, "-m", "coverage", "html", "-d", output_dir]
        report_result = run_process_with_timeout(report_cmd, timeout=30)
        
        if report_result["returncode"] == 0:
            logger.info(f"Coverage report generated in {output_dir}")
            result.message += f". Coverage report generated in {output_dir}"
        else:
            logger.error("Failed to generate coverage report")
            result.message += ". Failed to generate coverage report"
    
    return result

def run_regression_tests(timeout: int = 120, 
                        baseline_file: Optional[str] = None) -> TestResult:
    """Run regression tests"""
    # Create a timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Run all tests
    results = run_all_tests(get_test_files(), timeout)
    
    # Save current results
    current_results_file = f"regression_results_{timestamp}.json"
    with open(current_results_file, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    
    # If no baseline file is provided, create one and return
    if not baseline_file:
        logger.info(f"No baseline file provided. Created {current_results_file} as baseline.")
        return TestResult(
            name="RegressionTests",
            passed=True,
            message=f"Created baseline file {current_results_file}",
            details="",
            duration=sum(r.duration for r in results),
            category="regression"
        )
    
    # Compare with baseline
    try:
        with open(baseline_file, "r") as f:
            baseline_results = json.load(f)
        
        # Convert current results to dict for comparison
        current_results = [r.to_dict() for r in results]
        
        # Compare results
        regressions = []
        for baseline in baseline_results:
            # Find matching test in current results
            matching = next((r for r in current_results if r["name"] == baseline["name"]), None)
            
            if matching:
                # Check if test was passing before but failing now
                if baseline["passed"] and not matching["passed"]:
                    regressions.append(f"{baseline['name']}: Was passing, now failing")
                
                # Check if test is significantly slower now
                if baseline["passed"] and matching["passed"]:
                    if matching["duration"] > baseline["duration"] * 1.5:  # 50% slower
                        regressions.append(
                            f"{baseline['name']}: Performance regression " +
                            f"({baseline['duration']:.2f}s -> {matching['duration']:.2f}s)"
                        )
            else:
                # Test was removed or renamed
                regressions.append(f"{baseline['name']}: Test no longer exists")
        
        # Check for new tests
        new_tests = [r["name"] for r in current_results 
                    if not any(b["name"] == r["name"] for b in baseline_results)]
        
        # Create regression report
        if regressions:
            logger.error(f"Found {len(regressions)} regressions:")
            for regression in regressions:
                logger.error(f"  - {regression}")
            
            return TestResult(
                name="RegressionTests",
                passed=False,
                message=f"Found {len(regressions)} regressions",
                details="\n".join(regressions),
                duration=sum(r.duration for r in results),
                category="regression"
            )
        else:
            logger.info("No regressions found")
            if new_tests:
                logger.info(f"Found {len(new_tests)} new tests:")
                for test in new_tests:
                    logger.info(f"  - {test}")
            
            return TestResult(
                name="RegressionTests",
                passed=True,
                message=f"No regressions found. {len(new_tests)} new tests added.",
                details="\n".join(new_tests) if new_tests else "",
                duration=sum(r.duration for r in results),
                category="regression"
            )
    
    except Exception as e:
        logger.error(f"Error comparing with baseline: {str(e)}")
        return TestResult(
            name="RegressionTests",
            passed=False,
            message=f"Error comparing with baseline: {str(e)}",
            details=str(e),
            duration=sum(r.duration for r in results),
            category="regression"
        )

def get_test_files() -> List[str]:
    """Get all test files"""
    return [
        os.path.join("test_files", "basic_test.md"),
        os.path.join("test_files", "mermaid_test.md"),
        os.path.join("test_files", "latex_math_test.md"),
        os.path.join("test_files", "svg_test.md"),
        os.path.join("test_files", "multi_page_test.md"),
        os.path.join("test_files", "combined_features_test.md")
    ]

def run_all_tests(test_files: List[str], timeout: int = 30, 
                 output_dir: str = "test_results") -> List[TestResult]:
    """Run all tests"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize results
    results = []
    
    # Run unit tests
    results.extend(run_unit_tests(timeout))
    
    # Run page preview test
    results.append(run_page_preview_test("basic", timeout))
    
    # Run conversion tests for each test file and format
    formats = ["pdf", "html", "docx", "mdz"]
    for test_file in test_files:
        for output_format in formats:
            results.append(run_markdown_conversion_test(test_file, output_format, timeout))
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"test_results_{timestamp}.json")
    with open(results_file, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    
    # Generate HTML report
    html_report_file = os.path.join(output_dir, f"test_report_{timestamp}.html")
    generate_html_report(results, html_report_file)
    
    # Print summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    logger.info(f"Tests completed: {passed}/{total} passed ({passed/total*100:.2f}%)")
    logger.info(f"Results saved to {results_file}")
    logger.info(f"HTML report saved to {html_report_file}")
    
    return results

def generate_html_report(results: List[TestResult], output_file: str) -> None:
    """Generate an HTML report from test results"""
    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    pass_rate = passed / total * 100 if total > 0 else 0
    
    # Group results by category
    categories = {}
    for result in results:
        category = result.category or "uncategorized"
        if category not in categories:
            categories[category] = []
        categories[category].append(result)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .summary {{ display: flex; margin-bottom: 20px; }}
        .summary-box {{ padding: 10px; margin-right: 20px; border-radius: 5px; color: white; }}
        .total {{ background-color: #007bff; }}
        .passed {{ background-color: #28a745; }}
        .failed {{ background-color: #dc3545; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr.pass {{ background-color: #dff0d8; }}
        tr.fail {{ background-color: #f2dede; }}
        .details {{ display: none; white-space: pre-wrap; background-color: #f8f9fa; 
                  padding: 10px; border: 1px solid #ddd; margin-top: 5px; }}
        .toggle-details {{ cursor: pointer; color: #007bff; }}
        .performance-chart {{ width: 100%; height: 300px; margin-bottom: 20px; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Test Report</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <div class="summary-box total">
            <h3>Total Tests</h3>
            <p>{total}</p>
        </div>
        <div class="summary-box passed">
            <h3>Passed</h3>
            <p>{passed} ({pass_rate:.2f}%)</p>
        </div>
        <div class="summary-box failed">
            <h3>Failed</h3>
            <p>{failed} ({100-pass_rate:.2f}%)</p>
        </div>
    </div>
    
    <h2>Results by Category</h2>
"""
    
    # Add category tables
    for category, category_results in categories.items():
        cat_total = len(category_results)
        cat_passed = sum(1 for r in category_results if r.passed)
        cat_pass_rate = cat_passed / cat_total * 100 if cat_total > 0 else 0
        
        html += f"""
    <h3>{category.title()} ({cat_passed}/{cat_total} - {cat_pass_rate:.2f}%)</h3>
    <table>
        <tr>
            <th>Test</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Message</th>
        </tr>
"""
        
        for i, result in enumerate(category_results):
            status_class = "pass" if result.passed else "fail"
            status_text = "PASS" if result.passed else "FAIL"
            
            html += f"""
        <tr class="{status_class}">
            <td>{result.name}</td>
            <td>{status_text}</td>
            <td>{result.duration:.2f}s</td>
            <td>
                {result.message}
                <span class="toggle-details" onclick="toggleDetails('details-{category}-{i}')">Show Details</span>
                <div id="details-{category}-{i}" class="details">{result.details}</div>
            </td>
        </tr>
"""
        
        html += """
    </table>
"""
    
    # Add performance chart if there are performance metrics
    performance_results = [r for r in results if r.performance_metrics]
    if performance_results:
        html += """
    <h2>Performance Metrics</h2>
    <div class="performance-chart">
        <canvas id="performanceChart"></canvas>
    </div>
    
    <script>
        // Performance chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(performanceCtx, {
            type: 'bar',
            data: {
                labels: [
"""
        
        # Add labels
        for result in performance_results:
            html += f"                    '{result.name}',\n"
        
        html += """
                ],
                datasets: [{
                    label: 'Execution Time (s)',
                    data: [
"""
        
        # Add data
        for result in performance_results:
            execution_time = result.performance_metrics.get("execution_time", result.duration)
            html += f"                    {execution_time},\n"
        
        html += """
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time (seconds)'
                        }
                    }
                }
            }
        });
    </script>
"""
    
    # Add JavaScript for toggling details
    html += """
    <script>
        function toggleDetails(id) {
            const details = document.getElementById(id);
            if (details.style.display === 'block') {
                details.style.display = 'none';
            } else {
                details.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""
    
    # Write HTML to file
    with open(output_file, "w") as f:
        f.write(html)

def create_performance_test_file() -> None:
    """Create a basic performance test file if it doesn't exist"""
    content = """#!/usr/bin/env python3
\"\"\"
Performance tests for the Markdown to PDF Converter
\"\"\"

import os
import sys
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from PyQt6.QtWidgets import QApplication

def test_markdown_parsing_performance():
    \"\"\"Test markdown parsing performance\"\"\"
    start_time = time.time()
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create converter instance
    converter = AdvancedMarkdownToPDF()
    
    # Load test file
    test_file = os.path.join("test_files", "combined_features_test.md")
    with open(test_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Parse markdown
    converter.markdown_editor.setPlainText(markdown_content)
    converter.update_preview()
    
    # Process events
    app.processEvents()
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    print(f"Performance test: markdown_parsing - Time: {execution_time:.2f}s")
    return execution_time

def test_pdf_export_performance():
    \"\"\"Test PDF export performance\"\"\"
    start_time = time.time()
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create converter instance
    converter = AdvancedMarkdownToPDF()
    
    # Load test file
    test_file = os.path.join("test_files", "combined_features_test.md")
    with open(test_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Parse markdown
    converter.markdown_editor.setPlainText(markdown_content)
    converter.update_preview()
    
    # Process events
    app.processEvents()
    
    # Export to PDF
    output_file = os.path.join("test_results", "performance_test.pdf")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    converter.export_to_pdf(output_file)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    print(f"Performance test: pdf_export - Time: {execution_time:.2f}s")
    return execution_time

def main():
    \"\"\"Run all performance tests\"\"\"
    print("Running performance tests...")
    
    # Run tests
    parsing_time = test_markdown_parsing_performance()
    export_time = test_pdf_export_performance()
    
    # Print performance metrics
    print(f"PERFORMANCE_METRICS:{json.dumps({
        'markdown_parsing': parsing_time,
        'pdf_export': export_time
    })}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open("test_performance.py", "w") as f:
        f.write(content)

def create_visual_test_file() -> None:
    """Create a basic visual test file if it doesn't exist"""
    content = """#!/usr/bin/env python3
\"\"\"
Visual tests for the Markdown to PDF Converter
\"\"\"

import os
import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def capture_screenshot(widget, filename):
    \"\"\"Capture a screenshot of a widget\"\"\"
    # Create screenshots directory if it doesn't exist
    os.makedirs("screenshots", exist_ok=True)
    
    # Capture screenshot
    pixmap = widget.grab()
    
    # Save screenshot
    filepath = os.path.join("screenshots", filename)
    pixmap.save(filepath)
    
    return filepath

def compare_screenshots(file1, file2):
    \"\"\"Compare two screenshots\"\"\"
    # Check if both files exist
    if not os.path.exists(file1) or not os.path.exists(file2):
        return False
    
    # Load images
    pixmap1 = QPixmap(file1)
    pixmap2 = QPixmap(file2)
    
    # Check dimensions
    if pixmap1.width() != pixmap2.width() or pixmap1.height() != pixmap2.height():
        return False
    
    # Convert to images for pixel comparison
    image1 = pixmap1.toImage()
    image2 = pixmap2.toImage()
    
    # Compare pixels (simple approach)
    width = image1.width()
    height = image1.height()
    
    # Count different pixels
    different_pixels = 0
    for y in range(height):
        for x in range(width):
            if image1.pixel(x, y) != image2.pixel(x, y):
                different_pixels += 1
    
    # Calculate difference percentage
    total_pixels = width * height
    difference_percentage = different_pixels / total_pixels * 100
    
    # Return True if difference is less than 5%
    return difference_percentage < 5

def test_ui_appearance():
    \"\"\"Test the appearance of the UI\"\"\"
    # Create QApplication if it doesn't exist
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create converter instance
    converter = AdvancedMarkdownToPDF()
    
    # Show the window
    converter.show()
    
    # Process events
    app.processEvents()
    
    # Wait for UI to stabilize
    time.sleep(1)
    app.processEvents()
    
    # Capture screenshot
    screenshot_file = capture_screenshot(converter, "ui_appearance.png")
    
    # Check if reference screenshot exists
    reference_file = os.path.join("screenshots", "ui_appearance_reference.png")
    if not os.path.exists(reference_file):
        # Create reference screenshot
        os.rename(screenshot_file, reference_file)
        print("Visual test: ui_appearance - PASS (created reference)")
        return True
    
    # Compare with reference
    result = compare_screenshots(screenshot_file, reference_file)
    
    # Close the window
    converter.close()
    
    print(f"Visual test: ui_appearance - {'PASS' if result else 'FAIL'}")
    return result

def test_preview_rendering():
    \"\"\"Test the rendering of the preview\"\"\"
    # Create QApplication if it doesn't exist
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create converter instance
    converter = AdvancedMarkdownToPDF()
    
    # Load test file
    test_file = os.path.join("test_files", "basic_test.md")
    with open(test_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Parse markdown
    converter.markdown_editor.setPlainText(markdown_content)
    converter.update_preview()
    
    # Show the window
    converter.show()
    
    # Process events
    app.processEvents()
    
    # Wait for preview to render
    time.sleep(2)
    app.processEvents()
    
    # Capture screenshot of preview
    screenshot_file = capture_screenshot(converter.preview_widget, "preview_rendering.png")
    
    # Check if reference screenshot exists
    reference_file = os.path.join("screenshots", "preview_rendering_reference.png")
    if not os.path.exists(reference_file):
        # Create reference screenshot
        os.rename(screenshot_file, reference_file)
        print("Visual test: preview_rendering - PASS (created reference)")
        return True
    
    # Compare with reference
    result = compare_screenshots(screenshot_file, reference_file)
    
    # Close the window
    converter.close()
    
    print(f"Visual test: preview_rendering - {'PASS' if result else 'FAIL'}")
    return result

def main():
    \"\"\"Run all visual tests\"\"\"
    print("Running visual tests...")
    
    # Run tests
    ui_result = test_ui_appearance()
    preview_result = test_preview_rendering()
    
    # Return success if all tests passed
    return 0 if ui_result and preview_result else 1

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open("visual_test.py", "w") as f:
        f.write(content)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Markdown to PDF Converter Test Runner")
    parser.add_argument("--test", help="Run a specific test (e.g., 'PagePreview.basic')")
    parser.add_argument("--file", help="Test a specific file")
    parser.add_argument("--format", choices=["pdf", "html", "docx", "mdz"], default="pdf", 
                       help="Output format for conversion tests")
    parser.add_argument("--timeout", type=int, default=30, 
                       help="Test timeout in seconds (default: 30)")
    parser.add_argument("--output-dir", default="test_results", 
                       help="Output directory for test results (default: test_results)")
    parser.add_argument("--category", choices=TEST_CATEGORIES.keys(), default=None,
                       help="Test category to run")
    parser.add_argument("--coverage", action="store_true", 
                       help="Run tests with coverage reporting")
    parser.add_argument("--performance", action="store_true", 
                       help="Run performance tests")
    parser.add_argument("--visual", action="store_true", 
                       help="Run visual tests")
    parser.add_argument("--regression", action="store_true", 
                       help="Run regression tests")
    parser.add_argument("--baseline", 
                       help="Baseline file for regression tests")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run tests based on arguments
    if args.coverage:
        # Run tests with coverage
        result = run_coverage_tests(args.timeout, args.output_dir)
        logger.info(str(result))
        return 0 if result.passed else 1
    
    elif args.performance:
        # Run performance tests
        results = run_performance_tests(args.timeout)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(args.output_dir, f"performance_results_{timestamp}.json")
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Print summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        logger.info(f"Performance tests completed: {passed}/{total} passed")
        logger.info(f"Results saved to {results_file}")
        
        return 0 if all(r.passed for r in results) else 1
    
    elif args.visual:
        # Run visual tests
        results = run_visual_tests(args.timeout)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(args.output_dir, f"visual_results_{timestamp}.json")
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Print summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        logger.info(f"Visual tests completed: {passed}/{total} passed")
        logger.info(f"Results saved to {results_file}")
        
        return 0 if all(r.passed for r in results) else 1
    
    elif args.regression:
        # Run regression tests
        result = run_regression_tests(args.timeout, args.baseline)
        logger.info(str(result))
        return 0 if result.passed else 1
    
    elif args.category:
        # Run tests in the specified category
        if args.category not in TEST_CATEGORIES:
            logger.error(f"Unknown test category: {args.category}")
            return 1
        
        # Get test scripts for the category
        test_scripts = TEST_CATEGORIES[args.category]
        
        # Run each test script
        results = []
        for test_script in test_scripts:
            cmd = ["python", test_script]
            result = run_test(f"{args.category}.{test_script}", cmd, args.timeout, 
                             category=args.category)
            results.append(result)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(args.output_dir, f"test_results_{args.category}_{timestamp}.json")
        with open(results_file, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        # Generate HTML report
        html_report_file = os.path.join(args.output_dir, f"test_report_{args.category}_{timestamp}.html")
        generate_html_report(results, html_report_file)
        
        # Print summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        logger.info(f"Tests completed: {passed}/{total} passed ({passed/total*100:.2f}%)")
        logger.info(f"Results saved to {results_file}")
        logger.info(f"HTML report saved to {html_report_file}")
        
        return 0 if all(r.passed for r in results) else 1
    
    elif args.test:
        # Parse test name
        parts = args.test.split('.')
        if len(parts) != 2:
            logger.error(f"Invalid test name: {args.test}")
            return 1
        
        test_type, test_name = parts
        
        # Run the test
        if test_type == "PagePreview":
            result = run_page_preview_test(test_name, args.timeout)
        elif test_type == "Conversion":
            if not args.file:
                logger.error("File must be specified for conversion tests")
                return 1
            result = run_markdown_conversion_test(args.file, args.format, args.timeout)
        elif test_type == "MDZ":
            if not args.file:
                logger.error("File must be specified for MDZ tests")
                return 1
            result = run_mdz_test(args.file, args.timeout)
        elif test_type == "UnitTest":
            results = run_unit_tests(args.timeout)
            # Filter for the specific test
            result = next((r for r in results if r.name.endswith(test_name)), None)
            if not result:
                logger.error(f"Unit test not found: {test_name}")
                return 1
        else:
            logger.error(f"Unknown test type: {test_type}")
            return 1
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(args.output_dir, f"test_result_{args.test}_{timestamp}.json")
        with open(result_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        # Print result
        logger.info(str(result))
        logger.info(f"Result saved to {result_file}")
        
        # Return success or failure
        return 0 if result.passed else 1
    
    elif args.file:
        # Run conversion test for the specified file
        result = run_markdown_conversion_test(args.file, args.format, args.timeout)
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(args.output_dir, f"test_result_{Path(args.file).stem}_{args.format}_{timestamp}.json")
        with open(result_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        
        # Print result
        logger.info(str(result))
        logger.info(f"Result saved to {result_file}")
        
        # Return success or failure
        return 0 if result.passed else 1
    
    else:
        # Run all tests
        results = run_all_tests(get_test_files(), args.timeout, args.output_dir)
        
        # Return success if all tests passed
        return 0 if all(r.passed for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
