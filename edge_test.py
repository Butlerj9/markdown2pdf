#!/usr/bin/env python3
"""
Test script to ensure the top edge of the page is visible
"""

import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout, QLabel, QSpinBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("edge_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EdgeTestWindow(QMainWindow):
    """Test window for page edge visibility"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Edge Test")
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
        
        # Create control buttons
        button_layout = QHBoxLayout()
        
        # Test with zero margins
        zero_margin_btn = QPushButton("Test Zero Margins")
        zero_margin_btn.clicked.connect(self.test_zero_margins)
        button_layout.addWidget(zero_margin_btn)
        
        # Test with normal margins
        normal_margin_btn = QPushButton("Test Normal Margins")
        normal_margin_btn.clicked.connect(self.test_normal_margins)
        button_layout.addWidget(normal_margin_btn)
        
        # Add debug button
        debug_btn = QPushButton("Debug Page Layout")
        debug_btn.clicked.connect(self.debug_page_layout)
        button_layout.addWidget(debug_btn)
        
        # Add scroll to top button
        scroll_top_btn = QPushButton("Scroll to Top")
        scroll_top_btn.clicked.connect(self.scroll_to_top)
        button_layout.addWidget(scroll_top_btn)
        
        # Add widgets to layout
        layout.addWidget(self.preview, 3)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_display, 1)
        
        # Set up log handler
        self.log_handler = QTextEditLogger(self.log_display)
        logger.addHandler(self.log_handler)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Load test document
        QTimer.singleShot(500, self.test_zero_margins)
    
    def setup_document_settings(self, top_margin=0):
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
                    "top": top_margin,
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
    
    def create_test_html(self, with_border=True):
        """Create test HTML with visible page edges"""
        border_style = """
        <style>
        /* Add page border to visualize edges */
        .page-border {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid red;
            pointer-events: none;
            z-index: 1000;
        }
        
        /* Add top edge marker */
        .top-edge {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background-color: red;
            z-index: 1001;
        }
        
        /* Add ruler markers */
        .ruler-marker {
            position: absolute;
            width: 100%;
            height: 1px;
            background-color: rgba(0, 0, 255, 0.5);
            z-index: 1002;
        }
        
        .ruler-label {
            position: absolute;
            left: 5px;
            color: blue;
            font-size: 8px;
            z-index: 1003;
        }
        </style>
        """ if with_border else ""
        
        html = f"""
        <html>
        <head>
            {border_style}
        </head>
        <body>
            <h1>Page Edge Test</h1>
            <p>This document tests the visibility of page edges. The top edge of the page should be visible.</p>
            <p>The red border shows the page boundaries. The red bar at the top is the top edge of the page.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            <h1>Page 2</h1>
            <p>This is page 2. The top edge should also be visible here.</p>
        </body>
        </html>
        """
        
        return html
    
    def test_zero_margins(self):
        """Test with zero margins"""
        logger.info("Testing with zero margins")
        
        # Set up document settings with zero top margin
        self.setup_document_settings(top_margin=0)
        
        # Create test HTML
        html = self.create_test_html()
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def test_normal_margins(self):
        """Test with normal margins"""
        logger.info("Testing with normal margins")
        
        # Set up document settings with normal top margin
        self.setup_document_settings(top_margin=25)
        
        # Create test HTML
        html = self.create_test_html()
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def add_page_indicators(self):
        """Add visual indicators to show page boundaries"""
        logger.info("Adding page indicators")
        
        # Add visual indicators with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Add border to each page
            var pages = document.querySelectorAll('.page');
            if (!pages.length) return 'No pages found';
            
            pages.forEach(function(page, index) {
                // Remove any existing indicators
                var existingBorder = page.querySelector('.page-border');
                if (existingBorder) existingBorder.remove();
                
                var existingTopEdge = page.querySelector('.top-edge');
                if (existingTopEdge) existingTopEdge.remove();
                
                // Add page border
                var border = document.createElement('div');
                border.className = 'page-border';
                page.appendChild(border);
                
                // Add top edge marker
                var topEdge = document.createElement('div');
                topEdge.className = 'top-edge';
                page.appendChild(topEdge);
                
                // Add ruler markers every 10mm
                for (var i = 0; i <= 100; i += 10) {
                    var marker = document.createElement('div');
                    marker.className = 'ruler-marker';
                    marker.style.top = i + 'mm';
                    page.appendChild(marker);
                    
                    var label = document.createElement('div');
                    label.className = 'ruler-label';
                    label.style.top = i + 'mm';
                    label.textContent = i + 'mm';
                    page.appendChild(label);
                }
            });
            
            return 'Added indicators to ' + pages.length + ' pages';
        })()
        """)
        
        logger.info(f"Page indicators result: {js_result}")
        
        # Scroll to top
        self.scroll_to_top()
        
        # Debug page layout
        self.debug_page_layout()
    
    def debug_page_layout(self):
        """Debug page layout with detailed information"""
        logger.info("Debugging page layout")
        
        # Get detailed page layout information
        js_result = self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var style = window.getComputedStyle(page);
            var rect = page.getBoundingClientRect();
            var container = page.parentElement;
            var containerRect = container ? container.getBoundingClientRect() : null;
            
            // Get CSS variables
            var root = document.documentElement;
            var rootStyle = window.getComputedStyle(root);
            
            // Get first element
            var firstElement = page.firstElementChild;
            var firstElementStyle = firstElement ? window.getComputedStyle(firstElement) : null;
            var firstElementRect = firstElement ? firstElement.getBoundingClientRect() : null;
            
            return {
                // Page dimensions
                pageWidth: page.offsetWidth,
                pageHeight: page.offsetHeight,
                pageBoundingRect: {
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height
                },
                
                // Container dimensions
                containerBoundingRect: containerRect ? {
                    top: containerRect.top,
                    right: containerRect.right,
                    bottom: containerRect.bottom,
                    left: containerRect.left,
                    width: containerRect.width,
                    height: containerRect.height
                } : 'No container',
                
                // Page style
                paddingTop: style.paddingTop,
                paddingRight: style.paddingRight,
                paddingBottom: style.paddingBottom,
                paddingLeft: style.paddingLeft,
                marginTop: style.marginTop,
                marginRight: style.marginRight,
                marginBottom: style.marginBottom,
                marginLeft: style.marginLeft,
                
                // First element
                firstElementType: firstElement ? firstElement.tagName : 'None',
                firstElementBoundingRect: firstElementRect ? {
                    top: firstElementRect.top,
                    right: firstElementRect.right,
                    bottom: firstElementRect.bottom,
                    left: firstElementRect.left,
                    width: firstElementRect.width,
                    height: firstElementRect.height
                } : 'No first element',
                firstElementMarginTop: firstElementStyle ? firstElementStyle.marginTop : 'N/A',
                firstElementPaddingTop: firstElementStyle ? firstElementStyle.paddingTop : 'N/A',
                
                // CSS variables
                cssMarginTop: rootStyle.getPropertyValue('--margin-top'),
                cssMarginRight: rootStyle.getPropertyValue('--margin-right'),
                cssMarginBottom: rootStyle.getPropertyValue('--margin-bottom'),
                cssMarginLeft: rootStyle.getPropertyValue('--margin-left'),
                
                // Scroll position
                scrollTop: document.documentElement.scrollTop,
                scrollLeft: document.documentElement.scrollLeft,
                
                // Viewport
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight
            };
        })()
        """)
        
        logger.info(f"Page layout debug info: {js_result}")
    
    def scroll_to_top(self):
        """Scroll to the top of the page"""
        logger.info("Scrolling to top")
        
        # Scroll to top with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Scroll to top
            window.scrollTo(0, 0);
            
            // Also scroll the container if it exists
            var container = document.querySelector('.pages-container');
            if (container) container.scrollTop = 0;
            
            return 'Scrolled to top';
        })()
        """)
        
        logger.info(f"Scroll result: {js_result}")

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
    window = EdgeTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
