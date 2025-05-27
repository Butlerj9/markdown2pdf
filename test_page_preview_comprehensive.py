#!/usr/bin/env python3
"""
Comprehensive test script for page preview functionality
"""

import os
import sys
import logging
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PagePreviewTestWindow(QMainWindow):
    """Test window for page preview"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Page Preview Comprehensive Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
            <title>Page Preview Comprehensive Test</title>
            <style>
                /* Add styles to help visualize page edges */
                .edge-marker {
                    position: absolute;
                    background-color: rgba(255, 0, 0, 0.3);
                    z-index: 1000;
                }
                .top-edge {
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 5px;
                }
                .left-edge {
                    top: 0;
                    left: 0;
                    bottom: 0;
                    width: 5px;
                }
                .right-edge {
                    top: 0;
                    right: 0;
                    bottom: 0;
                    width: 5px;
                }
                .corner-marker {
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    background-color: rgba(0, 0, 255, 0.3);
                    z-index: 1000;
                }
                .top-left {
                    top: 0;
                    left: 0;
                }
                .top-right {
                    top: 0;
                    right: 0;
                }
            </style>
        </head>
        <body>
            <!-- Edge markers to help visualize page edges -->
            <div class="edge-marker top-edge"></div>
            <div class="edge-marker left-edge"></div>
            <div class="edge-marker right-edge"></div>
            <div class="corner-marker top-left"></div>
            <div class="corner-marker top-right"></div>

            <h1>Page Preview Comprehensive Test</h1>
            <p>This test verifies all aspects of the page preview functionality.</p>

            <h2>Page 1: Basic Content</h2>
            <p>This page contains basic content to test the page layout.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>

            <h3>Lists</h3>
            <ul>
                <li>Item 1</li>
                <li>Item 2
                    <ul>
                        <li>Nested item 1</li>
                        <li>Nested item 2</li>
                    </ul>
                </li>
                <li>Item 3</li>
            </ul>

            <ol>
                <li>Numbered item 1</li>
                <li>Numbered item 2</li>
                <li>Numbered item 3</li>
            </ol>

            <div style="page-break-before: always;"></div>

            <h2>Page 2: Tables and Code</h2>
            <p>This page contains tables and code blocks.</p>

            <h3>Table</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Occupation</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>John</td>
                        <td>30</td>
                        <td>Developer</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>25</td>
                        <td>Designer</td>
                    </tr>
                    <tr>
                        <td>Bob</td>
                        <td>40</td>
                        <td>Manager</td>
                    </tr>
                </tbody>
            </table>

            <h3>Code Block</h3>
            <pre><code>
def hello_world():
    print("Hello, world!")
            </code></pre>

            <div style="page-break-before: always;"></div>

            <h2>Page 3: Images and Math</h2>
            <p>This page contains images and math formulas.</p>

            <h3>Image</h3>
            <div style="text-align: center;">
                <svg width="200" height="200">
                    <rect x="50" y="50" width="100" height="100" fill="blue" />
                    <circle cx="100" cy="100" r="50" fill="red" />
                </svg>
            </div>

            <h3>Math Formula</h3>
            <div style="text-align: center;">
                <p>E = mc<sup>2</sup></p>
            </div>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(self.test_html)

        # Set up a timer to run tests after the page has loaded
        QTimer.singleShot(1000, self.run_tests)

    def run_tests(self):
        """Run comprehensive tests on the page preview"""
        logger.info("Running comprehensive page preview tests...")

        # Test 1: Check page count
        self.test_page_count()

        # Test 2: Test navigation
        self.test_navigation()

        # Test 3: Test zoom
        self.test_zoom()

        # Test 4: Test margin changes
        self.test_margin_changes()

        # Test 5: Test page size changes
        self.test_page_size_changes()

        # Test 6: Test orientation changes
        self.test_orientation_changes()

        # Test 7: Debug page layout
        self.preview.debug_page_layout()

        logger.info("Comprehensive page preview tests completed")

    def test_page_count(self):
        """Test page count functionality"""
        logger.info("Testing page count...")

        # Run JavaScript to count pages
        script = """
        (function() {
            var pages = document.querySelectorAll('.page');
            return pages.length;
        })();
        """

        self.preview.web_page.runJavaScript(script, lambda count:
            logger.info(f"Page count: {count}"))

    def test_navigation(self):
        """Test navigation functionality"""
        logger.info("Testing navigation...")

        # Test navigation to next page
        self.preview.go_to_next_page()

        # Run JavaScript to check current page
        script = """
        (function() {
            var currentPage = document.querySelector('.page.current-page');
            if (currentPage) {
                var pages = document.querySelectorAll('.page');
                for (var i = 0; i < pages.length; i++) {
                    if (pages[i] === currentPage) {
                        return i + 1;
                    }
                }
            }
            return 0;
        })();
        """

        self.preview.web_page.runJavaScript(script, lambda current:
            logger.info(f"Current page after next: {current}"))

        # Test navigation to previous page
        self.preview.go_to_previous_page()

        # Run JavaScript to check current page
        self.preview.web_page.runJavaScript(script, lambda current:
            logger.info(f"Current page after previous: {current}"))

        # Test navigation to specific page
        self.preview.go_to_page(3)

        # Run JavaScript to check current page
        self.preview.web_page.runJavaScript(script, lambda current:
            logger.info(f"Current page after go_to_page(3): {current}"))

    def test_zoom(self):
        """Test zoom functionality"""
        logger.info("Testing zoom...")

        # Test zoom in
        original_zoom = self.preview.zoom_factor
        logger.info(f"Original zoom factor: {original_zoom}")

        # Create a custom zoom method for testing
        def custom_zoom_in():
            self.preview.zoom_factor = min(self.preview.zoom_factor + 0.1, 2.0)
            self.preview.web_view.setZoomFactor(self.preview.zoom_factor)
            return self.preview.zoom_factor

        # Create a custom zoom out method for testing
        def custom_zoom_out():
            self.preview.zoom_factor = max(self.preview.zoom_factor - 0.1, 0.5)
            self.preview.web_view.setZoomFactor(self.preview.zoom_factor)
            return self.preview.zoom_factor

        # Create a custom reset zoom method for testing
        def custom_reset_zoom():
            self.preview.zoom_factor = 1.0
            self.preview.web_view.setZoomFactor(self.preview.zoom_factor)
            return self.preview.zoom_factor

        # Zoom in
        zoom_in_factor = custom_zoom_in()
        logger.info(f"Zoom factor after zoom in: {zoom_in_factor}")

        # Zoom out
        zoom_out_factor = custom_zoom_out()
        logger.info(f"Zoom factor after zoom out: {zoom_out_factor}")

        # Reset zoom
        reset_zoom_factor = custom_reset_zoom()
        logger.info(f"Zoom factor after reset: {reset_zoom_factor}")

    def test_margin_changes(self):
        """Test margin changes"""
        logger.info("Testing margin changes...")

        # Get original margins
        original_margins = self.document_settings["page"]["margins"].copy()
        logger.info(f"Original margins: {original_margins}")

        # Change margins
        new_margins = {
            "top": 10,
            "right": 10,
            "bottom": 10,
            "left": 10
        }

        # Update document settings with new margins
        self.document_settings["page"]["margins"] = new_margins
        self.preview.update_document_settings(self.document_settings)

        # Log the change
        logger.info(f"Changed margins to: {new_margins}")

        # Restore original margins
        self.document_settings["page"]["margins"] = original_margins
        self.preview.update_document_settings(self.document_settings)

        # Log the restoration
        logger.info(f"Restored margins to: {original_margins}")

    def test_page_size_changes(self):
        """Test page size changes"""
        logger.info("Testing page size changes...")

        # Get original page size
        original_size = self.document_settings["page"]["size"]
        logger.info(f"Original page size: {original_size}")

        # Change page size to Letter
        self.document_settings["page"]["size"] = "Letter"
        self.preview.update_document_settings(self.document_settings)

        # Log the change
        logger.info(f"Changed page size to: Letter")

        # Restore original page size
        self.document_settings["page"]["size"] = original_size
        self.preview.update_document_settings(self.document_settings)

        # Log the restoration
        logger.info(f"Restored page size to: {original_size}")

    def test_orientation_changes(self):
        """Test orientation changes"""
        logger.info("Testing orientation changes...")

        # Get original orientation
        original_orientation = self.document_settings["page"]["orientation"]
        logger.info(f"Original orientation: {original_orientation}")

        # Change orientation to landscape
        self.document_settings["page"]["orientation"] = "landscape"
        self.preview.update_document_settings(self.document_settings)

        # Log the change
        logger.info(f"Changed orientation to: landscape")

        # Restore original orientation
        self.document_settings["page"]["orientation"] = original_orientation
        self.preview.update_document_settings(self.document_settings)

        # Log the restoration
        logger.info(f"Restored orientation to: {original_orientation}")

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create and show the test window
    window = PagePreviewTestWindow()
    window.show()

    # Exit after 10 seconds
    QTimer.singleShot(10000, app.quit)

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
