#!/usr/bin/env python3
"""
PDF Analyzer for Markdown to PDF Converter Verification
------------------------------------------------------
This script analyzes PDF files to extract settings information for verification.
"""

import os
import re
import logging
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams, LTTextContainer, LTChar
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pdf_analyzer')

def analyze_pdf(pdf_file):
    """
    Analyze a PDF file to extract settings information
    
    Args:
        pdf_file (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing extracted settings
    """
    logger.info(f"Analyzing PDF file: {pdf_file}")
    
    if not os.path.exists(pdf_file):
        logger.error(f"PDF file not found: {pdf_file}")
        return {"error": f"PDF file not found: {pdf_file}"}
    
    try:
        # Extract basic information using PyPDF2
        basic_info = extract_basic_info(pdf_file)
        
        # Extract text content using pdfminer for more detailed analysis
        text_content = extract_text(pdf_file)
        
        # Extract font information
        font_info = extract_font_info(pdf_file)
        
        # Check for TOC presence
        toc_info = check_toc_presence(pdf_file, text_content)
        
        # Check heading numbering
        heading_info = check_heading_numbering(text_content)
        
        # Combine all information
        result = {
            **basic_info,
            **font_info,
            **toc_info,
            **heading_info
        }
        
        logger.info(f"PDF analysis complete: {pdf_file}")
        return result
    
    except Exception as e:
        logger.error(f"Error analyzing PDF file: {str(e)}")
        return {"error": f"Error analyzing PDF file: {str(e)}"}

def extract_basic_info(pdf_file):
    """Extract basic information from PDF file"""
    try:
        reader = PdfReader(pdf_file)
        
        # Get number of pages
        num_pages = len(reader.pages)
        
        # Get page size from first page
        page = reader.pages[0]
        media_box = page.mediabox
        width = float(media_box.width)
        height = float(media_box.height)
        
        # Determine page size and orientation
        page_size, orientation = determine_page_size(width, height)
        
        return {
            "num_pages": num_pages,
            "page_size": page_size,
            "orientation": orientation,
            "width_points": width,
            "height_points": height
        }
    
    except Exception as e:
        logger.error(f"Error extracting basic info: {str(e)}")
        return {"error": f"Error extracting basic info: {str(e)}"}

def determine_page_size(width, height):
    """
    Determine page size and orientation based on dimensions
    
    Common page sizes in points:
    - A4: 595 x 842 (portrait), 842 x 595 (landscape)
    - Letter: 612 x 792 (portrait), 792 x 612 (landscape)
    """
    # Normalize by making width the smaller dimension
    if width > height:
        w, h = height, width
        orientation = "landscape"
    else:
        w, h = width, height
        orientation = "portrait"
    
    # Check common page sizes with some tolerance
    tolerance = 5
    
    # A4
    if abs(w - 595) <= tolerance and abs(h - 842) <= tolerance:
        return "A4", orientation
    
    # Letter
    if abs(w - 612) <= tolerance and abs(h - 792) <= tolerance:
        return "Letter", orientation
    
    # If no match, return custom
    return f"Custom ({width:.1f}x{height:.1f})", orientation

def extract_font_info(pdf_file):
    """Extract font information from PDF file"""
    try:
        # Set up PDF parser
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        fonts = {}
        heading_fonts = {}
        body_font = None
        code_font = None
        
        with open(pdf_file, 'rb') as fp:
            for page in PDFPage.get_pages(fp):
                interpreter.process_page(page)
                layout = device.get_result()
                
                for element in layout:
                    if isinstance(element, LTTextContainer):
                        for text_line in element:
                            for character in text_line:
                                if isinstance(character, LTChar):
                                    font_name = character.fontname
                                    font_size = round(character.size)
                                    
                                    if font_name not in fonts:
                                        fonts[font_name] = {
                                            "sizes": set(),
                                            "count": 0
                                        }
                                    
                                    fonts[font_name]["sizes"].add(font_size)
                                    fonts[font_name]["count"] += 1
        
        # Process font information
        font_info = []
        for font_name, info in fonts.items():
            font_info.append({
                "name": font_name,
                "sizes": sorted(list(info["sizes"])),
                "count": info["count"]
            })
        
        # Sort by usage count (most used first)
        font_info.sort(key=lambda x: x["count"], reverse=True)
        
        # Try to determine body font (most used font)
        if font_info:
            body_font = {
                "family": font_info[0]["name"],
                "size": most_common_size(font_info[0]["sizes"])
            }
        
        # Try to identify heading fonts (usually larger sizes)
        heading_sizes = {}
        for font in font_info:
            for size in font["sizes"]:
                if size > (body_font["size"] if body_font else 10):
                    if size not in heading_sizes:
                        heading_sizes[size] = []
                    heading_sizes[size].append(font["name"])
        
        # Sort heading sizes in descending order
        for size in sorted(heading_sizes.keys(), reverse=True):
            if len(heading_fonts) < 6:  # Assume h1-h6
                heading_fonts[f"h{len(heading_fonts)+1}"] = {
                    "family": heading_sizes[size][0],
                    "size": size
                }
        
        return {
            "fonts": font_info,
            "body_font": body_font,
            "heading_fonts": heading_fonts
        }
    
    except Exception as e:
        logger.error(f"Error extracting font info: {str(e)}")
        return {"error": f"Error extracting font info: {str(e)}"}

def most_common_size(sizes):
    """Find the most common size in a list"""
    if not sizes:
        return None
    
    size_count = {}
    for size in sizes:
        if size not in size_count:
            size_count[size] = 0
        size_count[size] += 1
    
    return max(size_count.items(), key=lambda x: x[1])[0]

def check_toc_presence(pdf_file, text_content):
    """Check for the presence of a table of contents"""
    try:
        # Check if the PDF has bookmarks (TOC)
        reader = PdfReader(pdf_file)
        has_bookmarks = len(reader.outline) > 0 if reader.outline else False
        
        # Check for common TOC titles in the text
        toc_patterns = [
            r"(?i)^\s*table\s+of\s+contents\s*$",
            r"(?i)^\s*contents\s*$",
            r"(?i)^\s*toc\s*$"
        ]
        
        has_toc_title = False
        toc_title = None
        
        for pattern in toc_patterns:
            match = re.search(pattern, text_content, re.MULTILINE)
            if match:
                has_toc_title = True
                toc_title = match.group(0).strip()
                break
        
        # Try to determine TOC depth by looking for numbered headings
        toc_depth = 0
        if has_bookmarks or has_toc_title:
            # Look for patterns like "1. Section" or "1.1 Subsection"
            depth_patterns = [
                r"\d+\.\s+\w+",  # Level 1: "1. Section"
                r"\d+\.\d+\.\s+\w+",  # Level 2: "1.1 Section"
                r"\d+\.\d+\.\d+\.\s+\w+",  # Level 3: "1.1.1 Section"
                r"\d+\.\d+\.\d+\.\d+\.\s+\w+",  # Level 4: "1.1.1.1 Section"
            ]
            
            for i, pattern in enumerate(depth_patterns, 1):
                if re.search(pattern, text_content):
                    toc_depth = i
        
        return {
            "has_toc": has_bookmarks or has_toc_title,
            "toc_title": toc_title,
            "toc_depth": toc_depth
        }
    
    except Exception as e:
        logger.error(f"Error checking TOC presence: {str(e)}")
        return {"error": f"Error checking TOC presence: {str(e)}"}

def check_heading_numbering(text_content):
    """Check heading numbering style (technical vs. standard)"""
    try:
        # Check for technical numbering (1.1, 1.2, etc.)
        technical_pattern = r"\d+\.\d+\s+\w+"
        has_technical = bool(re.search(technical_pattern, text_content))
        
        # Check for standard numbering (just the heading text)
        standard_pattern = r"^(?![\d\.]+\s+)\w+.*$"
        has_standard = bool(re.search(standard_pattern, text_content, re.MULTILINE))
        
        # Determine numbering style
        if has_technical and not has_standard:
            numbering_style = "technical"
        elif has_standard and not has_technical:
            numbering_style = "standard"
        elif has_technical and has_standard:
            numbering_style = "mixed"
        else:
            numbering_style = "unknown"
        
        return {
            "heading_numbering": numbering_style
        }
    
    except Exception as e:
        logger.error(f"Error checking heading numbering: {str(e)}")
        return {"error": f"Error checking heading numbering: {str(e)}"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_analyzer.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    result = analyze_pdf(pdf_file)
    
    import json
    print(json.dumps(result, indent=2))
