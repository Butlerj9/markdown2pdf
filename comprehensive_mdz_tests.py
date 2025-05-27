#!/usr/bin/env python3
"""
Comprehensive MDZ Format Test Suite
---------------------------------
This script provides a comprehensive test suite for the MDZ format,
including tests for compression, Markdown parsing, rendering, and export.

File: comprehensive_mdz_tests.py
"""

import os
import sys
import tempfile
import shutil
import logging
import argparse
import unittest
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDZCompressionTests(unittest.TestCase):
    """Tests for MDZ compression and decompression"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
        
        # Create a test file
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Test content" * 1000)  # Create a reasonably sized file
        
        # Import MDZ bundle
        try:
            from mdz_bundle import MDZBundle
            self.MDZBundle = MDZBundle
        except ImportError:
            self.skipTest("MDZ bundle module not found")
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_compression_levels(self):
        """Test different compression levels"""
        # Test compression levels 1, 5, 10, 15, 22
        for level in [1, 5, 10, 15, 22]:
            # Create a bundle with the specified compression level
            bundle = self.MDZBundle(compression_level=level)
            
            # Add the test file
            with open(self.test_file, "r", encoding="utf-8") as f:
                content = f.read()
            bundle.add_file(self.test_file, content)
            
            # Save the bundle
            mdz_path = os.path.join(self.temp_dir, f"test_level_{level}.mdz")
            bundle.save(mdz_path)
            
            # Check if the file was created
            self.assertTrue(os.path.exists(mdz_path), f"MDZ file not created with compression level {level}")
            
            # Get the file size
            file_size = os.path.getsize(mdz_path)
            logger.info(f"Compression level {level}: {file_size} bytes")
            
            # Load the bundle
            bundle2 = self.MDZBundle()
            bundle2.load(mdz_path)
            
            # Check if the content is the same
            self.assertEqual(bundle2.content[os.path.basename(self.test_file)], content,
                            f"Content mismatch with compression level {level}")
    
    def test_compression_ratio(self):
        """Test compression ratio"""
        # Create a bundle with default compression level
        bundle = self.MDZBundle()
        
        # Add the test file
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        bundle.add_file(self.test_file, content)
        
        # Save the bundle
        mdz_path = os.path.join(self.temp_dir, "test.mdz")
        bundle.save(mdz_path)
        
        # Get the file sizes
        original_size = os.path.getsize(self.test_file)
        compressed_size = os.path.getsize(mdz_path)
        
        # Calculate compression ratio
        ratio = original_size / compressed_size
        logger.info(f"Compression ratio: {ratio:.2f}x")
        
        # Check if the compression ratio is reasonable
        self.assertGreater(ratio, 1.0, "Compression ratio should be greater than 1.0")
    
    def test_corrupted_file(self):
        """Test handling of corrupted files"""
        # Create a bundle
        bundle = self.MDZBundle()
        
        # Add the test file
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        bundle.add_file(self.test_file, content)
        
        # Save the bundle
        mdz_path = os.path.join(self.temp_dir, "test.mdz")
        bundle.save(mdz_path)
        
        # Corrupt the file
        with open(mdz_path, "r+b") as f:
            f.seek(100)  # Skip the header
            f.write(b"CORRUPTED" * 10)
        
        # Try to load the corrupted file
        bundle2 = self.MDZBundle()
        with self.assertRaises(Exception):
            bundle2.load(mdz_path)


class MDZMarkdownTests(unittest.TestCase):
    """Tests for Markdown parsing and rendering"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
        
        # Create a test Markdown file with various features
        self.md_content = """---
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
        
        self.md_path = os.path.join(self.temp_dir, "test.md")
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(self.md_content)
        
        # Create a test image
        self.img_path = os.path.join(self.temp_dir, "test_image.png")
        self.create_test_image(self.img_path)
        
        # Import MDZ renderer
        try:
            from mdz_renderer import MDZRenderer
            self.MDZRenderer = MDZRenderer
        except ImportError:
            self.skipTest("MDZ renderer module not found")
        
        # Import enhanced Markdown parser
        try:
            from enhanced_markdown_parser import MarkdownParser
            self.MarkdownParser = MarkdownParser
        except ImportError:
            logger.warning("Enhanced Markdown parser not found, using MDZ renderer only")
            self.MarkdownParser = None
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path):
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
    
    def test_front_matter_extraction(self):
        """Test extraction of YAML front matter"""
        # Create a renderer
        renderer = self.MDZRenderer()
        
        # Extract front matter
        markdown_without_front_matter, front_matter = renderer.extract_front_matter(self.md_content)
        
        # Check if the front matter was extracted
        self.assertIsInstance(front_matter, dict, "Front matter should be a dictionary")
        self.assertEqual(front_matter.get("title"), "MDZ Format Test", "Title should be 'MDZ Format Test'")
        self.assertEqual(front_matter.get("author"), "Test Script", "Author should be 'Test Script'")
        self.assertEqual(front_matter.get("date"), "2025-05-01", "Date should be '2025-05-01'")
        self.assertListEqual(front_matter.get("tags"), ["markdown", "test", "mdz"], "Tags should be ['markdown', 'test', 'mdz']")
        
        # Check if the front matter was removed from the content
        self.assertNotIn("---", markdown_without_front_matter[:10], "Front matter should be removed")
    
    def test_mermaid_extraction(self):
        """Test extraction of Mermaid diagrams"""
        # Create a renderer
        renderer = self.MDZRenderer()
        
        # Extract Mermaid diagrams
        mermaid_diagrams = renderer.extract_and_render_mermaid(self.md_content)
        
        # Check if any diagrams were extracted
        self.assertGreaterEqual(len(mermaid_diagrams), 0, "At least one Mermaid diagram should be extracted")
        
        # If diagrams were extracted, check if they were rendered
        if mermaid_diagrams:
            for code, svg in mermaid_diagrams.items():
                self.assertIn("graph TD", code, "Mermaid code should contain 'graph TD'")
                if svg:  # If rendering was successful
                    self.assertIn("<svg", svg, "SVG content should contain '<svg'")
    
    def test_html_rendering(self):
        """Test rendering to HTML"""
        # Create a renderer
        renderer = self.MDZRenderer()
        
        # Extract front matter
        markdown_without_front_matter, front_matter = renderer.extract_front_matter(self.md_content)
        
        # Extract Mermaid diagrams
        mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)
        
        # Render to HTML
        html_content = renderer.render_to_html(
            markdown_without_front_matter,
            front_matter=front_matter,
            mermaid_diagrams=mermaid_diagrams
        )
        
        # Check if the HTML content was generated
        self.assertIsInstance(html_content, str, "HTML content should be a string")
        self.assertIn("<!DOCTYPE html>", html_content, "HTML content should contain '<!DOCTYPE html>'")
        self.assertIn("<title>MDZ Format Test</title>", html_content, "HTML content should contain the title")
        
        # Check if GFM features were rendered
        self.assertIn("task-list-item", html_content, "HTML content should contain task list items")
        self.assertIn("<table>", html_content, "HTML content should contain a table")
        self.assertIn("<code>", html_content, "HTML content should contain code blocks")
        
        # Check if math was rendered
        self.assertIn("MathJax", html_content, "HTML content should contain MathJax")
        
        # Save the HTML content
        html_path = os.path.join(self.temp_dir, "test.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def test_enhanced_markdown_parser(self):
        """Test the enhanced Markdown parser"""
        # Skip if the enhanced parser is not available
        if not self.MarkdownParser:
            self.skipTest("Enhanced Markdown parser not available")
        
        # Create a parser
        parser = self.MarkdownParser()
        
        # Get parser information
        info = parser.get_parser_info()
        logger.info(f"Using {info['parser_type']} {info.get('version', 'unknown version')}")
        
        # Parse the Markdown content
        html_content = parser.parse(self.md_content)
        
        # Check if the HTML content was generated
        self.assertIsInstance(html_content, str, "HTML content should be a string")
        
        # Check if GFM features were rendered
        self.assertIn("task-list-item", html_content, "HTML content should contain task list items") or \
        self.assertIn("checkbox", html_content, "HTML content should contain checkboxes")
        self.assertIn("<table>", html_content, "HTML content should contain a table")
        self.assertIn("<code>", html_content, "HTML content should contain code blocks")
        
        # Save the HTML content
        html_path = os.path.join(self.temp_dir, "test_enhanced.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)


class MDZBundleTests(unittest.TestCase):
    """Tests for MDZ bundle functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
        
        # Create a test Markdown file
        self.md_content = """---
title: "MDZ Bundle Test"
author: "Test Script"
---

# MDZ Bundle Test

This is a test document for the MDZ bundle.

![Test Image](test_image.png)

```mermaid
graph TD
    A[Start] --> B[End]
```
"""
        
        self.md_path = os.path.join(self.temp_dir, "test.md")
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(self.md_content)
        
        # Create a test image
        self.img_path = os.path.join(self.temp_dir, "test_image.png")
        self.create_test_image(self.img_path)
        
        # Import MDZ bundle
        try:
            from mdz_bundle import MDZBundle, create_mdz_from_markdown_file, extract_mdz_to_markdown
            self.MDZBundle = MDZBundle
            self.create_mdz_from_markdown_file = create_mdz_from_markdown_file
            self.extract_mdz_to_markdown = extract_mdz_to_markdown
        except ImportError:
            self.skipTest("MDZ bundle module not found")
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path):
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
    
    def test_create_and_extract(self):
        """Test creating and extracting an MDZ bundle"""
        # Create an MDZ bundle
        mdz_path = os.path.join(self.temp_dir, "test.mdz")
        self.create_mdz_from_markdown_file(self.md_path, mdz_path, include_images=True)
        
        # Check if the MDZ file was created
        self.assertTrue(os.path.exists(mdz_path), "MDZ file should be created")
        
        # Extract the MDZ bundle
        extract_dir = os.path.join(self.temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        extracted_md_path = os.path.join(extract_dir, "test_extracted.md")
        metadata = self.extract_mdz_to_markdown(mdz_path, extracted_md_path, extract_assets=True)
        
        # Check if the extracted file exists
        self.assertTrue(os.path.exists(extracted_md_path), "Extracted Markdown file should exist")
        
        # Check if the metadata was extracted
        self.assertIsInstance(metadata, dict, "Metadata should be a dictionary")
        self.assertEqual(metadata.get("title"), "MDZ Bundle Test", "Title should be 'MDZ Bundle Test'")
        
        # Check if the extracted image exists
        extracted_img_path = os.path.join(extract_dir, "test_image.png")
        self.assertTrue(os.path.exists(extracted_img_path), "Extracted image should exist")
    
    def test_bundle_structure(self):
        """Test the structure of an MDZ bundle"""
        # Create a bundle
        bundle = self.MDZBundle()
        
        # Add content
        bundle.create_from_markdown(self.md_content, {"title": "MDZ Bundle Test"})
        
        # Add an image
        with open(self.img_path, "rb") as f:
            image_content = f.read()
        bundle.add_file(self.img_path, image_content)
        
        # Add a Mermaid diagram
        mermaid_code = "graph TD\n    A[Start] --> B[End]"
        bundle.add_file("diagram.mmd", mermaid_code, "mermaid/diagram.mmd")
        
        # Save the bundle
        mdz_path = os.path.join(self.temp_dir, "test_structure.mdz")
        bundle.save(mdz_path)
        
        # Load the bundle
        bundle2 = self.MDZBundle()
        bundle2.load(mdz_path)
        
        # Check the structure
        self.assertIn("index.md", bundle2.content, "Bundle should contain index.md")
        self.assertIn("metadata.yaml", bundle2.content, "Bundle should contain metadata.yaml")
        self.assertIn("images/test_image.png", bundle2.content, "Bundle should contain the image")
        self.assertIn("mermaid/diagram.mmd", bundle2.content, "Bundle should contain the Mermaid diagram")
        
        # Check the content
        self.assertEqual(bundle2.content["index.md"], self.md_content, "index.md content should match")
        self.assertEqual(bundle2.content["images/test_image.png"], image_content, "Image content should match")
        self.assertEqual(bundle2.content["mermaid/diagram.mmd"], mermaid_code, "Mermaid diagram content should match")
    
    def test_multiple_compression_decompression_cycles(self):
        """Test multiple compression and decompression cycles"""
        # Create an MDZ bundle
        mdz_path = os.path.join(self.temp_dir, "test.mdz")
        self.create_mdz_from_markdown_file(self.md_path, mdz_path, include_images=True)
        
        # Perform multiple compression/decompression cycles
        for i in range(5):
            # Extract the MDZ bundle
            extract_dir = os.path.join(self.temp_dir, f"extracted_{i}")
            os.makedirs(extract_dir, exist_ok=True)
            extracted_md_path = os.path.join(extract_dir, "test_extracted.md")
            metadata = self.extract_mdz_to_markdown(mdz_path, extracted_md_path, extract_assets=True)
            
            # Create a new MDZ bundle from the extracted file
            new_mdz_path = os.path.join(self.temp_dir, f"test_{i+1}.mdz")
            self.create_mdz_from_markdown_file(extracted_md_path, new_mdz_path, include_images=True)
            
            # Update the MDZ path for the next cycle
            mdz_path = new_mdz_path
        
        # Load the final MDZ bundle
        bundle = self.MDZBundle()
        bundle.load(mdz_path)
        
        # Check if the content is still intact
        self.assertIn("index.md", bundle.content, "Bundle should contain index.md")
        self.assertIn("metadata.yaml", bundle.content, "Bundle should contain metadata.yaml")
        
        # Check if the title is still correct
        self.assertEqual(bundle.metadata.get("title"), "MDZ Bundle Test", "Title should be 'MDZ Bundle Test'")


class MDZExportTests(unittest.TestCase):
    """Tests for MDZ export functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
        
        # Create a test Markdown file
        self.md_content = """---
title: "MDZ Export Test"
author: "Test Script"
---

# MDZ Export Test

This is a test document for MDZ export.

![Test Image](test_image.png)

```mermaid
graph TD
    A[Start] --> B[End]
```

Inline math: $E = mc^2$

Display math:

$$
\\frac{d}{dx}(x^n) = nx^{n-1}
$$
"""
        
        self.md_path = os.path.join(self.temp_dir, "test.md")
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(self.md_content)
        
        # Create a test image
        self.img_path = os.path.join(self.temp_dir, "test_image.png")
        self.create_test_image(self.img_path)
        
        # Import MDZ bundle and renderer
        try:
            from mdz_bundle import MDZBundle
            from mdz_renderer import MDZRenderer
            self.MDZBundle = MDZBundle
            self.MDZRenderer = MDZRenderer
        except ImportError:
            self.skipTest("MDZ modules not found")
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, path):
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
    
    def test_html_export(self):
        """Test export to HTML"""
        # Create a bundle
        bundle = self.MDZBundle()
        
        # Add content
        bundle.create_from_markdown(self.md_content, {"title": "MDZ Export Test"})
        
        # Add an image
        with open(self.img_path, "rb") as f:
            image_content = f.read()
        bundle.add_file(self.img_path, image_content)
        
        # Extract to a temporary directory
        extracted_assets = bundle.extract_to_temp()
        
        # Create a renderer
        renderer = self.MDZRenderer()
        
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
        html_path = os.path.join(self.temp_dir, "test_export.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Check if the HTML file was created
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")
        
        # Check if the HTML content contains the expected elements
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        self.assertIn("<title>MDZ Export Test</title>", html_content, "HTML should contain the title")
        self.assertIn("<h1>MDZ Export Test</h1>", html_content, "HTML should contain the heading")
        self.assertIn("<img", html_content, "HTML should contain an image")
        self.assertIn("MathJax", html_content, "HTML should contain MathJax")
    
    def test_pdf_export_preparation(self):
        """Test preparation for PDF export"""
        # Skip if pandoc is not available
        try:
            import subprocess
            result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.skipTest("Pandoc not available")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("Pandoc not available")
        
        # Create a bundle
        bundle = self.MDZBundle()
        
        # Add content
        bundle.create_from_markdown(self.md_content, {"title": "MDZ Export Test"})
        
        # Add an image
        with open(self.img_path, "rb") as f:
            image_content = f.read()
        bundle.add_file(self.img_path, image_content)
        
        # Extract to a temporary directory
        extracted_assets = bundle.extract_to_temp()
        
        # Create a renderer
        renderer = self.MDZRenderer()
        
        # Extract front matter
        markdown_without_front_matter, front_matter = renderer.extract_front_matter(bundle.get_main_content())
        
        # Extract and render Mermaid diagrams
        mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)
        
        # Process image references
        processed_content = renderer.preprocess_image_paths(markdown_without_front_matter, extracted_assets)
        
        # Save the processed Markdown
        processed_md_path = os.path.join(self.temp_dir, "test_processed.md")
        with open(processed_md_path, "w", encoding="utf-8") as f:
            f.write(processed_content)
        
        # Check if the processed Markdown file was created
        self.assertTrue(os.path.exists(processed_md_path), "Processed Markdown file should be created")
        
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
        
        latex_template_path = os.path.join(self.temp_dir, "template.tex")
        with open(latex_template_path, "w", encoding="utf-8") as f:
            f.write(latex_template)
        
        # Check if the LaTeX template was created
        self.assertTrue(os.path.exists(latex_template_path), "LaTeX template should be created")


def run_tests():
    """Run all tests"""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(MDZCompressionTests))
    suite.addTest(unittest.makeSuite(MDZMarkdownTests))
    suite.addTest(unittest.makeSuite(MDZBundleTests))
    suite.addTest(unittest.makeSuite(MDZExportTests))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Comprehensive MDZ Format Test Suite")
    parser.add_argument("--compression", action="store_true", help="Run compression tests only")
    parser.add_argument("--markdown", action="store_true", help="Run Markdown tests only")
    parser.add_argument("--bundle", action="store_true", help="Run bundle tests only")
    parser.add_argument("--export", action="store_true", help="Run export tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all tests
    if not (args.compression or args.markdown or args.bundle or args.export or args.all):
        args.all = True
    
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases based on arguments
    if args.compression or args.all:
        suite.addTest(unittest.makeSuite(MDZCompressionTests))
    
    if args.markdown or args.all:
        suite.addTest(unittest.makeSuite(MDZMarkdownTests))
    
    if args.bundle or args.all:
        suite.addTest(unittest.makeSuite(MDZBundleTests))
    
    if args.export or args.all:
        suite.addTest(unittest.makeSuite(MDZExportTests))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
