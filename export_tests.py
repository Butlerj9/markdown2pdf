#!/usr/bin/env python3
"""
Export Tests for Markdown to PDF Converter
-----------------------------------------
Provides detailed testing of export functionality.
"""

import os
import sys
import tempfile
import unittest
import logging
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

logger = get_logger()

class ExportTestCase(unittest.TestCase):
    """Test case for export functionality"""

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

        # Sample markdown content for testing
        self.sample_markdown = """# Export Test Document

This is a test document for the Markdown to PDF converter export functionality.

## Features to Test

- PDF Export with different engines
- DOCX Export
- HTML Export
- EPUB Export
- Export with different settings

### Code Block

```python
def test_export():
    print("Testing export functionality")
```

## Table

| Format | Status |
|--------|--------|
| PDF    | Testing |
| DOCX   | Testing |
| HTML   | Testing |
| EPUB   | Testing |

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

    def test_pdf_export_all_engines(self):
        """Test PDF export with all available engines"""
        # Get available engines
        engines = self.window.found_engines.keys()

        if not engines:
            self.skipTest("No PDF engines available")

        for engine in engines:
            # Set the engine
            self.window.update_preferred_engine(engine)

            # Define output file path
            output_file = os.path.join(self.output_dir, f"test_export_{engine}.pdf")

            # Export to PDF
            result = self.window.export_to_pdf(output_file)

            # Check if export was successful
            self.assertTrue(result, f"PDF export with engine {engine} failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"PDF file with engine {engine} was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"PDF file with engine {engine} is empty")

    def test_pdf_export_with_mermaid(self):
        """Test PDF export with Mermaid diagrams"""
        # Add Mermaid diagram to the markdown
        mermaid_markdown = self.sample_markdown + """
## Mermaid Diagram

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> A
```
"""
        # Set the markdown with Mermaid diagram
        self.window.markdown_editor.setPlainText(mermaid_markdown)

        # Update the preview
        self.window.update_preview()

        # Process events to ensure UI updates
        QApplication.processEvents()

        # Get available engines
        engines = self.window.found_engines.keys()

        if not engines:
            self.skipTest("No PDF engines available")

        for engine in engines:
            # Set the engine
            self.window.update_preferred_engine(engine)

            # Define output file path
            output_file = os.path.join(self.output_dir, f"test_export_mermaid_{engine}.pdf")

            # Export to PDF
            result = self.window.export_to_pdf(output_file)

            # Check if export was successful
            self.assertTrue(result, f"PDF export with Mermaid diagram using engine {engine} failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"PDF file with Mermaid diagram using engine {engine} was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"PDF file with Mermaid diagram using engine {engine} is empty")

    def test_docx_export_with_settings(self):
        """Test DOCX export with different settings"""
        # Test with different page sizes
        page_sizes = ["A4", "Letter", "A5"]

        for size in page_sizes:
            # Set page size
            self.window.page_size_combo.setCurrentText(size)

            # Define output file path
            output_file = os.path.join(self.output_dir, f"test_export_docx_{size}.docx")

            # Export to DOCX
            result = self.window.export_to_docx(output_file)

            # Check if export was successful
            self.assertTrue(result, f"DOCX export with page size {size} failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"DOCX file with page size {size} was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"DOCX file with page size {size} is empty")

    def test_html_export_with_settings(self):
        """Test HTML export with different settings"""
        # Test with different font settings
        test_fonts = ["Arial", "Times New Roman", "Courier New"]

        for font in test_fonts:
            # Set body font
            self.window.body_font_family.setCurrentText(font)

            # Define output file path
            output_file = os.path.join(self.output_dir, f"test_export_html_{font.replace(' ', '_')}.html")

            # Export to HTML
            result = self.window.export_to_html(output_file)

            # Check if export was successful
            self.assertTrue(result, f"HTML export with font {font} failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"HTML file with font {font} was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"HTML file with font {font} is empty")

            # Check if font is in the HTML
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(font.replace(' ', ''), content, f"HTML file does not contain font {font}")

    def test_epub_export_with_toc(self):
        """Test EPUB export with table of contents"""
        # Enable table of contents
        self.window.toc_include.setChecked(True)
        self.window.toc_depth.setValue(3)
        self.window.toc_title.setText("Contents")

        # Process events to ensure UI updates
        QApplication.processEvents()

        # Define output file path
        output_file = os.path.join(self.output_dir, "test_export_epub_toc.epub")

        try:
            # Export to EPUB
            result = self.window.export_to_epub(output_file)

            # Check if export was successful
            self.assertTrue(result, "EPUB export with TOC failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), "EPUB file with TOC was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, "EPUB file with TOC is empty")
        except Exception as e:
            self.fail(f"EPUB export failed with exception: {str(e)}")

    def test_export_with_page_breaks(self):
        """Test export with explicit page breaks"""
        # Create markdown with page breaks
        page_break_markdown = """# Page 1

This is content on page 1.

<!-- PAGE_BREAK -->

# Page 2

This is content on page 2.

<!-- PAGE_BREAK -->

# Page 3

This is content on page 3.
"""
        # Set the markdown with page breaks
        self.window.markdown_editor.setPlainText(page_break_markdown)

        # Update the preview
        self.window.update_preview()

        # Process events to ensure UI updates
        QApplication.processEvents()

        # Export to PDF
        output_file = os.path.join(self.output_dir, "test_export_page_breaks.pdf")
        result = self.window.export_to_pdf(output_file)

        # Check if export was successful
        self.assertTrue(result, "PDF export with page breaks failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "PDF file with page breaks was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "PDF file with page breaks is empty")

    def test_export_with_heading_numbering(self):
        """Test export with heading numbering"""
        # Enable heading numbering
        self.window.heading_numbering.setChecked(True)
        self.window.numbering_start.setCurrentIndex(0)  # H1

        # Export to PDF
        output_file = os.path.join(self.output_dir, "test_export_heading_numbering.pdf")
        result = self.window.export_to_pdf(output_file)

        # Check if export was successful
        self.assertTrue(result, "PDF export with heading numbering failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "PDF file with heading numbering was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "PDF file with heading numbering is empty")

    def test_export_with_custom_css(self):
        """Test export with custom CSS"""
        # Add custom CSS
        custom_css = """
body {
    background-color: #f0f0f0;
    color: #333333;
}

h1 {
    color: #0066cc;
    border-bottom: 2px solid #0066cc;
}

table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid #dddddd;
    padding: 8px;
}

th {
    background-color: #f2f2f2;
}
"""
        # Set custom CSS
        self.window.document_settings["custom_css"] = custom_css

        # Export to HTML
        output_file = os.path.join(self.output_dir, "test_export_custom_css.html")
        result = self.window.export_to_html(output_file)

        # Check if export was successful
        self.assertTrue(result, "HTML export with custom CSS failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "HTML file with custom CSS was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "HTML file with custom CSS is empty")

        # Check if custom CSS is in the HTML
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("background-color: #f0f0f0", content, "HTML file does not contain custom CSS")

def run_export_tests():
    """Run export tests and return results"""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(ExportTestCase))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

if __name__ == "__main__":
    # Run tests
    unittest.main()
