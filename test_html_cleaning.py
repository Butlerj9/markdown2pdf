#!/usr/bin/env python3
"""
Simple test to verify HTML cleaning functionality
"""

import re

def clean_html_content(html_content):
    """Clean HTML content to remove unwanted title elements and blank lines"""
    
    # Remove any title elements that might be creating blank space
    # This handles Pandoc's title generation even when we don't want it
    html_content = re.sub(r'<h1[^>]*class="title"[^>]*>.*?</h1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<p[^>]*class="title"[^>]*>.*?</p>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<div[^>]*class="title"[^>]*>.*?</div>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove empty paragraphs at the beginning that might be causing blank lines
    html_content = re.sub(r'^(\s*<p[^>]*>\s*</p>\s*)+', '', html_content, flags=re.MULTILINE)
    
    # Remove multiple consecutive line breaks at the start
    html_content = re.sub(r'^(\s*<br[^>]*>\s*)+', '', html_content, flags=re.MULTILINE)
    
    # Remove any standalone title text that might be left over
    html_content = re.sub(r'^\s*Document\s*$', '', html_content, flags=re.MULTILINE)
    
    # Clean up any extra whitespace at the beginning
    html_content = html_content.lstrip()
    
    return html_content

def test_html_cleaning():
    """Test the HTML cleaning functionality"""
    print("Testing HTML content cleaning...")
    
    # Test case 1: HTML with title elements
    test_html_1 = """<h1 class="title">Document</h1>
<p class="title">Some title</p>
<div class="title">Another title</div>
<p></p>
<br>
<br>
Document
<h1>JOSHUA DAVID BUTLER</h1>
<p>Oakland, CA 94612 | (510) 692-1491 | josh.d.butler@gmail.com</p>"""
    
    print("\nTest Case 1: HTML with title elements")
    print("Original HTML:")
    print(test_html_1)
    print("\nCleaned HTML:")
    cleaned_1 = clean_html_content(test_html_1)
    print(cleaned_1)
    
    # Check if cleaning worked
    issues = []
    if 'class="title"' in cleaned_1:
        issues.append("Title class elements still present")
    if cleaned_1.startswith('<p></p>'):
        issues.append("Empty paragraphs at start")
    if cleaned_1.startswith('<br'):
        issues.append("Line breaks at start")
    if 'Document\n' in cleaned_1 or cleaned_1.startswith('Document'):
        issues.append("Standalone 'Document' text still present")
    
    if not issues:
        print("✓ Test Case 1 PASSED: All title elements and blank lines removed")
    else:
        print(f"✗ Test Case 1 FAILED: {', '.join(issues)}")
    
    # Test case 2: Normal HTML without issues
    test_html_2 = """<h1>JOSHUA DAVID BUTLER</h1>
<p>Oakland, CA 94612 | (510) 692-1491 | josh.d.butler@gmail.com</p>
<h2>SUMMARY</h2>
<p>Highly experienced technology leader...</p>"""
    
    print("\nTest Case 2: Normal HTML without title issues")
    cleaned_2 = clean_html_content(test_html_2)
    
    if cleaned_2 == test_html_2:
        print("✓ Test Case 2 PASSED: Normal HTML unchanged")
    else:
        print("✗ Test Case 2 FAILED: Normal HTML was modified")
        print(f"Expected: {test_html_2}")
        print(f"Got: {cleaned_2}")
    
    # Test case 3: Edge case with multiple title variations
    test_html_3 = """<h1 class="title">Document Title</h1>
<p class="TITLE">Another Title</p>
<div class="Title">Yet Another</div>
<p></p>
<p> </p>
<br/>
<br />

Document

<h1>Real Content Starts Here</h1>"""
    
    print("\nTest Case 3: Multiple title variations and whitespace")
    cleaned_3 = clean_html_content(test_html_3)
    print("Cleaned HTML:")
    print(repr(cleaned_3))  # Use repr to see whitespace
    
    if cleaned_3.startswith('<h1>Real Content Starts Here</h1>'):
        print("✓ Test Case 3 PASSED: All title variations and whitespace removed")
    else:
        print("✗ Test Case 3 FAILED: Some title elements or whitespace remain")
    
    print("\nHTML cleaning tests completed!")

if __name__ == "__main__":
    test_html_cleaning()
