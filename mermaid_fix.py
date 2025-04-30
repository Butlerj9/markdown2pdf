#!/usr/bin/env python3
"""
Mermaid JS Downloader and Validator
----------------------------------
This script downloads a compatible version of mermaid.min.js from a CDN and validates
it to ensure it will work correctly in the Markdown to PDF Converter application.

Usage:
  python mermaid_fix.py [--force]

Options:
  --force    Force redownload even if a file already exists
"""

import os
import sys
import argparse
import tempfile
import hashlib
import urllib.request
import re

# Constants
CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"
EXPECTED_MD5 = "e1e7801bf530b891a33add8e1bd0d3b6"  # Known good hash for v9.4.3


def create_resources_dir():
    """Create resources directory if it doesn't exist."""
    # First determine the application directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(app_dir, "resources")
    
    # Create resources directory if it doesn't exist
    if not os.path.exists(resources_dir):
        try:
            os.makedirs(resources_dir)
            print(f"Created resources directory: {resources_dir}")
        except Exception as e:
            print(f"Error creating resources directory: {str(e)}")
            return None
            
    return resources_dir


def validate_mermaid_js(file_path):
    """
    Validate a mermaid.min.js file to ensure it's compatible.
    
    Returns:
        tuple: (is_valid, message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check 1: Size validation
    file_size = os.path.getsize(file_path)
    if file_size < 100000:  # Should be at least 100KB
        return False, f"File too small: {file_size} bytes"
    
    # Check 2: Content validation
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            content_str = content.decode('utf-8', errors='ignore')
            
            if b"function" not in content:
                return False, "Missing 'function' keyword"
            elif b"mermaid" not in content:
                return False, "Missing 'mermaid' keyword"
            
            # Check for illegal return statements outside functions
            # This is a common issue with some versions
            stripped_content = re.sub(r'\/\/.*', '', content_str)  # Remove comments
            # Look for return statements that aren't inside a function block
            if re.search(r'(^|\n|\r)\s*return\s*[^{]*;', stripped_content):
                return False, "Contains illegal return statement outside function"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
    
    # Check 3: MD5 hash validation (optional)
    file_hash = hashlib.md5(content).hexdigest()
    if file_hash != EXPECTED_MD5:
        print(f"Warning: File hash ({file_hash}) doesn't match expected hash ({EXPECTED_MD5})")
        # We'll still consider it valid if it passed the other checks
    
    return True, "File is valid"


def download_mermaid_js(target_path, force=False):
    """
    Download a known-compatible version of mermaid.min.js from CDN.
    
    Args:
        target_path: Path where the file should be saved
        force: Force download even if the file exists
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if file already exists and is valid
    if os.path.exists(target_path) and not force:
        is_valid, message = validate_mermaid_js(target_path)
        if is_valid:
            print(f"Existing mermaid.min.js file is valid: {target_path}")
            return True
        else:
            print(f"Existing file is invalid: {message}")
            try:
                os.remove(target_path)
                print(f"Removed invalid file: {target_path}")
            except Exception as e:
                print(f"Error removing invalid file: {str(e)}")
                return False
    
    try:
        # Use proper HTTP request with headers
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        request = urllib.request.Request(CDN_URL, headers=headers)
        
        # Download to temporary file first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            print(f"Downloading Mermaid.js from {CDN_URL}...")
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
                temp_file.write(content)
                temp_path = temp_file.name
        
        # Validate the downloaded file
        is_valid, message = validate_mermaid_js(temp_path)
        if is_valid:
            # Move to the target location
            import shutil
            shutil.move(temp_path, target_path)
            print(f"Successfully downloaded and validated Mermaid.js to: {target_path}")
            return True
        else:
            print(f"Downloaded file failed validation: {message}")
            os.remove(temp_path)
            return False
            
    except Exception as e:
        print(f"Error downloading Mermaid.js: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Download and validate a compatible version of mermaid.min.js')
    parser.add_argument('--force', action='store_true', help='Force redownload even if the file exists')
    
    args = parser.parse_args()
    
    # Create resources directory
    resources_dir = create_resources_dir()
    if resources_dir is None:
        return 1
    
    # Set target path
    target_path = os.path.join(resources_dir, "mermaid.min.js")
    
    # Download and validate
    success = download_mermaid_js(target_path, args.force)
    
    if success:
        print("Mermaid JS setup complete!")
        return 0
    else:
        print("Failed to set up Mermaid JS")
        return 1


if __name__ == "__main__":
    sys.exit(main())