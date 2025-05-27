#!/usr/bin/env python3
"""
Check for duplicate save_settings calls in mdz_integration.py
-----------------------------------------------------------
This script checks for duplicate save_settings calls in mdz_integration.py.
"""

import os
import re
import sys

def check_file(file_path):
    """Check a file for save_settings calls"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all occurrences of save_settings
    save_settings_calls = re.findall(r'self\.main_window\.save_settings\(\)', content)
    
    print(f"Found {len(save_settings_calls)} save_settings calls in {file_path}")
    
    # Find all methods that call save_settings
    methods = re.findall(r'def ([^\(]+)\([^)]*\):[^}]*self\.main_window\.save_settings\(\)', content, re.DOTALL)
    
    print(f"Methods that call save_settings:")
    for method in methods:
        print(f"  - {method}")
    
    return len(save_settings_calls)

def main():
    """Main function"""
    mdz_integration_path = 'mdz_integration.py'
    
    if not os.path.exists(mdz_integration_path):
        print(f"Error: {mdz_integration_path} not found")
        return 1
    
    num_calls = check_file(mdz_integration_path)
    
    if num_calls > 0:
        print(f"\nFound {num_calls} save_settings calls in {mdz_integration_path}")
        print("These should be removed to prevent duplicate settings saving.")
        return 1
    else:
        print(f"\nNo save_settings calls found in {mdz_integration_path}")
        print("Good job! No duplicate settings saving detected.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
