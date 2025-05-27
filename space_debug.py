#!/usr/bin/env python3
"""
Test script to identify and fix space at the top of the page
"""

import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("space_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SpaceDebugWindow(QMainWindow):
    """Test window for debugging space at the top of the page"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Space Debug")
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
        
        # Test with minimal HTML
        minimal_btn = QPushButton("Test Minimal HTML")
        minimal_btn.clicked.connect(self.test_minimal_html)
        button_layout.addWidget(minimal_btn)
        
        # Test with grid overlay
        grid_btn = QPushButton("Add Grid Overlay")
        grid_btn.clicked.connect(self.add_grid_overlay)
        button_layout.addWidget(grid_btn)
        
        # Inspect DOM
        inspect_btn = QPushButton("Inspect DOM")
        inspect_btn.clicked.connect(self.inspect_dom)
        button_layout.addWidget(inspect_btn)
        
        # Fix space
        fix_btn = QPushButton("Fix Space")
        fix_btn.clicked.connect(self.fix_space)
        button_layout.addWidget(fix_btn)
        
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
        QTimer.singleShot(500, self.test_minimal_html)
    
    def setup_document_settings(self):
        """Set up document settings with zero margins"""
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
                        "margin_top": 0,
                        "margin_bottom": 6
                    },
                    "h2": {
                        "family": "Arial",
                        "size": 16,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 0,
                        "margin_bottom": 5
                    },
                    "h3": {
                        "family": "Arial",
                        "size": 14,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 0,
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
    
    def test_minimal_html(self):
        """Test with minimal HTML to identify space issues"""
        logger.info("Testing with minimal HTML")
        
        # Create minimal HTML with red top border
        html = """
        <html>
        <head>
            <style>
            /* Add red top border to identify top edge */
            body {
                margin: 0;
                padding: 0;
            }
            
            .top-marker {
                height: 5px;
                background-color: red;
                margin: 0;
                padding: 0;
            }
            
            p {
                margin: 0;
                padding: 0;
            }
            </style>
        </head>
        <body>
            <div class="top-marker"></div>
            <p>This text should be immediately below the red line with no space.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.inspect_dom)
    
    def add_grid_overlay(self):
        """Add a grid overlay to help identify spacing issues"""
        logger.info("Adding grid overlay")
        
        # Add grid overlay with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Remove any existing grid
            var existingGrid = document.getElementById('grid-overlay');
            if (existingGrid) existingGrid.remove();
            
            // Create grid container
            var grid = document.createElement('div');
            grid.id = 'grid-overlay';
            grid.style.position = 'absolute';
            grid.style.top = '0';
            grid.style.left = '0';
            grid.style.right = '0';
            grid.style.bottom = '0';
            grid.style.pointerEvents = 'none';
            grid.style.zIndex = '1000';
            
            // Create horizontal lines every 10px
            for (var i = 0; i < 500; i += 10) {
                var hLine = document.createElement('div');
                hLine.style.position = 'absolute';
                hLine.style.left = '0';
                hLine.style.right = '0';
                hLine.style.top = i + 'px';
                hLine.style.height = '1px';
                hLine.style.backgroundColor = 'rgba(0, 0, 255, 0.2)';
                
                // Add label
                var label = document.createElement('div');
                label.style.position = 'absolute';
                label.style.left = '2px';
                label.style.top = (i - 8) + 'px';
                label.style.fontSize = '8px';
                label.style.color = 'blue';
                label.textContent = i + 'px';
                
                grid.appendChild(hLine);
                grid.appendChild(label);
            }
            
            // Add grid to page
            var page = document.querySelector('.page');
            if (page) {
                page.appendChild(grid);
                return 'Grid added to page';
            } else {
                document.body.appendChild(grid);
                return 'Grid added to body';
            }
        })()
        """)
        
        logger.info(f"Grid overlay result: {js_result}")
    
    def inspect_dom(self):
        """Inspect DOM to identify what's causing the space"""
        logger.info("Inspecting DOM")
        
        # Get detailed DOM information
        js_result = self.preview.execute_js("""
        (function() {
            // Get all elements in the page
            var page = document.querySelector('.page');
            if (!page) return 'No page found';
            
            // Get all direct children
            var children = page.children;
            var childInfo = [];
            
            for (var i = 0; i < children.length; i++) {
                var child = children[i];
                var style = window.getComputedStyle(child);
                var rect = child.getBoundingClientRect();
                
                childInfo.push({
                    index: i,
                    tagName: child.tagName,
                    className: child.className,
                    id: child.id,
                    offsetTop: child.offsetTop,
                    offsetHeight: child.offsetHeight,
                    marginTop: style.marginTop,
                    marginBottom: style.marginBottom,
                    paddingTop: style.paddingTop,
                    paddingBottom: style.paddingBottom,
                    boundingRect: {
                        top: rect.top,
                        bottom: rect.bottom,
                        height: rect.height
                    }
                });
            }
            
            // Get page style
            var pageStyle = window.getComputedStyle(page);
            var pageRect = page.getBoundingClientRect();
            
            // Get first element with class 'top-marker'
            var topMarker = document.querySelector('.top-marker');
            var topMarkerInfo = null;
            
            if (topMarker) {
                var topMarkerStyle = window.getComputedStyle(topMarker);
                var topMarkerRect = topMarker.getBoundingClientRect();
                
                topMarkerInfo = {
                    offsetTop: topMarker.offsetTop,
                    offsetHeight: topMarker.offsetHeight,
                    marginTop: topMarkerStyle.marginTop,
                    marginBottom: topMarkerStyle.marginBottom,
                    paddingTop: topMarkerStyle.paddingTop,
                    paddingBottom: topMarkerStyle.paddingBottom,
                    boundingRect: {
                        top: topMarkerRect.top,
                        bottom: topMarkerRect.bottom,
                        height: topMarkerRect.height
                    }
                };
            }
            
            return {
                pageInfo: {
                    paddingTop: pageStyle.paddingTop,
                    marginTop: pageStyle.marginTop,
                    borderTopWidth: pageStyle.borderTopWidth,
                    boundingRect: {
                        top: pageRect.top,
                        height: pageRect.height
                    }
                },
                childrenCount: children.length,
                children: childInfo,
                topMarker: topMarkerInfo
            };
        })()
        """)
        
        logger.info(f"DOM inspection result: {js_result}")
        
        # Check for any hidden elements
        hidden_elements = self.preview.execute_js("""
        (function() {
            // Find all elements with display:none or visibility:hidden
            var allElements = document.querySelectorAll('*');
            var hiddenElements = [];
            
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var style = window.getComputedStyle(element);
                
                if (style.display === 'none' || style.visibility === 'hidden') {
                    hiddenElements.push({
                        tagName: element.tagName,
                        className: element.className,
                        id: element.id,
                        display: style.display,
                        visibility: style.visibility
                    });
                }
            }
            
            return hiddenElements;
        })()
        """)
        
        logger.info(f"Hidden elements: {hidden_elements}")
    
    def fix_space(self):
        """Apply fixes to remove the space at the top"""
        logger.info("Applying fixes to remove space")
        
        # Apply fixes with JavaScript
        js_result = self.preview.execute_js("""
        (function() {
            // Target specific elements that might be causing space
            
            // 1. Fix any title elements
            var titleElements = document.querySelectorAll('h1.title, div.title, header.title-block');
            titleElements.forEach(function(element) {
                element.style.display = 'none';
                element.style.margin = '0';
                element.style.padding = '0';
                element.style.height = '0';
                element.style.minHeight = '0';
                element.style.maxHeight = '0';
                element.style.overflow = 'hidden';
            });
            
            // 2. Fix first element in the page
            var page = document.querySelector('.page');
            if (page && page.firstElementChild) {
                page.firstElementChild.style.marginTop = '0';
                page.firstElementChild.style.paddingTop = '0';
            }
            
            // 3. Fix any header elements
            var headers = document.querySelectorAll('header');
            headers.forEach(function(header) {
                header.style.margin = '0';
                header.style.padding = '0';
                header.style.height = 'auto';
                header.style.minHeight = '0';
            });
            
            // 4. Add a style to force zero top margin/padding on first elements
            var style = document.createElement('style');
            style.textContent = `
                .page > *:first-child {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
                
                .page h1:first-of-type,
                .page h2:first-of-type,
                .page h3:first-of-type,
                .page h4:first-of-type,
                .page h5:first-of-type,
                .page h6:first-of-type,
                .page p:first-of-type {
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }
                
                /* Force page to have zero top padding */
                .page {
                    padding-top: 0 !important;
                }
            `;
            document.head.appendChild(style);
            
            // 5. Check for any elements with position:absolute that might be taking space
            var absoluteElements = document.querySelectorAll('.page > [style*="position: absolute"]');
            absoluteElements.forEach(function(element) {
                element.style.top = '0';
                element.style.margin = '0';
                element.style.padding = '0';
            });
            
            return 'Applied fixes to remove space';
        })()
        """)
        
        logger.info(f"Fix result: {js_result}")
        
        # Inspect DOM after fixes
        QTimer.singleShot(500, self.inspect_dom)

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
    window = SpaceDebugWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
