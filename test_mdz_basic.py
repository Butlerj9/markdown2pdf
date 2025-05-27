#!/usr/bin/env python3
"""
Basic MDZ Format Test Script
--------------------------
This script provides basic tests for the MDZ format.

File: test_mdz_basic.py
"""

import os
import sys
import tempfile
import shutil
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_markdown():
    """Create a test Markdown file with various features"""
    content = """---
title: "MDZ Format Test"
author: "Test Script"
date: "2025-05-01"
tags: ["markdown", "test", "mdz"]
---

# MDZ Format Test

This is a test document for the MDZ format.

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

This document tests all the features of the MDZ format.
"""

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_test_")

    # Create the test Markdown file
    md_path = os.path.join(temp_dir, "test.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Create a test image
    img_path = os.path.join(temp_dir, "test_image.png")
    create_test_image(img_path)

    return temp_dir, md_path

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
        logger.info(f"Created test image: {path}")
    except ImportError:
        # If PIL is not available, create a simple binary file
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        logger.warning("PIL not available, created a dummy PNG file")

def test_mdz_bundle():
    """Test the MDZ bundle implementation"""
    try:
        from mdz_bundle import MDZBundle, create_mdz_from_markdown_file, extract_mdz_to_markdown
    except ImportError:
        logger.error("MDZ bundle module not found")
        return False

    # Create a test Markdown file
    temp_dir, md_path = create_test_markdown()

    try:
        # Create an MDZ bundle from the test file
        mdz_path = os.path.join(temp_dir, "test.mdz")
        logger.info(f"Creating MDZ bundle: {mdz_path}")
        create_mdz_from_markdown_file(md_path, mdz_path, include_images=True)

        # Check if the MDZ file was created
        if not os.path.exists(mdz_path):
            logger.error(f"MDZ file not created: {mdz_path}")
            return False

        # Extract the MDZ bundle
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        extracted_md_path = os.path.join(extract_dir, "test_extracted.md")
        logger.info(f"Extracting MDZ bundle to: {extracted_md_path}")
        metadata = extract_mdz_to_markdown(mdz_path, extracted_md_path, extract_assets=True)

        # Check if the extracted file exists
        if not os.path.exists(extracted_md_path):
            logger.error(f"Extracted Markdown file not created: {extracted_md_path}")
            return False

        # Check if the metadata was extracted
        if not metadata or not isinstance(metadata, dict):
            logger.error(f"Metadata not extracted: {metadata}")
            return False

        # Check if the title is correct
        if metadata.get("title") != "MDZ Format Test":
            logger.error(f"Incorrect title in metadata: {metadata.get('title')}")
            return False

        # Check if the extracted image exists
        # The image might be in an 'images' subdirectory
        extracted_img_path = os.path.join(os.path.dirname(extracted_md_path), "test_image.png")
        images_dir_path = os.path.join(os.path.dirname(extracted_md_path), "images", "test_image.png")

        if not (os.path.exists(extracted_img_path) or os.path.exists(images_dir_path)):
            logger.error(f"Extracted image not found: {extracted_img_path} or {images_dir_path}")
            return False

        logger.info("MDZ bundle test passed")
        return True

    except Exception as e:
        logger.error(f"Error testing MDZ bundle: {str(e)}")
        return False

    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory: {str(e)}")

def test_mdz_renderer():
    """Test the MDZ renderer implementation"""
    try:
        from mdz_renderer import MDZRenderer
    except ImportError:
        logger.error("MDZ renderer module not found")
        return False

    # Create a test Markdown file
    temp_dir, md_path = create_test_markdown()

    try:
        # Read the test Markdown file
        with open(md_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Create a renderer
        renderer = MDZRenderer()

        # Extract front matter
        markdown_without_front_matter, front_matter = renderer.extract_front_matter(markdown_content)

        # Check if the front matter was extracted
        if not front_matter or not isinstance(front_matter, dict):
            logger.error(f"Front matter not extracted: {front_matter}")
            return False

        # Check if the title is correct
        if front_matter.get("title") != "MDZ Format Test":
            logger.error(f"Incorrect title in front matter: {front_matter.get('title')}")
            return False

        # Extract and render Mermaid diagrams
        mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)

        # Render to HTML
        html_content = renderer.render_to_html(
            markdown_without_front_matter,
            front_matter=front_matter,
            mermaid_diagrams=mermaid_diagrams
        )

        # Check if the HTML content was generated
        if not html_content or not isinstance(html_content, str):
            logger.error(f"HTML content not generated: {html_content}")
            return False

        # Check if the title is in the HTML
        if front_matter.get("title") not in html_content:
            logger.error(f"Title not found in HTML content: {front_matter.get('title')}")
            return False

        # Save the HTML content
        html_path = os.path.join(temp_dir, "test.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML content saved to: {html_path}")
        logger.info("MDZ renderer test passed")
        return True

    except Exception as e:
        logger.error(f"Error testing MDZ renderer: {str(e)}")
        return False

    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory: {str(e)}")

def test_enhanced_markdown_parser():
    """Test the enhanced Markdown parser"""
    try:
        from enhanced_markdown_parser import MarkdownParser
    except ImportError:
        logger.error("Enhanced Markdown parser module not found")
        return False

    # Create a test Markdown file
    temp_dir, md_path = create_test_markdown()

    try:
        # Read the test Markdown file
        with open(md_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Create a parser
        parser = MarkdownParser()

        # Get parser information
        info = parser.get_parser_info()
        logger.info(f"Using {info['parser_type']} {info.get('version', 'unknown version')}")

        # Parse the Markdown content
        html_content = parser.parse(markdown_content)

        # Check if the HTML content was generated
        if not html_content or not isinstance(html_content, str):
            logger.error(f"HTML content not generated: {html_content}")
            return False

        # Save the HTML content
        html_path = os.path.join(temp_dir, "test_enhanced.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML content saved to: {html_path}")
        logger.info("Enhanced Markdown parser test passed")
        return True

    except Exception as e:
        logger.error(f"Error testing enhanced Markdown parser: {str(e)}")
        return False

    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Basic MDZ Format Test Script")
    parser.add_argument("--bundle", action="store_true", help="Test the MDZ bundle implementation")
    parser.add_argument("--renderer", action="store_true", help="Test the MDZ renderer implementation")
    parser.add_argument("--parser", action="store_true", help="Test the enhanced Markdown parser")
    parser.add_argument("--all", action="store_true", help="Test all components")

    args = parser.parse_args()

    # If no arguments are provided, test all components
    if not (args.bundle or args.renderer or args.parser or args.all):
        args.all = True

    # Test the MDZ bundle implementation
    if args.bundle or args.all:
        logger.info("Testing MDZ bundle implementation...")
        if test_mdz_bundle():
            logger.info("MDZ bundle test passed")
        else:
            logger.error("MDZ bundle test failed")

    # Test the MDZ renderer implementation
    if args.renderer or args.all:
        logger.info("Testing MDZ renderer implementation...")
        if test_mdz_renderer():
            logger.info("MDZ renderer test passed")
        else:
            logger.error("MDZ renderer test failed")

    # Test the enhanced Markdown parser
    if args.parser or args.all:
        logger.info("Testing enhanced Markdown parser...")
        if test_enhanced_markdown_parser():
            logger.info("Enhanced Markdown parser test passed")
        else:
            logger.error("Enhanced Markdown parser test failed")

    logger.info("MDZ format tests completed")

if __name__ == "__main__":
    main()
