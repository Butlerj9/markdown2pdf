#!/usr/bin/env python3
"""
Test script for the page preview layout
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from visual_test import VisualTester

def test_preview_layout():
    """Test the page preview layout"""
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = AdvancedMarkdownToPDF()
    main_window.show()
    
    # Create visual tester
    tester = VisualTester(app)
    
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
    
    # Set up test function
    def run_test():
        # Set the content in the editor
        main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        main_window.update_preview()
        
        # Wait for the preview to update
        QTimer.singleShot(2000, take_screenshot)
    
    def take_screenshot():
        # Take a screenshot
        tester.take_screenshot("preview_layout")
        
        # Exit the application
        QTimer.singleShot(1000, app.quit)
    
    # Run the test after a short delay
    QTimer.singleShot(1000, run_test)
    
    # Run the application
    app.exec()
    
    # Return the screenshot path
    return os.path.join(tester.screenshot_dir, "preview_layout.png")

if __name__ == "__main__":
    screenshot_path = test_preview_layout()
    print(f"Screenshot saved to: {screenshot_path}")
