#!/usr/bin/env python3
"""
Simple test script to verify JavaScript syntax
"""

import os
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys

class SimpleTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple JavaScript Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Create test HTML with JavaScript
        self.create_test_html()
        
    def create_test_html(self):
        # Variables that would be inserted into JavaScript
        page_width = 210
        page_height = 297
        margin_top = 25
        margin_right = 25
        margin_bottom = 25
        margin_left = 25
        zoom_factor = 0.9
        
        # Create JavaScript with the variables
        js_script = f"""
        (function() {{
            console.log('Testing JavaScript syntax');
            
            // Convert mm to px (assuming 96 DPI, 1 inch = 25.4 mm)
            var mmToPx = 96 / 25.4;
            var pageWidthMM = {page_width};
            var pageHeightMM = {page_height};
            var marginTopMM = {margin_top};
            var marginRightMM = {margin_right};
            var marginBottomMM = {margin_bottom};
            var marginLeftMM = {margin_left};
            var pageWidthPx = pageWidthMM * mmToPx;
            var pageHeightPx = pageHeightMM * mmToPx;
            var marginTopPx = marginTopMM * mmToPx;
            var marginRightPx = marginRightMM * mmToPx;
            var marginBottomPx = marginBottomMM * mmToPx;
            var marginLeftPx = marginLeftMM * mmToPx;
            
            console.log('Page dimensions (mm): ' + pageWidthMM + 'x' + pageHeightMM);
            console.log('Page dimensions (px): ' + pageWidthPx + 'x' + pageHeightPx);
            console.log('Margins (mm): T:' + marginTopMM + ' R:' + marginRightMM + ' B:' + marginBottomMM + ' L:' + marginLeftMM);
            
            // Set CSS variables for page dimensions and zoom
            document.documentElement.style.setProperty('--page-width', pageWidthMM + 'mm');
            document.documentElement.style.setProperty('--page-height', pageHeightMM + 'mm');
            document.documentElement.style.setProperty('--margin-top', marginTopPx + 'px');
            document.documentElement.style.setProperty('--margin-right', marginRightPx + 'px');
            document.documentElement.style.setProperty('--margin-bottom', marginBottomPx + 'px');
            document.documentElement.style.setProperty('--margin-left', marginLeftPx + 'px');
            var zoomFactor = {zoom_factor};
            document.documentElement.style.setProperty('--zoom-factor', zoomFactor);
            
            // Add styling
            var style = document.createElement('style');
            style.textContent = "/* Root styles */\\n" +
                ":root {{\\n" +
                "    --page-width: " + pageWidthMM + "mm;\\n" +
                "    --page-height: " + pageHeightMM + "mm;\\n" +
                "    --margin-top: " + marginTopMM + "mm;\\n" +
                "    --margin-right: " + marginRightMM + "mm;\\n" +
                "    --margin-bottom: " + marginBottomMM + "mm;\\n" +
                "    --margin-left: " + marginLeftMM + "mm;\\n" +
                "    --zoom-factor: 1;\\n" +
                "}}";
            
            document.head.appendChild(style);
            
            // Create a container
            var container = document.createElement('div');
            container.className = 'container';
            container.style.width = pageWidthMM + 'mm';
            container.style.height = pageHeightMM + 'mm';
            container.style.margin = '20px auto';
            container.style.border = '1px solid #000';
            container.style.position = 'relative';
            
            // Apply zoom
            container.style.transform = 'scale(' + zoomFactor + ')';
            container.style.transformOrigin = 'center top';
            
            // Add content
            container.innerHTML = '<h1>Test Content</h1><p>This is a test of JavaScript syntax.</p>';
            
            // Add to document
            document.body.appendChild(container);
            
            console.log('JavaScript test completed successfully');
            return 'Success';
        }})();
        """
        
        # Create HTML with the JavaScript
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>JavaScript Syntax Test</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f0f0f0;
                }}
            </style>
        </head>
        <body>
            <h1>JavaScript Syntax Test</h1>
            <div id="result"></div>
            
            <script>
            {js_script}
            </script>
        </body>
        </html>
        """
        
        # Create a temporary HTML file
        html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        html_file.write(html_content.encode('utf-8'))
        html_file.close()
        
        # Load the HTML file
        file_url = QUrl.fromLocalFile(html_file.name)
        self.web_view.load(file_url)
        
        # Store the file name for cleanup
        self.temp_file = html_file.name
        
    def closeEvent(self, event):
        # Clean up temporary file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except:
                pass
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = SimpleTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
