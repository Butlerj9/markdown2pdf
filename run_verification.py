#!/usr/bin/env python3
"""
Markdown to PDF Converter Output Verification
--------------------------------------------
This script runs the entire verification process:
1. Generates test files with various settings combinations
2. Analyzes the output files to verify settings are correctly applied
3. Produces a detailed report showing which settings are correctly reflected in each output format
"""

import os
import sys
import argparse
import subprocess
import tempfile
import datetime
import logging
import json
import time
import signal
import threading
import psutil

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('run_verification')

def setup_watchdog(timeout_sec):
    """
    Set up a watchdog timer to kill the process if it runs for too long

    Args:
        timeout_sec (int): Timeout in seconds
    """
    def watchdog_handler():
        logger.error(f"Watchdog timer expired after {timeout_sec} seconds - forcibly terminating process")
        # Kill all child processes
        try:
            current_process = psutil.Process(os.getpid())
            children = current_process.children(recursive=True)
            for child in children:
                try:
                    logger.warning(f"Terminating child process: {child.pid}")
                    child.terminate()
                except:
                    pass

            # Give them a moment to terminate
            time.sleep(0.5)

            # Force kill any remaining processes
            for child in children:
                try:
                    if child.is_running():
                        logger.warning(f"Force killing child process: {child.pid}")
                        child.kill()
                except:
                    pass
        except Exception as e:
            logger.error(f"Error cleaning up processes: {str(e)}")

        # Kill the main process
        os._exit(1)

    # Start watchdog timer
    watchdog = threading.Timer(timeout_sec, watchdog_handler)
    watchdog.daemon = True
    watchdog.start()

    return watchdog

def run_export_tests(output_dir=None, verbose=False, timeout=120):
    """
    Run export tests with various settings combinations

    Args:
        output_dir (str, optional): Directory to save output files
        verbose (bool, optional): Enable verbose output
        timeout (int, optional): Timeout in seconds for the export tests

    Returns:
        tuple: (success, output_dir, records_dir)
    """
    logger.info(f"Running export tests with settings recording (timeout: {timeout}s)")

    # Create output directory if not specified
    if not output_dir:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(tempfile.gettempdir(), f"markdown_pdf_test_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

    # Build command - use minimal test script for faster execution
    cmd = [sys.executable, "test_minimal_exports.py"]

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["TEST_OUTPUT_DIR"] = output_dir
    env["TEST_TIMEOUT"] = str(timeout // 2)  # Set a timeout for individual tests

    if verbose:
        env["VERBOSE"] = "1"

    # Run the export tests
    logger.info(f"Running export tests, saving output to: {output_dir} (timeout: {timeout}s)")
    try:
        # Set up process-specific watchdog (more aggressive than the subprocess timeout)
        process_watchdog = setup_watchdog(timeout + 10)  # Add 10 seconds buffer

        process = subprocess.run(
            cmd,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout  # Add timeout to prevent hanging
        )

        # Cancel the process watchdog
        process_watchdog.cancel()

        # Log output
        if process.stdout:
            logger.info("Export test output:")
            for line in process.stdout.splitlines():
                logger.info(f"  {line}")

        if process.stderr:
            logger.warning("Export test errors:")
            for line in process.stderr.splitlines():
                logger.warning(f"  {line}")

        # Find the settings records directory
        records_dir = os.path.join(output_dir, "settings_records")
        if not os.path.exists(records_dir):
            logger.error(f"Settings records directory not found: {records_dir}")
            return False, output_dir, None

        return True, output_dir, records_dir

    except subprocess.TimeoutExpired:
        logger.error(f"Export tests timed out after {timeout} seconds")
        return False, output_dir, None

    except subprocess.CalledProcessError as e:
        logger.error(f"Error running export tests: {str(e)}")
        if e.stdout:
            logger.info("Export test output:")
            for line in e.stdout.splitlines():
                logger.info(f"  {line}")

        if e.stderr:
            logger.error("Export test errors:")
            for line in e.stderr.splitlines():
                logger.error(f"  {line}")

        return False, output_dir, None

def verify_outputs(records_dir, output_file=None, verbose=False, timeout=120):
    """
    Verify output files against expected settings

    Args:
        records_dir (str): Directory containing settings records
        output_file (str, optional): Path to save the verification report
        verbose (bool, optional): Enable verbose output
        timeout (int, optional): Timeout in seconds for the verification process

    Returns:
        bool: True if verification succeeded, False otherwise
    """
    logger.info(f"Verifying output files from records in: {records_dir} (timeout: {timeout}s)")

    # Build command
    cmd = [sys.executable, "verify_outputs.py", "--records-dir", records_dir]

    if output_file:
        cmd.extend(["--output", output_file])

    if verbose:
        cmd.append("--verbose")

    # Run the verification
    try:
        # Set up process-specific watchdog (more aggressive than the subprocess timeout)
        process_watchdog = setup_watchdog(timeout + 10)  # Add 10 seconds buffer

        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout  # Add timeout to prevent hanging
        )

        # Cancel the process watchdog
        process_watchdog.cancel()

        # Log output
        if process.stdout:
            logger.info("Verification output:")
            for line in process.stdout.splitlines():
                logger.info(f"  {line}")
                # Print to console as well
                print(line)

        if process.stderr:
            logger.warning("Verification errors:")
            for line in process.stderr.splitlines():
                logger.warning(f"  {line}")

        return process.returncode == 0

    except subprocess.TimeoutExpired:
        logger.error(f"Verification process timed out after {timeout} seconds")
        return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Error verifying outputs: {str(e)}")
        if e.stdout:
            logger.info("Verification output:")
            for line in e.stdout.splitlines():
                logger.info(f"  {line}")
                # Print to console as well
                print(line)

        if e.stderr:
            logger.error("Verification errors:")
            for line in e.stderr.splitlines():
                logger.error(f"  {line}")

        return False

def generate_html_report(json_report_path, html_output_path):
    """
    Generate an HTML report from the JSON report

    Args:
        json_report_path (str): Path to the JSON report
        html_output_path (str): Path to save the HTML report

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Generating HTML report from: {json_report_path}")

    try:
        # Load the JSON report
        with open(json_report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

        # Generate HTML
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to PDF Converter Verification Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .summary {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .format-results {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .format-card {
            flex: 1;
            min-width: 250px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success-rate {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .good {
            color: #28a745;
        }
        .warning {
            color: #ffc107;
        }
        .danger {
            color: #dc3545;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .discrepancy {
            background-color: #fff3cd;
        }
        .error {
            background-color: #f8d7da;
        }
        .details-toggle {
            cursor: pointer;
            color: #007bff;
            text-decoration: underline;
        }
        .details {
            display: none;
            margin-top: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Markdown to PDF Converter Verification Report</h1>
        <p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

        <div class="summary">
            <h2>Summary</h2>
            <p>Total files analyzed: """ + str(report["summary"]["total_files"]) + """</p>
            <p>Files with errors: """ + str(report["summary"]["files_with_errors"]) + """</p>
            <p>Files with discrepancies: """ + str(report["summary"]["files_with_discrepancies"]) + """</p>
            <div class="success-rate """ + ("good" if report["summary"]["success_rate"] >= 0.9 else "warning" if report["summary"]["success_rate"] >= 0.7 else "danger") + """">
                Overall Success Rate: """ + f"{report['summary']['success_rate']*100:.1f}%" + """
            </div>
        </div>

        <h2>Results by Format</h2>
        <div class="format-results">
"""

        # Add format cards
        for format_type, stats in report["format_results"].items():
            html += f"""
            <div class="format-card">
                <h3>{format_type.upper()}</h3>
                <p>Total: {stats['total']}</p>
                <p>Success: {stats['success']}</p>
                <p>Errors: {stats['errors']}</p>
                <p>Discrepancies: {stats['discrepancies']}</p>
                <div class="success-rate {
                    'good' if stats['success_rate'] >= 0.9 else
                    'warning' if stats['success_rate'] >= 0.7 else
                    'danger'
                }">
                    Success Rate: {stats['success_rate']*100:.1f}%
                </div>
            </div>
"""

        html += """
        </div>

        <h2>Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Format</th>
                    <th>Engine</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add detailed results
        for result in report["detailed_results"]:
            status = "Error" if "error" in result else "Discrepancies" if result["discrepancies"] else "Success"
            row_class = "error" if "error" in result else "discrepancy" if result["discrepancies"] else ""

            html += f"""
                <tr class="{row_class}">
                    <td>{result['test_id']}</td>
                    <td>{result['format'].upper()}</td>
                    <td>{result.get('engine', 'N/A')}</td>
                    <td>{status}</td>
                    <td>
"""

            if "error" in result:
                html += f"<span>{result['error']}</span>"
            elif result["discrepancies"]:
                html += f"""
                        <span class="details-toggle" onclick="toggleDetails('details-{result['test_id']}')">
                            {len(result['discrepancies'])} discrepancies (click to show)
                        </span>
                        <div id="details-{result['test_id']}" class="details">
                            <ul>
"""

                for discrepancy in result["discrepancies"]:
                    html += f"""
                                <li>
                                    <strong>{discrepancy['setting']}:</strong>
                                    Expected: {discrepancy['expected']},
                                    Actual: {discrepancy['actual']}
                                </li>
"""

                html += """
                            </ul>
                        </div>
"""
            else:
                html += "<span>All settings verified</span>"

            html += """
                    </td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>

    <script>
        function toggleDetails(id) {
            const element = document.getElementById(id);
            if (element.style.display === "block") {
                element.style.display = "none";
            } else {
                element.style.display = "block";
            }
        }
    </script>
</body>
</html>
"""

        # Save the HTML report
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"HTML report saved to: {html_output_path}")
        return True

    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run Markdown to PDF Converter output verification')
    parser.add_argument('--output-dir', help='Directory to save output files')
    parser.add_argument('--skip-export', action='store_true', help='Skip export tests and use existing records')
    parser.add_argument('--records-dir', help='Directory containing settings records (required if --skip-export is used)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--export-timeout', type=int, default=60, help='Timeout in seconds for export tests (default: 60)')
    parser.add_argument('--verify-timeout', type=int, default=60, help='Timeout in seconds for verification process (default: 60)')
    parser.add_argument('--global-timeout', type=int, default=300, help='Global timeout for the entire process in seconds (default: 300)')
    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Set up global watchdog timer
    logger.info(f"Setting up global watchdog timer ({args.global_timeout} seconds)")
    watchdog = setup_watchdog(args.global_timeout)

    start_time = time.time()

    # Create output directory if not specified
    output_dir = args.output_dir
    if not output_dir:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(tempfile.gettempdir(), f"markdown_pdf_verification_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Output directory: {output_dir}")

    # Step 1: Run export tests (unless skipped)
    if args.skip_export:
        if not args.records_dir:
            logger.error("--records-dir is required when --skip-export is used")
            return 1

        records_dir = args.records_dir
        logger.info(f"Skipping export tests, using existing records from: {records_dir}")
    else:
        logger.info("Step 1: Running export tests")
        success, test_output_dir, records_dir = run_export_tests(
            output_dir,
            args.verbose,
            timeout=args.export_timeout
        )

        if not success:
            logger.error("Export tests failed")
            return 1

        logger.info(f"Export tests completed successfully")
        logger.info(f"Test output directory: {test_output_dir}")
        logger.info(f"Settings records directory: {records_dir}")

    # Step 2: Verify outputs
    logger.info("Step 2: Verifying outputs")
    json_report_path = os.path.join(output_dir, "verification_report.json")
    success = verify_outputs(
        records_dir,
        json_report_path,
        args.verbose,
        timeout=args.verify_timeout
    )

    if not success:
        logger.warning("Verification found issues")
    else:
        logger.info("Verification completed successfully")

    # Step 3: Generate HTML report
    logger.info("Step 3: Generating HTML report")
    html_report_path = os.path.join(output_dir, "verification_report.html")
    generate_html_report(json_report_path, html_report_path)

    # Print summary
    elapsed_time = time.time() - start_time
    logger.info(f"Verification process completed in {elapsed_time:.1f} seconds")
    logger.info(f"JSON report: {json_report_path}")
    logger.info(f"HTML report: {html_report_path}")

    # Open the HTML report
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(html_report_path)}")
    except:
        logger.warning("Could not open HTML report automatically")

    # Cancel the watchdog timer
    try:
        watchdog.cancel()
        logger.info("Watchdog timer cancelled")
    except:
        pass

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
