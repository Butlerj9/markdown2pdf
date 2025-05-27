#!/usr/bin/env python3
"""
Test script to verify margin and font settings fixes in page preview
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QSpinBox
from PyQt6.QtCore import Qt

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from page_preview import PagePreview

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MarginTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Margin and Font Settings Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # Margin controls
        controls_layout.addWidget(QLabel("Top Margin:"))
        self.top_margin = QSpinBox()
        self.top_margin.setRange(5, 50)
        self.top_margin.setValue(25)
        self.top_margin.valueChanged.connect(self.update_settings)
        controls_layout.addWidget(self.top_margin)
        
        controls_layout.addWidget(QLabel("Left Margin:"))
        self.left_margin = QSpinBox()
        self.left_margin.setRange(5, 50)
        self.left_margin.setValue(25)
        self.left_margin.valueChanged.connect(self.update_settings)
        controls_layout.addWidget(self.left_margin)
        
        # Font size control
        controls_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.update_settings)
        controls_layout.addWidget(self.font_size)
        
        # Test button
        test_btn = QPushButton("Test Settings")
        test_btn.clicked.connect(self.test_settings)
        controls_layout.addWidget(test_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Create page preview
        self.page_preview = PagePreview()
        layout.addWidget(self.page_preview)
        
        # Set up initial document settings
        self.setup_document_settings()
        
        # Load test content
        self.load_test_content()
        
    def setup_document_settings(self):
        """Set up initial document settings"""
        self.document_settings = {
            "page": {
                "width": 210,
                "height": 297,
                "margins": {
                    "top": self.top_margin.value(),
                    "right": 25,
                    "bottom": 25,
                    "left": self.left_margin.value()
                }
            },
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": self.font_size.value(),
                    "line_height": 1.5
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#ffffff",
                "links": "#0000ff"
            }
        }
        
        # Apply settings to page preview
        self.page_preview.set_document_settings(self.document_settings)
        
    def update_settings(self):
        """Update document settings when controls change"""
        self.document_settings["page"]["margins"]["top"] = self.top_margin.value()
        self.document_settings["page"]["margins"]["left"] = self.left_margin.value()
        self.document_settings["fonts"]["body"]["size"] = self.font_size.value()
        
        # Apply updated settings
        self.page_preview.set_document_settings(self.document_settings)
        
    def test_settings(self):
        """Test the current settings"""
        logger.info("Testing current settings:")
        logger.info(f"Top margin: {self.top_margin.value()}mm")
        logger.info(f"Left margin: {self.left_margin.value()}mm")
        logger.info(f"Font size: {self.font_size.value()}pt")
        
        # Get margin CSS from page preview
        margin_css = self.page_preview.get_margin_css()
        logger.info(f"Generated margin CSS: {margin_css}")
        
        # Get usable dimensions
        width, height = self.page_preview.get_usable_page_dimensions()
        logger.info(f"Usable page dimensions: {width}mm x {height}mm")
        
    def load_test_content(self):
        """Load test content"""
        test_html = """
        <h1>Test Document</h1>
        <p>This is a test document to verify that margin and font settings are working correctly.</p>
        <p>The margins should be adjustable using the controls above, and the font size should also be adjustable.</p>
        <h2>Section 2</h2>
        <p>This content should respect the margin settings and use the specified font size.</p>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
        <h3>Subsection</h3>
        <p>More content to test pagination and margin calculations.</p>
        <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
        <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        """
        
        self.page_preview.update_preview(test_html)

def main():
    app = QApplication(sys.argv)
    
    # Set up Qt for web engine
    from PyQt6.QtCore import QCoreApplication
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    window = MarginTestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
