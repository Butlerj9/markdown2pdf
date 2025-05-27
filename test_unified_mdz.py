#!/usr/bin/env python3
"""
Test script for the unified MDZ format handler
"""

import os
import tempfile
import shutil
from unified_mdz import UnifiedMDZ, CompressionMethod, get_mdz_info

def test_standard_method():
    """Test the standard (tar-based) method"""
    print("Testing standard method...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
    
    try:
        # Create test files
        markdown_content = """---
title: Test Document
author: Test User
---

# Test Document

This is a test document.

## Section 1

Some content in section 1.

## Section 2

Some content in section 2.
"""
        
        # Create a test markdown file
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w") as f:
            f.write(markdown_content)
        
        # Create a test image file
        img_file = os.path.join(temp_dir, "test.png")
        with open(img_file, "wb") as f:
            f.write(b"This is not a real PNG file, just a test.")
        
        # Create an MDZ bundle
        bundle = UnifiedMDZ(compression_method=CompressionMethod.STANDARD)
        bundle.create_from_markdown(markdown_content, {"title": "Test Document", "author": "Test User"})
        bundle.add_file("images/test.png", b"This is not a real PNG file, just a test.")
        
        # Save the bundle
        mdz_file = os.path.join(temp_dir, "test_standard.mdz")
        bundle.save(mdz_file)
        
        print(f"Created MDZ file: {mdz_file}")
        
        # Get file info
        info = get_mdz_info(mdz_file)
        print(f"File size: {info['file_size']} bytes")
        print(f"Compression method: {info['compression_method']}")
        print(f"Compression ratio: {info['compression_ratio']:.2f}x")
        print(f"File types: {info['file_types']}")
        
        # Load the bundle
        bundle2 = UnifiedMDZ()
        bundle2.load(mdz_file)
        
        # Check the content
        assert bundle2.get_main_content() == markdown_content
        assert bundle2.get_metadata() == {"title": "Test Document", "author": "Test User"}
        assert bundle2.content["images/test.png"] == b"This is not a real PNG file, just a test."
        
        print("Standard method test passed!")
        return mdz_file
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_secure_method():
    """Test the secure (checksum dictionary) method"""
    print("\nTesting secure method...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
    
    try:
        # Create test files
        markdown_content = """---
title: Test Document
author: Test User
---

# Test Document

This is a test document.

## Section 1

Some content in section 1.

## Section 2

Some content in section 2.
"""
        
        # Create a test markdown file
        md_file = os.path.join(temp_dir, "test.md")
        with open(md_file, "w") as f:
            f.write(markdown_content)
        
        # Create a test image file
        img_file = os.path.join(temp_dir, "test.png")
        with open(img_file, "wb") as f:
            f.write(b"This is not a real PNG file, just a test.")
        
        # Create an MDZ bundle
        bundle = UnifiedMDZ(compression_method=CompressionMethod.SECURE)
        bundle.create_from_markdown(markdown_content, {"title": "Test Document", "author": "Test User"})
        bundle.add_file("images/test.png", b"This is not a real PNG file, just a test.")
        
        # Save the bundle
        mdz_file = os.path.join(temp_dir, "test_secure.mdz")
        bundle.save(mdz_file)
        
        print(f"Created MDZ file: {mdz_file}")
        
        # Get file info
        info = get_mdz_info(mdz_file)
        print(f"File size: {info['file_size']} bytes")
        print(f"Compression method: {info['compression_method']}")
        print(f"Compression ratio: {info['compression_ratio']:.2f}x")
        print(f"File types: {info['file_types']}")
        
        # Load the bundle
        bundle2 = UnifiedMDZ()
        bundle2.load(mdz_file)
        
        # Check the content
        assert bundle2.get_main_content() == markdown_content
        assert bundle2.get_metadata() == {"title": "Test Document", "author": "Test User"}
        assert bundle2.content["images/test.png"] == b"This is not a real PNG file, just a test."
        
        print("Secure method test passed!")
        return mdz_file
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

def test_auto_detection():
    """Test automatic detection of the compression method"""
    print("\nTesting auto detection...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
    
    try:
        # Create test files for both methods
        standard_file = test_standard_method()
        secure_file = test_secure_method()
        
        # Copy the files to the temp directory
        standard_copy = os.path.join(temp_dir, "standard.mdz")
        secure_copy = os.path.join(temp_dir, "secure.mdz")
        
        shutil.copy(standard_file, standard_copy)
        shutil.copy(secure_file, secure_copy)
        
        # Load the standard file
        bundle1 = UnifiedMDZ()
        bundle1.load(standard_copy)
        print(f"Detected method for standard file: {bundle1.compression_method}")
        assert bundle1.compression_method == CompressionMethod.STANDARD
        
        # Load the secure file
        bundle2 = UnifiedMDZ()
        bundle2.load(secure_copy)
        print(f"Detected method for secure file: {bundle2.compression_method}")
        assert bundle2.compression_method == CompressionMethod.SECURE
        
        print("Auto detection test passed!")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_standard_method()
    test_secure_method()
    test_auto_detection()
    print("\nAll tests passed!")
