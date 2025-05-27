#!/usr/bin/env python3
"""
Page Preview Test Enhancements
-----------------------------
Enhancements for the page preview test script to add timeout handling and dialog closing.
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QEventLoop

# Configure logging
log_filename = f"page_preview_test_enhancements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestTimeoutError(Exception):
    """Exception raised when a test times out"""
    pass

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    raise TestTimeoutError("Test timed out")

def close_dialogs():
    """Close any open dialogs"""
    app = QApplication.instance()
    if app:
        closed = False
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMessageBox) and widget.isVisible():
                logger.info(f"Closing dialog: {widget.windowTitle()}")
                widget.close()
                closed = True
        return closed
    return False

def setup_dialog_closer(interval=1000):
    """Set up a timer to close dialogs periodically"""
    app = QApplication.instance()
    if app:
        timer = QTimer()
        timer.timeout.connect(close_dialogs)
        timer.start(interval)
        return timer
    return None

def wait_with_timeout(timeout=30, interval=1000):
    """Wait for a specified time with timeout handling"""
    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        # Set up dialog closer
        timer = setup_dialog_closer(interval)
        
        # Wait for the specified time
        loop = QEventLoop()
        QTimer.singleShot(timeout * 1000, loop.quit)
        loop.exec()
        
        # Stop the timer
        if timer:
            timer.stop()
        
        # Reset the alarm
        signal.alarm(0)
    except TestTimeoutError:
        logger.error(f"Timeout after {timeout} seconds")
        # Close any open dialogs
        close_dialogs()
        # Reset the alarm
        signal.alarm(0)
        return False
    
    return True

def run_with_timeout(func, args=None, kwargs=None, timeout=30):
    """Run a function with timeout handling"""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    
    # Set up timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        # Set up dialog closer
        timer = setup_dialog_closer()
        
        # Run the function
        result = func(*args, **kwargs)
        
        # Stop the timer
        if timer:
            timer.stop()
        
        # Reset the alarm
        signal.alarm(0)
        
        return result
    except TestTimeoutError:
        logger.error(f"Function {func.__name__} timed out after {timeout} seconds")
        # Close any open dialogs
        close_dialogs()
        # Reset the alarm
        signal.alarm(0)
        return None

def patch_test_page_preview():
    """Patch the test_page_preview.py script to add timeout handling and dialog closing"""
    # Import the original script
    import test_page_preview
    
    # Patch the main function
    original_main = test_page_preview.main
    
    def patched_main():
        """Patched main function with timeout handling and dialog closing"""
        # Set up dialog closer
        timer = setup_dialog_closer()
        
        # Set up timeout handler for the entire script
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(120)  # 2 minute timeout for the entire script
        
        try:
            # Run the original main function
            return original_main()
        except TestTimeoutError:
            logger.error("Test timed out after 120 seconds")
            # Close any open dialogs
            close_dialogs()
            return 1
        finally:
            # Reset the alarm
            signal.alarm(0)
            
            # Stop the timer
            if timer:
                timer.stop()
    
    # Replace the original main function
    test_page_preview.main = patched_main
    
    return test_page_preview

def main():
    """Main function"""
    # Patch the test_page_preview.py script
    patched_module = patch_test_page_preview()
    
    # Run the patched script
    return patched_module.main()

if __name__ == "__main__":
    sys.exit(main())
