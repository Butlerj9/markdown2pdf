#!/usr/bin/env python3
"""
UI Test Framework for Markdown to PDF Converter
----------------------------------------------
This script provides automated UI testing capabilities including:
- Application launching
- Screenshot capture
- Mouse event simulation
- Log file monitoring
- Results reporting

Usage:
1. Create a test_config.json file with test parameters
2. Run this script to execute the tests
3. Check test_results.json for results and screenshots directory for captures
"""

import os
import sys
import json
import time
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path
import pyautogui
import keyboard
import threading
import glob
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ui_test_framework.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UITestFramework")

# Constants
CONFIG_FILE = "ui_test_config.json"
RESULTS_FILE = "ui_test_results.json"
SCREENSHOTS_DIR = "ui_test_screenshots"
LOG_DIR = "ui_test_logs"
DEFAULT_TIMEOUT = 120  # seconds
POLL_INTERVAL = 0.5  # seconds
CONFIG_POLL_INTERVAL = 2.0  # seconds

class UITestFramework:
    """Automated UI testing framework for the Markdown to PDF Converter"""
    
    def __init__(self):
        """Initialize the test framework"""
        self.config = {}
        self.results = {
            "status": "initialized",
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "screenshots": [],
            "logs": [],
            "errors": []
        }
        self.process = None
        self.log_watcher = None
        self.setup_directories()
    
    def setup_directories(self):
        """Set up necessary directories"""
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)
            logger.info(f"Created screenshots directory: {SCREENSHOTS_DIR}")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
            logger.info(f"Created logs directory: {LOG_DIR}")
    
    def load_config(self):
        """Load the test configuration from JSON file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_FILE}")
                return True
            else:
                logger.warning(f"Configuration file {CONFIG_FILE} not found")
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.results["errors"].append(f"Config load error: {str(e)}")
            return False
    
    def save_results(self):
        """Save test results to JSON file"""
        try:
            self.results["timestamp"] = datetime.now().isoformat()
            with open(RESULTS_FILE, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Saved results to {RESULTS_FILE}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def take_screenshot(self, name):
        """Take a screenshot and save it to the screenshots directory"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{SCREENSHOTS_DIR}/{name}_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            logger.info(f"Saved screenshot: {filename}")
            self.results["screenshots"].append(filename)
            return filename
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            self.results["errors"].append(f"Screenshot error: {str(e)}")
            return None
    
    def click_at_position(self, x, y, button="left"):
        """Click at the specified position"""
        try:
            pyautogui.click(x, y, button=button)
            logger.info(f"Clicked at position ({x}, {y}) with {button} button")
            return True
        except Exception as e:
            logger.error(f"Error clicking at position ({x}, {y}): {str(e)}")
            self.results["errors"].append(f"Click error at ({x}, {y}): {str(e)}")
            return False
    
    def type_text(self, text):
        """Type the specified text"""
        try:
            pyautogui.typewrite(text)
            logger.info(f"Typed text: {text}")
            return True
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
            self.results["errors"].append(f"Type error: {str(e)}")
            return False
    
    def press_key(self, key):
        """Press the specified key"""
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error pressing key {key}: {str(e)}")
            self.results["errors"].append(f"Key press error ({key}): {str(e)}")
            return False
    
    def launch_application(self, command=None):
        """Launch the application with the specified command"""
        if command is None and "launch_command" in self.config:
            command = self.config["launch_command"]
        
        if not command:
            logger.error("No launch command specified")
            self.results["errors"].append("No launch command specified")
            return False
        
        try:
            logger.info(f"Launching application: {command}")
            
            # Create a log file for the application output
            log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stdout_log = os.path.join(LOG_DIR, f"app_stdout_{log_timestamp}.log")
            stderr_log = os.path.join(LOG_DIR, f"app_stderr_{log_timestamp}.log")
            
            # Open log files
            stdout_file = open(stdout_log, 'w')
            stderr_file = open(stderr_log, 'w')
            
            # Launch the process
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Start log watcher thread
            self.log_watcher = threading.Thread(
                target=self._watch_logs,
                args=(self.process.stdout, self.process.stderr, stdout_file, stderr_file)
            )
            self.log_watcher.daemon = True
            self.log_watcher.start()
            
            # Wait for application to start
            time.sleep(2)
            
            # Take a screenshot after launch
            self.take_screenshot("app_launch")
            
            # Add log files to results
            self.results["logs"].append({
                "stdout": stdout_log,
                "stderr": stderr_log
            })
            
            return True
        except Exception as e:
            logger.error(f"Error launching application: {str(e)}")
            self.results["errors"].append(f"Launch error: {str(e)}")
            return False
    
    def _watch_logs(self, stdout, stderr, stdout_file, stderr_file):
        """Watch and log application output"""
        try:
            while True:
                # Read stdout
                stdout_line = stdout.readline()
                if stdout_line:
                    logger.info(f"APP STDOUT: {stdout_line.strip()}")
                    stdout_file.write(stdout_line)
                    stdout_file.flush()
                
                # Read stderr
                stderr_line = stderr.readline()
                if stderr_line:
                    logger.warning(f"APP STDERR: {stderr_line.strip()}")
                    stderr_file.write(stderr_line)
                    stderr_file.flush()
                
                # Check if process has ended
                if not stdout_line and not stderr_line and self.process.poll() is not None:
                    break
                
                # Small delay to prevent high CPU usage
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in log watcher: {str(e)}")
        finally:
            # Close log files
            stdout_file.close()
            stderr_file.close()
    
    def wait_for_window(self, title, timeout=DEFAULT_TIMEOUT):
        """Wait for a window with the specified title to appear"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                windows = pyautogui.getWindowsWithTitle(title)
                if windows:
                    logger.info(f"Found window with title: {title}")
                    return windows[0]
            except Exception as e:
                logger.error(f"Error finding window: {str(e)}")
            
            time.sleep(POLL_INTERVAL)
        
        logger.warning(f"Timeout waiting for window with title: {title}")
        self.results["errors"].append(f"Window wait timeout: {title}")
        return None
    
    def find_image_on_screen(self, image_path, confidence=0.8, timeout=DEFAULT_TIMEOUT):
        """Find an image on the screen and return its position"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
                if location:
                    logger.info(f"Found image {image_path} at {location}")
                    return location
            except Exception as e:
                logger.error(f"Error finding image: {str(e)}")
            
            time.sleep(POLL_INTERVAL)
        
        logger.warning(f"Timeout waiting for image: {image_path}")
        self.results["errors"].append(f"Image find timeout: {image_path}")
        return None
    
    def click_image_on_screen(self, image_path, confidence=0.8, timeout=DEFAULT_TIMEOUT):
        """Find an image on the screen and click it"""
        location = self.find_image_on_screen(image_path, confidence, timeout)
        if location:
            x, y = pyautogui.center(location)
            return self.click_at_position(x, y)
        return False
    
    def run_test_sequence(self):
        """Run the test sequence defined in the configuration"""
        if not self.config:
            logger.error("No configuration loaded")
            return False
        
        if "test_sequence" not in self.config:
            logger.error("No test sequence defined in configuration")
            return False
        
        sequence = self.config["test_sequence"]
        total_tests = len(sequence)
        self.results["tests_run"] = total_tests
        
        for i, step in enumerate(sequence):
            logger.info(f"Running test step {i+1}/{total_tests}: {step.get('description', 'Unnamed step')}")
            
            try:
                step_type = step.get("type")
                
                if step_type == "launch":
                    success = self.launch_application(step.get("command"))
                
                elif step_type == "screenshot":
                    success = self.take_screenshot(step.get("name", f"step_{i+1}")) is not None
                
                elif step_type == "click":
                    success = self.click_at_position(step["x"], step["y"], step.get("button", "left"))
                
                elif step_type == "click_image":
                    success = self.click_image_on_screen(
                        step["image_path"],
                        step.get("confidence", 0.8),
                        step.get("timeout", DEFAULT_TIMEOUT)
                    )
                
                elif step_type == "type":
                    success = self.type_text(step["text"])
                
                elif step_type == "key":
                    success = self.press_key(step["key"])
                
                elif step_type == "wait":
                    time.sleep(step.get("seconds", 1))
                    success = True
                
                elif step_type == "wait_for_window":
                    success = self.wait_for_window(step["title"], step.get("timeout", DEFAULT_TIMEOUT)) is not None
                
                elif step_type == "wait_for_image":
                    success = self.find_image_on_screen(
                        step["image_path"],
                        step.get("confidence", 0.8),
                        step.get("timeout", DEFAULT_TIMEOUT)
                    ) is not None
                
                else:
                    logger.warning(f"Unknown step type: {step_type}")
                    success = False
                
                if success:
                    logger.info(f"Step {i+1} succeeded")
                    self.results["tests_passed"] += 1
                else:
                    logger.error(f"Step {i+1} failed")
                    self.results["tests_failed"] += 1
                    
                    # Take a screenshot on failure
                    self.take_screenshot(f"failure_step_{i+1}")
                    
                    # Stop on failure if configured
                    if step.get("stop_on_failure", False):
                        logger.warning("Stopping test sequence due to failure")
                        break
                
            except Exception as e:
                logger.error(f"Error in test step {i+1}: {str(e)}")
                logger.error(traceback.format_exc())
                self.results["errors"].append(f"Step {i+1} error: {str(e)}")
                self.results["tests_failed"] += 1
                
                # Take a screenshot on error
                self.take_screenshot(f"error_step_{i+1}")
                
                # Stop on error if configured
                if step.get("stop_on_error", True):
                    logger.warning("Stopping test sequence due to error")
                    break
        
        self.results["status"] = "completed"
        return self.results["tests_failed"] == 0
    
    def terminate_application(self):
        """Terminate the application process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("Application terminated")
                return True
            except Exception as e:
                logger.error(f"Error terminating application: {str(e)}")
                try:
                    self.process.kill()
                    logger.info("Application killed")
                except Exception as e2:
                    logger.error(f"Error killing application: {str(e2)}")
                return False
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.terminate_application()
        self.save_results()
        logger.info("Cleanup completed")

def create_default_config():
    """Create a default configuration file if none exists"""
    if os.path.exists(CONFIG_FILE):
        return
    
    default_config = {
        "launch_command": "python markdown_to_pdf_converter.py",
        "test_sequence": [
            {
                "type": "launch",
                "description": "Launch the application",
                "command": "python markdown_to_pdf_converter.py"
            },
            {
                "type": "wait",
                "description": "Wait for application to initialize",
                "seconds": 3
            },
            {
                "type": "screenshot",
                "description": "Capture main window",
                "name": "main_window"
            },
            {
                "type": "click",
                "description": "Click File menu",
                "x": 30,
                "y": 30
            },
            {
                "type": "wait",
                "description": "Wait for menu to appear",
                "seconds": 1
            },
            {
                "type": "screenshot",
                "description": "Capture File menu",
                "name": "file_menu"
            }
        ]
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    logger.info(f"Created default configuration file: {CONFIG_FILE}")

def monitor_config_file():
    """Monitor the configuration file for changes and run tests when requested"""
    framework = UITestFramework()
    
    logger.info(f"Monitoring {CONFIG_FILE} for changes...")
    
    last_modified = 0
    if os.path.exists(CONFIG_FILE):
        last_modified = os.path.getmtime(CONFIG_FILE)
    
    while True:
        try:
            # Check if config file exists
            if not os.path.exists(CONFIG_FILE):
                create_default_config()
                last_modified = os.path.getmtime(CONFIG_FILE)
            
            # Check if config file has been modified
            current_modified = os.path.getmtime(CONFIG_FILE)
            if current_modified > last_modified:
                logger.info(f"Configuration file {CONFIG_FILE} has been modified")
                last_modified = current_modified
                
                # Load the configuration
                if framework.load_config():
                    # Check if tests should be run
                    if framework.config.get("run_tests", False):
                        logger.info("Running tests as requested in configuration")
                        
                        # Run the tests
                        framework.run_test_sequence()
                        
                        # Reset the run_tests flag
                        framework.config["run_tests"] = False
                        with open(CONFIG_FILE, 'w') as f:
                            json.dump(framework.config, f, indent=2)
                        
                        # Clean up
                        framework.cleanup()
                        
                        # Create a new framework instance for the next run
                        framework = UITestFramework()
            
            # Sleep for a while
            time.sleep(CONFIG_POLL_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
            break
        
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
            logger.error(traceback.format_exc())
            time.sleep(CONFIG_POLL_INTERVAL)

def main():
    """Main function"""
    logger.info("Starting UI test framework")
    
    # Create default config if none exists
    create_default_config()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Run in monitoring mode
        monitor_config_file()
        return 0
    
    # Initialize test framework
    framework = UITestFramework()
    
    try:
        # Load configuration
        if not framework.load_config():
            logger.error("Failed to load configuration")
            return 1
        
        # Run test sequence
        success = framework.run_test_sequence()
        
        # Report results
        if success:
            logger.info("All tests passed successfully")
        else:
            logger.warning("Some tests failed")
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        # Clean up
        framework.cleanup()

if __name__ == "__main__":
    sys.exit(main())
