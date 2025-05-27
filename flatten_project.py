#!/usr/bin/env python3
"""
Project Flattening Script
-------------------------
File: src--flatten_project.py

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
import time
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
    """
    Check if a path should be excluded from flattening.
    
    Args:
        path (str): Path to check for exclusion
        
    Returns:
        bool: True if the path should be excluded, False otherwise
    """
    # Check if any part of the path is in the excluded directories
    parts = Path(path).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    
    # Check file extension
    if Path(path).suffix.lower() in EXCLUDE_EXTENSIONS:
        return True
    
    # Exclude the target directory itself to avoid infinite recursion
    if os.path.abspath(path) == os.path.abspath(target_dir):
        return True
        
    return False


def flatten_directory(source_dir, target_dir, prefix="", dry_run=False):
    """
    Recursively flatten a directory structure.
    
    Args:
        source_dir (str): Source directory to flatten
        target_dir (str): Target directory for flattened files
        prefix (str): Current path prefix (used in recursion)
        dry_run (bool): If True, don't copy files, just print what would be done
        
    Returns:
        tuple: (files_processed, files_skipped)
    """
    files_processed = 0
    files_skipped = 0
    
    # Create target directory if it doesn't exist and not in dry run mode
    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)
    
    try:
        # Get all items in the source directory
        items = os.listdir(source_dir)
        
        for item in items:
            source_path = os.path.join(source_dir, item)
            
            # Skip excluded items
            if is_excluded(source_path):
                print(f"Skipping excluded item: {source_path}")
                files_skipped += 1
                continue
            
            # Define the new prefix
            new_prefix = f"{prefix}--{item}" if prefix else item
            
            if os.path.isdir(source_path):
                # Recursively process subdirectories
                sub_processed, sub_skipped = flatten_directory(source_path, target_dir, new_prefix, dry_run)
                files_processed += sub_processed
                files_skipped += sub_skipped
            else:
                # Copy the file to the target directory with the new name
                target_path = os.path.join(target_dir, new_prefix)
                
                if dry_run:
                    print(f"Would copy: {source_path} -> {target_path}")
                else:
                    # Check if the target file already exists
                    if os.path.exists(target_path):
                        # Handle file collision by adding a timestamp
                        file_name, file_ext = os.path.splitext(new_prefix)
                        timestamp = int(time.time())
                        new_name = f"{file_name}_{timestamp}{file_ext}"
                        target_path = os.path.join(target_dir, new_name)
                        print(f"File collision detected. Renaming to {new_name}")
                    
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"Copied: {source_path} -> {target_path}")
                        files_processed += 1
                    except Exception as e:
                        print(f"Error copying {source_path}: {str(e)}")
                        files_skipped += 1
    
    except Exception as e:
        print(f"Error processing directory {source_dir}: {str(e)}")
    
    return files_processed, files_skipped


def main():
    """
    Main function to parse arguments and initiate directory flattening.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description='Flatten a directory structure with double-dash notation.')
    parser.add_argument('source_dir', nargs='?', default=os.getcwd(), 
                        help='Source directory to flatten (default: current directory)')
    parser.add_argument('target_dir', nargs='?', default=os.path.join(os.getcwd(), 'flattened'),
                        help='Target directory for flattened files (default: ./flattened)')
    parser.add_argument('--clear', action='store_true', 
                        help='Clear the target directory before flattening')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without copying files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Convert to absolute paths
    source_dir = os.path.abspath(args.source_dir)
    global target_dir  # Make target_dir accessible to the is_excluded function
    target_dir = os.path.abspath(args.target_dir)
    
    # Ensure source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return 1
    
    # Prevent source being inside target and vice versa to avoid loops
    if os.path.commonpath([source_dir]) == os.path.commonpath([source_dir, target_dir]):
        print(f"Error: Target directory '{target_dir}' is inside source directory. This would create an infinite loop.")
        return 1
        
    if os.path.commonpath([target_dir]) == os.path.commonpath([source_dir, target_dir]):
        print(f"Error: Source directory '{source_dir}' is inside target directory. This could lead to unexpected results.")
        return 1
    
    # Clear target directory if requested and not in dry run mode
    if args.clear and os.path.exists(target_dir) and not args.dry_run:
        print(f"Clearing target directory: {target_dir}")
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"Error clearing target directory: {str(e)}")
            return 1
    
    # Create target directory if it doesn't exist and not in dry run mode
    if not args.dry_run:
        try:
            os.makedirs(target_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating target directory: {str(e)}")
            return 1
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Flattening directory structure:")
    print(f"  Source: {source_dir}")
    print(f"  Target: {target_dir}")
    
    start_time = time.time()
    
    # Flatten the directory structure
    files_processed, files_skipped = flatten_directory(
        source_dir, target_dir, dry_run=args.dry_run
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\nFlattening {'simulation' if args.dry_run else 'operation'} complete!")
    print(f"  Files processed: {files_processed}")
    print(f"  Files skipped: {files_skipped}")
    print(f"  Time elapsed: {elapsed_time:.2f} seconds")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())