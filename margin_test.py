#!/usr/bin/env python3
"""
Test script to diagnose margin issues
"""

import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout, QLabel, QSpinBox
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("margin_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarginTestWindow(QMainWindow):
    """Test window for margin testing"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Margin Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create preview widget
        self.preview = PagePreview()
        
        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Create margin controls
        margin_layout = QHBoxLayout()
        
        # Top margin
        margin_layout.addWidget(QLabel("Top Margin (mm):"))
        self.top_margin = QSpinBox()
        self.top_margin.setRange(0, 50)
        self.top_margin.setValue(0)
        margin_layout.addWidget(self.top_margin)
        
        # Right margin
        margin_layout.addWidget(QLabel("Right Margin (mm):"))
        self.right_margin = QSpinBox()
        self.right_margin.setRange(0, 50)
        self.right_margin.setValue(25)
        margin_layout.addWidget(self.right_margin)
        
        # Bottom margin
        margin_layout.addWidget(QLabel("Bottom Margin (mm):"))
        self.bottom_margin = QSpinBox()
        self.bottom_margin.setRange(0, 50)
        self.bottom_margin.setValue(25)
        margin_layout.addWidget(self.bottom_margin)
        
        # Left margin
        margin_layout.addWidget(QLabel("Left Margin (mm):"))
        self.left_margin = QSpinBox()
        self.left_margin.setRange(0, 50)
        self.left_margin.setValue(25)
        margin_layout.addWidget(self.left_margin)
        
        # Apply button
        apply_button = QPushButton("Apply Margins")
        apply_button.clicked.connect(self.apply_margins)
        margin_layout.addWidget(apply_button)
        
        # Debug button
        debug_button = QPushButton("Debug Margins")
        debug_button.clicked.connect(self.debug_margins)
        margin_layout.addWidget(debug_button)
        
        # Add widgets to layout
        layout.addWidget(self.preview, 3)
        layout.addLayout(margin_layout)
        layout.addWidget(self.log_display, 1)
        
        # Set up log handler
        self.log_handler = QTextEditLogger(self.log_display)
        logger.addHandler(self.log_handler)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Load test document
        QTimer.singleShot(500, self.load_test_document)
    
    def setup_document_settings(self):
        """Set up document settings"""
        settings = {
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 11,
                    "line_height": 1.5
                },
                "headings": {
                    "h1": {
                        "family": "Arial",
                        "size": 18,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 12,
                        "margin_bottom": 6
                    },
                    "h2": {
                        "family": "Arial",
                        "size": 16,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 10,
                        "margin_bottom": 5
                    },
                    "h3": {
                        "family": "Arial",
                        "size": 14,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 8,
                        "margin_bottom": 4
                    }
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#ffffff",
                "links": "#0000ff"
            },
            "page": {
                "size": "A4",
                "orientation": "portrait",
                "margins": {
                    "top": 0,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            },
            "paragraphs": {
                "margin_top": 0,
                "margin_bottom": 10,
                "spacing": 1.5,
                "first_line_indent": 0,
                "alignment": "left"
            },
            "lists": {
                "bullet_indent": 20,
                "number_indent": 20,
                "item_spacing": 5,
                "bullet_style_l1": "Disc",
                "bullet_style_l2": "Circle",
                "bullet_style_l3": "Square",
                "number_style_l1": "Decimal",
                "number_style_l2": "Lower Alpha",
                "number_style_l3": "Lower Roman",
                "nested_indent": 20
            },
            "table": {
                "border_color": "#cccccc",
                "header_bg": "#f0f0f0",
                "cell_padding": 5
            },
            "code": {
                "font_family": "Courier New",
                "font_size": 10,
                "background": "#f5f5f5",
                "border_color": "#e0e0e0"
            },
            "format": {
                "technical_numbering": False,
                "numbering_start": 1
            }
        }
        
        # Apply document settings
        self.preview.update_document_settings(settings)
    
    def load_test_document(self):
        """Load a test document with visible top edge markers"""
        logger.info("Loading test document")
        
        # Create test HTML with visible top edge markers
        html = """
        <html>
        <head>
            <style>
            /* Add a visible top edge marker */
            .top-edge-marker {
                background-color: red;
                height: 2px;
                width: 100%;
                margin: 0;
                padding: 0;
            }
            
            /* Add a visible margin indicator */
            .margin-indicator {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
                border: 1px dashed rgba(255, 0, 0, 0.5);
                box-sizing: border-box;
            }
            </style>
        </head>
        <body>
            <div class="top-edge-marker"></div>
            <h1>Margin Test Document</h1>
            <p>This document tests the top margin. The red line should be at the very top of the content area with no margin when top margin is set to 0.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            <div class="top-edge-marker"></div>
            <h1>Page 2</h1>
            <p>This is page 2. The red line should be at the very top of the content area with no margin when top margin is set to 0.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.check_margins)
    
    def apply_margins(self):
        """Apply the current margin settings"""
        logger.info("Applying margins")
        
        # Get margin values
        top = self.top_margin.value()
        right = self.right_margin.value()
        bottom = self.bottom_margin.value()
        left = self.left_margin.value()
        
        logger.info(f"Setting margins: T:{top}mm R:{right}mm B:{bottom}mm L:{left}mm")
        
        # Update document settings
        settings = self.preview.document_settings.copy()
        settings["page"]["margins"] = {
            "top": top,
            "right": right,
            "bottom": bottom,
            "left": left
        }
        
        # Apply document settings
        self.preview.update_document_settings(settings)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.check_margins)
    
    def check_margins(self):
        """Check the current margins"""
        logger.info("Checking margins")
        
        # Get margin values from CSS
        js_result = self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var style = window.getComputedStyle(page);
            return {
                paddingTop: style.paddingTop,
                paddingRight: style.paddingRight,
                paddingBottom: style.paddingBottom,
                paddingLeft: style.paddingLeft,
                marginTop: style.marginTop,
                marginRight: style.marginRight,
                marginBottom: style.marginBottom,
                marginLeft: style.marginLeft
            };
        })()
        """)
        
        logger.info(f"Page CSS margins: {js_result}")
        
        # Check if top edge marker is visible
        top_edge = self.preview.execute_js("""
        (function() {
            var marker = document.querySelector('.top-edge-marker');
            if (!marker) return 'No marker found';
            
            var rect = marker.getBoundingClientRect();
            var page = document.querySelector('.page');
            var pageRect = page.getBoundingClientRect();
            
            return {
                markerTop: rect.top,
                markerHeight: rect.height,
                pageTop: pageRect.top,
                offsetFromPageTop: rect.top - pageRect.top
            };
        })()
        """)
        
        logger.info(f"Top edge marker position: {top_edge}")
        
        # Add a visual margin indicator
        self.preview.execute_js("""
        (function() {
            // Remove any existing indicators
            var oldIndicator = document.querySelector('.margin-indicator');
            if (oldIndicator) oldIndicator.remove();
            
            // Add a new indicator
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var indicator = document.createElement('div');
            indicator.className = 'margin-indicator';
            page.appendChild(indicator);
            
            return 'Margin indicator added';
        })()
        """)
    
    def debug_margins(self):
        """Debug margins with detailed information"""
        logger.info("Debugging margins")
        
        # Get detailed margin information
        js_result = self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var style = window.getComputedStyle(page);
            var firstChild = page.firstElementChild;
            var firstChildStyle = firstChild ? window.getComputedStyle(firstChild) : null;
            
            // Get CSS variables
            var root = document.documentElement;
            var rootStyle = window.getComputedStyle(root);
            
            return {
                // Page dimensions
                pageWidth: page.offsetWidth,
                pageHeight: page.offsetHeight,
                
                // Page style
                paddingTop: style.paddingTop,
                paddingRight: style.paddingRight,
                paddingBottom: style.paddingBottom,
                paddingLeft: style.paddingLeft,
                
                // First child style
                firstChildType: firstChild ? firstChild.tagName : 'None',
                firstChildMarginTop: firstChildStyle ? firstChildStyle.marginTop : 'N/A',
                firstChildPaddingTop: firstChildStyle ? firstChildStyle.paddingTop : 'N/A',
                
                // CSS variables
                cssMarginTop: rootStyle.getPropertyValue('--margin-top'),
                cssMarginRight: rootStyle.getPropertyValue('--margin-right'),
                cssMarginBottom: rootStyle.getPropertyValue('--margin-bottom'),
                cssMarginLeft: rootStyle.getPropertyValue('--margin-left'),
                
                // Box model
                boxSizing: style.boxSizing,
                
                // Computed values
                computedPaddingTop: parseFloat(style.paddingTop),
                computedPaddingRight: parseFloat(style.paddingRight),
                computedPaddingBottom: parseFloat(style.paddingBottom),
                computedPaddingLeft: parseFloat(style.paddingLeft)
            };
        })()
        """)
        
        logger.info(f"Detailed margin information: {js_result}")
        
        # Check if the page is properly positioned
        position = self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var rect = page.getBoundingClientRect();
            var container = document.querySelector('.pages-container') || document.body;
            var containerRect = container.getBoundingClientRect();
            
            return {
                pageTop: rect.top,
                pageLeft: rect.left,
                containerTop: containerRect.top,
                containerLeft: containerRect.left,
                offsetFromContainer: {
                    top: rect.top - containerRect.top,
                    left: rect.left - containerRect.left
                }
            };
        })()
        """)
        
        logger.info(f"Page position: {position}")

class QTextEditLogger(logging.Handler):
    """Logger that outputs to a QTextEdit"""
    
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = MarginTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
