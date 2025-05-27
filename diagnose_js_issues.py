#!/usr/bin/env python3
"""
Diagnose JavaScript Issues in Markdown to PDF Converter
------------------------------------------------------
This script uses the UI testing framework to diagnose JavaScript issues
in the Markdown to PDF Converter application.
"""

import os
import sys
import json
import time
import logging
import subprocess
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("diagnose_js_issues.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiagnoseJSIssues")

# Constants
CONFIG_FILE = "ui_test_config.json"
RESULTS_FILE = "ui_test_results.json"
LOG_DIR = "ui_test_logs"
SCREENSHOTS_DIR = "ui_test_screenshots"
JS_ERROR_PATTERN = re.compile(r"JavaScript Error: (.+)")
SYNTAX_ERROR_PATTERN = re.compile(r"SyntaxError: (.+)")

def create_diagnostic_config():
    """Create a diagnostic configuration file"""
    config = {
        "launch_command": "python markdown_to_pdf_converter.py",
        "run_tests": True,
        "test_sequence": [
            {
                "type": "launch",
                "description": "Launch the application",
                "command": "python markdown_to_pdf_converter.py"
            },
            {
                "type": "wait",
                "description": "Wait for application to initialize",
                "seconds": 5
            },
            {
                "type": "screenshot",
                "description": "Capture initial state",
                "name": "initial_state"
            },
            {
                "type": "click",
                "description": "Click on editor area",
                "x": 300,
                "y": 200
            },
            {
                "type": "type",
                "description": "Type test markdown content",
                "text": "# Test Heading\n\nThis is a test paragraph.\n\n## Second Level Heading\n\n- List item 1\n- List item 2\n\n### Third Level Heading\n\n1. Numbered item 1\n2. Numbered item 2\n\n```python\nprint('Hello, world!')\n```"
            },
            {
                "type": "wait",
                "description": "Wait for preview to update",
                "seconds": 3
            },
            {
                "type": "screenshot",
                "description": "Capture preview with content",
                "name": "preview_with_content"
            },
            {
                "type": "click",
                "description": "Click zoom in button",
                "x": 650,
                "y": 100
            },
            {
                "type": "wait",
                "description": "Wait for zoom to apply",
                "seconds": 2
            },
            {
                "type": "screenshot",
                "description": "Capture after zoom in",
                "name": "after_zoom_in"
            },
            {
                "type": "click",
                "description": "Click zoom out button",
                "x": 550,
                "y": 100
            },
            {
                "type": "wait",
                "description": "Wait for zoom to apply",
                "seconds": 2
            },
            {
                "type": "screenshot",
                "description": "Capture after zoom out",
                "name": "after_zoom_out"
            },
            {
                "type": "wait",
                "description": "Wait for final state",
                "seconds": 5
            },
            {
                "type": "screenshot",
                "description": "Capture final state",
                "name": "final_state"
            }
        ]
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created diagnostic configuration file: {CONFIG_FILE}")

def run_ui_tests():
    """Run the UI tests using the framework"""
    try:
        logger.info("Running UI tests...")
        result = subprocess.run(
            ["python", "ui_test_framework.py"],
            capture_output=True,
            text=True
        )
        
        logger.info(f"UI tests completed with return code: {result.returncode}")
        logger.info(f"Output: {result.stdout}")
        
        if result.stderr:
            logger.error(f"Error output: {result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error running UI tests: {str(e)}")
        return False

def analyze_logs():
    """Analyze the log files for JavaScript errors"""
    js_errors = []
    
    # Find the most recent log files
    stdout_logs = sorted(
        [f for f in os.listdir(LOG_DIR) if f.startswith("app_stdout_")],
        reverse=True
    )
    
    if not stdout_logs:
        logger.warning("No log files found")
        return js_errors
    
    # Read the most recent log file
    log_file = os.path.join(LOG_DIR, stdout_logs[0])
    logger.info(f"Analyzing log file: {log_file}")
    
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Find JavaScript errors
        for line in log_content.splitlines():
            js_error_match = JS_ERROR_PATTERN.search(line)
            if js_error_match:
                error_message = js_error_match.group(1)
                js_errors.append(error_message)
                logger.info(f"Found JavaScript error: {error_message}")
            
            syntax_error_match = SYNTAX_ERROR_PATTERN.search(line)
            if syntax_error_match:
                error_message = syntax_error_match.group(1)
                js_errors.append(f"Syntax error: {error_message}")
                logger.info(f"Found JavaScript syntax error: {error_message}")
    
    except Exception as e:
        logger.error(f"Error analyzing log file: {str(e)}")
    
    return js_errors

def create_report(js_errors):
    """Create a diagnostic report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "js_errors": js_errors,
        "screenshots": [
            f for f in os.listdir(SCREENSHOTS_DIR)
            if os.path.isfile(os.path.join(SCREENSHOTS_DIR, f))
        ],
        "recommendations": []
    }
    
    # Add recommendations based on errors
    for error in js_errors:
        if "SyntaxError" in error:
            if "template literal" in error.lower() or "unexpected token" in error.lower():
                report["recommendations"].append(
                    "Replace template literals (backticks) with standard string concatenation"
                )
            elif "unexpected token" in error.lower():
                report["recommendations"].append(
                    "Check for syntax errors in JavaScript code (missing brackets, commas, etc.)"
                )
        elif "undefined" in error.lower():
            report["recommendations"].append(
                "Check for undefined variables or functions in JavaScript code"
            )
    
    # Add general recommendations
    if not report["recommendations"]:
        report["recommendations"].append(
            "Simplify the JavaScript code to use more basic features"
        )
        report["recommendations"].append(
            "Replace complex DOM manipulation with simpler approaches"
        )
    
    # Save the report
    report_file = f"js_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Created diagnostic report: {report_file}")
    return report_file

def main():
    """Main function"""
    logger.info("Starting JavaScript issue diagnosis")
    
    # Create diagnostic configuration
    create_diagnostic_config()
    
    # Run UI tests
    success = run_ui_tests()
    
    # Analyze logs for JavaScript errors
    js_errors = analyze_logs()
    
    if js_errors:
        logger.info(f"Found {len(js_errors)} JavaScript errors")
        
        # Create diagnostic report
        report_file = create_report(js_errors)
        
        print("\n=== JavaScript Issue Diagnosis ===")
        print(f"Found {len(js_errors)} JavaScript errors:")
        for i, error in enumerate(js_errors, 1):
            print(f"{i}. {error}")
        
        print("\nRecommendations:")
        with open(report_file, 'r') as f:
            report = json.load(f)
            for i, recommendation in enumerate(report["recommendations"], 1):
                print(f"{i}. {recommendation}")
        
        print(f"\nDetailed report saved to: {report_file}")
        print(f"Screenshots saved to: {SCREENSHOTS_DIR}")
        print(f"Log files saved to: {LOG_DIR}")
    else:
        logger.info("No JavaScript errors found")
        print("\n=== JavaScript Issue Diagnosis ===")
        print("No JavaScript errors found in the logs.")
        print("This could mean either:")
        print("1. There are no JavaScript errors")
        print("2. The errors are not being logged properly")
        print("\nCheck the screenshots in the screenshots directory for visual issues.")
    
    return 0 if success and not js_errors else 1

if __name__ == "__main__":
    sys.exit(main())
