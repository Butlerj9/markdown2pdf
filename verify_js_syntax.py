#!/usr/bin/env python3
"""
Verify JavaScript Syntax
---------------------
Script to verify that the JavaScript syntax errors in page_preview.py have been fixed
"""

import sys
import re
from page_preview import PagePreview

def check_js_syntax():
    """Check JavaScript syntax in page_preview.py"""
    # Create an instance of PagePreview to access its methods
    preview = PagePreview()
    
    # Check for Python variable interpolation in JavaScript
    with open('page_preview.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for problematic patterns
    problems = []
    
    # Check for f-strings with JavaScript
    if 'page_layout_script = f"""' in content:
        problems.append("Found f-string for JavaScript: page_layout_script = f\"\"\"")
    
    # Check for Python variable interpolation in JavaScript
    if re.search(r'var zoomFactor = {self\.zoom_factor};', content):
        problems.append("Found Python variable interpolation: var zoomFactor = {self.zoom_factor};")
    
    if re.search(r'var pageWidthMM = {page_width};', content):
        problems.append("Found Python variable interpolation: var pageWidthMM = {page_width};")
    
    if re.search(r'var pageHeightMM = {page_height};', content):
        problems.append("Found Python variable interpolation: var pageHeightMM = {page_height};")
    
    if re.search(r'var marginTopMM = {margin_top};', content):
        problems.append("Found Python variable interpolation: var marginTopMM = {margin_top};")
    
    if re.search(r'var marginRightMM = {margin_right};', content):
        problems.append("Found Python variable interpolation: var marginRightMM = {margin_right};")
    
    if re.search(r'var marginBottomMM = {margin_bottom};', content):
        problems.append("Found Python variable interpolation: var marginBottomMM = {margin_bottom};")
    
    if re.search(r'var marginLeftMM = {margin_left};', content):
        problems.append("Found Python variable interpolation: var marginLeftMM = {margin_left};")
    
    # Report results
    if problems:
        print("Found JavaScript syntax issues:")
        for problem in problems:
            print(f"- {problem}")
        return False
    else:
        print("No JavaScript syntax issues found. Fixes appear to be working.")
        return True

if __name__ == "__main__":
    success = check_js_syntax()
    sys.exit(0 if success else 1)
