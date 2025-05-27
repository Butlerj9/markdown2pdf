#!/usr/bin/env python3
"""
Test script that simulates the main application's environment
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer
from page_preview import PagePreview
from zoom_fix_minimal import apply_zoom_fix
from logging_config import get_logger

logger = get_logger()

class TestMainAppWindow(QMainWindow):
    """Test window that simulates the main application's environment"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App Simulation")
        self.setGeometry(100, 100, 1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create page preview
        self.preview = PagePreview()
        
        # Set up zoom controls in a separate layout
        preview_layout = QVBoxLayout()
        self.preview.setup_zoom_controls(preview_layout)
        layout.addLayout(preview_layout)
        
        # Apply zoom fix
        self.preview = apply_zoom_fix(self.preview)
        
        layout.addWidget(self.preview)
        
        # Create test controls
        controls_layout = QVBoxLayout()
        
        # Add test buttons
        test_btn = QPushButton("Load Test Content")
        test_btn.clicked.connect(self.load_test_content)
        controls_layout.addWidget(test_btn)
        
        # Add controls to main layout
        layout.addLayout(controls_layout)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Load initial test content
        QTimer.singleShot(500, self.load_test_content)
    
    def setup_document_settings(self):
        """Set up document settings for testing"""
        self.document_settings = {
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 11,
                    "line_height": 1.5
                },
                "headings": {
                    "h1": {
                        "family": "Arial",
                        "size": 24,
                        "color": "#000000",
                        "spacing": 0,
                        "margin_top": 24,
                        "margin_bottom": 12
                    },
                    "h2": {
                        "family": "Arial",
                        "size": 20,
                        "color": "#000000",
                        "spacing": 0,
                        "margin_top": 18,
                        "margin_bottom": 10
                    },
                    "h3": {
                        "family": "Arial",
                        "size": 16,
                        "color": "#000000",
                        "spacing": 0,
                        "margin_top": 14,
                        "margin_bottom": 8
                    }
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#ffffff",
                "links": "#0000ff"
            },
            "paragraphs": {
                "margin_top": 0,
                "margin_bottom": 10,
                "first_line_indent": 0,
                "alignment": "left"
            },
            "code": {
                "font_family": "Courier New",
                "font_size": 10
            },
            "page": {
                "size": "A4",
                "orientation": "portrait",
                "width": 210,
                "height": 297,
                "margins": {
                    "top": 25,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            }
        }
        
        # Apply settings to preview
        self.preview.set_document_settings(self.document_settings)
    
    def load_test_content(self):
        """Load test content into the preview"""
        logger.info("Loading test content")
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Main App Simulation</title>
            <meta charset="utf-8">
        </head>
        <body>
            <div class="page">
                <h1>Main App Simulation</h1>
                <p>This is a test document to verify the zoom fix implementation in the main application's environment.</p>
                
                <h2>Instructions</h2>
                <p>Use the zoom controls to zoom in and out. The page should maintain its proportions and stay centered in the preview area.</p>
                
                <h2>Test Content</h2>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                
                <h3>Code Block</h3>
                <pre><code>
                def hello_world():
                    print("Hello, world!")
                </code></pre>
                
                <h3>Table</h3>
                <table border="1">
                    <thead>
                        <tr>
                            <th>Header 1</th>
                            <th>Header 2</th>
                            <th>Header 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Row 1, Cell 1</td>
                            <td>Row 1, Cell 2</td>
                            <td>Row 1, Cell 3</td>
                        </tr>
                        <tr>
                            <td>Row 2, Cell 1</td>
                            <td>Row 2, Cell 2</td>
                            <td>Row 2, Cell 3</td>
                        </tr>
                    </tbody>
                </table>
                
                <p>End of test document.</p>
            </div>
        </body>
        </html>
        """
        
        self.preview.load_html(html_content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainAppWindow()
    window.show()
    sys.exit(app.exec())