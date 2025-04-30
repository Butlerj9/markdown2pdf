#!/usr/bin/env python3
"""
Project Flattening Script
-------------------------
This script flattens a directory structure by copying files to a target directory
with directory structure encoded in the filenames using double-dash notation.

For example:
  src/utils/helper.py -> target/src--utils--helper.py

Usage:
  python flatten_project.py [source_dir] [target_dir]

If arguments are not provided, the script uses the current directory as source
and creates a 'flattened' directory as target.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Directories to exclude from flattening
EXCLUDE_DIRS = [
    '.git', 
    '.github',
    '__pycache__', 
    'venv', 
    'env',
    'node_modules',
    'build',
    'dist',
    'flattened',
    '.vscode',
    '.idea'
]

# File extensions to exclude
EXCLUDE_EXTENSIONS = [
    '.pyc',
    '.pyo',
    '.pyd',
    '.so',
    '.dll',
    '.exe',
    '.obj',
    '.o',
    '.a',
    '.lib',
    '.egg-info',
    '.DS_Store',
    '.class'
]


def is_excluded(path):
    """Check if a path should be excluded from flattening."""
    # Check if any part of the path is in the excluded directories
    parts = Path(path).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    
    # Check file extension
    if Path(path).suffix.lower() in EXCLUDE_EXTENSIONS:
        return True
        
    return False


def flatten_directory(source_dir, target_dir, prefix=""):
    """
    Recursively flatten a directory structure.
    
    Args:
        source_dir: Source directory to flatten
        target_dir: Target directory for flattened files
        prefix: Current path prefix (used in recursion)
    """
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Get all items in the source directory
    items = os.listdir(source_dir)
    
    for item in items:
        source_path = os.path.join(source_dir, item)
        
        # Skip excluded items
        if is_excluded(source_path):
            print(f"Skipping excluded item: {source_path}")
            continue
        
        # Define the new prefix
        new_prefix = f"{prefix}--{item}" if prefix else item
        
        if os.path.isdir(source_path):
            # Recursively process subdirectories
            flatten_directory(source_path, target_dir, new_prefix)
        else:
            # Copy the file to the target directory with the new name
            target_path = os.path.join(target_dir, new_prefix)
            shutil.copy2(source_path, target_path)
            print(f"Copied: {source_path} -> {target_path}")


def main():
    parser = argparse.ArgumentParser(description='Flatten a directory structure with double-dash notation.')
    parser.add_argument('source_dir', nargs='?', default=os.getcwd(), 
                        help='Source directory to flatten (default: current directory)')
    parser.add_argument('target_dir', nargs='?', default=os.path.join(os.getcwd(), 'flattened'),
                        help='Target directory for flattened files (default: ./flattened)')
    parser.add_argument('--clear', action='store_true', 
                        help='Clear the target directory before flattening')
    
    args = parser.parse_args()
    
    # Convert to absolute paths
    source_dir = os.path.abspath(args.source_dir)
    target_dir = os.path.abspath(args.target_dir)
    
    # Ensure source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return 1
    
    # Clear target directory if requested
    if args.clear and os.path.exists(target_dir):
        print(f"Clearing target directory: {target_dir}")
        shutil.rmtree(target_dir)
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"Flattening directory structure:")
    print(f"  Source: {source_dir}")
    print(f"  Target: {target_dir}")
    
    # Flatten the directory structure
    flatten_directory(source_dir, target_dir)
    
    print("Flattening complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())