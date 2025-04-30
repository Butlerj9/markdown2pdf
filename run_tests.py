#!/usr/bin/env python3
"""
Test Runner for Markdown to PDF Converter
----------------------------------------
Provides a command-line interface for running tests.
"""

import os
import sys
import argparse
import unittest
import signal
import time
import multiprocessing
import threading
import psutil
import traceback
from PyQt6.QtWidgets import QApplication

# Import test modules
try:
    from unit_tests import ExportTests, SettingsTests, ExportWithSettingsTests
    from export_tests import ExportTestCase
    from settings_tests import SettingsTestCase
    UNIT_TESTING_AVAILABLE = True
except ImportError:
    UNIT_TESTING_AVAILABLE = False
    print("Warning: Unit testing modules not available")

try:
    from visual_test import VisualTester
    import visual_test_runner
    VISUAL_TESTING_AVAILABLE = True
except ImportError:
    VISUAL_TESTING_AVAILABLE = False
    print("Warning: Visual testing modules not available")

def run_single_test(test_case, test_name, verbose=False):
    """Run a single test with timeout protection"""
    print(f"Running test: {test_name}")

    # Create a test suite with just this test
    suite = unittest.TestSuite()
    suite.addTest(test_case(test_name))

    # Run the test with timeout protection
    result = None

    def run_test():
        nonlocal result
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
        result = runner.run(suite)

    # Start the test in a separate thread
    test_thread = threading.Thread(target=run_test)
    test_thread.daemon = True
    test_thread.start()

    # Wait for the test to complete with timeout
    timeout = 30  # 30 seconds timeout per test
    test_thread.join(timeout)

    # If the test is still running after timeout
    if test_thread.is_alive():
        print(f"ERROR: Test {test_name} timed out after {timeout} seconds")

        # Force kill any pandoc processes that might be hanging
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'pandoc' in proc.info['name'].lower() or 'xelatex' in proc.info['name'].lower():
                    print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    return result.wasSuccessful() if result else False

def run_unit_tests(test_type=None, verbose=False):
    """Run unit tests with improved error handling and timeouts"""
    if not UNIT_TESTING_AVAILABLE:
        print("Unit testing is not available.")
        return False

    # Get all test methods from the test cases
    export_tests = []
    settings_tests = []

    # Collect export tests
    for method_name in dir(ExportTestCase):
        if method_name.startswith('test_'):
            export_tests.append(method_name)

    # Collect settings tests
    for method_name in dir(SettingsTestCase):
        if method_name.startswith('test_'):
            settings_tests.append(method_name)

    # Determine which tests to run
    tests_to_run = []
    if test_type == "export":
        for test_name in export_tests:
            tests_to_run.append((ExportTestCase, test_name))
    elif test_type == "settings":
        for test_name in settings_tests:
            tests_to_run.append((SettingsTestCase, test_name))
    else:
        # Run all tests
        for test_name in export_tests:
            tests_to_run.append((ExportTestCase, test_name))
        for test_name in settings_tests:
            tests_to_run.append((SettingsTestCase, test_name))

    # Run each test individually with timeout protection
    all_passed = True
    for test_case, test_name in tests_to_run:
        try:
            test_passed = run_single_test(test_case, test_name, verbose)
            all_passed = all_passed and test_passed
        except Exception as e:
            print(f"ERROR: Exception running test {test_name}: {str(e)}")
            traceback.print_exc()
            all_passed = False

    return all_passed

def run_single_visual_test(test_func, test_name, create_reference=False):
    """Run a single visual test with timeout protection"""
    print(f"Running visual test: {test_name}")

    # Run the test with timeout protection
    result = True

    def run_test():
        nonlocal result
        try:
            if create_reference:
                # Set create_reference flag if available
                if hasattr(visual_test_runner, 'CREATE_REFERENCE'):
                    visual_test_runner.CREATE_REFERENCE = True

            # Call the test function
            test_func()
        except Exception as e:
            print(f"ERROR: Visual test {test_name} failed: {str(e)}")
            traceback.print_exc()
            result = False

    # Start the test in a separate thread
    test_thread = threading.Thread(target=run_test)
    test_thread.daemon = True
    test_thread.start()

    # Wait for the test to complete with timeout
    timeout = 60  # 60 seconds timeout per visual test
    test_thread.join(timeout)

    # If the test is still running after timeout
    if test_thread.is_alive():
        print(f"ERROR: Visual test {test_name} timed out after {timeout} seconds")

        # Force kill any processes that might be hanging
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'python' in proc.info['name'].lower() or 'pandoc' in proc.info['name'].lower():
                    if proc.pid != os.getpid():  # Don't kill ourselves
                        print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    return result

def run_visual_tests(test_name=None, create_reference=False):
    """Run visual tests with improved error handling and timeouts"""
    if not VISUAL_TESTING_AVAILABLE:
        print("Visual testing is not available.")
        return False

    # Create QApplication if it doesn't exist
    app = QApplication.instance() or QApplication(sys.argv)

    # Define test functions
    test_functions = {
        "basic_ui": visual_test_runner.test_basic_ui,
        "heading_numbering": visual_test_runner.test_heading_numbering,
        "page_breaks": visual_test_runner.test_page_breaks,
        "edit_toolbar": visual_test_runner.test_edit_toolbar
    }

    # Determine which tests to run
    if test_name and test_name in test_functions:
        tests_to_run = [(test_name, test_functions[test_name])]
    else:
        # Run all tests
        tests_to_run = [(name, func) for name, func in test_functions.items()]

    # Run each test individually with timeout protection
    all_passed = True
    for name, func in tests_to_run:
        try:
            test_passed = run_single_visual_test(func, name, create_reference)
            all_passed = all_passed and test_passed
        except Exception as e:
            print(f"ERROR: Exception running visual test {name}: {str(e)}")
            traceback.print_exc()
            all_passed = False

    return all_passed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for Markdown to PDF Converter")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--visual", action="store_true", help="Run visual tests")
    parser.add_argument("--export", action="store_true", help="Run export tests")
    parser.add_argument("--settings", action="store_true", help="Run settings tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-reference", action="store_true", help="Create reference screenshots for visual tests")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds for each test (default: 30)")
    parser.add_argument("--test", type=str, help="Run a specific test by name")

    args = parser.parse_args()

    # Default to running all tests if no specific tests are specified
    if not (args.unit or args.visual or args.export or args.settings or args.all):
        args.all = True

    # Set up signal handler for graceful termination
    def signal_handler(sig, frame):
        print("\nTest runner interrupted. Cleaning up...")
        # Kill any pandoc or LaTeX processes that might be running
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if ('pandoc' in proc.info['name'].lower() or
                    'xelatex' in proc.info['name'].lower() or
                    'pdflatex' in proc.info['name'].lower() or
                    'lualatex' in proc.info['name'].lower()):
                    print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        sys.exit(1)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGBREAK'):  # Windows
        signal.signal(signal.SIGBREAK, signal_handler)
    else:  # Unix
        signal.signal(signal.SIGTERM, signal_handler)

    success = True

    try:
        # Run unit tests
        if args.unit or args.export or args.settings or args.all:
            print("Running unit tests...")
            if args.test:
                # Run a specific test
                test_found = False
                for test_case in [ExportTestCase, SettingsTestCase]:
                    for method_name in dir(test_case):
                        if method_name == args.test or method_name == f"test_{args.test}":
                            print(f"Running specific test: {method_name}")
                            success = run_single_test(test_case, method_name, args.verbose) and success
                            test_found = True
                            break
                    if test_found:
                        break
                if not test_found:
                    print(f"ERROR: Test '{args.test}' not found")
                    success = False
            elif args.export:
                success = run_unit_tests("export", args.verbose) and success
            elif args.settings:
                success = run_unit_tests("settings", args.verbose) and success
            else:
                success = run_unit_tests(None, args.verbose) and success

        # Run visual tests
        if args.visual or args.all:
            print("Running visual tests...")
            if args.test:
                success = run_visual_tests(args.test, args.create_reference) and success
            else:
                success = run_visual_tests(None, args.create_reference) and success

    except KeyboardInterrupt:
        print("\nTest runner interrupted. Cleaning up...")
        # Kill any pandoc or LaTeX processes that might be running
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if ('pandoc' in proc.info['name'].lower() or
                    'xelatex' in proc.info['name'].lower() or
                    'pdflatex' in proc.info['name'].lower() or
                    'lualatex' in proc.info['name'].lower()):
                    print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected exception in test runner: {str(e)}")
        traceback.print_exc()
        return 1

    if success:
        print("\nAll tests completed successfully!")
    else:
        print("\nSome tests failed. See above for details.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
