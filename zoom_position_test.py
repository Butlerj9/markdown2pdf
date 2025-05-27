#!/usr/bin/env python3
"""
Test script to fix zoom and positioning issues
"""

import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout, QLabel, QSpinBox, QComboBox
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zoom_position_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ZoomPositionTestWindow(QMainWindow):
    """Test window for zoom and positioning issues"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoom and Position Test")
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
        self.top_margin.setValue(25)
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
        
        # Create zoom controls
        zoom_layout = QHBoxLayout()
        
        # Zoom level
        zoom_layout.addWidget(QLabel("Zoom Level:"))
        self.zoom_level = QComboBox()
        self.zoom_level.addItems(["50%", "75%", "90%", "100%", "110%", "125%", "150%", "200%"])
        self.zoom_level.setCurrentText("100%")
        self.zoom_level.currentTextChanged.connect(self.change_zoom)
        zoom_layout.addWidget(self.zoom_level)
        
        # Fit to width button
        fit_width_btn = QPushButton("Fit to Width")
        fit_width_btn.clicked.connect(self.fit_to_width)
        zoom_layout.addWidget(fit_width_btn)
        
        # Fit to page button
        fit_page_btn = QPushButton("Fit to Page")
        fit_page_btn.clicked.connect(self.fit_to_page)
        zoom_layout.addWidget(fit_page_btn)
        
        # Test buttons
        button_layout = QHBoxLayout()
        
        # Test with zero margins
        zero_margins_btn = QPushButton("Zero Margins")
        zero_margins_btn.clicked.connect(self.test_zero_margins)
        button_layout.addWidget(zero_margins_btn)
        
        # Test with normal margins
        normal_margins_btn = QPushButton("Normal Margins")
        normal_margins_btn.clicked.connect(self.test_normal_margins)
        button_layout.addWidget(normal_margins_btn)
        
        # Add debug button
        debug_btn = QPushButton("Debug View")
        debug_btn.clicked.connect(self.debug_view)
        button_layout.addWidget(debug_btn)
        
        # Add widgets to layout
        layout.addWidget(self.preview, 3)
        layout.addLayout(margin_layout)
        layout.addLayout(zoom_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_display, 1)
        
        # Set up log handler
        self.log_handler = QTextEditLogger(self.log_display)
        logger.addHandler(self.log_handler)
        
        # Set up document settings
        self.setup_document_settings()
        
        # Load test document
        QTimer.singleShot(500, self.load_test_document)
    
    def setup_document_settings(self, top=25, right=25, bottom=25, left=25):
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
        """Load a test document with visible page edges"""
        logger.info("Loading test document")
        
        # Create test HTML with visible page edges
        html = """
        <html>
        <head>
            <style>
            /* Add page border to visualize edges */
            .page-border {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                border: 2px solid #666;
                pointer-events: none;
                z-index: 999;
            }
            
            /* Add corner markers */
            .corner-marker {
                position: absolute;
                width: 20px;
                height: 20px;
                background-color: rgba(255, 0, 0, 0.3);
                z-index: 1000;
                pointer-events: none;
            }
            
            .top-left {
                top: 0;
                left: 0;
                border-right: 1px solid red;
                border-bottom: 1px solid red;
            }
            
            .top-right {
                top: 0;
                right: 0;
                border-left: 1px solid red;
                border-bottom: 1px solid red;
            }
            
            .bottom-left {
                bottom: 0;
                left: 0;
                border-right: 1px solid red;
                border-top: 1px solid red;
            }
            
            .bottom-right {
                bottom: 0;
                right: 0;
                border-left: 1px solid red;
                border-top: 1px solid red;
            }
            
            /* Add edge markers */
            .edge-marker {
                position: absolute;
                background-color: rgba(0, 0, 255, 0.3);
                z-index: 1000;
                pointer-events: none;
            }
            
            .top-edge {
                top: 0;
                left: 20px;
                right: 20px;
                height: 5px;
                border-bottom: 1px solid blue;
            }
            
            .left-edge {
                top: 20px;
                left: 0;
                bottom: 20px;
                width: 5px;
                border-right: 1px solid blue;
            }
            
            .right-edge {
                top: 20px;
                right: 0;
                bottom: 20px;
                width: 5px;
                border-left: 1px solid blue;
            }
            
            .bottom-edge {
                bottom: 0;
                left: 20px;
                right: 20px;
                height: 5px;
                border-top: 1px solid blue;
            }
            </style>
        </head>
        <body>
            <h1>JOSHUA DAVID BUTLER</h1>
            <p>Oakland, CA 94603 | (510) 695-4804 | joshua.butler@gmail.com</p>
            
            <h2>SUMMARY</h2>
            <p>Highly experienced technology leader with 20+ years in software development, hardware/software integration, and startup leadership. Expert in embedded systems, AI/ML implementation, and R&D innovation. Passionate advocate of AI-driven engineering methodologies, consistently improving software production throughput by 10-20%. Proven track record of building and leading technical teams across multiple industries. Lifelong learner with deep cross-disciplinary engineering expertise, further accelerated by recent advancements in large language models and continuous AI workflow integrations.</p>
            
            <h2>PROFESSIONAL EXPERIENCE</h2>
            <h3>CATALYPT, Oakland, CA</h3>
            <h4>Founder & CEO | 10/2022 - Present</h4>
            <ul>
                <li>Founded AI-first technology consultancy focused on helping businesses implement transformative AI solutions</li>
                <li>Developed proprietary frameworks for AI integration that consistently deliver 5-20% productivity improvements</li>
                <li>Led R&D initiatives exploring novel applications of large language models in software development and automation</li>
                <li>Architected and implemented custom AI solutions for clients across legal, education, software development, and research sectors</li>
            </ul>
            
            <div style="page-break-before: always;"></div>
            <h2>Page 2</h2>
            <p>This is page 2. All page edges should be visible.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
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
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def change_zoom(self, zoom_text):
        """Change the zoom level"""
        logger.info(f"Changing zoom to {zoom_text}")
        
        # Extract zoom percentage
        zoom_percent = float(zoom_text.strip('%')) / 100.0
        
        # Set zoom level
        self.preview.set_zoom(zoom_percent)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def fit_to_width(self):
        """Fit the page to width"""
        logger.info("Fitting page to width")
        
        # Calculate zoom to fit width
        self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var container = document.querySelector('.pages-container');
            if (!container) container = document.body;
            
            var pageWidth = page.offsetWidth;
            var containerWidth = container.offsetWidth;
            
            // Calculate zoom factor to fit width (with some margin)
            var zoomFactor = (containerWidth - 40) / pageWidth;
            
            // Set zoom factor
            document.documentElement.style.setProperty('--zoom-factor', zoomFactor);
            
            // Apply zoom
            var pagesContainer = document.querySelector('.pages-container');
            if (pagesContainer) {
                pagesContainer.style.transform = 'scale(' + zoomFactor + ')';
            }
            
            return 'Fit to width: ' + zoomFactor;
        })()
        """)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def fit_to_page(self):
        """Fit the entire page in view"""
        logger.info("Fitting entire page in view")
        
        # Calculate zoom to fit page
        self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var container = document.querySelector('.pages-container');
            if (!container) container = document.body;
            
            var pageWidth = page.offsetWidth;
            var pageHeight = page.offsetHeight;
            var containerWidth = container.offsetWidth;
            var containerHeight = container.offsetHeight;
            
            // Calculate zoom factor to fit page (with some margin)
            var zoomFactorWidth = (containerWidth - 40) / pageWidth;
            var zoomFactorHeight = (containerHeight - 40) / pageHeight;
            var zoomFactor = Math.min(zoomFactorWidth, zoomFactorHeight);
            
            // Set zoom factor
            document.documentElement.style.setProperty('--zoom-factor', zoomFactor);
            
            // Apply zoom
            var pagesContainer = document.querySelector('.pages-container');
            if (pagesContainer) {
                pagesContainer.style.transform = 'scale(' + zoomFactor + ')';
            }
            
            return 'Fit to page: ' + zoomFactor;
        })()
        """)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.add_page_indicators)
    
    def test_zero_margins(self):
        """Test with zero margins"""
        logger.info("Testing with zero margins")
        
        # Set all margins to 0
        self.top_margin.setValue(0)
        self.right_margin.setValue(0)
        self.bottom_margin.setValue(0)
        self.left_margin.setValue(0)
        self.apply_margins()
    
    def test_normal_margins(self):
        """Test with normal margins"""
        logger.info("Testing with normal margins")
        
        # Set normal margins
        self.top_margin.setValue(25)
        self.right_margin.setValue(25)
        self.bottom_margin.setValue(25)
        self.left_margin.setValue(25)
        self.apply_margins()
    
    def add_page_indicators(self):
        """Add visual indicators for page edges"""
        logger.info("Adding page edge indicators")
        
        # Add visual indicators with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Get all pages
            var pages = document.querySelectorAll('.page');
            if (!pages.length) return 'No pages found';
            
            // Process each page
            pages.forEach(function(page, index) {
                // Remove any existing indicators
                var existingIndicators = page.querySelectorAll('.page-border, .corner-marker, .edge-marker');
                existingIndicators.forEach(function(indicator) {
                    indicator.remove();
                });
                
                // Add page border
                var border = document.createElement('div');
                border.className = 'page-border';
                page.appendChild(border);
                
                // Add corner markers
                var topLeft = document.createElement('div');
                topLeft.className = 'corner-marker top-left';
                page.appendChild(topLeft);
                
                var topRight = document.createElement('div');
                topRight.className = 'corner-marker top-right';
                page.appendChild(topRight);
                
                var bottomLeft = document.createElement('div');
                bottomLeft.className = 'corner-marker bottom-left';
                page.appendChild(bottomLeft);
                
                var bottomRight = document.createElement('div');
                bottomRight.className = 'corner-marker bottom-right';
                page.appendChild(bottomRight);
                
                // Add edge markers
                var topEdge = document.createElement('div');
                topEdge.className = 'edge-marker top-edge';
                page.appendChild(topEdge);
                
                var leftEdge = document.createElement('div');
                leftEdge.className = 'edge-marker left-edge';
                page.appendChild(leftEdge);
                
                var rightEdge = document.createElement('div');
                rightEdge.className = 'edge-marker right-edge';
                page.appendChild(rightEdge);
                
                var bottomEdge = document.createElement('div');
                bottomEdge.className = 'edge-marker bottom-edge';
                page.appendChild(bottomEdge);
            });
            
            return 'Added indicators to ' + pages.length + ' pages';
        })()
        """)
        
        logger.info(f"Page indicators result: {js_result}")
        
        # Debug view
        self.debug_view()
    
    def debug_view(self):
        """Debug view positioning and zoom"""
        logger.info("Debugging view positioning and zoom")
        
        # Get detailed view information
        js_result = self.preview.execute_js("""
        (function() {
            // Get page and container
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            var container = document.querySelector('.pages-container');
            if (!container) container = document.body;
            
            // Get dimensions
            var pageRect = page.getBoundingClientRect();
            var containerRect = container.getBoundingClientRect();
            
            // Get zoom factor
            var zoomFactor = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--zoom-factor'));
            
            // Get scroll position
            var scrollTop = document.documentElement.scrollTop;
            var scrollLeft = document.documentElement.scrollLeft;
            
            return {
                // Page dimensions
                pageWidth: page.offsetWidth,
                pageHeight: page.offsetHeight,
                pageBoundingRect: {
                    top: pageRect.top,
                    right: pageRect.right,
                    bottom: pageRect.bottom,
                    left: pageRect.left,
                    width: pageRect.width,
                    height: pageRect.height
                },
                
                // Container dimensions
                containerWidth: container.offsetWidth,
                containerHeight: container.offsetHeight,
                containerBoundingRect: {
                    top: containerRect.top,
                    right: containerRect.right,
                    bottom: containerRect.bottom,
                    left: containerRect.left,
                    width: containerRect.width,
                    height: containerRect.height
                },
                
                // Zoom and scroll
                zoomFactor: zoomFactor,
                scrollTop: scrollTop,
                scrollLeft: scrollLeft,
                
                // Viewport
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                
                // Check if edges are visible
                edgesVisible: {
                    top: pageRect.top >= 0,
                    right: pageRect.right <= window.innerWidth,
                    bottom: pageRect.bottom <= window.innerHeight,
                    left: pageRect.left >= 0
                }
            };
        })()
        """)
        
        logger.info(f"View debug info: {js_result}")

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
    window = ZoomPositionTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
