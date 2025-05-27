#!/usr/bin/env python3
"""
Test Enhanced Page Preview
-------------------------
This script tests the enhanced page preview functionality.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer

# Import our custom modules
from page_preview import PagePreview
from enhanced_page_preview import apply_enhanced_preview_fix

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWindow(QMainWindow):
    """Test window for the enhanced page preview"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Page Preview Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create page preview widget
        self.page_preview = PagePreview()
        
        # Apply enhanced page preview fix
        self.page_preview = apply_enhanced_preview_fix(self.page_preview)
        
        # Add page preview to layout
        layout.addWidget(self.page_preview)
        
        # Create test controls
        test_controls = QWidget()
        test_layout = QVBoxLayout(test_controls)
        
        # Add test document button
        load_test_doc_btn = QPushButton("Load Test Document")
        load_test_doc_btn.clicked.connect(self.load_test_document)
        test_layout.addWidget(load_test_doc_btn)
        
        # Add status label
        self.status_label = QLabel("Ready")
        test_layout.addWidget(self.status_label)
        
        # Add test controls to main layout
        layout.addWidget(test_controls)
        
        # Set up timer to load test document automatically
        QTimer.singleShot(500, self.load_test_document)
    
    def load_test_document(self):
        """Load a test document into the page preview"""
        logger.info("Loading test document")
        self.status_label.setText("Loading test document...")
        
        # Create a test HTML document with multiple pages
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Document</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }
                h1 {
                    color: #333;
                }
                p {
                    margin-bottom: 1em;
                }
            </style>
        </head>
        <body>
            <h1>Test Document</h1>
            <p>This is a test document to verify the enhanced page preview functionality.</p>
            <p>The document should be displayed with proper margins and without the "Document" string at the top.</p>
            <p>The title should be aligned with the margin on the rendered page.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 2</h1>
            <p>This is the second page of the test document.</p>
            <p>The page navigation should work correctly, allowing you to navigate between pages.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 3</h1>
            <p>This is the third page of the test document.</p>
            <p>The zoom functionality should work correctly, allowing you to zoom in and out.</p>
            <p>The panning functionality should work correctly, allowing you to pan around the document.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
        </body>
        </html>
        """
        
        # Load the test HTML into the page preview
        self.page_preview.set_html(test_html)
        
        # Update status
        self.status_label.setText("Test document loaded")
        logger.info("Test document loaded")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
