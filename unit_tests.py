#!/usr/bin/env python3
"""
Unit Testing Framework for Markdown to PDF Converter
---------------------------------------------------
Provides automated unit testing of core functionality.
"""

import os
import sys
import tempfile
import unittest
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

logger = get_logger()

class TestResult:
    """Class to store test results"""
    def __init__(self, name, success, message=""):
        self.name = name
        self.success = success
        self.message = message
        self.timestamp = None  # Can be set later if needed

    def __str__(self):
        return f"{self.name}: {'✓' if self.success else '✗'} - {self.message}"

class MarkdownConverterTestCase(unittest.TestCase):
    """Base test case for Markdown to PDF Converter"""
    
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
        self.sample_markdown = """# Test Document

This is a test document for the Markdown to PDF converter.

## Features to Test

- PDF Export
- DOCX Export
- HTML Export
- EPUB Export
- Settings Panel

### Code Block

```python
def hello_world():
    print("Hello, World!")
```

## Table

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

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

class ExportTests(MarkdownConverterTestCase):
    """Tests for export functionality"""
    
    def test_pdf_export(self):
        """Test PDF export functionality"""
        # Define output file path
        output_file = os.path.join(self.output_dir, "test_export.pdf")
        
        # Export to PDF
        result = self.window.export_to_pdf(output_file)
        
        # Check if export was successful
        self.assertTrue(result, "PDF export failed")
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "PDF file was not created")
        
        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "PDF file is empty")
    
    def test_docx_export(self):
        """Test DOCX export functionality"""
        # Define output file path
        output_file = os.path.join(self.output_dir, "test_export.docx")
        
        # Export to DOCX
        result = self.window.export_to_docx(output_file)
        
        # Check if export was successful
        self.assertTrue(result, "DOCX export failed")
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "DOCX file was not created")
        
        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "DOCX file is empty")
    
    def test_html_export(self):
        """Test HTML export functionality"""
        # Define output file path
        output_file = os.path.join(self.output_dir, "test_export.html")
        
        # Export to HTML
        result = self.window.export_to_html(output_file)
        
        # Check if export was successful
        self.assertTrue(result, "HTML export failed")
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "HTML file was not created")
        
        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "HTML file is empty")
        
        # Basic content check
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("<h1", content, "HTML file does not contain h1 tag")
            self.assertIn("<table", content, "HTML file does not contain table tag")
            self.assertIn("<code", content, "HTML file does not contain code tag")
    
    def test_epub_export(self):
        """Test EPUB export functionality"""
        # Define output file path
        output_file = os.path.join(self.output_dir, "test_export.epub")
        
        # Export to EPUB
        result = self.window.export_to_epub(output_file)
        
        # Check if export was successful
        self.assertTrue(result, "EPUB export failed")
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "EPUB file was not created")
        
        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "EPUB file is empty")
    
    def test_format_detection(self):
        """Test format detection from file extension"""
        # Test PDF detection
        output_file = os.path.join(self.output_dir, "test_export.pdf")
        self.assertEqual(self.detect_format(output_file), "pdf", "Failed to detect PDF format")
        
        # Test DOCX detection
        output_file = os.path.join(self.output_dir, "test_export.docx")
        self.assertEqual(self.detect_format(output_file), "docx", "Failed to detect DOCX format")
        
        # Test HTML detection
        output_file = os.path.join(self.output_dir, "test_export.html")
        self.assertEqual(self.detect_format(output_file), "html", "Failed to detect HTML format")
        
        # Test EPUB detection
        output_file = os.path.join(self.output_dir, "test_export.epub")
        self.assertEqual(self.detect_format(output_file), "epub", "Failed to detect EPUB format")
        
        # Test unknown extension
        output_file = os.path.join(self.output_dir, "test_export.xyz")
        self.assertEqual(self.detect_format(output_file), "pdf", "Did not default to PDF for unknown format")
    
    def detect_format(self, output_file):
        """Helper method to detect format from file extension"""
        ext = os.path.splitext(output_file)[1].lower()
        if ext in ['.pdf', '.docx', '.html', '.epub']:
            return ext[1:]  # Remove the dot
        return "pdf"  # Default to PDF

class SettingsTests(MarkdownConverterTestCase):
    """Tests for settings functionality"""
    
    def test_page_size_setting(self):
        """Test page size setting"""
        # Get original page size
        original_size = self.window.document_settings["page"]["size"]
        
        # Change page size to A5
        self.window.page_size_combo.setCurrentText("A5")
        
        # Check if setting was updated
        self.assertEqual(self.window.document_settings["page"]["size"], "A5", 
                         "Page size setting was not updated")
        
        # Change page size back to original
        self.window.page_size_combo.setCurrentText(original_size)
        
        # Check if setting was restored
        self.assertEqual(self.window.document_settings["page"]["size"], original_size, 
                         "Page size setting was not restored")
    
    def test_orientation_setting(self):
        """Test orientation setting"""
        # Get original orientation
        original_orientation = self.window.document_settings["page"]["orientation"]
        
        # Change orientation to Landscape if it's Portrait, or vice versa
        new_orientation = "Landscape" if original_orientation.lower() == "portrait" else "Portrait"
        self.window.orientation_combo.setCurrentText(new_orientation)
        
        # Check if setting was updated
        self.assertEqual(self.window.document_settings["page"]["orientation"].lower(), 
                         new_orientation.lower(), 
                         "Orientation setting was not updated")
        
        # Change orientation back to original
        self.window.orientation_combo.setCurrentText(original_orientation)
        
        # Check if setting was restored
        self.assertEqual(self.window.document_settings["page"]["orientation"].lower(), 
                         original_orientation.lower(), 
                         "Orientation setting was not restored")
    
    def test_margin_settings(self):
        """Test margin settings"""
        # Get original margins
        original_margins = self.window.document_settings["page"]["margins"].copy()
        
        # Change margins to 30
        test_value = 30
        self.window.margin_top.setValue(test_value)
        self.window.margin_right.setValue(test_value)
        self.window.margin_bottom.setValue(test_value)
        self.window.margin_left.setValue(test_value)
        
        # Check if settings were updated
        margins = self.window.document_settings["page"]["margins"]
        self.assertEqual(margins["top"], test_value, "Top margin setting was not updated")
        self.assertEqual(margins["right"], test_value, "Right margin setting was not updated")
        self.assertEqual(margins["bottom"], test_value, "Bottom margin setting was not updated")
        self.assertEqual(margins["left"], test_value, "Left margin setting was not updated")
        
        # Restore original margins
        self.window.margin_top.setValue(original_margins["top"])
        self.window.margin_right.setValue(original_margins["right"])
        self.window.margin_bottom.setValue(original_margins["bottom"])
        self.window.margin_left.setValue(original_margins["left"])
        
        # Check if settings were restored
        margins = self.window.document_settings["page"]["margins"]
        self.assertEqual(margins["top"], original_margins["top"], "Top margin setting was not restored")
        self.assertEqual(margins["right"], original_margins["right"], "Right margin setting was not restored")
        self.assertEqual(margins["bottom"], original_margins["bottom"], "Bottom margin setting was not restored")
        self.assertEqual(margins["left"], original_margins["left"], "Left margin setting was not restored")
    
    def test_font_settings(self):
        """Test font settings"""
        # Get original font settings
        original_font = self.window.document_settings["fonts"]["body"]["font_family"]
        original_size = self.window.document_settings["fonts"]["body"]["font_size"]
        
        # Change font family
        test_font = "Arial" if original_font != "Arial" else "Times New Roman"
        self.window.body_font_family.setCurrentText(test_font)
        
        # Check if font family was updated
        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_family"], test_font, 
                         "Font family setting was not updated")
        
        # Change font size
        test_size = 14 if original_size != 14 else 12
        self.window.body_font_size.setValue(test_size)
        
        # Check if font size was updated
        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_size"], test_size, 
                         "Font size setting was not updated")
        
        # Restore original settings
        self.window.body_font_family.setCurrentText(original_font)
        self.window.body_font_size.setValue(original_size)
        
        # Check if settings were restored
        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_family"], original_font, 
                         "Font family setting was not restored")
        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_size"], original_size, 
                         "Font size setting was not restored")
    
    def test_heading_settings(self):
        """Test heading settings"""
        # Get original heading settings
        original_font = self.window.document_settings["fonts"]["headings"]["h1"]["font_family"]
        original_size = self.window.document_settings["fonts"]["headings"]["h1"]["font_size"]
        
        # Change heading font family
        test_font = "Arial" if original_font != "Arial" else "Times New Roman"
        self.window.h1_font_family.setCurrentText(test_font)
        
        # Check if heading font family was updated
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_family"], test_font, 
                         "Heading font family setting was not updated")
        
        # Change heading font size
        test_size = 24 if original_size != 24 else 20
        self.window.h1_font_size.setValue(test_size)
        
        # Check if heading font size was updated
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_size"], test_size, 
                         "Heading font size setting was not updated")
        
        # Restore original settings
        self.window.h1_font_family.setCurrentText(original_font)
        self.window.h1_font_size.setValue(original_size)
        
        # Check if settings were restored
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_family"], original_font, 
                         "Heading font family setting was not restored")
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_size"], original_size, 
                         "Heading font size setting was not restored")
    
    def test_settings_persistence(self):
        """Test that settings are saved and loaded correctly"""
        # Change a setting
        test_value = 30
        self.window.margin_top.setValue(test_value)
        
        # Save settings
        self.window.save_settings()
        
        # Create a new window instance
        new_window = AdvancedMarkdownToPDF()
        
        # Check if setting was loaded correctly
        self.assertEqual(new_window.document_settings["page"]["margins"]["top"], test_value, 
                         "Setting was not persisted between instances")
        
        # Close the new window
        new_window.close()
        QApplication.processEvents()

class ExportWithSettingsTests(MarkdownConverterTestCase):
    """Tests for export with different settings"""
    
    def test_export_with_different_page_sizes(self):
        """Test export with different page sizes"""
        # List of page sizes to test
        page_sizes = ["A4", "Letter", "A5"]
        
        for size in page_sizes:
            # Set page size
            self.window.page_size_combo.setCurrentText(size)
            
            # Export to PDF
            output_file = os.path.join(self.output_dir, f"test_export_{size}.pdf")
            result = self.window.export_to_pdf(output_file)
            
            # Check if export was successful
            self.assertTrue(result, f"PDF export with page size {size} failed")
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"PDF file with page size {size} was not created")
            
            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"PDF file with page size {size} is empty")
    
    def test_export_with_different_orientations(self):
        """Test export with different orientations"""
        # List of orientations to test
        orientations = ["Portrait", "Landscape"]
        
        for orientation in orientations:
            # Set orientation
            self.window.orientation_combo.setCurrentText(orientation)
            
            # Export to PDF
            output_file = os.path.join(self.output_dir, f"test_export_{orientation}.pdf")
            result = self.window.export_to_pdf(output_file)
            
            # Check if export was successful
            self.assertTrue(result, f"PDF export with orientation {orientation} failed")
            
            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"PDF file with orientation {orientation} was not created")
            
            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"PDF file with orientation {orientation} is empty")

def run_tests():
    """Run all tests and return results"""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(ExportTests))
    suite.addTest(unittest.makeSuite(SettingsTests))
    suite.addTest(unittest.makeSuite(ExportWithSettingsTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Convert unittest results to our TestResult format
    test_results = []
    for test in result.failures + result.errors:
        test_name = test[0].id().split('.')[-1]
        test_results.append(TestResult(test_name, False, str(test[1])))
    
    for test in result.successes if hasattr(result, 'successes') else []:
        test_name = test.id().split('.')[-1]
        test_results.append(TestResult(test_name, True, "Test passed"))
    
    return test_results

if __name__ == "__main__":
    # Run tests
    unittest.main()
