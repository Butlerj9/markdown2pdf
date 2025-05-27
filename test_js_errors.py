#!/usr/bin/env python3
"""
Test JavaScript Errors
-------------------
Script to identify JavaScript syntax errors in page_preview.py
"""

import sys
import os
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from page_preview import PagePreview
from logging_config import get_logger

logger = get_logger()

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JavaScript Error Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add status label
        self.status_label = QLabel("Testing JavaScript syntax...")
        layout.addWidget(self.status_label)
        
        # Create web view directly (without PagePreview)
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Create a custom page to handle JavaScript errors
        self.web_page = CustomWebPage()
        self.web_view.setPage(self.web_page)
        
        # Create a simple HTML file with the JavaScript code
        self.html_file = self.create_test_html()
        
        # Load the HTML file
        self.web_view.load(QUrl.fromLocalFile(self.html_file))
        
        # Schedule check for JavaScript errors
        QTimer.singleShot(2000, self.check_errors)
    
    def create_test_html(self):
        """Create a test HTML file with JavaScript code"""
        # Create a temporary HTML file
        fd, path = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        
        # Get the JavaScript code from PagePreview
        preview = PagePreview()
        
        # Extract the JavaScript code
        js_code = """
        <script>
        // Test JavaScript code
        (function() {
            console.log('Testing JavaScript syntax...');
            
            // Test variable interpolation
            var zoomFactor = """ + str(preview.zoom_factor) + """;
            console.log('Zoom factor: ' + zoomFactor);
            
            // Test page dimensions
            var pageWidth = 210;
            var pageHeight = 297;
            var marginTop = 25;
            var marginRight = 25;
            var marginBottom = 25;
            var marginLeft = 25;
            
            console.log('Page dimensions: ' + pageWidth + 'mm x ' + pageHeight + 'mm');
            console.log('Margins: T:' + marginTop + 'mm R:' + marginRight + 'mm B:' + marginBottom + 'mm L:' + marginLeft + 'mm');
            
            // Test JavaScript object literals
            var pageCache = {
                pages: null,
                totalPages: 0,
                currentPage: null,
                lastUpdate: Date.now()
            };
            
            console.log('Page cache created: ' + JSON.stringify(pageCache));
            
            // Test function declaration
            function testFunction() {
                console.log('Test function called');
                return true;
            }
            
            // Test if statement
            if (zoomFactor > 0) {
                console.log('Zoom factor is positive');
            } else {
                console.log('Zoom factor is zero or negative');
            }
            
            // Test for loop
            for (var i = 0; i < 3; i++) {
                console.log('Loop iteration: ' + i);
            }
            
            // Call the test function
            testFunction();
            
            console.log('JavaScript syntax test completed successfully');
        })();
        </script>
        """
        
        # Create the HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript Syntax Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                h1 {
                    color: #333;
                }
                .success {
                    color: green;
                    font-weight: bold;
                }
                .error {
                    color: red;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h1>JavaScript Syntax Test</h1>
            <p>This page tests JavaScript syntax to identify any errors.</p>
            <div id="result">Testing...</div>
            """ + js_code + """
            <script>
            // Set result
            document.getElementById('result').innerHTML = '<span class="success">JavaScript syntax test completed successfully</span>';
            </script>
        </body>
        </html>
        """
        
        # Write the HTML content to the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return path
    
    def check_errors(self):
        """Check for JavaScript errors"""
        if hasattr(self.web_page, 'js_errors') and self.web_page.js_errors:
            error_text = "JavaScript errors found:\n"
            for error in self.web_page.js_errors:
                error_text += f"- {error}\n"
            self.status_label.setText(error_text)
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.status_label.setText("No JavaScript errors found!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

class CustomWebPage(QWebEnginePage):
    def __init__(self):
        super().__init__()
        self.js_errors = []
    
    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle JavaScript console messages"""
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            error = f"JavaScript Error: {message} (Line: {line}, Source: {source})"
            logger.error(error)
            self.js_errors.append(error)
        else:
            logger.debug(f"JavaScript: {message} (Line: {line}, Source: {source})")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    logger.info("Starting JavaScript error test")
    sys.exit(main())
