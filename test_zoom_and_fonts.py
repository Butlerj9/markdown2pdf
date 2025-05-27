#!/usr/bin/env python3
"""
Test script to verify zoom and font functionality in the page preview component.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZoomFontTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoom and Font Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # Font selection
        font_label = QLabel("Font:")
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Arial",
            "Times New Roman", 
            "Georgia",
            "Helvetica",
            "Courier New",
            "Verdana"
        ])
        self.font_combo.currentTextChanged.connect(self.change_font)
        
        # Font size selection
        size_label = QLabel("Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["10", "11", "12", "14", "16", "18", "20", "24"])
        self.size_combo.setCurrentText("12")
        self.size_combo.currentTextChanged.connect(self.change_font_size)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_50_btn = QPushButton("50%")
        zoom_75_btn = QPushButton("75%")
        zoom_100_btn = QPushButton("100%")
        zoom_125_btn = QPushButton("125%")
        zoom_150_btn = QPushButton("150%")
        
        zoom_50_btn.clicked.connect(lambda: self.set_zoom(50))
        zoom_75_btn.clicked.connect(lambda: self.set_zoom(75))
        zoom_100_btn.clicked.connect(lambda: self.set_zoom(100))
        zoom_125_btn.clicked.connect(lambda: self.set_zoom(125))
        zoom_150_btn.clicked.connect(lambda: self.set_zoom(150))
        
        # Add controls to layout
        controls_layout.addWidget(font_label)
        controls_layout.addWidget(self.font_combo)
        controls_layout.addWidget(size_label)
        controls_layout.addWidget(self.size_combo)
        controls_layout.addWidget(zoom_label)
        controls_layout.addWidget(zoom_50_btn)
        controls_layout.addWidget(zoom_75_btn)
        controls_layout.addWidget(zoom_100_btn)
        controls_layout.addWidget(zoom_125_btn)
        controls_layout.addWidget(zoom_150_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Create page preview
        self.page_preview = PagePreview()
        layout.addWidget(self.page_preview)
        
        # Set up document settings
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
                    "top": 25,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            },
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 12
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
        
    def load_test_content(self):
        """Load test HTML content"""
        test_html = """
        <h1>Font and Zoom Test</h1>
        <p>This is a test paragraph to verify that font changes are properly applied to the page preview.</p>
        <p>The current font should be: <strong>Arial, 12pt</strong></p>
        <p>Use the controls above to change the font family and size, and test the zoom functionality.</p>
        
        <h2>Sample Content</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
        <ul>
            <li>First item</li>
            <li>Second item</li>
            <li>Third item</li>
        </ul>
        
        <h3>Code Example</h3>
        <pre><code>def hello_world():
    print("Hello, World!")
    return True</code></pre>
        
        <p>This content should reflect any font and zoom changes immediately.</p>
        """
        
        self.page_preview.update_preview(test_html)
        
    def change_font(self, font_family):
        """Change the font family"""
        logger.info(f"Changing font to: {font_family}")
        self.document_settings["fonts"]["body"]["family"] = font_family
        self.page_preview.update_document_settings(self.document_settings)
        
    def change_font_size(self, font_size):
        """Change the font size"""
        logger.info(f"Changing font size to: {font_size}")
        self.document_settings["fonts"]["body"]["size"] = int(font_size)
        self.page_preview.update_document_settings(self.document_settings)
        
    def set_zoom(self, zoom_percent):
        """Set the zoom level"""
        logger.info(f"Setting zoom to: {zoom_percent}%")
        self.page_preview.update_zoom(zoom_percent)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = ZoomFontTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
