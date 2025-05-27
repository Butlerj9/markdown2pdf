#!/usr/bin/env python3
"""
Test script to identify JavaScript errors
"""

import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("js_error_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestWindow(QMainWindow):
    """Test window for JavaScript error identification"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JavaScript Error Test")
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
        
        # Create test buttons
        test_button = QPushButton("Test HTML with CSS")
        test_button.clicked.connect(self.test_html_with_css)
        
        test_js_button = QPushButton("Test JavaScript")
        test_js_button.clicked.connect(self.test_javascript)
        
        # Add widgets to layout
        layout.addWidget(self.preview, 3)
        layout.addWidget(self.log_display, 1)
        layout.addWidget(test_button)
        layout.addWidget(test_js_button)
        
        # Set up log handler
        self.log_handler = QTextEditLogger(self.log_display)
        logger.addHandler(self.log_handler)
        
        # Set up document settings
        self.setup_document_settings()
    
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
                    "top": 25,
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
    
    def test_html_with_css(self):
        """Test HTML with CSS to identify syntax errors"""
        self.log_display.clear()
        logger.info("Testing HTML with CSS")
        
        # Create test HTML with CSS
        html = """
        <html>
        <head>
            <style>
            /* Test CSS selectors */
            h1.title { display: none; }
            div.title { display: none; }
            header.title-block { display: none; }
            </style>
        </head>
        <body>
            <h1 class="title">Hidden Title</h1>
            <div class="title">Hidden Div</div>
            <header class="title-block">Hidden Header</header>
            
            <h1>Visible Heading</h1>
            <p>This is a test paragraph.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 2 Heading</h1>
            <p>This is page 2.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.check_html_result)
    
    def check_html_result(self):
        """Check the result of HTML rendering"""
        logger.info("Checking HTML rendering result")
        
        # Check if content is rendered
        js_result = self.preview.execute_js("document.body.textContent.includes('Visible Heading')")
        logger.info(f"Content rendered: {js_result}")
        
        # Check for JavaScript errors
        js_errors = self.preview.execute_js("""
        (function() {
            // Check for any error indicators in the console
            return document.querySelector('.error-message') ? true : false;
        })()
        """)
        
        logger.info(f"JavaScript errors detected: {js_errors}")
        
        # Check CSS
        css_result = self.preview.execute_js("""
        (function() {
            var style = document.querySelector('style');
            return style ? style.textContent : 'No style found';
        })()
        """)
        
        logger.info(f"CSS content: {css_result}")
    
    def test_javascript(self):
        """Test JavaScript execution"""
        self.log_display.clear()
        logger.info("Testing JavaScript execution")
        
        # Create test HTML with JavaScript
        html = """
        <html>
        <head>
            <script>
            // Test JavaScript
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded');
                
                // Test navigation functions
                window.testNavigation = function() {
                    console.log('Testing navigation');
                    
                    // Create some pages
                    var container = document.createElement('div');
                    container.className = 'pages-container';
                    
                    for (var i = 1; i <= 3; i++) {
                        var page = document.createElement('div');
                        page.className = 'page';
                        page.id = 'page-' + i;
                        page.innerHTML = '<h1>Page ' + i + '</h1><p>This is page ' + i + '.</p>';
                        container.appendChild(page);
                    }
                    
                    document.body.appendChild(container);
                    
                    // Mark first page as current
                    document.querySelector('.page').classList.add('current-page');
                    
                    console.log('Created ' + document.querySelectorAll('.page').length + ' pages');
                    
                    return 'Navigation test setup complete';
                };
            });
            </script>
        </head>
        <body>
            <h1>JavaScript Test</h1>
            <p>This page tests JavaScript execution.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        QTimer.singleShot(1000, self.check_javascript_result)
    
    def check_javascript_result(self):
        """Check the result of JavaScript execution"""
        logger.info("Checking JavaScript execution result")
        
        # Run the test navigation function
        js_result = self.preview.execute_js("window.testNavigation ? window.testNavigation() : 'Function not found'")
        logger.info(f"Navigation test result: {js_result}")
        
        # Check if pages were created
        pages_count = self.preview.execute_js("document.querySelectorAll('.page').length")
        logger.info(f"Pages created: {pages_count}")
        
        # Test navigation
        nav_result = self.preview.execute_js("""
        (function() {
            if (typeof window.navigateToPage === 'function') {
                return window.navigateToPage(2);
            } else {
                return 'Navigation function not found';
            }
        })()
        """)
        
        logger.info(f"Navigation result: {nav_result}")
        
        # Get any JavaScript errors
        errors = self.preview.execute_js("""
        (function() {
            // This is just a placeholder - in a real app we'd have error tracking
            return document.querySelector('.error-message') ? 
                document.querySelector('.error-message').textContent : 
                'No errors detected';
        })()
        """)
        
        logger.info(f"JavaScript errors: {errors}")

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
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
