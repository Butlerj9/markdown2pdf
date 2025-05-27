#!/usr/bin/env python3
"""
Fix JavaScript Syntax
------------------
This script fixes JavaScript syntax errors in page_preview.py.
"""

import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_js_syntax(file_path):
    """Fix JavaScript syntax errors in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove "// No return statement needed here" comments
    content = content.replace('// No return statement needed here', '')
    
    # Fix 2: Fix "Illegal return statement" errors
    content = re.sub(r'return;(\s*\})', r'\1', content)
    
    # Fix 3: Add null checks to prevent "Cannot read properties of null" errors
    content = content.replace('var pages = document.querySelectorAll(\'.page\');',
                             'var pages = document.querySelectorAll(\'.page\');')
    
    content = content.replace('if (pages.length > 0) {',
                             'if (pages && pages.length > 0) {')
    
    content = content.replace('pages[i].style.transform',
                             'if (pages[i] && pages[i].style) { pages[i].style.transform')
    
    content = content.replace('pages[i].style.display = \'block\';',
                             'pages[i].style.display = \'block\'; }')
    
    # Fix 4: Add try-catch blocks around JavaScript code that might fail
    content = content.replace('function ensurePageVisible() {',
                             'function ensurePageVisible() { try {')
    
    content = content.replace('// Run immediately\nensurePageVisible();',
                             '// Run immediately\ntry {\n    ensurePageVisible();\n} catch (e) {\n    console.error("Error in initial ensurePageVisible call:", e);\n}')
    
    content = content.replace('// Run again after a delay\nsetTimeout(function() {\n    ensurePageVisible();\n}, 1000);',
                             '// Run again after a delay\nsetTimeout(function() {\n    try {\n        ensurePageVisible();\n    } catch (e) {\n        console.error("Error in delayed ensurePageVisible call:", e);\n    }\n}, 1000);')
    
    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Fixed JavaScript syntax errors in {file_path}")
    return True

def main():
    """Main function"""
    logger.info("Starting JavaScript syntax fix")
    
    # Check if page_preview.py exists
    if not os.path.exists('page_preview.py'):
        logger.error("page_preview.py not found")
        return 1
    
    # Fix JavaScript syntax errors
    if fix_js_syntax('page_preview.py'):
        logger.info("Successfully fixed JavaScript syntax errors")
        return 0
    else:
        logger.error("Failed to fix JavaScript syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
