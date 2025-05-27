#!/usr/bin/env python3
"""
Test script for loading a multi-page document in the test window.
"""

import sys
from PyQt6.QtWidgets import QApplication

# Import the test window
from test_page_preview_simple import TestWindow

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create and show the main window
    window = TestWindow()
    window.show()

    # Load a multi-page document
    window.load_multi_page_document()

    # Prevent the automatic loading of the simple document
    window.load_simple_document = lambda: None

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
