#!/usr/bin/env python3
"""
Focused test for debugging margin issues
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
        logging.FileHandler("margin_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MarginDebugWindow(QMainWindow):
    """Test window for debugging margin issues"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Margin Debug")
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
    
    def setup_document_settings(self, top=0, right=25, bottom=25, left=25):
        """Set up document settings with specified margins"""
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
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
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
        """Load a test document with margin indicators"""
        logger.info("Loading test document")
        
        # Create test HTML with margin indicators
        html = """
        <html>
        <head>
            <style>
            /* Add margin indicators */
            .margin-indicator {
                position: absolute;
                border: 1px dashed rgba(255, 0, 0, 0.5);
                pointer-events: none;
                z-index: 1000;
            }
            
            .top-indicator {
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background-color: rgba(255, 0, 0, 0.2);
                border-bottom: 1px solid red;
            }
            
            .left-indicator {
                top: 0;
                left: 0;
                bottom: 0;
                width: 5px;
                background-color: rgba(0, 0, 255, 0.2);
                border-right: 1px solid blue;
            }
            
            .right-indicator {
                top: 0;
                right: 0;
                bottom: 0;
                width: 5px;
                background-color: rgba(0, 255, 0, 0.2);
                border-left: 1px solid green;
            }
            
            .bottom-indicator {
                bottom: 0;
                left: 0;
                right: 0;
                height: 5px;
                background-color: rgba(255, 255, 0, 0.2);
                border-top: 1px solid yellow;
            }
            
            /* Add ruler markers */
            .ruler-marker {
                position: absolute;
                background-color: rgba(0, 0, 0, 0.2);
                z-index: 999;
            }
            
            .ruler-label {
                position: absolute;
                font-size: 8px;
                color: #666;
                z-index: 999;
            }
            
            .horizontal-marker {
                height: 1px;
                left: 0;
                right: 0;
            }
            
            .vertical-marker {
                width: 1px;
                top: 0;
                bottom: 0;
            }
            </style>
        </head>
        <body>
            <h1>Margin Test Document</h1>
            <p>This document tests margins. The colored borders indicate the margins:</p>
            <ul>
                <li>Red: Top margin</li>
                <li>Blue: Left margin</li>
                <li>Green: Right margin</li>
                <li>Yellow: Bottom margin</li>
            </ul>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            <h1>Page 2</h1>
            <p>This is page 2. The margins should be consistent with page 1.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_margin_indicators)
    
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
        self.setup_document_settings(top, right, bottom, left)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_margin_indicators)
    
    def add_margin_indicators(self):
        """Add visual indicators for margins"""
        logger.info("Adding margin indicators")
        
        # Add visual indicators with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Get all pages
            var pages = document.querySelectorAll('.page');
            if (!pages.length) return 'No pages found';
            
            // Process each page
            pages.forEach(function(page, index) {
                // Remove any existing indicators
                var existingIndicators = page.querySelectorAll('.margin-indicator, .ruler-marker, .ruler-label');
                existingIndicators.forEach(function(indicator) {
                    indicator.remove();
                });
                
                // Get page dimensions
                var rect = page.getBoundingClientRect();
                var style = window.getComputedStyle(page);
                
                // Get padding values (margins)
                var paddingTop = parseFloat(style.paddingTop);
                var paddingRight = parseFloat(style.paddingRight);
                var paddingBottom = parseFloat(style.paddingBottom);
                var paddingLeft = parseFloat(style.paddingLeft);
                
                console.log('Page ' + (index + 1) + ' padding: T:' + paddingTop + 'px R:' + paddingRight + 
                           'px B:' + paddingBottom + 'px L:' + paddingLeft + 'px');
                
                // Add top margin indicator
                var topIndicator = document.createElement('div');
                topIndicator.className = 'margin-indicator top-indicator';
                topIndicator.style.height = paddingTop + 'px';
                page.appendChild(topIndicator);
                
                // Add left margin indicator
                var leftIndicator = document.createElement('div');
                leftIndicator.className = 'margin-indicator left-indicator';
                leftIndicator.style.width = paddingLeft + 'px';
                page.appendChild(leftIndicator);
                
                // Add right margin indicator
                var rightIndicator = document.createElement('div');
                rightIndicator.className = 'margin-indicator right-indicator';
                rightIndicator.style.width = paddingRight + 'px';
                page.appendChild(rightIndicator);
                
                // Add bottom margin indicator
                var bottomIndicator = document.createElement('div');
                bottomIndicator.className = 'margin-indicator bottom-indicator';
                bottomIndicator.style.height = paddingBottom + 'px';
                page.appendChild(bottomIndicator);
                
                // Add horizontal ruler markers every 10mm
                for (var i = 0; i <= 100; i += 10) {
                    // Convert mm to px (assuming 96 DPI, 1 inch = 25.4 mm)
                    var mmToPx = 96 / 25.4;
                    var positionPx = i * mmToPx;
                    
                    // Add horizontal marker
                    var hMarker = document.createElement('div');
                    hMarker.className = 'ruler-marker horizontal-marker';
                    hMarker.style.top = positionPx + 'px';
                    page.appendChild(hMarker);
                    
                    // Add label
                    var hLabel = document.createElement('div');
                    hLabel.className = 'ruler-label';
                    hLabel.style.top = positionPx + 'px';
                    hLabel.style.left = '2px';
                    hLabel.textContent = i + 'mm';
                    page.appendChild(hLabel);
                }
                
                // Add vertical ruler markers every 10mm
                for (var i = 0; i <= 100; i += 10) {
                    // Convert mm to px
                    var positionPx = i * mmToPx;
                    
                    // Add vertical marker
                    var vMarker = document.createElement('div');
                    vMarker.className = 'ruler-marker vertical-marker';
                    vMarker.style.left = positionPx + 'px';
                    page.appendChild(vMarker);
                    
                    // Add label
                    var vLabel = document.createElement('div');
                    vLabel.className = 'ruler-label';
                    vLabel.style.left = positionPx + 'px';
                    vLabel.style.top = '2px';
                    vLabel.textContent = i + 'mm';
                    page.appendChild(vLabel);
                }
            });
            
            return 'Added indicators to ' + pages.length + ' pages';
        })()
        """)
        
        logger.info(f"Margin indicators result: {js_result}")
        
        # Debug margins
        self.debug_margins()
    
    def debug_margins(self):
        """Debug margins with detailed information"""
        logger.info("Debugging margins")
        
        # Get detailed margin information
        js_result = self.preview.execute_js("""
        (function() {
            // Get all pages
            var pages = document.querySelectorAll('.page');
            if (!pages.length) return 'No pages found';
            
            // Get the first page
            var page = pages[0];
            var style = window.getComputedStyle(page);
            
            // Get CSS variables
            var root = document.documentElement;
            var rootStyle = window.getComputedStyle(root);
            
            // Get first element
            var firstElement = page.firstElementChild;
            var firstElementStyle = firstElement ? window.getComputedStyle(firstElement) : null;
            
            return {
                // Page dimensions
                pageWidth: page.offsetWidth,
                pageHeight: page.offsetHeight,
                
                // Page style
                paddingTop: style.paddingTop,
                paddingRight: style.paddingRight,
                paddingBottom: style.paddingBottom,
                paddingLeft: style.paddingLeft,
                
                // CSS variables
                cssMarginTop: rootStyle.getPropertyValue('--margin-top'),
                cssMarginRight: rootStyle.getPropertyValue('--margin-right'),
                cssMarginBottom: rootStyle.getPropertyValue('--margin-bottom'),
                cssMarginLeft: rootStyle.getPropertyValue('--margin-left'),
                
                // First element
                firstElementType: firstElement ? firstElement.tagName : 'None',
                firstElementMarginTop: firstElementStyle ? firstElementStyle.marginTop : 'N/A',
                firstElementMarginLeft: firstElementStyle ? firstElementStyle.marginLeft : 'N/A',
                
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
        
        # Get CSS variables
        css_vars = self.preview.execute_js("""
        (function() {
            var style = getComputedStyle(document.documentElement);
            return {
                marginTop: style.getPropertyValue('--margin-top'),
                marginRight: style.getPropertyValue('--margin-right'),
                marginBottom: style.getPropertyValue('--margin-bottom'),
                marginLeft: style.getPropertyValue('--margin-left'),
                pageWidth: style.getPropertyValue('--page-width'),
                pageHeight: style.getPropertyValue('--page-height')
            };
        })()
        """)
        
        logger.info(f"CSS variables: {css_vars}")

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
    window = MarginDebugWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
