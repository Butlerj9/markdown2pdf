#!/usr/bin/env python3
"""
Simple test script to run the main application
"""

import sys
import os
import time

def run_main():
    """Run the main application with a timeout"""
    print("Starting main application test...")
    
    # Import the main module
    import main
    
    # Set a timeout to automatically exit after 5 seconds
    def exit_after_timeout():
        time.sleep(5)
        print("Test timeout reached, exiting...")
        os._exit(0)
    
    # Start the timeout thread
    import threading
    timeout_thread = threading.Thread(target=exit_after_timeout)
    timeout_thread.daemon = True
    timeout_thread.start()
    
    # Run the main function
    try:
        main.main()
    except Exception as e:
        print(f"Error running main application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(run_main())
