#!/usr/bin/env python3
"""
EPUB Analyzer for Markdown to PDF Converter Verification
-------------------------------------------------------
This script analyzes EPUB files to extract settings information for verification.
"""

import os
import re
import logging
import zipfile
import tempfile
import cssutils
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('epub_analyzer')

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

def analyze_epub(epub_file):
    """
    Analyze an EPUB file to extract settings information
    
    Args:
        epub_file (str): Path to the EPUB file
        
    Returns:
        dict: Dictionary containing extracted settings
    """
    logger.info(f"Analyzing EPUB file: {epub_file}")
    
    if not os.path.exists(epub_file):
        logger.error(f"EPUB file not found: {epub_file}")
        return {"error": f"EPUB file not found: {epub_file}"}
    
    try:
        # Create a temporary directory to extract EPUB contents
        temp_dir = tempfile.mkdtemp()
        
        # Extract EPUB content
        book = epub.read_epub(epub_file)
        
        # Extract metadata
        metadata = extract_metadata(book)
        
        # Extract CSS styles
        css_info = extract_css_styles(book)
        
        # Check for TOC presence
        toc_info = check_toc_presence(book)
        
        # Check heading numbering
        heading_info = check_heading_numbering(book)
        
        # Combine all information
        result = {
            **metadata,
            **css_info,
            **toc_info,
            **heading_info
        }
        
        logger.info(f"EPUB analysis complete: {epub_file}")
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing EPUB file: {str(e)}")
        return {"error": f"Error analyzing EPUB file: {str(e)}"}

def extract_metadata(book):
    """Extract metadata from EPUB book"""
    try:
        metadata = {
            "title": book.get_metadata('DC', 'title'),
            "creator": book.get_metadata('DC', 'creator'),
            "language": book.get_metadata('DC', 'language'),
            "identifier": book.get_metadata('DC', 'identifier')
        }
        
        # Clean up metadata (extract first value from each list)
        for key, value in metadata.items():
            if isinstance(value, list) and len(value) > 0:
                metadata[key] = value[0][0]
            else:
                metadata[key] = None
        
        return {
            "metadata": metadata
        }
    
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        return {"error": f"Error extracting metadata: {str(e)}"}

def extract_css_styles(book):
    """Extract CSS styles from EPUB"""
    try:
        css_info = {
            "styles": {},
            "body_font": None,
            "heading_fonts": {},
            "code_font": None
        }
        
        # Extract CSS files
        for item in book.get_items():
            if item.media_type == 'text/css':
                css_content = item.get_content().decode('utf-8')
                sheet = cssutils.parseString(css_content)
                
                for rule in sheet:
                    if rule.type == rule.STYLE_RULE:
                        selector = rule.selectorText
                        properties = {prop.name: prop.value for prop in rule.style}
                        css_info["styles"][selector] = properties
        
        # Extract body font
        body_style = css_info["styles"].get('body', {})
        if body_style:
            font_family = body_style.get('font-family')
            font_size = body_style.get('font-size')
            
            if font_family or font_size:
                css_info["body_font"] = {
                    "family": font_family.strip("'\"") if font_family else None,
                    "size": extract_size_value(font_size) if font_size else None
                }
        
        # Extract heading fonts
        for i in range(1, 7):  # h1 to h6
            heading_selector = f'h{i}'
            heading_style = css_info["styles"].get(heading_selector, {})
            
            if heading_style:
                font_family = heading_style.get('font-family')
                font_size = heading_style.get('font-size')
                
                if font_family or font_size:
                    css_info["heading_fonts"][heading_selector] = {
                        "family": font_family.strip("'\"") if font_family else None,
                        "size": extract_size_value(font_size) if font_size else None
                    }
        
        # Extract code font
        code_style = css_info["styles"].get('code', {})
        pre_style = css_info["styles"].get('pre', {})
        
        if code_style or pre_style:
            font_family = code_style.get('font-family') or pre_style.get('font-family')
            font_size = code_style.get('font-size') or pre_style.get('font-size')
            
            if font_family or font_size:
                css_info["code_font"] = {
                    "family": font_family.strip("'\"") if font_family else None,
                    "size": extract_size_value(font_size) if font_size else None
                }
        
        return css_info
    
    except Exception as e:
        logger.error(f"Error extracting CSS styles: {str(e)}")
        return {"error": f"Error extracting CSS styles: {str(e)}"}

def extract_size_value(size_str):
    """Extract numeric value from size string (e.g., '12pt', '1.5em')"""
    if not size_str:
        return None
    
    match = re.search(r'([\d\.]+)(\w+)', size_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        return {"value": value, "unit": unit}
    
    return None

def check_toc_presence(book):
    """Check for the presence of a table of contents"""
    try:
        # Check if the book has a table of contents
        toc = book.toc
        has_toc = len(toc) > 0
        
        # Determine TOC depth
        toc_depth = 0
        if has_toc:
            # Function to recursively determine depth
            def get_depth(items, current_depth=1):
                max_depth = current_depth
                for item in items:
                    if isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], list):
                        # This is a nested TOC item
                        child_depth = get_depth(item[1], current_depth + 1)
                        max_depth = max(max_depth, child_depth)
                return max_depth
            
            toc_depth = get_depth(toc)
        
        # Try to find TOC title
        toc_title = None
        if has_toc:
            # Look for TOC title in HTML content
            for item in book.get_items():
                if item.media_type == 'application/xhtml+xml':
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'lxml')
                    
                    # Look for common TOC elements
                    toc_elements = [
                        soup.find('nav', {'id': 'toc'}),
                        soup.find('div', {'id': 'toc'}),
                        soup.find('nav', {'class': 'toc'}),
                        soup.find('div', {'class': 'toc'})
                    ]
                    
                    for el in toc_elements:
                        if el:
                            # Check for heading inside TOC
                            heading = el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            if heading:
                                toc_title = heading.get_text().strip()
                                break
                    
                    if toc_title:
                        break
        
        return {
            "has_toc": has_toc,
            "toc_title": toc_title,
            "toc_depth": toc_depth
        }
    
    except Exception as e:
        logger.error(f"Error checking TOC presence: {str(e)}")
        return {"error": f"Error checking TOC presence: {str(e)}"}

def check_heading_numbering(book):
    """Check heading numbering style (technical vs. standard)"""
    try:
        technical_count = 0
        standard_count = 0
        
        # Analyze HTML content
        for item in book.get_items():
            if item.media_type == 'application/xhtml+xml':
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'lxml')
                
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                for heading in headings:
                    text = heading.get_text().strip()
                    
                    # Check for technical numbering (1.1, 1.2, etc.)
                    if re.match(r'^\d+(\.\d+)*\s+\w+', text):
                        technical_count += 1
                    else:
                        standard_count += 1
        
        # Determine numbering style
        if technical_count > 0 and standard_count == 0:
            numbering_style = "technical"
        elif standard_count > 0 and technical_count == 0:
            numbering_style = "standard"
        elif technical_count > 0 and standard_count > 0:
            numbering_style = "mixed"
        else:
            numbering_style = "unknown"
        
        return {
            "heading_numbering": numbering_style,
            "technical_headings": technical_count,
            "standard_headings": standard_count
        }
    
    except Exception as e:
        logger.error(f"Error checking heading numbering: {str(e)}")
        return {"error": f"Error checking heading numbering: {str(e)}"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python epub_analyzer.py <epub_file>")
        sys.exit(1)
    
    epub_file = sys.argv[1]
    result = analyze_epub(epub_file)
    
    import json
    print(json.dumps(result, indent=2))
