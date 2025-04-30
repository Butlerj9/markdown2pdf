#!/usr/bin/env python3
"""
Settings Tests for Markdown to PDF Converter
-------------------------------------------
Provides detailed testing of settings panel functionality.
"""

import os
import sys
import tempfile
import unittest
import logging
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer, QSettings

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

logger = get_logger()

class SettingsTestCase(unittest.TestCase):
    """Test case for settings functionality"""

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
        self.sample_markdown = """# Settings Test Document

This is a test document for the Markdown to PDF converter settings functionality.

## Headings

### Level 3 Heading

#### Level 4 Heading

## Lists

- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
- Item 3

1. Numbered item 1
2. Numbered item 2
   1. Subnumbered item 2.1
   2. Subnumbered item 2.2
3. Numbered item 3

## Code Block

```python
def test_settings():
    print("Testing settings functionality")
```

## Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |

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

    def test_page_settings_ui_to_model(self):
        """Test that page settings UI changes update the model"""
        # Test page size
        self.window.page_size_combo.setCurrentText("A5")
        self.assertEqual(self.window.document_settings["page"]["size"], "A5",
                         "Page size setting was not updated")

        # Test orientation
        self.window.orientation_combo.setCurrentText("Landscape")
        self.assertEqual(self.window.document_settings["page"]["orientation"].lower(), "landscape",
                         "Orientation setting was not updated")

        # Test margins
        test_value = 25
        self.window.margin_top.setValue(test_value)
        self.window.margin_right.setValue(test_value)
        self.window.margin_bottom.setValue(test_value)
        self.window.margin_left.setValue(test_value)

        margins = self.window.document_settings["page"]["margins"]
        self.assertEqual(margins["top"], test_value, "Top margin setting was not updated")
        self.assertEqual(margins["right"], test_value, "Right margin setting was not updated")
        self.assertEqual(margins["bottom"], test_value, "Bottom margin setting was not updated")
        self.assertEqual(margins["left"], test_value, "Left margin setting was not updated")

    def test_font_settings_ui_to_model(self):
        """Test that font settings UI changes update the model"""
        # Test body font
        self.window.body_font_family.setCurrentText("Arial")
        self.window.body_font_size.setValue(14)
        self.window.line_height.setValue(1.8)

        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_family"], "Arial",
                         "Body font family setting was not updated")
        self.assertEqual(self.window.document_settings["fonts"]["body"]["font_size"], 14,
                         "Body font size setting was not updated")
        self.assertEqual(self.window.document_settings["fonts"]["body"]["line_height"], 1.8,
                         "Line height setting was not updated")

        # Test heading fonts
        self.window.h1_font_family.setCurrentText("Times New Roman")
        self.window.h1_font_size.setValue(24)

        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_family"], "Times New Roman",
                         "H1 font family setting was not updated")
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["h1"]["font_size"], 24,
                         "H1 font size setting was not updated")

        # Test heading numbering
        self.window.heading_numbering.setChecked(True)
        self.window.numbering_start.setCurrentIndex(1)  # H2

        self.assertTrue(self.window.document_settings["fonts"]["headings"]["numbering"],
                        "Heading numbering setting was not updated")
        self.assertEqual(self.window.document_settings["fonts"]["headings"]["numbering_start"], "h2",
                         "Numbering start setting was not updated")

    def test_paragraph_settings_ui_to_model(self):
        """Test that paragraph settings UI changes update the model"""
        # Test paragraph spacing
        self.window.paragraph_spacing.setValue(1.5)
        self.assertEqual(self.window.document_settings["paragraph"]["spacing"], 1.5,
                         "Paragraph spacing setting was not updated")

        # Test first line indent
        self.window.first_line_indent.setValue(2.0)
        self.assertEqual(self.window.document_settings["paragraph"]["first_line_indent"], 2.0,
                         "First line indent setting was not updated")

        # Test alignment
        self.window.alignment_combo.setCurrentText("Justify")
        self.assertEqual(self.window.document_settings["paragraph"]["alignment"].lower(), "justify",
                         "Alignment setting was not updated")

    def test_list_settings_ui_to_model(self):
        """Test that list settings UI changes update the model"""
        # Test list indent
        self.window.list_indent.setValue(2.0)
        self.assertEqual(self.window.document_settings["list"]["indent"], 2.0,
                         "List indent setting was not updated")

        # Test bullet style
        self.window.bullet_style.setCurrentText("Square")
        self.assertEqual(self.window.document_settings["list"]["bullet_style"].lower(), "square",
                         "Bullet style setting was not updated")

    def test_table_settings_ui_to_model(self):
        """Test that table settings UI changes update the model"""
        # Test table style
        self.window.table_style.setCurrentText("Striped")
        self.assertEqual(self.window.document_settings["table"]["style"].lower(), "striped",
                         "Table style setting was not updated")

        # Test cell padding
        self.window.cell_padding.setValue(8)
        self.assertEqual(self.window.document_settings["table"]["cell_padding"], 8,
                         "Cell padding setting was not updated")

    def test_code_settings_ui_to_model(self):
        """Test that code settings UI changes update the model"""
        # Test code font
        self.window.code_font_family.setCurrentText("Courier New")
        self.window.code_font_size.setValue(12)

        self.assertEqual(self.window.document_settings["code"]["font_family"], "Courier New",
                         "Code font family setting was not updated")
        self.assertEqual(self.window.document_settings["code"]["font_size"], 12,
                         "Code font size setting was not updated")

        # Test code background
        self.window.code_background.setText("#E0E0E0")
        self.assertEqual(self.window.document_settings["code"]["background"], "#E0E0E0",
                         "Code background setting was not updated")

    def test_toc_settings_ui_to_model(self):
        """Test that TOC settings UI changes update the model"""
        # Test TOC include
        self.window.include_toc.setChecked(True)
        self.assertTrue(self.window.document_settings["toc"]["include"],
                        "TOC include setting was not updated")

        # Test TOC depth
        self.window.toc_depth.setValue(4)
        self.assertEqual(self.window.document_settings["toc"]["depth"], 4,
                         "TOC depth setting was not updated")

        # Test TOC title
        self.window.toc_title.setText("Contents")
        self.assertEqual(self.window.document_settings["toc"]["title"], "Contents",
                         "TOC title setting was not updated")

    def test_settings_persistence(self):
        """Test that settings are saved and loaded correctly"""
        # Change various settings
        self.window.page_size_combo.setCurrentText("A5")
        self.window.orientation_combo.setCurrentText("Landscape")
        self.window.margin_top.setValue(25)
        self.window.body_font_family.setCurrentText("Arial")
        self.window.body_font_size.setValue(14)
        self.window.heading_numbering.setChecked(True)
        self.window.include_toc.setChecked(True)

        # Save settings
        self.window.save_settings()

        # Create a new window instance
        new_window = AdvancedMarkdownToPDF()

        # Check if settings were loaded correctly
        self.assertEqual(new_window.document_settings["page"]["size"], "A5",
                         "Page size setting was not persisted")
        self.assertEqual(new_window.document_settings["page"]["orientation"].lower(), "landscape",
                         "Orientation setting was not persisted")
        self.assertEqual(new_window.document_settings["page"]["margins"]["top"], 25,
                         "Margin setting was not persisted")
        self.assertEqual(new_window.document_settings["fonts"]["body"]["font_family"], "Arial",
                         "Font family setting was not persisted")
        self.assertEqual(new_window.document_settings["fonts"]["body"]["font_size"], 14,
                         "Font size setting was not persisted")
        self.assertTrue(new_window.document_settings["fonts"]["headings"]["numbering"],
                        "Heading numbering setting was not persisted")
        self.assertTrue(new_window.document_settings["toc"]["include"],
                        "TOC include setting was not persisted")

        # Close the new window
        new_window.close()
        QApplication.processEvents()

    def test_settings_toggle(self):
        """Test the settings toggle functionality"""
        # Enable custom settings
        self.window.settings_toggle.setChecked(True)

        # Change a setting
        self.window.page_size_combo.setCurrentText("A5")
        self.assertEqual(self.window.document_settings["page"]["size"], "A5",
                         "Setting was not updated when custom settings enabled")

        # Disable custom settings
        self.window.settings_toggle.setChecked(False)

        # Try to change a setting
        original_size = self.window.document_settings["page"]["size"]
        self.window.page_size_combo.setCurrentText("Letter")

        # The setting should not change because custom settings are disabled
        # Instead, it should apply the selected style preset
        self.assertNotEqual(self.window.document_settings["page"]["size"], "Letter",
                            "Setting was updated when custom settings disabled")

    def test_style_presets(self):
        """Test the style presets functionality"""
        # Disable custom settings to use presets
        self.window.settings_toggle.setChecked(False)

        # Get available presets
        presets = [self.window.preset_combo.itemText(i) for i in range(self.window.preset_combo.count())]

        # Test each preset
        for preset in presets:
            # Select the preset
            self.window.preset_combo.setCurrentText(preset)

            # Apply the preset
            self.window.apply_style_preset(preset)

            # Check if settings were updated
            # We can't check specific values as they depend on the preset,
            # but we can check that the settings object is not empty
            self.assertIsNotNone(self.window.document_settings,
                                "Settings object is None after applying preset")
            self.assertIsNotNone(self.window.document_settings["page"],
                                "Page settings are None after applying preset")
            self.assertIsNotNone(self.window.document_settings["fonts"],
                                "Font settings are None after applying preset")

    def test_settings_reflect_in_preview(self):
        """Test that settings changes are reflected in the preview"""
        # This test is more complex as it requires checking the actual preview content
        # We'll focus on a few key settings that should have visible effects

        # Change heading font size to a very large value
        self.window.h1_font_size.setValue(36)

        # Update preview
        self.window.update_preview()
        QApplication.processEvents()

        # Check if preview was updated
        # This is a basic check - in a real test, we would use the visual testing framework
        # to capture and compare screenshots
        self.assertIsNotNone(self.window.preview_widget,
                            "Preview widget is None after updating settings")

        # Change page size to a very small value
        self.window.page_size_combo.setCurrentText("A6")

        # Update preview
        self.window.update_preview()
        QApplication.processEvents()

        # Check if preview was updated
        self.assertIsNotNone(self.window.preview_widget,
                            "Preview widget is None after updating settings")

    def test_settings_file_structure(self):
        """Test the structure of the settings file"""
        # Save settings
        self.window.save_settings()

        # Get settings from QSettings
        settings = QSettings("MarkdownToPDF", "AdvancedConverter")
        document_settings = settings.value("document_settings")

        # Check if settings were saved
        self.assertIsNotNone(document_settings, "Settings were not saved")

        # Check if settings have the expected structure
        self.assertIn("page", document_settings, "Settings missing 'page' section")
        self.assertIn("fonts", document_settings, "Settings missing 'fonts' section")
        self.assertIn("paragraph", document_settings, "Settings missing 'paragraph' section")
        self.assertIn("list", document_settings, "Settings missing 'list' section")
        self.assertIn("table", document_settings, "Settings missing 'table' section")
        self.assertIn("code", document_settings, "Settings missing 'code' section")
        self.assertIn("toc", document_settings, "Settings missing 'toc' section")

        # Check if page settings have the expected structure
        self.assertIn("size", document_settings["page"], "Page settings missing 'size'")
        self.assertIn("orientation", document_settings["page"], "Page settings missing 'orientation'")
        self.assertIn("margins", document_settings["page"], "Page settings missing 'margins'")

        # Check if font settings have the expected structure
        self.assertIn("body", document_settings["fonts"], "Font settings missing 'body'")
        self.assertIn("headings", document_settings["fonts"], "Font settings missing 'headings'")

def run_settings_tests():
    """Run settings tests and return results"""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(SettingsTestCase))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

if __name__ == "__main__":
    # Run tests
    unittest.main()
