#!/usr/bin/env python3
"""
Test JavaScript Syntax Errors
--------------------------
Script to test for JavaScript syntax errors in page_preview.py
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
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
        self.setWindowTitle("JavaScript Syntax Error Test")
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
        
        # Add test buttons
        self.test1_button = QPushButton("Test 1: Basic JavaScript")
        self.test1_button.clicked.connect(self.run_test1)
        layout.addWidget(self.test1_button)
        
        self.test2_button = QPushButton("Test 2: Object Literals")
        self.test2_button.clicked.connect(self.run_test2)
        layout.addWidget(self.test2_button)
        
        self.test3_button = QPushButton("Test 3: Control Structures")
        self.test3_button.clicked.connect(self.run_test3)
        layout.addWidget(self.test3_button)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Run the first test automatically
        self.run_test1()
    
    def run_test1(self):
        """Run basic JavaScript test"""
        print("\n=== Running Test 1: Basic JavaScript ===")
        
        # Variables for testing
        zoom_factor = 0.9
        page_width = 210
        page_height = 297
        
        # Create JavaScript
        js_code = """
        (function() {
            console.log('Test 1: Basic JavaScript');
            
            var zoomFactor = %s;
            var pageWidth = %s;
            var pageHeight = %s;
            
            console.log('Zoom factor: ' + zoomFactor);
            console.log('Page dimensions: ' + pageWidth + 'x' + pageHeight);
            
            console.log('Test 1 completed successfully');
        })();
        """ % (zoom_factor, page_width, page_height)
        
        # Create HTML with the JavaScript
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript Syntax Error Test</title>
        </head>
        <body>
            <h1>Test 1: Basic JavaScript</h1>
            <div id="output"></div>
            
            <script>
            %s
            document.getElementById('output').innerHTML = 'Test 1 completed successfully';
            </script>
        </body>
        </html>
        """ % js_code
        
        # Load the HTML
        self.web_view.setHtml(html)
    
    def run_test2(self):
        """Run object literals test"""
        print("\n=== Running Test 2: Object Literals ===")
        
        # Create JavaScript
        js_code = """
        (function() {
            console.log('Test 2: Object Literals');
            
            // Create a page cache object
            window.pageCache = {
                pages: document.querySelectorAll('.page'),
                totalPages: document.querySelectorAll('.page').length,
                currentPage: document.querySelector('.page.current-page'),
                lastUpdate: Date.now()
            };
            
            console.log('Page cache created');
            
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
            
            console.log('Test 2 completed successfully');
        })();
        """
        
        # Create HTML with the JavaScript
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript Syntax Error Test</title>
        </head>
        <body>
            <h1>Test 2: Object Literals</h1>
            <div id="output"></div>
            
            <script>
            %s
            document.getElementById('output').innerHTML = 'Test 2 completed successfully';
            </script>
        </body>
        </html>
        """ % js_code
        
        # Load the HTML
        self.web_view.setHtml(html)
    
    def run_test3(self):
        """Run control structures test"""
        print("\n=== Running Test 3: Control Structures ===")
        
        # Create JavaScript
        js_code = """
        (function() {
            console.log('Test 3: Control Structures');
            
            // Test if statement
            var totalPages = 3;
            
            if (totalPages === 0) {
                console.error('No pages found');
            } else {
                console.log('Found ' + totalPages + ' pages');
            }
            
            // Test for loop
            for (var i = 0; i < totalPages; i++) {
                console.log('Processing page ' + (i + 1));
            }
            
            console.log('Test 3 completed successfully');
        })();
        """
        
        # Create HTML with the JavaScript
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript Syntax Error Test</title>
        </head>
        <body>
            <h1>Test 3: Control Structures</h1>
            <div id="output"></div>
            
            <script>
            %s
            document.getElementById('output').innerHTML = 'Test 3 completed successfully';
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
