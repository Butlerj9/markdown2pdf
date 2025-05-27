#!/usr/bin/env python3
"""
Direct test script for page preview
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer

class TestWindow(QMainWindow):
    """Test window for page preview"""

    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Page Preview Test")
        self.setGeometry(100, 100, 800, 600)

        # Create the web view
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)

        # Get the absolute path to the test HTML file
        html_path = os.path.abspath("test.html")

        # Load the HTML file
        self.web_view.load(QUrl.fromLocalFile(html_path))

        # Set up a timer to test navigation
        QTimer.singleShot(2000, self.test_navigation)

    def test_navigation(self):
        """Test navigation"""
        # Run JavaScript to count pages
        self.web_view.page().runJavaScript(
            "document.querySelectorAll('.page').length",
            lambda count: print(f"Page count: {count}")
        )

        # Run JavaScript to check if first page is marked as current
        self.web_view.page().runJavaScript(
            "document.querySelector('.page.current-page') ? 1 : 0",
            lambda current: print(f"Current page: {current}")
        )

        # Test navigation to next page
        self.web_view.page().runJavaScript(
            "window.navigateToPage('next')",
            lambda result: print(f"Navigation to next page result: {result}")
        )

        # Set up another timer to check the current page after navigation
        QTimer.singleShot(1000, self.check_current_page)

    def check_current_page(self):
        """Check the current page"""
        # Check if any page has the current-page class
        self.web_view.page().runJavaScript(
            "document.querySelector('.page.current-page') ? true : false",
            lambda has_current: print(f"Has current page class: {has_current}")
        )

        # Check which page has the current-page class
        self.web_view.page().runJavaScript(
            """
            (function() {
                var currentPage = document.querySelector('.page.current-page');
                if (currentPage) {
                    var pages = document.querySelectorAll('.page');
                    for (var i = 0; i < pages.length; i++) {
                        if (pages[i] === currentPage) {
                            return i + 1;
                        }
                    }
                }
                return 0;
            })();
            """,
            lambda current: print(f"Current page index: {current}")
        )

        # Check all page classes
        self.web_view.page().runJavaScript(
            """
            (function() {
                var pages = document.querySelectorAll('.page');
                var classes = [];
                for (var i = 0; i < pages.length; i++) {
                    classes.push(pages[i].className);
                }
                return classes;
            })();
            """,
            lambda classes: print(f"Page classes: {classes}")
        )

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create the test window
    window = TestWindow()
    window.show()

    # Exit after 5 seconds
    QTimer.singleShot(5000, app.quit)

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
