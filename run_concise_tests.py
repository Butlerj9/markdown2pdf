#!/usr/bin/env python3
"""
Concise test runner for markdown to PDF converter
"""

import os
import sys
import time
import argparse
import subprocess
import json
from datetime import datetime

def run_test(format_type, test_name=None, timeout=120):
    """Run a specific test with minimal output"""
    start_time = time.time()

    # Create a modified environment with reduced logging
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"  # Ensure unbuffered output

    cmd = ["python", "test_export_verification.py", f"--format={format_type}", "--quiet"]
    if test_name:
        cmd.append(f"--test={test_name}")

    # Run the process and capture output in real-time
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        bufsize=1
    )

    results = []
    has_failure = False

    try:
        # Process output in real-time
        for line in process.stdout:
            line = line.strip()
            if "/" in line and "%" in line and ("OK" in line or "FAIL" in line):
                print(line)
                results.append(line)
                if "FAIL" in line:
                    has_failure = True

        # Wait for process to complete
        process.wait(timeout=timeout)

        # Check if there were any failures
        return not has_failure

    except subprocess.TimeoutExpired:
        process.kill()
        print(f"{format_type.upper()} test timed out after {timeout} seconds")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run markdown to PDF converter tests with concise output")
    parser.add_argument("--format", choices=["pdf", "html", "epub", "docx", "all"], default="all",
                      help="Format to test (default: all)")
    parser.add_argument("--timeout", type=int, default=120,
                      help="Timeout in seconds for each test (default: 120)")
    args = parser.parse_args()

    formats_to_test = ["pdf", "html", "epub", "docx"] if args.format == "all" else [args.format]

    print(f"Running tests for formats: {', '.join(formats_to_test)}")
    print("=" * 80)
    print("Test            Format Engine     Settings             Time     Size     Status")
    print("-" * 80)

    results = {}
    for format_type in formats_to_test:
        results[format_type] = run_test(format_type, timeout=args.timeout)

    print("=" * 80)
    print("Test Summary:")
    for format_type, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{format_type.upper():<10} {status}")

    # Return non-zero exit code if any test failed
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
