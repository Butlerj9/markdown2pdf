#!/usr/bin/env python3
"""
Simple test for page preview functionality
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplePreviewTest(QMainWindow):
    """Simple test window for page preview"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Page Preview Test")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create page preview
        self.page_preview = PagePreview(self)
        layout.addWidget(self.page_preview)
        
        # Create control buttons
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)
        
        # Add test buttons
        test_html_btn = QPushButton("Test HTML")
        test_html_btn.clicked.connect(self.load_test_html)
        control_layout.addWidget(test_html_btn)
        
        test_zoom_btn = QPushButton("Test Zoom")
        test_zoom_btn.clicked.connect(self.test_zoom)
        control_layout.addWidget(test_zoom_btn)
        
        test_pagination_btn = QPushButton("Test Pagination")
        test_pagination_btn.clicked.connect(self.test_pagination)
        control_layout.addWidget(test_pagination_btn)
        
        test_font_color_btn = QPushButton("Test Font/Color")
        test_font_color_btn.clicked.connect(self.test_font_color)
        control_layout.addWidget(test_font_color_btn)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Schedule initial test
        QTimer.singleShot(500, self.load_test_html)
    
    def setup_document_settings(self):
        """Set up document settings"""
        self.document_settings = {
            "page": {
                "size": "A4",
                "width": 210,
                "height": 297,
                "orientation": "portrait",
                "margins": {
                    "top": 25,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            },
            "fonts": {
                "body": {
                    "family": "Arial, sans-serif",
                    "size": 12
                },
                "headings": {
                    "family": "Arial, sans-serif",
                    "size": 16
                }
            },
            "colors": {
                "text": "#333333",
                "background": "#ffffff",
                "links": "#0066cc"
            }
        }
        
        # Apply settings to page preview
        self.page_preview.set_document_settings(self.document_settings)
    
    def load_test_html(self):
        """Load test HTML content"""
        logger.info("Loading test HTML")
        
        test_html = """
        <html>
        <head>
            <title>Test Document</title>
        </head>
        <body>
            <h1>Test Document</h1>
            <p>This is a test document to verify page preview functionality.</p>
            
            <h2>Font and Color Test</h2>
            <p>This paragraph should use the font and color settings from the document settings.</p>
            <p><a href="#">This is a link</a> that should use the link color from the document settings.</p>
            
            <h2>Page Break Test</h2>
            <p>The content below should appear on a new page.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h2>Second Page</h2>
            <p>This content should appear on the second page.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h2>Third Page</h2>
            <p>This content should appear on the third page.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.page_preview.update_preview(test_html)
        logger.info("Test HTML loaded")
    
    def test_zoom(self):
        """Test zoom functionality"""
        logger.info("Testing zoom functionality")
        
        # Test sequence with delays
        QTimer.singleShot(500, self.page_preview.zoom_in)
        QTimer.singleShot(1000, self.page_preview.zoom_in)
        QTimer.singleShot(1500, self.page_preview.fit_to_page)
        QTimer.singleShot(2000, self.page_preview.fit_to_width)
        QTimer.singleShot(2500, self.page_preview.reset_zoom)
    
    def test_pagination(self):
        """Test pagination functionality"""
        logger.info("Testing pagination")
        
        # Test sequence with delays
        QTimer.singleShot(500, lambda: self.page_preview.go_to_page(2))
        QTimer.singleShot(1000, lambda: self.page_preview.go_to_page(3))
        QTimer.singleShot(1500, lambda: self.page_preview.go_to_page(1))
    
    def test_font_color(self):
        """Test font and color settings"""
        logger.info("Testing font and color settings")
        
        # Change font settings
        self.document_settings["fonts"]["body"]["family"] = "Georgia, serif"
        self.document_settings["fonts"]["body"]["size"] = 14
        self.document_settings["colors"]["text"] = "#0000FF"  # Blue text
        self.document_settings["colors"]["links"] = "#FF0000"  # Red links
        
        # Apply new settings
        self.page_preview.update_document_settings(self.document_settings)
        logger.info("Font and color settings updated")
        
        # Reset after delay
        QTimer.singleShot(2000, self.reset_font_color)
    
    def reset_font_color(self):
        """Reset font and color settings"""
        logger.info("Resetting font and color settings")
        
        # Reset settings
        self.document_settings["fonts"]["body"]["family"] = "Arial, sans-serif"
        self.document_settings["fonts"]["body"]["size"] = 12
        self.document_settings["colors"]["text"] = "#333333"
        self.document_settings["colors"]["links"] = "#0066cc"
        
        # Apply reset settings
        self.page_preview.update_document_settings(self.document_settings)
        logger.info("Font and color settings reset")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = SimplePreviewTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
