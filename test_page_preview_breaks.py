#!/usr/bin/env python3
"""
Test script for page break detection in page preview
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PageBreakTestWindow(QMainWindow):
    """Test window for page break detection"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Page Break Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add status label
        self.status_label = QLabel("Testing page breaks...")
        layout.addWidget(self.status_label)

        # Create page preview
        self.preview = PagePreview()
        layout.addWidget(self.preview)

        # Set document settings
        self.document_settings = {
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

        # Update document settings
        self.preview.update_document_settings(self.document_settings)

        # Create test HTML with explicit page breaks
        self.test_html = """
        <html>
        <head>
            <title>Page Break Test</title>
        </head>
        <body>
            <h1>Page 1</h1>
            <p>This is the content of page 1.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 2</h1>
            <p>This is the content of page 2.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 3</h1>
            <p>This is the content of page 3.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(self.test_html)

        # Set up a timer to check page count after a delay
        QTimer.singleShot(2000, self.check_page_count)

    def check_page_count(self):
        """Check the page count"""
        # Run JavaScript to count pages
        script = """
        (function() {
            var pages = document.querySelectorAll('.page');
            return pages.length;
        })();
        """

        self.preview.web_page.runJavaScript(script, self.update_status)

    def update_status(self, page_count):
        """Update status label with page count"""
        self.status_label.setText(f"Found {page_count} pages")

        # Check if page count is correct
        if page_count == 3:
            self.status_label.setText(f"SUCCESS: Found {page_count} pages as expected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText(f"ERROR: Found {page_count} pages, expected 3")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Debug page layout
        self.preview.debug_page_layout()

        # Debug page breaks
        self.preview.debug_page_breaks()

        # Check page breaks
        self.check_page_breaks()

    def check_page_breaks(self):
        """Check page breaks"""
        # Run JavaScript to check page breaks
        script = """
        (function() {
            // Check for page break elements
            var pageBreaks = document.querySelectorAll('div[style*="page-break-before"]');
            console.log('Found ' + pageBreaks.length + ' page break elements');

            // Check for pages
            var pages = document.querySelectorAll('.page');
            console.log('Found ' + pages.length + ' pages');

            // Return results
            return {
                pageBreaks: pageBreaks.length,
                pages: pages.length
            };
        })();
        """

        self.preview.web_page.runJavaScript(script, self.log_page_breaks)

    def log_page_breaks(self, result):
        """Log page break results"""
        if result:
            logger.info(f"Page break check: {result}")

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create and show the test window
    window = PageBreakTestWindow()
    window.show()

    # Exit after 10 seconds
    QTimer.singleShot(10000, app.quit)

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
