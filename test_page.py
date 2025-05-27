#!/usr/bin/env python3
"""
Test Page for JavaScript Debugging
---------------------------------
A simple test script to diagnose JavaScript issues in the page preview.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl
from logging_config import get_logger

logger = get_logger()

class CustomWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage that logs JavaScript console messages with enhanced error reporting"""

    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle console.log messages from JavaScript with detailed error information"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")

        # For errors, provide more detailed logging
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            logger.error(f"JavaScript Error: {message}")
            logger.error(f"  Source: {source}")
            logger.error(f"  Line: {line}")
            
            # Extract the specific syntax error if possible
            if "SyntaxError" in message:
                error_parts = message.split(":")
                if len(error_parts) > 1:
                    error_type = error_parts[0].strip()
                    error_detail = ":".join(error_parts[1:]).strip()
                    logger.error(f"  Error Type: {error_type}")
                    logger.error(f"  Error Detail: {error_detail}")
        else:
            logger.debug(f"JS Console ({level_str}): {message} [{source}:{line}]")
            
        super().javaScriptConsoleMessage(level, message, line, source)

class TestWindow(QMainWindow):
    """Test window for JavaScript debugging"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JavaScript Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Add test buttons
        self.test1_button = QPushButton("Test 1: Basic JavaScript")
        self.test1_button.clicked.connect(self.run_test1)
        
        self.test2_button = QPushButton("Test 2: Template Literals")
        self.test2_button.clicked.connect(self.run_test2)
        
        self.test3_button = QPushButton("Test 3: DOM Manipulation")
        self.test3_button.clicked.connect(self.run_test3)
        
        # Add widgets to layout
        layout.addWidget(self.test1_button)
        layout.addWidget(self.test2_button)
        layout.addWidget(self.test3_button)
        layout.addWidget(self.web_view)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Load initial HTML
        self.load_initial_html()
    
    def load_initial_html(self):
        """Load initial HTML content"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>JavaScript Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 20px;
                    background-color: #f0f0f0;
                }
                .result {
                    margin-top: 20px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    background-color: white;
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
            <h1>JavaScript Test Page</h1>
            <p>Click the buttons above to run different JavaScript tests.</p>
            <div id="result" class="result">
                <p>Results will appear here...</p>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def run_test1(self):
        """Run basic JavaScript test"""
        script = """
        (function() {
            console.log('Running Test 1: Basic JavaScript');
            
            // Basic operations
            var a = 5;
            var b = 10;
            var c = a + b;
            
            // Update result
            var resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<p class="success">Test 1 Successful!</p>';
            resultDiv.innerHTML += '<p>5 + 10 = ' + c + '</p>';
            
            return 'Test 1 completed';
        })();
        """
        self.execute_js(script)
    
    def run_test2(self):
        """Run template literals test"""
        script = """
        (function() {
            console.log('Running Test 2: Template Literals');
            
            try {
                // Test with regular string concatenation
                var name = 'World';
                var greeting = 'Hello, ' + name + '!';
                
                // Update result
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p class="success">Test 2 Successful!</p>';
                resultDiv.innerHTML += '<p>Regular concatenation: ' + greeting + '</p>';
                
                // Now try with a template literal-like syntax but using concatenation
                var color = 'blue';
                var style = 'color: ' + color + '; font-weight: bold;';
                resultDiv.innerHTML += '<p style="' + style + '">Styled text using concatenation</p>';
                
                return 'Test 2 completed';
            } catch (e) {
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p class="error">Test 2 Failed: ' + e.message + '</p>';
                console.error('Test 2 error:', e);
                return 'Test 2 failed: ' + e.message;
            }
        })();
        """
        self.execute_js(script)
    
    def run_test3(self):
        """Run DOM manipulation test"""
        script = """
        (function() {
            console.log('Running Test 3: DOM Manipulation');
            
            try {
                // Create elements
                var container = document.createElement('div');
                container.className = 'test-container';
                container.style.border = '1px solid #ddd';
                container.style.padding = '10px';
                container.style.marginTop = '10px';
                
                // Create heading
                var heading = document.createElement('h3');
                heading.textContent = 'DOM Test';
                heading.style.color = '#333';
                container.appendChild(heading);
                
                // Create paragraph
                var paragraph = document.createElement('p');
                paragraph.textContent = 'This paragraph was created dynamically.';
                container.appendChild(paragraph);
                
                // Update result
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p class="success">Test 3 Successful!</p>';
                resultDiv.appendChild(container);
                
                return 'Test 3 completed';
            } catch (e) {
                var resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p class="error">Test 3 Failed: ' + e.message + '</p>';
                console.error('Test 3 error:', e);
                return 'Test 3 failed: ' + e.message;
            }
        })();
        """
        self.execute_js(script)
    
    def execute_js(self, script):
        """Execute JavaScript in the web view"""
        try:
            logger.debug(f"Executing JavaScript: {script[:50]}...")
            self.web_page.runJavaScript(script, self.handle_js_result)
        except Exception as e:
            logger.error(f"Error executing JavaScript: {str(e)}")
    
    def handle_js_result(self, result):
        """Handle JavaScript execution result"""
        logger.debug(f"JavaScript execution result: {result}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
