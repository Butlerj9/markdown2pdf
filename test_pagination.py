#!/usr/bin/env python3
"""
Test script for pagination in page preview
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaginationTestWindow(QMainWindow):
    """Test window for pagination"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pagination Test")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create page preview
        self.preview = PagePreview(self)
        layout.addWidget(self.preview)
        
        # Create control buttons
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)
        
        # Add navigation buttons
        self.prev_btn = QPushButton("Previous Page")
        self.prev_btn.clicked.connect(self.go_to_previous_page)
        control_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next Page")
        self.next_btn.clicked.connect(self.go_to_next_page)
        control_layout.addWidget(self.next_btn)
        
        # Add page info label
        self.page_info = QLabel("Page: 0 / 0")
        control_layout.addWidget(self.page_info)
        
        # Add test buttons
        test_btn = QPushButton("Load Test Content")
        test_btn.clicked.connect(self.load_test_content)
        control_layout.addWidget(test_btn)
        
        test_page_breaks_btn = QPushButton("Test Page Breaks")
        test_page_breaks_btn.clicked.connect(self.test_page_breaks)
        control_layout.addWidget(test_page_breaks_btn)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Schedule initial test
        QTimer.singleShot(500, self.load_test_content)
    
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
        self.preview.set_document_settings(self.document_settings)
    
    def load_test_content(self):
        """Load test content with multiple pages"""
        logger.info("Loading test content with multiple pages")
        
        test_html = """
        <html>
        <head>
            <title>Pagination Test</title>
        </head>
        <body>
            <h1>Page 1</h1>
            <p>This is the content of page 1.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 2</h1>
            <p>This is the content of page 2.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 3</h1>
            <p>This is the content of page 3.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(test_html)
        logger.info("Test content loaded")
        
        # Update page info after a delay
        QTimer.singleShot(1000, self.update_page_info)
    
    def update_page_info(self):
        """Update page info label"""
        try:
            current_page = self.preview.page_entry.value()
            total_pages = int(self.preview.total_pages_label.text())
            self.page_info.setText(f"Page: {current_page} / {total_pages}")
        except Exception as e:
            logger.error(f"Error updating page info: {str(e)}")
    
    def go_to_previous_page(self):
        """Go to the previous page"""
        logger.info("Going to previous page")
        self.preview.go_to_previous_page()
        QTimer.singleShot(500, self.update_page_info)
    
    def go_to_next_page(self):
        """Go to the next page"""
        logger.info("Going to next page")
        self.preview.go_to_next_page()
        QTimer.singleShot(500, self.update_page_info)
    
    def test_page_breaks(self):
        """Test page breaks"""
        logger.info("Testing page breaks")
        try:
            result = self.preview.test_page_breaks()
            logger.info(f"Page break test result: {result}")
        except Exception as e:
            logger.error(f"Error testing page breaks: {str(e)}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = PaginationTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
