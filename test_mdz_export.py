#!/usr/bin/env python3
"""
MDZ Export Test Script
-------------------
This script tests the export functionality of the MDZ format.

File: test_mdz_export.py
"""

import os
import sys
import tempfile
import shutil
import logging
import argparse
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_mdz_file():
    """
    Create a test MDZ file
    
    Returns:
        Tuple of (temp_dir, mdz_path)
    """
    try:
        from mdz_bundle import MDZBundle
    except ImportError:
        logger.error("MDZ bundle module not found")
        return None, None
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_export_test_")
    
    # Create a test Markdown file
    md_content = """---
title: "MDZ Export Test"
author: "Test Script"
date: "2025-05-01"
---

# MDZ Export Test

This is a test document for MDZ export functionality.

## Features

### GitHub Flavored Markdown

- [x] Task list item 1
- [ ] Task list item 2
- [ ] Task list item 3

### Tables

| Name  | Age | Occupation |
|-------|-----|------------|
| Alice | 28  | Engineer   |
| Bob   | 35  | Designer   |
| Carol | 42  | Manager    |

### Code Blocks

```python
def hello_world():
    print("Hello, world!")
```

### Mermaid Diagrams

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process 1]
    B -->|No| D[Process 2]
    C --> E[End]
    D --> E
```

### LaTeX Math

Inline math: $E = mc^2$

Display math:

$$
\\frac{d}{dx}(x^n) = nx^{n-1}
$$

### Images

![Test Image](test_image.png)

## Conclusion

This document tests all the export features of the MDZ format.
"""
    
    md_path = os.path.join(temp_dir, "test.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Create a test image
    img_path = os.path.join(temp_dir, "test_image.png")
    create_test_image(img_path)
    
    # Create an MDZ bundle
    bundle = MDZBundle()
    
    # Add content
    bundle.create_from_markdown(md_content, {"title": "MDZ Export Test"})
    
    # Add the image
    with open(img_path, "rb") as f:
        image_content = f.read()
    bundle.add_file(img_path, image_content)
    
    # Save the bundle
    mdz_path = os.path.join(temp_dir, "test.mdz")
    bundle.save(mdz_path)
    
    logger.info(f"Created test MDZ file: {mdz_path}")
    return temp_dir, mdz_path

def create_test_image(path):
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 100x100 white image
        img = Image.new("RGB", (100, 100), color="white")
        
        # Draw a red rectangle
        draw = ImageDraw.Draw(img)
        draw.rectangle([(10, 10), (90, 90)], outline="red", width=2)
        
        # Save the image
        img.save(path)
    except ImportError:
        # If PIL is not available, create a simple binary file
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

def test_html_export(mdz_path):
    """
    Test export to HTML
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        Path to the exported HTML file, or None if export failed
    """
    try:
        from mdz_bundle import MDZBundle
        from mdz_renderer import MDZRenderer
    except ImportError:
        logger.error("MDZ modules not found")
        return None
    
    # Load the MDZ bundle
    bundle = MDZBundle()
    bundle.load(mdz_path)
    
    # Extract to a temporary directory
    extracted_assets = bundle.extract_to_temp()
    
    # Create a renderer
    renderer = MDZRenderer()
    
    # Extract front matter
    markdown_without_front_matter, front_matter = renderer.extract_front_matter(bundle.get_main_content())
    
    # Extract and render Mermaid diagrams
    mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)
    
    # Render to HTML
    html_content = renderer.render_to_html(
        markdown_without_front_matter,
        front_matter=front_matter,
        mermaid_diagrams=mermaid_diagrams,
        asset_paths=extracted_assets
    )
    
    # Save the HTML content
    html_path = os.path.join(os.path.dirname(mdz_path), "test_export.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    logger.info(f"Exported HTML file: {html_path}")
    return html_path

def test_pdf_export(mdz_path):
    """
    Test export to PDF
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        Path to the exported PDF file, or None if export failed
    """
    # Check if pandoc is installed
    try:
        result = subprocess.run(["pandoc", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        if result.returncode != 0:
            logger.error("Pandoc is not installed")
            return None
    except FileNotFoundError:
        logger.error("Pandoc is not installed")
        return None
    
    try:
        from mdz_bundle import MDZBundle
    except ImportError:
        logger.error("MDZ bundle module not found")
        return None
    
    # Load the MDZ bundle
    bundle = MDZBundle()
    bundle.load(mdz_path)
    
    # Extract to a temporary directory
    extracted_assets = bundle.extract_to_temp()
    temp_dir = bundle.temp_dir
    
    # Create a temporary Markdown file with the extracted content
    temp_md_path = os.path.join(temp_dir, "temp.md")
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(bundle.get_main_content())
    
    # Create a PDF file path
    pdf_path = os.path.join(os.path.dirname(mdz_path), "test_export.pdf")
    
    # Create a LaTeX template for PDF export
    latex_template = """\\documentclass{article}
\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{xcolor}
\\usepackage{fontspec}
\\setmainfont{Latin Modern Roman}
\\title{$title$}
\\author{$author$}
\\date{$date$}
\\begin{document}
\\maketitle
$body$
\\end{document}
"""
    
    latex_template_path = os.path.join(temp_dir, "template.tex")
    with open(latex_template_path, "w", encoding="utf-8") as f:
        f.write(latex_template)
    
    # Run pandoc to convert Markdown to PDF
    try:
        cmd = [
            "pandoc",
            temp_md_path,
            "--pdf-engine=xelatex",
            f"--template={latex_template_path}",
            f"--output={pdf_path}",
            "--standalone",
            "--toc"
        ]
        
        # Add metadata
        for key, value in bundle.get_metadata().items():
            if isinstance(value, str):
                cmd.append(f"--metadata={key}={value}")
        
        # Run the command
        result = subprocess.run(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode != 0:
            logger.error(f"Error exporting to PDF: {result.stderr}")
            return None
        
        logger.info(f"Exported PDF file: {pdf_path}")
        return pdf_path
    
    except Exception as e:
        logger.error(f"Error exporting to PDF: {str(e)}")
        return None

def test_epub_export(mdz_path):
    """
    Test export to EPUB
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        Path to the exported EPUB file, or None if export failed
    """
    # Check if pandoc is installed
    try:
        result = subprocess.run(["pandoc", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        if result.returncode != 0:
            logger.error("Pandoc is not installed")
            return None
    except FileNotFoundError:
        logger.error("Pandoc is not installed")
        return None
    
    try:
        from mdz_bundle import MDZBundle
    except ImportError:
        logger.error("MDZ bundle module not found")
        return None
    
    # Load the MDZ bundle
    bundle = MDZBundle()
    bundle.load(mdz_path)
    
    # Extract to a temporary directory
    extracted_assets = bundle.extract_to_temp()
    temp_dir = bundle.temp_dir
    
    # Create a temporary Markdown file with the extracted content
    temp_md_path = os.path.join(temp_dir, "temp.md")
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(bundle.get_main_content())
    
    # Create an EPUB file path
    epub_path = os.path.join(os.path.dirname(mdz_path), "test_export.epub")
    
    # Run pandoc to convert Markdown to EPUB
    try:
        cmd = [
            "pandoc",
            temp_md_path,
            f"--output={epub_path}",
            "--standalone",
            "--toc"
        ]
        
        # Add metadata
        for key, value in bundle.get_metadata().items():
            if isinstance(value, str):
                cmd.append(f"--metadata={key}={value}")
        
        # Run the command
        result = subprocess.run(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode != 0:
            logger.error(f"Error exporting to EPUB: {result.stderr}")
            return None
        
        logger.info(f"Exported EPUB file: {epub_path}")
        return epub_path
    
    except Exception as e:
        logger.error(f"Error exporting to EPUB: {str(e)}")
        return None

def test_docx_export(mdz_path):
    """
    Test export to DOCX
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        Path to the exported DOCX file, or None if export failed
    """
    # Check if pandoc is installed
    try:
        result = subprocess.run(["pandoc", "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        if result.returncode != 0:
            logger.error("Pandoc is not installed")
            return None
    except FileNotFoundError:
        logger.error("Pandoc is not installed")
        return None
    
    try:
        from mdz_bundle import MDZBundle
    except ImportError:
        logger.error("MDZ bundle module not found")
        return None
    
    # Load the MDZ bundle
    bundle = MDZBundle()
    bundle.load(mdz_path)
    
    # Extract to a temporary directory
    extracted_assets = bundle.extract_to_temp()
    temp_dir = bundle.temp_dir
    
    # Create a temporary Markdown file with the extracted content
    temp_md_path = os.path.join(temp_dir, "temp.md")
    with open(temp_md_path, "w", encoding="utf-8") as f:
        f.write(bundle.get_main_content())
    
    # Create a DOCX file path
    docx_path = os.path.join(os.path.dirname(mdz_path), "test_export.docx")
    
    # Run pandoc to convert Markdown to DOCX
    try:
        cmd = [
            "pandoc",
            temp_md_path,
            f"--output={docx_path}",
            "--standalone",
            "--toc"
        ]
        
        # Add metadata
        for key, value in bundle.get_metadata().items():
            if isinstance(value, str):
                cmd.append(f"--metadata={key}={value}")
        
        # Run the command
        result = subprocess.run(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode != 0:
            logger.error(f"Error exporting to DOCX: {result.stderr}")
            return None
        
        logger.info(f"Exported DOCX file: {docx_path}")
        return docx_path
    
    except Exception as e:
        logger.error(f"Error exporting to DOCX: {str(e)}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MDZ Export Test Script")
    parser.add_argument("--html", action="store_true", help="Test export to HTML")
    parser.add_argument("--pdf", action="store_true", help="Test export to PDF")
    parser.add_argument("--epub", action="store_true", help="Test export to EPUB")
    parser.add_argument("--docx", action="store_true", help="Test export to DOCX")
    parser.add_argument("--all", action="store_true", help="Test all export formats")
    
    args = parser.parse_args()
    
    # If no arguments are provided, show help
    if not (args.html or args.pdf or args.epub or args.docx or args.all):
        parser.print_help()
        return
    
    # Create a test MDZ file
    temp_dir, mdz_path = create_test_mdz_file()
    if not mdz_path:
        logger.error("Failed to create test MDZ file")
        return
    
    try:
        # Test export to HTML
        if args.html or args.all:
            logger.info("Testing export to HTML...")
            html_path = test_html_export(mdz_path)
            if html_path:
                print(f"HTML export successful: {html_path}")
            else:
                print("HTML export failed")
        
        # Test export to PDF
        if args.pdf or args.all:
            logger.info("Testing export to PDF...")
            pdf_path = test_pdf_export(mdz_path)
            if pdf_path:
                print(f"PDF export successful: {pdf_path}")
            else:
                print("PDF export failed")
        
        # Test export to EPUB
        if args.epub or args.all:
            logger.info("Testing export to EPUB...")
            epub_path = test_epub_export(mdz_path)
            if epub_path:
                print(f"EPUB export successful: {epub_path}")
            else:
                print("EPUB export failed")
        
        # Test export to DOCX
        if args.docx or args.all:
            logger.info("Testing export to DOCX...")
            docx_path = test_docx_export(mdz_path)
            if docx_path:
                print(f"DOCX export successful: {docx_path}")
            else:
                print("DOCX export failed")
        
        logger.info("MDZ export tests completed")
        
        # Keep the temporary directory for testing
        print(f"\nTest files are located in: {temp_dir}")
        print("Please delete this directory when you're done testing.")
    
    except Exception as e:
        logger.error(f"Error testing MDZ export: {str(e)}")
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory: {str(e)}")

if __name__ == "__main__":
    main()
