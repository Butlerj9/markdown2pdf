#!/usr/bin/env python3
"""
Test Page Preview (Version 2)
--------------------------
A simplified version of the page preview component for testing
"""

import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt

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
        self.setWindowTitle("Page Preview Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Set custom page with console logging
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Add web view to layout
        layout.addWidget(self.web_view)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Load test HTML
        self.load_test_html()
    
    def load_test_html(self):
        """Load test HTML with JavaScript"""
        # Variables for testing
        zoom_factor = 0.9
        page_width = 210
        page_height = 297
        margin_top = 25
        margin_right = 25
        margin_bottom = 25
        margin_left = 25
        
        # Create JavaScript
        js_code = """
        (function() {
            console.log('Applying page layout styling');
            
            // Convert mm to px (assuming 96 DPI, 1 inch = 25.4 mm)
            var mmToPx = 96 / 25.4;
            var pageWidthMM = %s;
            var pageHeightMM = %s;
            var marginTopMM = %s;
            var marginRightMM = %s;
            var marginBottomMM = %s;
            var marginLeftMM = %s;
            var zoomFactor = %s;
            
            console.log('Page dimensions (mm): ' + pageWidthMM + 'x' + pageHeightMM);
            
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
                
                // Add current-page class to target page
                var targetIndex = Math.max(0, Math.min(pageNum - 1, totalPages - 1));
                pages[targetIndex].classList.add('current-page');
                
                // Scroll to the target page
                pages[targetIndex].scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                return true;
            };
            
            console.log('JavaScript test completed successfully');
        })();
        """ % (page_width, page_height, margin_top, margin_right, margin_bottom, margin_left, zoom_factor)
        
        # Create HTML with the JavaScript
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Preview Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .page {
                    width: 210mm;
                    min-height: 297mm;
                    padding: 25mm;
                    margin-bottom: 20px;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                    box-sizing: border-box;
                    position: relative;
                }
                h1 {
                    font-size: 24pt;
                    margin-top: 0;
                }
                p {
                    font-size: 12pt;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            <div class="page">
                <h1>Page 1</h1>
                <p>This is the first page of the document.</p>
            </div>
            <div class="page">
                <h1>Page 2</h1>
                <p>This is the second page of the document.</p>
            </div>
            <div class="page">
                <h1>Page 3</h1>
                <p>This is the third page of the document.</p>
            </div>
            
            <script>
            %s
            </script>
        </body>
        </html>
        """ % js_code
        
        # Load the HTML
        self.web_view.setHtml(html)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
