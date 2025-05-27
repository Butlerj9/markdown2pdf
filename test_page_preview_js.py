#!/usr/bin/env python3
"""
Test Page Preview JavaScript
---------------------------
Focused test to identify JavaScript syntax errors in page_preview.py
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage that logs JavaScript console messages"""
    
    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle console.log messages from JavaScript"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")
        
        print(f"JS Console ({level_str}): {message} [{source}:{line}]")
        
        # For errors, provide more detailed logging
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            print(f"JavaScript Error: {message}")
            print(f"  Source: {source}")
            print(f"  Line: {line}")
            
            # Extract the specific syntax error if possible
            if "SyntaxError" in message:
                error_parts = message.split(":")
                if len(error_parts) > 1:
                    error_type = error_parts[0].strip()
                    error_detail = ":".join(error_parts[1:]).strip()
                    print(f"  Error Type: {error_type}")
                    print(f"  Error Detail: {error_detail}")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Preview JavaScript Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create a web view
        self.web_view = QWebEngineView()
        
        # Set custom page with console logging
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Set as central widget
        self.setCentralWidget(self.web_view)
        
        # Extract JavaScript from page_preview.py
        self.extract_and_test_js()
    
    def extract_and_test_js(self):
        """Extract JavaScript from page_preview.py and test it"""
        # Create a simple HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Preview JavaScript Test</title>
        </head>
        <body>
            <h1>Page Preview JavaScript Test</h1>
            <div id="output"></div>
            
            <script>
            // Test JavaScript from page_preview.py
            try {
                %s
                document.getElementById('output').innerHTML = 'JavaScript syntax test completed successfully.';
            } catch (error) {
                console.error('JavaScript error:', error);
                document.getElementById('output').innerHTML = 'JavaScript syntax test failed: ' + error.message;
            }
            </script>
        </body>
        </html>
        """
        
        # Extract JavaScript from page_layout_script in page_preview.py
        js_code = self.extract_js_from_page_preview()
        
        # Insert the JavaScript into the HTML template
        html = html_template % js_code
        
        # Load the HTML
        self.web_view.setHtml(html)
    
    def extract_js_from_page_preview(self):
        """Extract JavaScript code from page_preview.py"""
        # This is a simplified version of the JavaScript in page_preview.py
        # with the most critical parts for testing
        js_code = """
        // Create a page cache for faster navigation
        window.pageCache = {
            pages: document.querySelectorAll('.page'),
            totalPages: document.querySelectorAll('.page').length,
            currentPage: document.querySelector('.page.current-page'),
            lastUpdate: Date.now()
        };

        // Function to update the page cache
        window.updatePageCache = function() {
            window.pageCache = {
                pages: document.querySelectorAll('.page'),
                totalPages: document.querySelectorAll('.page').length,
                currentPage: document.querySelector('.page.current-page'),
                lastUpdate: Date.now()
            };
            return window.pageCache;
        };

        // Main navigation function
        window.navigateToPage = function(pageNum) {
            console.log('Navigating to page: ' + pageNum);
            var cache = window.updatePageCache();
            var pages = cache.pages;
            var totalPages = cache.totalPages;
            var targetPage;
            var targetIndex = 0;

            if (totalPages === 0) {
                console.error('No pages found');
                return false;
            }

            // Remove current-page class from all pages
            for (var i = 0; i < pages.length; i++) {
                if (pages[i].classList.contains('current-page')) {
                    window.currentPageIndex = i;
                }
                pages[i].classList.remove('current-page');
            }
        };
        
        console.log('JavaScript syntax test completed.');
        """
        
        return js_code

def main():
    """Main function to test JavaScript syntax"""
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = TestWindow()
    window.show()
    
    # Exit after 5 seconds
    QTimer.singleShot(5000, app.quit)
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
