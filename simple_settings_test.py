#!/usr/bin/env python3
"""
Simple Settings Test
------------------
This script tests that settings are not saved multiple times.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("Starting simple settings test")
    
    # Check if mdz_integration.py contains any save_settings calls
    with open('mdz_integration.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count the number of save_settings calls
    save_settings_calls = content.count('self.main_window.save_settings()')
    
    # Count the number of commented save_settings calls
    commented_calls = content.count('# Don\'t call save_settings here')
    
    logger.info(f"Found {save_settings_calls} save_settings calls in mdz_integration.py")
    logger.info(f"Found {commented_calls} commented save_settings calls in mdz_integration.py")
    
    # Check if all save_settings calls are commented out
    if save_settings_calls == 0:
        logger.info("All save_settings calls are commented out - GOOD!")
        return 0
    else:
        logger.error("Some save_settings calls are still active - BAD!")
        
        # Find the lines with save_settings calls
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if 'self.main_window.save_settings()' in line and '# Don\'t call save_settings here' not in line:
                logger.error(f"Line {i+1}: {line}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
