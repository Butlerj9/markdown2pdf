#!/usr/bin/env python3
"""
HTML Analyzer for Markdown to PDF Converter Verification
-------------------------------------------------------
This script analyzes HTML files to extract settings information for verification.
"""

import os
import re
import logging
import cssutils
from bs4 import BeautifulSoup

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('html_analyzer')

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)

def analyze_html(html_file):
    """
    Analyze an HTML file to extract settings information
    
    Args:
        html_file (str): Path to the HTML file
        
    Returns:
        dict: Dictionary containing extracted settings
    """
    logger.info(f"Analyzing HTML file: {html_file}")
    
    if not os.path.exists(html_file):
        logger.error(f"HTML file not found: {html_file}")
        return {"error": f"HTML file not found: {html_file}"}
    
    try:
        # Read the HTML file
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract CSS styles
        css_info = extract_css_styles(soup)
        
        # Check for TOC presence
        toc_info = check_toc_presence(soup)
        
        # Check heading numbering
        heading_info = check_heading_numbering(soup)
        
        # Extract page settings
        page_info = extract_page_settings(soup, css_info)
        
        # Combine all information
        result = {
            **css_info,
            **toc_info,
            **heading_info,
            **page_info
        }
        
        logger.info(f"HTML analysis complete: {html_file}")
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing HTML file: {str(e)}")
        return {"error": f"Error analyzing HTML file: {str(e)}"}

def extract_css_styles(soup):
    """Extract CSS styles from HTML"""
    try:
        css_info = {
            "styles": {},
            "body_font": None,
            "heading_fonts": {},
            "code_font": None
        }
        
        # Extract inline styles
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                sheet = cssutils.parseString(style_tag.string)
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

def check_toc_presence(soup):
    """Check for the presence of a table of contents"""
    try:
        # Look for common TOC elements
        toc_elements = [
            soup.find('nav', {'id': 'TOC'}),  # Pandoc default TOC
            soup.find('div', {'id': 'TOC'}),  # Alternative TOC
            soup.find('nav', {'class': 'toc'}),
            soup.find('div', {'class': 'toc'})
        ]
        
        has_toc = any(el is not None for el in toc_elements)
        
        # Find TOC title
        toc_title = None
        if has_toc:
            for el in toc_elements:
                if el:
                    # Check for heading inside TOC
                    heading = el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if heading:
                        toc_title = heading.get_text().strip()
                        break
        
        # Determine TOC depth
        toc_depth = 0
        if has_toc:
            for el in toc_elements:
                if el:
                    # Count levels of nested lists
                    lists = el.find_all('ul')
                    if lists:
                        # Calculate max nesting level
                        max_depth = 1  # Start with 1 for the top level
                        for ul in lists:
                            # Count parents that are also lists
                            depth = 1
                            parent = ul.parent
                            while parent:
                                if parent.name == 'ul' or parent.name == 'ol':
                                    depth += 1
                                parent = parent.parent
                            max_depth = max(max_depth, depth)
                        
                        toc_depth = max_depth
                        break
        
        return {
            "has_toc": has_toc,
            "toc_title": toc_title,
            "toc_depth": toc_depth
        }
    
    except Exception as e:
        logger.error(f"Error checking TOC presence: {str(e)}")
        return {"error": f"Error checking TOC presence: {str(e)}"}

def check_heading_numbering(soup):
    """Check heading numbering style (technical vs. standard)"""
    try:
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        technical_count = 0
        standard_count = 0
        
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

def extract_page_settings(soup, css_info):
    """Extract page settings from HTML/CSS"""
    try:
        page_info = {
            "page_size": None,
            "orientation": None,
            "margins": None
        }
        
        # Check for @page rule in CSS
        for selector, properties in css_info["styles"].items():
            if selector == '@page':
                # Check for size property
                size = properties.get('size')
                if size:
                    # Parse size value (e.g., "A4 landscape", "letter portrait")
                    size_parts = size.lower().split()
                    if len(size_parts) >= 1:
                        page_info["page_size"] = size_parts[0].upper()
                    
                    if len(size_parts) >= 2:
                        page_info["orientation"] = size_parts[1]
                
                # Check for margin properties
                margin = properties.get('margin')
                if margin:
                    page_info["margins"] = margin
        
        return page_info
    
    except Exception as e:
        logger.error(f"Error extracting page settings: {str(e)}")
        return {"error": f"Error extracting page settings: {str(e)}"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python html_analyzer.py <html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    result = analyze_html(html_file)
    
    import json
    print(json.dumps(result, indent=2))
