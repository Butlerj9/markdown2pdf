#!/usr/bin/env python3
"""
Simple test for page breaks in Markdown to PDF Converter
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = AdvancedMarkdownToPDF()
    
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
    window.markdown_editor.setPlainText(test_content)
    
    # Update the preview
    window.update_preview()
    
    # Show the window
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
