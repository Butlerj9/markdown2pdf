#!/usr/bin/env python3
"""
Unit Testing Framework for Markdown to PDF Converter
---------------------------------------------------
Provides automated unit testing of core functionality.
"""

import os
import sys
import json
import tempfile
import unittest
import logging
import argparse
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

# Try to import content processors
try:
    from content_processors.processor_registry import ProcessorRegistry
    from content_processors.base_processor import ContentProcessor
    from content_processors.mermaid_processor import MermaidContentProcessor
    from content_processors.math_processor import MathContentProcessor
    from content_processors.image_processor import ImageContentProcessor
    from content_processors.code_processor import CodeBlockProcessor
    CONTENT_PROCESSORS_AVAILABLE = True
except ImportError:
    CONTENT_PROCESSORS_AVAILABLE = False

# Try to import MDZ functionality
try:
    from mdz_export import MDZExporter, create_mdz_file, extract_mdz_file
    MDZ_AVAILABLE = True
except ImportError:
    MDZ_AVAILABLE = False

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
        result = self.window._export_to_pdf(output_file)

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
        result = self.window._export_to_docx(output_file)

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
        result = self.window._export_to_html(output_file)

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
        result = self.window._export_to_epub(output_file)

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

        # Process events to ensure the setting is updated
        QApplication.processEvents()

        # Wait for settings to be saved
        time.sleep(1)

        # Force sync the settings to disk
        self.window.settings.sync()

        # Process events again
        QApplication.processEvents()

        # Check if setting was updated
        self.assertEqual(self.window.document_settings["page"]["orientation"].lower(),
                         new_orientation.lower(),
                         "Orientation setting was not updated")

        # Change orientation back to original
        self.window.orientation_combo.setCurrentText(original_orientation)

        # Process events to ensure the setting is updated
        QApplication.processEvents()

        # Wait for settings to be saved
        time.sleep(1)

        # Force sync the settings to disk
        self.window.settings.sync()

        # Process events again
        QApplication.processEvents()

        # Wait a bit more to ensure settings are fully written to disk
        time.sleep(1)

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

    def test_code_font_settings(self):
        """Test code font settings"""
        # Get original code font settings
        original_font = self.window.document_settings["code"]["font_family"]
        original_size = self.window.document_settings["code"]["font_size"]

        # Create a new font
        test_font = "Arial" if original_font != "Arial" else "Times New Roman"
        test_size = 14 if original_size != 14 else 12

        # Update settings directly
        self.window.document_settings["code"]["font_family"] = test_font
        self.window.document_settings["code"]["font_size"] = test_size

        # Check if settings were updated
        self.assertEqual(self.window.document_settings["code"]["font_family"], test_font,
                         "Code font family setting was not updated")
        self.assertEqual(self.window.document_settings["code"]["font_size"], test_size,
                         "Code font size setting was not updated")

        # Restore original settings
        self.window.document_settings["code"]["font_family"] = original_font
        self.window.document_settings["code"]["font_size"] = original_size

        # Check if settings were restored
        self.assertEqual(self.window.document_settings["code"]["font_family"], original_font,
                         "Code font family setting was not restored")
        self.assertEqual(self.window.document_settings["code"]["font_size"], original_size,
                         "Code font size setting was not restored")

    def test_body_font_settings(self):
        """Test body font settings"""
        # Get original body font settings
        original_font = self.window.document_settings["fonts"]["body"]["family"]
        original_size = self.window.document_settings["fonts"]["body"]["size"]

        # Create a new font
        test_font = "Arial" if original_font != "Arial" else "Times New Roman"
        test_size = 14 if original_size != 14 else 12

        # Update settings directly
        self.window.document_settings["fonts"]["body"]["family"] = test_font
        self.window.document_settings["fonts"]["body"]["size"] = test_size

        # Check if settings were updated
        self.assertEqual(self.window.document_settings["fonts"]["body"]["family"], test_font,
                         "Body font family setting was not updated")
        self.assertEqual(self.window.document_settings["fonts"]["body"]["size"], test_size,
                         "Body font size setting was not updated")

        # Restore original settings
        self.window.document_settings["fonts"]["body"]["family"] = original_font
        self.window.document_settings["fonts"]["body"]["size"] = original_size

        # Check if settings were restored
        self.assertEqual(self.window.document_settings["fonts"]["body"]["family"], original_font,
                         "Body font family setting was not restored")
        self.assertEqual(self.window.document_settings["fonts"]["body"]["size"], original_size,
                         "Body font size setting was not restored")

    def test_settings_persistence(self):
        """Test that settings are saved and loaded correctly"""
        # Get current value
        current_value = self.window.document_settings["page"]["margins"]["top"]

        # Change a setting to a different value
        test_value = 30 if current_value != 30 else 25
        self.window.margin_top.setValue(test_value)

        # Save settings and wait for it to complete
        self.window.save_settings(timeout=5)

        # Process events to ensure settings are saved
        QApplication.processEvents()

        # Wait a bit to ensure settings are written to disk
        time.sleep(2)

        # Force sync the settings to disk
        self.window.settings.sync()

        # Process events again
        QApplication.processEvents()

        # Wait a bit more to ensure settings are fully written to disk
        time.sleep(1)

        # Create a new window instance
        new_window = AdvancedMarkdownToPDF()

        # Process events to ensure settings are loaded
        QApplication.processEvents()

        # Wait for settings to be loaded
        time.sleep(1)
        QApplication.processEvents()

        # Check if setting was loaded correctly
        self.assertEqual(new_window.document_settings["page"]["margins"]["top"], float(test_value),
                         "Setting was not persisted between instances")

        # Restore original value
        self.window.margin_top.setValue(current_value)
        self.window.save_settings(timeout=5)

        # Process events to ensure settings are saved
        QApplication.processEvents()

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
            result = self.window._export_to_pdf(output_file)

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
            result = self.window._export_to_pdf(output_file)

            # Check if export was successful
            self.assertTrue(result, f"PDF export with orientation {orientation} failed")

            # Check if file was created
            self.assertTrue(os.path.exists(output_file), f"PDF file with orientation {orientation} was not created")

            # Check file size (should be non-zero)
            self.assertGreater(os.path.getsize(output_file), 0, f"PDF file with orientation {orientation} is empty")


@unittest.skipIf(not CONTENT_PROCESSORS_AVAILABLE, "Content processors not available")
class ContentProcessorTests(unittest.TestCase):
    """Tests for content processors"""

    def setUp(self):
        """Set up before each test"""
        # Create a registry
        from content_processors.processor_registry import ProcessorRegistry
        self.registry = ProcessorRegistry()

        # Register processors
        from content_processors.mermaid_processor import MermaidContentProcessor
        from content_processors.math_processor import MathContentProcessor
        from content_processors.image_processor import ImageContentProcessor
        from content_processors.code_processor import CodeBlockProcessor

        self.registry.register_processor(MermaidContentProcessor)
        self.registry.register_processor(MathContentProcessor)
        self.registry.register_processor(ImageContentProcessor)
        self.registry.register_processor(CodeBlockProcessor)

    def test_processor_registry(self):
        """Test processor registry"""
        # Check if processors are registered
        processors = self.registry.get_all_processors()
        self.assertGreater(len(processors), 0, "No processors registered")

    def test_mermaid_processor(self):
        """Test Mermaid processor"""
        # Create test content
        content = """```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```"""

        # Get the processor
        from content_processors.mermaid_processor import MermaidContentProcessor
        processor = MermaidContentProcessor()

        # Detect Mermaid diagrams
        detected = processor.detect(content)
        self.assertGreater(len(detected), 0, "Mermaid diagram not detected")

        # Process for preview
        processed = processor.process_for_preview(content, {"code": content})
        self.assertIn("<div class=\"mermaid", processed, "Mermaid diagram not processed correctly for preview")

    def test_math_processor(self):
        """Test Math processor"""
        # Create test content
        content = """Inline math: $E = mc^2$

Block math:

$$
\\frac{d}{dx}\\left( \\int_{0}^{x} f(u)\\,du\\right)=f(x)
$$"""

        # Get the processor
        from content_processors.math_processor import MathContentProcessor
        processor = MathContentProcessor()

        # Detect math expressions
        detected = processor.detect(content)
        self.assertGreater(len(detected), 0, "Math expressions not detected")

        # Process for preview
        processed = processor.process_for_preview(content, {"code": "E = mc^2", "type": "inline"})
        self.assertIn("\\\\(", processed, "Math expression not processed correctly for preview")

    def test_image_processor(self):
        """Test Image processor"""
        # Create test content
        content = """![Test Image](test_image.png)

<img src="test_image.png" alt="HTML Image" width="300" />"""

        # Get the processor
        from content_processors.image_processor import ImageContentProcessor
        processor = ImageContentProcessor()

        # Detect images
        detected = processor.detect(content)
        self.assertGreater(len(detected), 0, "Images not detected")

        # Process for preview
        processed = processor.process_for_preview(content, {"type": "markdown_image", "src": "test_image.png", "alt": "Test Image"})
        self.assertIn("<img src=", processed, "Image not processed correctly for preview")

    def test_code_processor(self):
        """Test Code processor"""
        # Create test content
        content = """```python
def hello_world():
    print("Hello, world!")
```"""

        # Get the processor
        from content_processors.code_processor import CodeBlockProcessor
        processor = CodeBlockProcessor()

        # Detect code blocks
        detected = processor.detect(content)
        self.assertGreater(len(detected), 0, "Code block not detected")

        # Process for preview
        processed = processor.process_for_preview(content, {"type": "code", "language": "python", "content": "def hello_world():\n    print(\"Hello, world!\")"})
        self.assertIn("<pre><code", processed, "Code block not processed correctly for preview")


@unittest.skipIf(not MDZ_AVAILABLE, "MDZ functionality not available")
class MDZTests(unittest.TestCase):
    """Tests for MDZ format functionality"""

    def setUp(self):
        """Set up before each test"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name

        # Create a test markdown file
        self.markdown_content = """# MDZ Test

This is a test document for MDZ format.

## Features

- Zstandard compression
- File checksum as password
- Bundled assets

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

## Math Example

$E = mc^2$
"""

        self.markdown_path = os.path.join(self.output_dir, "test.md")
        with open(self.markdown_path, "w", encoding="utf-8") as f:
            f.write(self.markdown_content)

        # Create a test image
        self.image_path = os.path.join(self.output_dir, "test_image.png")
        with open(self.image_path, "wb") as f:
            f.write(b"This is a test image")

    def tearDown(self):
        """Clean up after each test"""
        self.temp_dir.cleanup()

    def test_mdz_export(self):
        """Test MDZ export functionality"""
        # Create an MDZ exporter
        from mdz_export import MDZExporter
        exporter = MDZExporter()

        # Export to MDZ
        output_file = os.path.join(self.output_dir, "test.mdz")
        result = exporter.export_to_mdz(
            markdown_text=self.markdown_content,
            output_file=output_file,
            document_settings={"title": "MDZ Test"},
            assets=[{"path": self.image_path, "data": open(self.image_path, "rb").read()}]
        )

        # Check if export was successful
        self.assertTrue(result, "MDZ export failed")

        # Check if file was created
        self.assertTrue(os.path.exists(output_file), "MDZ file was not created")

        # Check file size (should be non-zero)
        self.assertGreater(os.path.getsize(output_file), 0, "MDZ file is empty")

    def test_mdz_extract(self):
        """Test MDZ extraction functionality"""
        # Create an MDZ file
        from mdz_export import MDZExporter, extract_mdz_file
        exporter = MDZExporter()

        # Export to MDZ
        mdz_path = os.path.join(self.output_dir, "test_extract.mdz")
        exporter.export_to_mdz(
            markdown_text=self.markdown_content,
            output_file=mdz_path,
            document_settings={"title": "MDZ Test"},
            assets=[{"path": self.image_path, "data": open(self.image_path, "rb").read()}]
        )

        # Extract the MDZ file
        extract_dir = os.path.join(self.output_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        markdown_content, metadata = extract_mdz_file(mdz_path, extract_dir)

        # Check if extraction was successful
        self.assertIsNotNone(markdown_content, "MDZ extraction failed")
        self.assertIsNotNone(metadata, "MDZ metadata extraction failed")

        # Check if content matches
        self.assertEqual(markdown_content.strip(), self.markdown_content.strip(), "Extracted content does not match original")

def run_tests(output_file=None):
    """Run all tests and return results"""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add test cases using the non-deprecated method
    for test_class in [ExportTests, SettingsTests, ExportWithSettingsTests]:
        for name in dir(test_class):
            if name.startswith('test_'):
                suite.addTest(test_class(name))

    # Add content processor tests if available
    if CONTENT_PROCESSORS_AVAILABLE:
        for name in dir(ContentProcessorTests):
            if name.startswith('test_'):
                suite.addTest(ContentProcessorTests(name))

    # Add MDZ tests if available
    if MDZ_AVAILABLE:
        for name in dir(MDZTests):
            if name.startswith('test_'):
                suite.addTest(MDZTests(name))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Convert unittest results to our TestResult format
    test_results = []
    for test in result.failures + result.errors:
        test_name = test[0].id().split('.')[-1]
        test_results.append(TestResult(test_name, False, str(test[1])))

    # Add successful tests
    for test in result.successes if hasattr(result, 'successes') else []:
        test_name = test.id().split('.')[-1]
        test_results.append(TestResult(test_name, True, "Test passed"))

    # If no successes attribute, infer successful tests from test cases
    if not hasattr(result, 'successes'):
        all_test_names = set()
        for test_class in [ExportTests, SettingsTests, ExportWithSettingsTests]:
            for name in dir(test_class):
                if name.startswith('test_'):
                    all_test_names.add(name)

        if CONTENT_PROCESSORS_AVAILABLE:
            for name in dir(ContentProcessorTests):
                if name.startswith('test_'):
                    all_test_names.add(name)

        if MDZ_AVAILABLE:
            for name in dir(MDZTests):
                if name.startswith('test_'):
                    all_test_names.add(name)

        # Get failed test names
        failed_test_names = set(test[0].id().split('.')[-1] for test in result.failures + result.errors)

        # Add successful tests
        for name in all_test_names:
            if name not in failed_test_names:
                test_results.append(TestResult(name, True, "Test passed"))

    # Save results to file if specified
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([{
                    "name": r.name,
                    "success": r.success,
                    "message": r.message,
                    "timestamp": r.timestamp
                } for r in test_results], f, indent=2)
            logger.info(f"Test results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")

    return test_results

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run unit tests for Markdown to PDF Converter")
    parser.add_argument("--output", help="Output file for test results")
    args = parser.parse_args()

    # Run tests
    results = run_tests(args.output)

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed

    print(f"\nTest Summary:")
    print(f"- Total Tests: {total}")
    print(f"- Passed: {passed}")
    print(f"- Failed: {failed}")
    print(f"- Pass Rate: {passed/total*100:.2f}%")

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
