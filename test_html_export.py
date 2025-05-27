#!/usr/bin/env python3
"""
Test HTML Export Functionality
-----------------------------
Tests the HTML export functionality of the Markdown to PDF Converter.
"""

import os
import sys
import tempfile
import unittest
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

logger = get_logger()

class HTMLExportTest(unittest.TestCase):
    """Test HTML export functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests"""
        # Create QApplication if it doesn't exist
        cls.app = QApplication.instance() or QApplication(sys.argv)

        # Create a temporary directory for test outputs
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = cls.temp_dir.name

        logger.info(f"Test output directory: {cls.output_dir}")

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Clean up temporary directory
        cls.temp_dir.cleanup()

    def setUp(self):
        """Set up before each test"""
        # Create a fresh instance of the application
        self.window = AdvancedMarkdownToPDF()

        # Sample markdown content
        self.sample_markdown = """# HTML Export Test

This is a test document for HTML export.

## Features

- GitHub Flavored Markdown
- YAML front matter
- Mermaid diagrams
- SVG embedding
- LaTeX math

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

## Math Example

$E = mc^2$

## Mermaid Example

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```
"""

        # Set the sample markdown in the editor
        self.window.markdown_editor.setPlainText(self.sample_markdown)

        # Update the preview
        self.window.update_preview()

        # Process events to ensure UI updates
        QApplication.processEvents()

    def tearDown(self):
        """Clean up after each test"""
        # Close the window
        self.window.close()

        # Process events to ensure window closes
        QApplication.processEvents()

    def test_html_export(self):
        """Test HTML export functionality"""
        # Export to HTML
        output_file = os.path.join(self.output_dir, "test_export.html")
        result = self.window._export_to_html(output_file)

        # Check if export was successful
        self.assertTrue(result, "HTML export failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "HTML file was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "HTML file is empty")

        # Check file content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Check for HTML structure
            self.assertIn("<!DOCTYPE html>", content, "HTML file does not have DOCTYPE")
            self.assertIn("<html", content, "HTML file does not have html tag")
            self.assertIn("<head", content, "HTML file does not have head tag")
            self.assertIn("<body", content, "HTML file does not have body tag")

            # Check for content
            self.assertIn("HTML Export Test", content, "HTML file does not contain title")
            self.assertIn("GitHub Flavored Markdown", content, "HTML file does not contain expected content")

            # Check for code block
            self.assertIn("<pre", content, "HTML file does not have pre tag for code block")
            # The code might be formatted differently in the HTML output
            self.assertTrue(
                "def hello_world" in content or
                "def</span> <span" in content or
                "def</span><span" in content or
                "<span class=\"kw\">def</span>" in content,
                "HTML file does not contain code example"
            )

            # Check for math
            self.assertTrue(
                "mc^2" in content or
                "mc<sup>2</sup>" in content or
                "<em>m</em><em>c</em><sup>2</sup>" in content,
                "HTML file does not contain math example"
            )

            # Check for Mermaid
            self.assertIn("mermaid", content.lower(), "HTML file does not contain mermaid example")

    def test_html_export_with_settings(self):
        """Test HTML export with different settings"""
        # Set custom settings
        self.window.document_settings["fonts"]["body"]["family"] = "Arial"
        self.window.document_settings["fonts"]["body"]["size"] = 14
        self.window.document_settings["colors"]["text"] = "#333333"
        self.window.document_settings["colors"]["background"] = "#f5f5f5"

        # Export to HTML
        output_file = os.path.join(self.output_dir, "test_export_with_settings.html")
        result = self.window._export_to_html(output_file)

        # Check if export was successful
        self.assertTrue(result, "HTML export with settings failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "HTML file with settings was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "HTML file with settings is empty")

        # Check file content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Check for custom settings
            self.assertIn("Arial", content, "HTML file does not contain custom font family")
            self.assertIn("#333333", content, "HTML file does not contain custom text color")
            self.assertIn("#f5f5f5", content, "HTML file does not contain custom background color")

def run_tests():
    """Run all tests"""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add test cases
    for name in dir(HTMLExportTest):
        if name.startswith('test_'):
            suite.addTest(HTMLExportTest(name))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success if all tests passed
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run tests
    success = run_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
