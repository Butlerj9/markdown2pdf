#!/usr/bin/env python3
"""
Test Page Layout Script
----------------------
A simplified test script to diagnose JavaScript issues in the page layout script.
"""

import sys
import os
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit
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
    """Test window for page layout script debugging"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Layout Test")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Create script editor
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("Enter JavaScript to test...")
        self.script_editor.setMinimumHeight(200)
        
        # Add test buttons
        self.load_button = QPushButton("Load Basic HTML")
        self.load_button.clicked.connect(self.load_basic_html)
        
        self.test_button = QPushButton("Run Script")
        self.test_button.clicked.connect(self.run_script)
        
        self.simplified_button = QPushButton("Run Simplified Page Layout")
        self.simplified_button.clicked.connect(self.run_simplified_layout)
        
        # Add widgets to layout
        layout.addWidget(self.load_button)
        layout.addWidget(self.simplified_button)
        layout.addWidget(self.script_editor)
        layout.addWidget(self.test_button)
        layout.addWidget(self.web_view)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Load initial HTML
        self.load_basic_html()
        
        # Set initial script
        self.script_editor.setText("""
(function() {
    // Get or create the style element
    var style = document.getElementById('test-style');
    if (!style) {
        style = document.createElement('style');
        style.id = 'test-style';
        document.head.appendChild(style);
    }
    
    // Apply basic styling
    style.textContent = 
        'body { background-color: #e0e0e0; padding: 20px; }' +
        '.page { background-color: white; margin: 20px auto; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }' +
        'h1 { color: #2c3e50; }' +
        'h2 { color: #3498db; }' +
        'h3 { color: #e74c3c; }';
    
    console.log('Applied test styling');
})();
        """)
    
    def load_basic_html(self):
        """Load basic HTML content"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Page Layout Test</title>
        </head>
        <body>
            <div class="page">
                <h1>Heading 1</h1>
                <p>This is a paragraph with some text. The text should be properly formatted and styled.</p>
                <h2>Heading 2</h2>
                <p>Another paragraph with more text. This text should also be properly formatted.</p>
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                    <li>List item 3</li>
                </ul>
                <h3>Heading 3</h3>
                <p>A third paragraph with even more text. This text should be properly formatted as well.</p>
            </div>
            <div class="page">
                <h2>Second Page</h2>
                <p>This is the second page of the document. It should be properly styled as well.</p>
                <ol>
                    <li>Numbered item 1</li>
                    <li>Numbered item 2</li>
                    <li>Numbered item 3</li>
                </ol>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def run_script(self):
        """Run the script from the editor"""
        script = self.script_editor.toPlainText()
        self.execute_js(script)
    
    def run_simplified_layout(self):
        """Run a simplified version of the page layout script"""
        script = """
        (function() {
            console.log('Running simplified page layout script');
            
            try {
                // Get or create the style element
                var style = document.getElementById('page-style');
                if (!style) {
                    style = document.createElement('style');
                    style.id = 'page-style';
                    document.head.appendChild(style);
                }
                
                // Apply basic styling with regular string concatenation
                style.textContent = 
                    'body { background-color: #e0e0e0; padding: 40px; margin: 0; display: flex; flex-direction: column; align-items: center; }' +
                    '.page { background-color: white; width: 210mm; min-height: 297mm; margin: 0 0 40px 0; padding: 25mm; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); box-sizing: border-box; position: relative; border: 1px solid #ccc; }' +
                    '.page h1 { color: #2c3e50; font-family: Arial, sans-serif; }' +
                    '.page h2 { color: #3498db; font-family: Arial, sans-serif; }' +
                    '.page h3 { color: #e74c3c; font-family: Arial, sans-serif; }';
                
                console.log('Applied page styling');
                
                // Create a container for all pages
                var pagesContainer = document.createElement('div');
                pagesContainer.className = 'pages-container';
                pagesContainer.style.display = 'flex';
                pagesContainer.style.flexDirection = 'column';
                pagesContainer.style.alignItems = 'center';
                pagesContainer.style.width = '100%';
                
                // Get all existing pages
                var pages = document.querySelectorAll('.page');
                console.log('Found ' + pages.length + ' pages');
                
                // Save the original body content
                var originalContent = document.body.innerHTML;
                
                // Clear the body
                document.body.innerHTML = '';
                
                // Add the pages container to the body
                document.body.appendChild(pagesContainer);
                
                // Add each page to the container
                pages.forEach(function(page, index) {
                    pagesContainer.appendChild(page);
                    
                    // Add page number
                    var pageNumber = document.createElement('div');
                    pageNumber.style.position = 'absolute';
                    pageNumber.style.bottom = '10px';
                    pageNumber.style.right = '10px';
                    pageNumber.style.fontSize = '12px';
                    pageNumber.style.color = '#666';
                    pageNumber.textContent = 'Page ' + (index + 1) + ' of ' + pages.length;
                    page.appendChild(pageNumber);
                });
                
                console.log('Page layout applied successfully');
                return 'Success';
            } catch (e) {
                console.error('Error applying page layout:', e);
                return 'Error: ' + e.message;
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
