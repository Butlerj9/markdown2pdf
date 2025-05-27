#!/usr/bin/env python3
"""
MDZ Integration Tester
-------------------
This script provides comprehensive integration testing for the MDZ format stack,
testing various combinations of input files and command line options.

File: mdz_integration_tester.py
"""

import os
import sys
import logging
import argparse
import tempfile
import shutil
import json
import yaml
import re
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDZIntegrationTester:
    """
    MDZ Integration Tester class for comprehensive testing of the MDZ format stack
    """

    def __init__(self, output_dir: Optional[str] = None, test_files_dir: Optional[str] = None):
        """
        Initialize the MDZ integration tester

        Args:
            output_dir: Optional directory to store test results
            test_files_dir: Optional directory containing test files
        """
        # Create a temporary directory if no output directory is provided
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        else:
            self.output_dir = tempfile.mkdtemp(prefix="mdz_integration_test_")

        # Use the provided test files directory or look for the one created by the validator
        if test_files_dir:
            self.test_files_dir = test_files_dir
        else:
            # Try to find the test files directory created by the validator
            validator_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mdz_validation_results")
            if os.path.exists(validator_output_dir):
                self.test_files_dir = os.path.join(validator_output_dir, "test_files")
            else:
                # Create a new test files directory
                self.test_files_dir = os.path.join(self.output_dir, "test_files")
                os.makedirs(self.test_files_dir, exist_ok=True)

                # Generate test files
                self._generate_test_files()

        # Create subdirectories for test results
        self.results_dir = os.path.join(self.output_dir, "integration_results")
        os.makedirs(self.results_dir, exist_ok=True)

        # Initialize test results
        self.test_results = {}

        # Define test combinations
        self.test_combinations = self._define_test_combinations()

    def _generate_test_files(self):
        """Generate test files if they don't exist"""
        logger.info("Generating test files...")

        # Run the validator to generate test files
        try:
            from mdz_comprehensive_validator import MDZValidator
            validator = MDZValidator(output_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "mdz_validation_results"))
            validator.generate_test_files()
            logger.info("Generated test files using MDZValidator")
        except ImportError:
            logger.error("MDZValidator not found, cannot generate test files")
            sys.exit(1)

    def _define_test_combinations(self) -> List[Dict[str, Any]]:
        """
        Define test combinations

        Returns:
            List of test combinations
        """
        combinations = []

        # Get all MDZ files in the test files directory
        mdz_files = [f for f in os.listdir(self.test_files_dir) if f.endswith(".mdz")]

        # Define output formats
        output_formats = ["html", "pdf", "epub", "docx"]

        # Define command line options
        option_sets = [
            {"toc": True, "numbering": True, "theme": "default"},
            {"toc": False, "numbering": False, "theme": "default"},
            {"toc": True, "numbering": False, "theme": "dark"},
            {"toc": False, "numbering": True, "theme": "light"}
        ]

        # Create combinations
        for mdz_file in mdz_files:
            for output_format in output_formats:
                for options in option_sets:
                    combinations.append({
                        "input_file": os.path.join(self.test_files_dir, mdz_file),
                        "output_format": output_format,
                        "options": options,
                        "test_id": f"{mdz_file.replace('.mdz', '')}_{output_format}_{hashlib.md5(str(options).encode()).hexdigest()[:6]}"
                    })

        return combinations

    def run_test(self, test_combination: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test

        Args:
            test_combination: Test combination

        Returns:
            Test result
        """
        input_file = test_combination["input_file"]
        output_format = test_combination["output_format"]
        options = test_combination["options"]
        test_id = test_combination["test_id"]

        # Create a directory for this test
        test_dir = os.path.join(self.results_dir, test_id)
        os.makedirs(test_dir, exist_ok=True)

        # Define output file
        output_file = os.path.join(test_dir, f"output.{output_format}")

        # For MDZ files, we need to extract them first
        if input_file.endswith(".mdz"):
            # Create a temporary directory for extraction
            temp_dir = os.path.join(test_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            # Extract the MDZ file
            try:
                from mdz_bundle import extract_mdz_to_markdown
                md_file = os.path.join(temp_dir, os.path.basename(input_file).replace(".mdz", ".md"))
                extract_mdz_to_markdown(input_file, md_file, extract_assets=True)
                input_file = md_file
            except ImportError:
                logger.error("MDZ bundle module not found")
                return {
                    "test_id": test_id,
                    "input_file": input_file,
                    "output_format": output_format,
                    "options": options,
                    "success": False,
                    "elapsed_time": 0,
                    "output_exists": False,
                    "output_size": 0,
                    "validation_result": {"success": False, "errors": ["MDZ bundle module not found"]},
                    "error": "MDZ bundle module not found"
                }
            except Exception as e:
                logger.error(f"Error extracting MDZ file: {str(e)}")
                return {
                    "test_id": test_id,
                    "input_file": input_file,
                    "output_format": output_format,
                    "options": options,
                    "success": False,
                    "elapsed_time": 0,
                    "output_exists": False,
                    "output_size": 0,
                    "validation_result": {"success": False, "errors": [f"Error extracting MDZ file: {str(e)}"]},
                    "error": f"Error extracting MDZ file: {str(e)}"
                }

        # Build the command
        cmd = [
            sys.executable,
            "mdz_renderer.py",
            input_file,
            "--output", output_file,
            "--format", output_format
        ]

        # Add options
        if options.get("toc", False):
            cmd.extend(["--toc"])
        if options.get("numbering", False):
            cmd.extend(["--numbering"])
        if options.get("theme"):
            cmd.extend(["--theme", options["theme"]])

        # Run the command
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = result.returncode == 0
            elapsed_time = time.time() - start_time

            # Save the output
            with open(os.path.join(test_dir, "stdout.txt"), "w", encoding="utf-8") as f:
                f.write(result.stdout)
            with open(os.path.join(test_dir, "stderr.txt"), "w", encoding="utf-8") as f:
                f.write(result.stderr)

            # Check if the output file was created
            output_exists = os.path.exists(output_file)
            output_size = os.path.getsize(output_file) if output_exists else 0

            # Validate the output
            validation_result = self._validate_output(output_file, output_format, options)

            # Create the test result
            test_result = {
                "test_id": test_id,
                "input_file": input_file,
                "output_format": output_format,
                "options": options,
                "success": success and output_exists and validation_result["success"],
                "elapsed_time": elapsed_time,
                "output_exists": output_exists,
                "output_size": output_size,
                "validation_result": validation_result,
                "error": result.stderr if not success else None
            }

            return test_result

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error running test {test_id}: {str(e)}")

            # Create the test result
            test_result = {
                "test_id": test_id,
                "input_file": input_file,
                "output_format": output_format,
                "options": options,
                "success": False,
                "elapsed_time": elapsed_time,
                "output_exists": False,
                "output_size": 0,
                "validation_result": {"success": False, "errors": [str(e)]},
                "error": str(e)
            }

            return test_result

    def _validate_output(self, output_file: str, output_format: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the output file

        Args:
            output_file: Path to the output file
            output_format: Output format
            options: Command line options

        Returns:
            Validation result
        """
        # Check if the file exists
        if not os.path.exists(output_file):
            return {"success": False, "errors": ["Output file does not exist"]}

        # Check if the file is not empty
        if os.path.getsize(output_file) == 0:
            return {"success": False, "errors": ["Output file is empty"]}

        # Validate based on the output format
        if output_format == "html":
            return self._validate_html(output_file, options)
        elif output_format == "pdf":
            return self._validate_pdf(output_file, options)
        elif output_format == "epub":
            return self._validate_epub(output_file, options)
        elif output_format == "docx":
            return self._validate_docx(output_file, options)
        else:
            return {"success": False, "errors": [f"Unknown output format: {output_format}"]}

    def _validate_html(self, output_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate HTML output

        Args:
            output_file: Path to the HTML file
            options: Command line options

        Returns:
            Validation result
        """
        errors = []

        try:
            # Read the HTML content
            with open(output_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Check for basic HTML structure
            if not html_content.startswith("<!DOCTYPE html>"):
                errors.append("Invalid HTML structure")

            # Check for title
            if "<title>" not in html_content:
                errors.append("Missing title")

            # Check for content
            if "<body>" not in html_content:
                errors.append("Missing body")

            # Check for table of contents if enabled
            if options.get("toc", False):
                # The TOC CSS is included in the HTML
                if ".toc {" not in html_content:
                    errors.append("Missing table of contents CSS")

            # Check for theme
            theme = options.get("theme", "default")
            if theme == "dark":
                if "background-color: #1e1e1e;" not in html_content:
                    errors.append(f"Theme '{theme}' not applied")
            elif theme == "light":
                if "background-color: #ffffff;" not in html_content:
                    errors.append(f"Theme '{theme}' not applied")

            # Check for numbering
            if options.get("numbering", False):
                if "counter-reset: h1;" not in html_content:
                    errors.append("Numbering not applied")

            return {"success": len(errors) == 0, "errors": errors}

        except Exception as e:
            return {"success": False, "errors": [f"Error validating HTML: {str(e)}"]}

    def _validate_pdf(self, output_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PDF output

        Args:
            output_file: Path to the PDF file
            options: Command line options

        Returns:
            Validation result
        """
        # For PDF, we can only check if the file exists and has content
        # More detailed validation would require a PDF parser
        return {"success": True, "errors": []}

    def _validate_epub(self, output_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate EPUB output

        Args:
            output_file: Path to the EPUB file
            options: Command line options

        Returns:
            Validation result
        """
        # For EPUB, we can only check if the file exists and has content
        # More detailed validation would require an EPUB parser
        return {"success": True, "errors": []}

    def _validate_docx(self, output_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate DOCX output

        Args:
            output_file: Path to the DOCX file
            options: Command line options

        Returns:
            Validation result
        """
        # For DOCX, we can only check if the file exists and has content
        # More detailed validation would require a DOCX parser
        return {"success": True, "errors": []}

    def run_tests(self, max_tests: Optional[int] = None, skip_formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run all tests

        Args:
            max_tests: Maximum number of tests to run
            skip_formats: List of output formats to skip

        Returns:
            Test results
        """
        logger.info(f"Running {len(self.test_combinations)} test combinations...")

        # Filter test combinations
        filtered_combinations = self.test_combinations
        if skip_formats:
            filtered_combinations = [c for c in filtered_combinations if c["output_format"] not in skip_formats]
        if max_tests:
            filtered_combinations = filtered_combinations[:max_tests]

        # Run tests
        results = []
        for i, combination in enumerate(filtered_combinations):
            logger.info(f"Running test {i+1}/{len(filtered_combinations)}: {combination['test_id']}")
            result = self.run_test(combination)
            results.append(result)

            # Log the result
            if result["success"]:
                logger.info(f"Test {result['test_id']} passed in {result['elapsed_time']:.2f}s")
            else:
                logger.error(f"Test {result['test_id']} failed in {result['elapsed_time']:.2f}s")
                if result.get("error"):
                    logger.error(f"Error: {result['error']}")

        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - passed_tests

        # Group results by output format
        results_by_format = {}
        for result in results:
            output_format = result["output_format"]
            if output_format not in results_by_format:
                results_by_format[output_format] = []
            results_by_format[output_format].append(result)

        # Calculate statistics by format
        stats_by_format = {}
        for output_format, format_results in results_by_format.items():
            total = len(format_results)
            passed = sum(1 for r in format_results if r["success"])
            failed = total - passed
            stats_by_format[output_format] = {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": passed / total if total > 0 else 0
            }

        # Save the results
        results_file = os.path.join(self.results_dir, "test_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "stats_by_format": stats_by_format,
                "results": results
            }, f, indent=2)

        # Generate a report
        self._generate_report(results, stats_by_format)

        logger.info(f"Test results saved to {results_file}")
        logger.info(f"Total tests: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}")

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "stats_by_format": stats_by_format,
            "results": results
        }

    def _generate_report(self, results: List[Dict[str, Any]], stats_by_format: Dict[str, Dict[str, Any]]) -> None:
        """
        Generate a test report

        Args:
            results: Test results
            stats_by_format: Statistics by format
        """
        report_file = os.path.join(self.results_dir, "test_report.html")

        # Create the report
        report = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDZ Integration Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 1em;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
        }}
        table, th, td {{
            border: 1px solid #dfe2e5;
        }}
        th, td {{
            padding: 0.5em;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
        }}
        .success {{
            color: green;
        }}
        .failure {{
            color: red;
        }}
        .summary {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 2em;
        }}
        .summary-box {{
            border: 1px solid #dfe2e5;
            border-radius: 5px;
            padding: 1em;
            width: 30%;
            text-align: center;
        }}
        .summary-box h3 {{
            margin-top: 0;
        }}
        .pass-rate {{
            font-size: 2em;
            font-weight: bold;
        }}
        .format-summary {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-bottom: 2em;
        }}
        .format-box {{
            border: 1px solid #dfe2e5;
            border-radius: 5px;
            padding: 1em;
            width: 22%;
            text-align: center;
            margin-bottom: 1em;
        }}
        .format-box h3 {{
            margin-top: 0;
        }}
        .format-pass-rate {{
            font-size: 1.5em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>MDZ Integration Test Report</h1>

    <div class="summary">
        <div class="summary-box">
            <h3>Total Tests</h3>
            <div class="pass-rate">{len(results)}</div>
        </div>
        <div class="summary-box">
            <h3>Passed Tests</h3>
            <div class="pass-rate success">{sum(1 for r in results if r["success"])}</div>
        </div>
        <div class="summary-box">
            <h3>Failed Tests</h3>
            <div class="pass-rate failure">{sum(1 for r in results if not r["success"])}</div>
        </div>
    </div>

    <h2>Results by Format</h2>

    <div class="format-summary">
"""

        # Add format summaries
        for output_format, stats in stats_by_format.items():
            report += f"""
        <div class="format-box">
            <h3>{output_format.upper()}</h3>
            <div class="format-pass-rate {'success' if stats['pass_rate'] == 1.0 else 'failure'}">{stats['pass_rate']:.0%}</div>
            <div>Passed: {stats['passed']}/{stats['total']}</div>
        </div>
"""

        report += """
    </div>

    <h2>Test Results</h2>

    <table>
        <thead>
            <tr>
                <th>Test ID</th>
                <th>Input File</th>
                <th>Output Format</th>
                <th>Options</th>
                <th>Status</th>
                <th>Time (s)</th>
                <th>Output Size</th>
            </tr>
        </thead>
        <tbody>
"""

        # Add test results
        for result in results:
            input_file = os.path.basename(result["input_file"])
            options_str = ", ".join(f"{k}={v}" for k, v in result["options"].items())
            status = "Success" if result["success"] else "Failure"
            status_class = "success" if result["success"] else "failure"

            report += f"""
            <tr>
                <td>{result['test_id']}</td>
                <td>{input_file}</td>
                <td>{result['output_format']}</td>
                <td>{options_str}</td>
                <td class="{status_class}">{status}</td>
                <td>{result['elapsed_time']:.2f}</td>
                <td>{result['output_size']} bytes</td>
            </tr>
"""

        report += """
        </tbody>
    </table>

    <h2>Failed Tests</h2>

    <table>
        <thead>
            <tr>
                <th>Test ID</th>
                <th>Input File</th>
                <th>Output Format</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
"""

        # Add failed test details
        failed_tests = [r for r in results if not r["success"]]
        if failed_tests:
            for result in failed_tests:
                input_file = os.path.basename(result["input_file"])
                error = result.get("error", "Unknown error") or "Unknown error"
                validation_errors = result.get("validation_result", {}).get("errors", [])
                if validation_errors:
                    error += "<br>" + "<br>".join(validation_errors)

                report += f"""
                <tr>
                    <td>{result['test_id']}</td>
                    <td>{input_file}</td>
                    <td>{result['output_format']}</td>
                    <td>{error}</td>
                </tr>
"""
        else:
            report += """
                <tr>
                    <td colspan="4">No failed tests</td>
                </tr>
"""

        report += """
        </tbody>
    </table>
</body>
</html>
"""

        # Save the report
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Test report saved to {report_file}")


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MDZ Integration Tester")
    parser.add_argument("--output-dir", "-o", help="Directory to store test results")
    parser.add_argument("--test-files-dir", "-t", help="Directory containing test files")
    parser.add_argument("--max-tests", "-m", type=int, help="Maximum number of tests to run")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip PDF export tests")
    parser.add_argument("--skip-epub", action="store_true", help="Skip EPUB export tests")
    parser.add_argument("--skip-docx", action="store_true", help="Skip DOCX export tests")

    args = parser.parse_args()

    # Create a tester
    tester = MDZIntegrationTester(output_dir=args.output_dir, test_files_dir=args.test_files_dir)

    # Determine which formats to skip
    skip_formats = []
    if args.skip_pdf:
        skip_formats.append("pdf")
    if args.skip_epub:
        skip_formats.append("epub")
    if args.skip_docx:
        skip_formats.append("docx")

    # Run tests
    results = tester.run_tests(max_tests=args.max_tests, skip_formats=skip_formats)

    # Print summary
    print("\nTest Summary:")
    print(f"  Total tests: {results['total_tests']}")
    print(f"  Passed tests: {results['passed_tests']}")
    print(f"  Failed tests: {results['failed_tests']}")
    print(f"  Pass rate: {results['pass_rate']:.2%}")

    print("\nResults by format:")
    for output_format, stats in results['stats_by_format'].items():
        print(f"  {output_format.upper()}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.2%})")

    print(f"\nTest results saved to {os.path.join(tester.results_dir, 'test_results.json')}")
    print(f"Test report saved to {os.path.join(tester.results_dir, 'test_report.html')}")

    # Return appropriate exit code
    return 0 if results['failed_tests'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
