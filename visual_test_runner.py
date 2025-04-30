#!/usr/bin/env python3
"""
Visual Test Runner for Markdown to PDF Converter
-----------------------------------------------
Runs visual tests for the application.
"""

import os
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from visual_test import VisualTester
from logging_config import get_logger

logger = get_logger()

class VisualTestRunner:
    """Class for running visual tests on the application"""
    
    def __init__(self):
        """Initialize the test runner"""
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.main_window = None
        self.tester = VisualTester(self.app)
        self.tests = []
        self.current_test_index = 0
    
    def start_application(self):
        """Start the application for testing"""
        self.main_window = AdvancedMarkdownToPDF()
        self.main_window.show()
        logger.info("Application started for visual testing")
    
    def add_test(self, test_func, test_name):
        """Add a test to the queue"""
        self.tests.append((test_func, test_name))
    
    def run_next_test(self):
        """Run the next test in the queue"""
        if self.current_test_index < len(self.tests):
            test_func, test_name = self.tests[self.current_test_index]
            logger.info(f"Running test {self.current_test_index + 1}/{len(self.tests)}: {test_name}")
            
            self.tester.start_test(test_name)
            test_func()
            
            self.current_test_index += 1
            QTimer.singleShot(1000, self.run_next_test)
        else:
            logger.info("All tests completed")
            QTimer.singleShot(1000, self.app.quit)
    
    def run_tests(self):
        """Run all tests in the queue"""
        logger.info(f"Starting {len(self.tests)} visual tests")
        self.current_test_index = 0
        
        # Start the application
        self.start_application()
        
        # Allow time for the application to initialize
        QTimer.singleShot(2000, self.run_next_test)
        
        # Run the application event loop
        self.app.exec()

# Test functions
def test_basic_ui():
    """Test the basic UI elements"""
    runner = VisualTestRunner()
    
    def test_func():
        # Take a screenshot of the main window
        runner.tester.take_screenshot("main_window")
        
        # Verify against reference if it exists
        runner.tester.verify_against_reference("main_window")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "basic_ui")
    runner.run_tests()

def test_heading_numbering():
    """Test the heading numbering functionality"""
    runner = VisualTestRunner()
    
    def test_func():
        # Set up test content
        test_content = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4
## Another Heading 2
### Another Heading 3
"""
        # Set the content in the editor
        runner.main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        runner.main_window.update_preview()
        QTest.qWait(1000)
        
        # Take a screenshot
        runner.tester.take_screenshot("heading_numbering_h1")
        
        # Change numbering start to H2
        runner.main_window.numbering_start.setCurrentIndex(1)  # H2
        QTest.qWait(1000)
        
        # Take another screenshot
        runner.tester.take_screenshot("heading_numbering_h2")
        
        # Change numbering start to H3
        runner.main_window.numbering_start.setCurrentIndex(2)  # H3
        QTest.qWait(1000)
        
        # Take another screenshot
        runner.tester.take_screenshot("heading_numbering_h3")
        
        # Verify against references if they exist
        runner.tester.verify_against_reference("heading_numbering_h1")
        runner.tester.verify_against_reference("heading_numbering_h2")
        runner.tester.verify_against_reference("heading_numbering_h3")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "heading_numbering")
    runner.run_tests()

def test_page_breaks():
    """Test the page break functionality"""
    runner = VisualTestRunner()
    
    def test_func():
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
        runner.main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        runner.main_window.update_preview()
        QTest.qWait(1000)
        
        # Take a screenshot of page 1
        runner.tester.take_screenshot("page_break_page1")
        
        # Navigate to page 2
        runner.main_window.page_preview.next_page()
        QTest.qWait(500)
        
        # Take a screenshot of page 2
        runner.tester.take_screenshot("page_break_page2")
        
        # Navigate to page 3
        runner.main_window.page_preview.next_page()
        QTest.qWait(500)
        
        # Take a screenshot of page 3
        runner.tester.take_screenshot("page_break_page3")
        
        # Verify against references if they exist
        runner.tester.verify_against_reference("page_break_page1")
        runner.tester.verify_against_reference("page_break_page2")
        runner.tester.verify_against_reference("page_break_page3")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "page_breaks")
    runner.run_tests()

def test_edit_toolbar():
    """Test the edit toolbar functionality"""
    runner = VisualTestRunner()
    
    def test_func():
        # Clear the editor
        runner.main_window.markdown_editor.clear()
        QTest.qWait(500)
        
        # Take a screenshot of the empty editor
        runner.tester.take_screenshot("edit_toolbar_empty")
        
        # Use the bold button
        runner.main_window.edit_toolbar.insert_bold()
        runner.main_window.markdown_editor.insertPlainText("Bold Text")
        QTest.qWait(500)
        
        # Take a screenshot
        runner.tester.take_screenshot("edit_toolbar_bold")
        
        # Add a new line and use italic
        runner.main_window.markdown_editor.insertPlainText("\n\n")
        runner.main_window.edit_toolbar.insert_italic()
        runner.main_window.markdown_editor.insertPlainText("Italic Text")
        QTest.qWait(500)
        
        # Take a screenshot
        runner.tester.take_screenshot("edit_toolbar_italic")
        
        # Add a new line and use heading
        runner.main_window.markdown_editor.insertPlainText("\n\n")
        runner.main_window.edit_toolbar.insert_heading(1)
        runner.main_window.markdown_editor.insertPlainText("Heading 1")
        QTest.qWait(500)
        
        # Update the preview
        runner.main_window.update_preview()
        QTest.qWait(1000)
        
        # Take a screenshot of the preview
        runner.tester.take_screenshot("edit_toolbar_preview")
        
        # Verify against references if they exist
        runner.tester.verify_against_reference("edit_toolbar_empty")
        runner.tester.verify_against_reference("edit_toolbar_bold")
        runner.tester.verify_against_reference("edit_toolbar_italic")
        runner.tester.verify_against_reference("edit_toolbar_preview")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "edit_toolbar")
    runner.run_tests()

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "basic_ui":
            test_basic_ui()
        elif test_name == "heading_numbering":
            test_heading_numbering()
        elif test_name == "page_breaks":
            test_page_breaks()
        elif test_name == "edit_toolbar":
            test_edit_toolbar()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: basic_ui, heading_numbering, page_breaks, edit_toolbar")
    else:
        # Run a simple test by default
        test_basic_ui()
