#!/usr/bin/env python3
"""
Comprehensive visual test for the Markdown to PDF Converter
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from visual_test import VisualTester

class ComprehensiveVisualTest:
    """Class for running comprehensive visual tests"""

    def __init__(self):
        """Initialize the test"""
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.tester = None
        self.test_results = {}
        self.current_test = None

    def setup(self):
        """Set up the test environment"""
        # Create main window
        self.main_window = AdvancedMarkdownToPDF()
        self.main_window.show()

        # Create visual tester
        self.tester = VisualTester(self.app)

        # Maximize window for consistent screenshots
        self.main_window.showMaximized()

    def run_tests(self):
        """Run all tests"""
        self.setup()

        # Define test sequence
        tests = [
            self.test_page_layout,
            self.test_heading_numbering,
            self.test_page_breaks,
            self.test_edit_toolbar
        ]

        # Run tests sequentially
        def run_next_test(index=0):
            if index < len(tests):
                test_func = tests[index]
                print(f"Running test: {test_func.__name__}")
                self.current_test = test_func.__name__
                test_func(lambda: QTimer.singleShot(1000, lambda: run_next_test(index + 1)))
            else:
                # All tests completed
                print("\nTest Results:")
                for test_name, result in self.test_results.items():
                    print(f"{test_name}: {'PASS' if result else 'FAIL'}")

                # Exit application
                QTimer.singleShot(1000, self.app.quit)

        # Start the first test after a short delay
        QTimer.singleShot(2000, lambda: run_next_test(0))

        # Run the application
        self.app.exec()

    def test_page_layout(self, callback):
        """Test the page preview layout"""
        # Set up test content with multiple pages
        test_content = """# Test Document

This is a test document with multiple pages.

<!-- PAGE_BREAK -->

## Page 2

This is the second page of the document.

<!-- PAGE_BREAK -->

## Page 3

This is the third page of the document.
"""

        # Set the content in the editor
        self.main_window.markdown_editor.setPlainText(test_content)

        # Update the preview
        self.main_window.update_preview()

        # Wait for the preview to update
        QTimer.singleShot(2000, lambda: self.take_screenshot_and_continue("page_layout", callback))

    def test_heading_numbering(self, callback):
        """Test the heading numbering functionality"""
        # Set up test content
        test_content = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4
## Another Heading 2
### Another Heading 3
"""
        # Set the content in the editor
        self.main_window.markdown_editor.setPlainText(test_content)

        # Enable technical numbering
        self.main_window.technical_numbering.setChecked(True)

        # Update the preview
        self.main_window.update_preview()
        QTest.qWait(1000)

        # Take a screenshot with H1 numbering
        self.tester.take_screenshot("heading_numbering_h1")

        # Change numbering start to H2
        self.main_window.numbering_start.setCurrentIndex(1)  # H2
        QTest.qWait(1000)

        # Take a screenshot with H2 numbering
        self.tester.take_screenshot("heading_numbering_h2")

        # Change numbering start to H3
        self.main_window.numbering_start.setCurrentIndex(2)  # H3
        QTest.qWait(1000)

        # Take a screenshot with H3 numbering
        self.tester.take_screenshot("heading_numbering_h3")

        # Continue to next test
        QTimer.singleShot(1000, callback)

    def test_page_breaks(self, callback):
        """Test the page break functionality"""
        # Set up test content with explicit page breaks
        test_content = """# Page 1
This is content on page 1.

<!-- PAGE_BREAK -->

# Page 2
This is content on page 2.

<!-- PAGE_BREAK -->

# Page 3
This is content on page 3.
"""
        # Set the content in the editor
        self.main_window.markdown_editor.setPlainText(test_content)

        # Update the preview
        self.main_window.update_preview()
        QTest.qWait(1000)

        # Take a screenshot of all pages
        self.tester.take_screenshot("page_breaks_all")

        # Continue to next test
        QTimer.singleShot(1000, callback)

    def test_edit_toolbar(self, callback):
        """Test the edit toolbar functionality"""
        # Clear the editor
        self.main_window.markdown_editor.clear()
        QTest.qWait(500)

        # Take a screenshot of the empty editor with toolbar
        self.tester.take_screenshot("edit_toolbar_empty")

        # Use the bold button
        cursor = self.main_window.markdown_editor.textCursor()
        self.main_window.edit_toolbar.insert_bold()
        self.main_window.markdown_editor.insertPlainText("Bold Text")
        QTest.qWait(500)

        # Add a new line and use italic
        self.main_window.markdown_editor.insertPlainText("\n\n")
        self.main_window.edit_toolbar.insert_italic()
        self.main_window.markdown_editor.insertPlainText("Italic Text")
        QTest.qWait(500)

        # Add a new line and use heading
        self.main_window.markdown_editor.insertPlainText("\n\n")
        self.main_window.edit_toolbar.insert_heading(1)
        self.main_window.markdown_editor.insertPlainText("Heading 1")
        QTest.qWait(500)

        # Update the preview
        self.main_window.update_preview()
        QTest.qWait(1000)

        # Take a screenshot of the editor with formatted text
        self.tester.take_screenshot("edit_toolbar_formatted")

        # Continue to next test
        QTimer.singleShot(1000, callback)

    def take_screenshot_and_continue(self, name, callback):
        """Take a screenshot and continue to the next test"""
        screenshot_path = self.tester.take_screenshot(name)
        print(f"Screenshot saved to: {screenshot_path}")

        # Mark test as passed
        self.test_results[self.current_test] = True

        # Continue to next test
        callback()

if __name__ == "__main__":
    test = ComprehensiveVisualTest()
    test.run_tests()
