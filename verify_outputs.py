#!/usr/bin/env python3
"""
Output Verification Framework for Markdown to PDF Converter
----------------------------------------------------------
This script verifies that the settings used in the Markdown to PDF converter
are correctly reflected in the output files.
"""

import os
import json
import argparse
import logging
import time
import threading
import signal
import sys
from pdf_analyzer import analyze_pdf
from html_analyzer import analyze_html
from epub_analyzer import analyze_epub
from docx_analyzer import analyze_docx

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('verify_outputs')

def setup_watchdog(timeout_sec):
    """
    Set up a watchdog timer to kill the process if it runs for too long

    Args:
        timeout_sec (int): Timeout in seconds
    """
    def watchdog_handler():
        logger.error(f"Watchdog timer expired after {timeout_sec} seconds - forcibly terminating process")
        # Kill the process
        os._exit(1)

    # Start watchdog timer
    watchdog = threading.Timer(timeout_sec, watchdog_handler)
    watchdog.daemon = True
    watchdog.start()

    return watchdog

def load_settings_records(records_dir):
    """
    Load all settings records from the records directory

    Args:
        records_dir (str): Path to the directory containing settings records

    Returns:
        list: List of settings records
    """
    logger.info(f"Loading settings records from: {records_dir}")

    records = []
    for filename in os.listdir(records_dir):
        if filename.startswith("settings_record_") and filename.endswith(".json"):
            record_path = os.path.join(records_dir, filename)
            try:
                with open(record_path, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                    records.append(record)
                    logger.debug(f"Loaded record: {filename}")
            except Exception as e:
                logger.error(f"Error loading record {filename}: {str(e)}")

    logger.info(f"Loaded {len(records)} settings records")
    return records

def analyze_with_timeout(func, output_file, timeout=30):
    """
    Run an analyzer function with a timeout

    Args:
        func (callable): Analyzer function to run
        output_file (str): Path to the output file
        timeout (int): Timeout in seconds

    Returns:
        dict: Analysis results or error
    """
    result = [None]
    exception = [None]
    finished = [False]

    def target():
        try:
            result[0] = func(output_file)
        except Exception as e:
            exception[0] = e
        finally:
            finished[0] = True

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

    # Wait for thread to finish or timeout
    start_time = time.time()
    while not finished[0] and (time.time() - start_time) < timeout:
        time.sleep(0.1)

    if not finished[0]:
        return {"error": f"Analysis timed out after {timeout} seconds"}

    if exception[0]:
        return {"error": f"Error during analysis: {str(exception[0])}"}

    return result[0]

def analyze_output_file(record):
    """
    Analyze the output file based on its format

    Args:
        record (dict): Settings record containing output file information

    Returns:
        dict: Analysis results
    """
    output_file = record["output_file"]
    format_type = record["format"]

    logger.info(f"Analyzing {format_type.upper()} file: {os.path.basename(output_file)}")

    if not os.path.exists(output_file):
        logger.error(f"Output file not found: {output_file}")
        return {"error": f"Output file not found: {output_file}"}

    try:
        # Use a timeout for each analyzer to prevent hanging
        if format_type == "pdf":
            logger.info(f"Running PDF analyzer with timeout (30s)")
            return analyze_with_timeout(analyze_pdf, output_file)
        elif format_type == "html":
            logger.info(f"Running HTML analyzer with timeout (30s)")
            return analyze_with_timeout(analyze_html, output_file)
        elif format_type == "epub":
            logger.info(f"Running EPUB analyzer with timeout (30s)")
            return analyze_with_timeout(analyze_epub, output_file)
        elif format_type == "docx":
            logger.info(f"Running DOCX analyzer with timeout (30s)")
            return analyze_with_timeout(analyze_docx, output_file)
        else:
            logger.error(f"Unsupported format: {format_type}")
            return {"error": f"Unsupported format: {format_type}"}
    except Exception as e:
        logger.error(f"Error analyzing {format_type} file: {str(e)}")
        return {"error": f"Error analyzing {format_type} file: {str(e)}"}

def compare_settings(expected, actual, format_type):
    """
    Compare expected settings with actual settings

    Args:
        expected (dict): Expected settings from the record
        actual (dict): Actual settings from the analysis
        format_type (str): Format type (pdf, html, epub, docx)

    Returns:
        list: List of discrepancies
    """
    discrepancies = []

    # Helper function to add a discrepancy
    def add_discrepancy(setting, expected_value, actual_value):
        discrepancies.append({
            "setting": setting,
            "expected": expected_value,
            "actual": actual_value
        })

    # Check for error in analysis
    if "error" in actual:
        add_discrepancy("analysis", "success", actual["error"])
        return discrepancies

    # Compare page settings
    if "page_size" in actual:
        expected_page_size = expected["settings"]["page"]["size"]
        if expected_page_size.lower() not in actual["page_size"].lower():
            add_discrepancy("page_size", expected_page_size, actual["page_size"])

    # Compare orientation
    if "orientation" in actual:
        expected_orientation = expected["settings"]["page"]["orientation"]
        if expected_orientation.lower() != actual["orientation"].lower():
            add_discrepancy("orientation", expected_orientation, actual["orientation"])

    # Compare TOC settings
    if "has_toc" in actual:
        expected_toc = expected["settings"]["toc"]["include"]
        if expected_toc != actual["has_toc"]:
            add_discrepancy("toc_include", expected_toc, actual["has_toc"])

    if "toc_depth" in actual and actual["has_toc"]:
        expected_depth = expected["settings"]["toc"]["depth"]
        # Only check if the actual depth is less than expected
        # (some formats might not show all levels even if specified)
        if actual["toc_depth"] < expected_depth:
            add_discrepancy("toc_depth", expected_depth, actual["toc_depth"])

    # Compare heading numbering
    if "heading_numbering" in actual:
        expected_numbering = "technical" if expected["settings"]["format"]["technical_numbering"] else "standard"
        if expected_numbering != actual["heading_numbering"] and actual["heading_numbering"] != "mixed":
            add_discrepancy("heading_numbering", expected_numbering, actual["heading_numbering"])

    # Compare font settings (format-specific)
    if format_type == "pdf" and "body_font" in actual and actual["body_font"]:
        # For PDF, check if the font family contains the expected font name
        if expected["settings"]["font"]["use_master_font"]:
            expected_font = expected["settings"]["font"]["master_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)
        else:
            expected_font = expected["settings"]["font"]["body_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)

    # For HTML and EPUB, check CSS styles
    if format_type in ["html", "epub"] and "body_font" in actual and actual["body_font"]:
        if expected["settings"]["font"]["use_master_font"]:
            expected_font = expected["settings"]["font"]["master_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)
        else:
            expected_font = expected["settings"]["font"]["body_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)

    # For DOCX, check document styles
    if format_type == "docx" and "body_font" in actual and actual["body_font"]:
        if expected["settings"]["font"]["use_master_font"]:
            expected_font = expected["settings"]["font"]["master_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)
        else:
            expected_font = expected["settings"]["font"]["body_font"]["family"]
            actual_font = actual["body_font"]["family"]
            if expected_font and actual_font and expected_font.lower() not in actual_font.lower():
                add_discrepancy("body_font", expected_font, actual_font)

    # Add more format-specific comparisons as needed

    return discrepancies

def generate_report(results, output_file=None):
    """
    Generate a verification report

    Args:
        results (list): List of verification results
        output_file (str, optional): Path to save the report

    Returns:
        dict: Summary of the verification results
    """
    # Generate summary
    total_files = len(results)
    files_with_errors = sum(1 for r in results if "error" in r)
    files_with_discrepancies = sum(1 for r in results if r["discrepancies"])

    summary = {
        "total_files": total_files,
        "files_with_errors": files_with_errors,
        "files_with_discrepancies": files_with_discrepancies,
        "success_rate": (total_files - files_with_errors - files_with_discrepancies) / total_files if total_files > 0 else 0
    }

    # Group results by format
    format_results = {}
    for result in results:
        format_type = result["format"]
        if format_type not in format_results:
            format_results[format_type] = {
                "total": 0,
                "errors": 0,
                "discrepancies": 0,
                "success": 0
            }

        format_results[format_type]["total"] += 1

        if "error" in result:
            format_results[format_type]["errors"] += 1
        elif result["discrepancies"]:
            format_results[format_type]["discrepancies"] += 1
        else:
            format_results[format_type]["success"] += 1

    # Calculate success rates for each format
    for format_type, stats in format_results.items():
        stats["success_rate"] = stats["success"] / stats["total"] if stats["total"] > 0 else 0

    # Create full report
    report = {
        "summary": summary,
        "format_results": format_results,
        "detailed_results": results
    }

    # Save report if output file is specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Verification report saved to {output_file}")

    return report

def print_report_summary(report):
    """Print a summary of the verification report"""
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)

    summary = report["summary"]
    print(f"Total files analyzed: {summary['total_files']}")
    print(f"Files with errors: {summary['files_with_errors']}")
    print(f"Files with discrepancies: {summary['files_with_discrepancies']}")
    print(f"Success rate: {summary['success_rate']*100:.1f}%")

    print("\nResults by format:")
    for format_type, stats in report["format_results"].items():
        print(f"\n{format_type.upper()}:")
        print(f"  Total: {stats['total']}")
        print(f"  Success: {stats['success']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Discrepancies: {stats['discrepancies']}")
        print(f"  Success rate: {stats['success_rate']*100:.1f}%")

    # Print top discrepancies
    all_discrepancies = []
    for result in report["detailed_results"]:
        if "discrepancies" in result and result["discrepancies"]:
            for discrepancy in result["discrepancies"]:
                all_discrepancies.append({
                    "format": result["format"],
                    "test_id": result["test_id"],
                    "setting": discrepancy["setting"],
                    "expected": discrepancy["expected"],
                    "actual": discrepancy["actual"]
                })

    if all_discrepancies:
        print("\nTop discrepancies:")
        # Group by setting
        setting_counts = {}
        for discrepancy in all_discrepancies:
            setting = discrepancy["setting"]
            if setting not in setting_counts:
                setting_counts[setting] = 0
            setting_counts[setting] += 1

        # Print top 5 most common discrepancies
        for setting, count in sorted(setting_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {setting}: {count} occurrences")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Verify output files against expected settings')
    parser.add_argument('--records-dir', required=True, help='Directory containing settings records')
    parser.add_argument('--output', help='Path to save the verification report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--timeout', type=int, default=120, help='Timeout in seconds (default: 120)')
    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Set up watchdog timer
    logger.info(f"Setting up watchdog timer ({args.timeout} seconds)")
    watchdog = setup_watchdog(args.timeout)

    # Load settings records
    records = load_settings_records(args.records_dir)

    # Analyze output files and compare with expected settings
    results = []
    for record in records:
        logger.info(f"Processing record {record['test_id']}: {record['format']} file")

        # Skip records with failed exports
        if record.get("result") == "failure":
            logger.info(f"Skipping record {record['test_id']} as the export failed")
            results.append({
                "test_id": record["test_id"],
                "format": record["format"],
                "engine": record.get("engine"),
                "output_file": record["output_file"],
                "error": "Export failed",
                "discrepancies": []
            })
            continue

        # Analyze the output file
        actual_settings = analyze_output_file(record)

        # Check for analysis error
        if "error" in actual_settings:
            results.append({
                "test_id": record["test_id"],
                "format": record["format"],
                "engine": record.get("engine"),
                "output_file": record["output_file"],
                "error": actual_settings["error"],
                "discrepancies": []
            })
            continue

        # Compare expected and actual settings
        discrepancies = compare_settings(record, actual_settings, record["format"])

        # Add result
        results.append({
            "test_id": record["test_id"],
            "format": record["format"],
            "engine": record.get("engine"),
            "output_file": record["output_file"],
            "discrepancies": discrepancies
        })

    # Generate and print report
    report = generate_report(results, args.output)
    print_report_summary(report)

    # Cancel the watchdog timer
    try:
        watchdog.cancel()
        logger.info("Watchdog timer cancelled")
    except:
        pass

    # Return success if no errors or discrepancies
    return 0 if report["summary"]["files_with_errors"] == 0 and report["summary"]["files_with_discrepancies"] == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
