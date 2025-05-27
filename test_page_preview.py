#!/usr/bin/env python3
"""
Test Page Preview
----------------
Command-line tool to test the page preview functionality with debugging output.
"""

import sys
import os
import argparse
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt, QTimer
from page_preview import PagePreview
from logging_config import get_logger

logger = get_logger()

class PagePreviewTestWindow(QMainWindow):
    """Test window for page preview functionality"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Page Preview Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create controls
        controls_layout = QHBoxLayout()

        # Zoom controls
        zoom_label = QLabel("Zoom:")
        controls_layout.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "175%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.change_zoom)
        controls_layout.addWidget(self.zoom_combo)

        # Page size controls
        page_size_label = QLabel("Page Size:")
        controls_layout.addWidget(page_size_label)

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "Letter", "Legal"])
        self.page_size_combo.setCurrentText("A4")
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        controls_layout.addWidget(self.page_size_combo)

        # Orientation controls
        orientation_label = QLabel("Orientation:")
        controls_layout.addWidget(orientation_label)

        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        self.orientation_combo.setCurrentText("Portrait")
        self.orientation_combo.currentTextChanged.connect(self.change_orientation)
        controls_layout.addWidget(self.orientation_combo)

        # Debug button
        self.debug_btn = QPushButton("Debug Layout")
        self.debug_btn.clicked.connect(self.debug_layout)
        controls_layout.addWidget(self.debug_btn)

        # Test page navigation button
        self.test_nav_btn = QPushButton("Test Navigation")
        self.test_nav_btn.clicked.connect(self.test_page_navigation)
        controls_layout.addWidget(self.test_nav_btn)

        # Test infinite loop fix button
        self.test_loop_btn = QPushButton("Test Loop Fix")
        self.test_loop_btn.clicked.connect(self.test_infinite_loop_fix)
        controls_layout.addWidget(self.test_loop_btn)

        # Add controls to main layout
        main_layout.addLayout(controls_layout)

        # Create page preview
        self.page_preview = PagePreview()
        main_layout.addWidget(self.page_preview, 1)  # 1 = stretch factor

        # Set up document settings
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

        # Update page preview with settings
        self.page_preview.update_document_settings(self.document_settings)

        # Set up zoom controls
        self.page_preview.setup_zoom_controls(None)

        # Add zero margin test button
        zero_margin_btn = QPushButton("Test Zero Margins")
        zero_margin_btn.clicked.connect(self.test_zero_margins)
        controls_layout.addWidget(zero_margin_btn)

        # Add normal margin test button
        normal_margin_btn = QPushButton("Test Normal Margins")
        normal_margin_btn.clicked.connect(self.test_normal_margins)
        controls_layout.addWidget(normal_margin_btn)

        # Load sample HTML
        self.load_sample_html()

        # Set up timer for periodic debug
        self.debug_timer = QTimer()
        self.debug_timer.timeout.connect(self.debug_layout)
        self.debug_timer.start(5000)  # Debug every 5 seconds

    def load_sample_html(self):
        """Load sample HTML content for testing"""
        sample_html = """
        <html>
        <head>
            <title>Page Preview Test</title>
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

            <h1>Page Preview Test</h1>
            <p>This is a test of the page preview functionality with debugging output.</p>

            <h2>Page Edges Visibility Test</h2>
            <p>All page edges (top, right, left) should be visible on initial load.</p>
            <p>The page should not be overly zoomed in.</p>
            <p>Red markers show the page edges.</p>
            <p>Blue markers show the corners.</p>

            <h2>Margin Test</h2>
            <p>The margins should be accurate to the actual printing.</p>
            <ul>
                <li>Top margin: 25mm</li>
                <li>Right margin: 25mm</li>
                <li>Bottom margin: 25mm</li>
                <li>Left margin: 25mm</li>
            </ul>

            <h2>Zero Margin Test</h2>
            <p>When using the "Test Zero Margins" button:</p>
            <ul>
                <li>The left side should be at the edge when margin is 0</li>
                <li>The top should be at the edge when margin is 0</li>
                <li>All page edges should still be visible</li>
            </ul>

            <h2>Zoom Test</h2>
            <p>The zoom should be set to 90% by default to ensure all edges are visible.</p>
            <p>When zooming in or out, the page should remain properly positioned.</p>

            <div style="page-break-before: always;"></div>

            <h2>Second Page</h2>
            <p>This content should appear on the second page.</p>

            <h3>Code Block</h3>
            <pre><code>
            def hello_world():
                print("Hello, world!")
                return True
            </code></pre>

            <h3>Table</h3>
            <table border="1">
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                    <th>Header 3</th>
                </tr>
                <tr>
                    <td>Cell 1,1</td>
                    <td>Cell 1,2</td>
                    <td>Cell 1,3</td>
                </tr>
                <tr>
                    <td>Cell 2,1</td>
                    <td>Cell 2,2</td>
                    <td>Cell 2,3</td>
                </tr>
            </table>

            <div style="page-break-before: always;"></div>

            <h2>Third Page</h2>
            <p>This content should appear on the third page.</p>
        </body>
        </html>
        """

        self.page_preview.update_preview(sample_html)

    def change_zoom(self, zoom_text):
        """Change the zoom level"""
        zoom_value = int(zoom_text.rstrip('%'))
        logger.debug(f"Changing zoom to {zoom_value}%")
        self.page_preview.update_zoom(zoom_value)

    def change_page_size(self, size):
        """Change the page size"""
        logger.debug(f"Changing page size to {size}")
        self.document_settings["page"]["size"] = size
        self.page_preview.update_document_settings(self.document_settings)

    def change_orientation(self, orientation):
        """Change the page orientation"""
        orientation = orientation.lower()
        logger.debug(f"Changing orientation to {orientation}")
        self.document_settings["page"]["orientation"] = orientation
        self.page_preview.update_document_settings(self.document_settings)

    def debug_layout(self):
        """Debug the page layout"""
        logger.debug("Manual debug of page layout requested")
        # Use fit_to_page instead of apply_page_layout
        self.page_preview.fit_to_page()
        # Log page count
        logger.debug("Checking page count")
        # Check if update_page_count exists
        if hasattr(self.page_preview, 'update_page_count'):
            self.page_preview.update_page_count()

    def test_zero_margins(self):
        """Test with zero margins"""
        logger.debug("Testing with zero margins")
        self.document_settings["page"]["margins"] = {
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
        }
        self.page_preview.update_document_settings(self.document_settings)
        # Debug after a short delay to ensure changes are applied
        QTimer.singleShot(500, self.debug_layout)

    def test_normal_margins(self):
        """Test with normal margins"""
        logger.debug("Testing with normal margins")
        self.document_settings["page"]["margins"] = {
            "top": 25,
            "right": 25,
            "bottom": 25,
            "left": 25
        }
        self.page_preview.update_document_settings(self.document_settings)
        # Debug after a short delay to ensure changes are applied
        QTimer.singleShot(500, self.debug_layout)

    def test_page_navigation(self):
        """Test page navigation functionality"""
        logger.debug("Testing page navigation")

        # Set up a sequence of navigation tests with delays
        QTimer.singleShot(1000, lambda: self.navigate_to_page(2))
        QTimer.singleShot(2000, lambda: self.navigate_to_page(3))
        QTimer.singleShot(3000, lambda: self.navigate_to_page(1))

    def navigate_to_page(self, page_number):
        """Navigate to a specific page and log the result"""
        logger.debug(f"Navigating to page {page_number}")
        self.page_preview.go_to_page(page_number)

    def check_page_count(self):
        """Check and log the current page count"""
        logger.debug("Checking page count")
        # Use fit_to_page to ensure all pages are properly rendered
        self.page_preview.fit_to_page()

    def test_infinite_loop_fix(self):
        """Test the fix for the infinite loop issue"""
        logger.debug("Testing infinite loop fix")

        # Create HTML with no pages to trigger the verification loop
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Infinite Loop Test</title>
        </head>
        <body>
            <div id="content-container">
                <h1>Infinite Loop Test</h1>
                <p>This test verifies that the page preview doesn't get stuck in an infinite loop.</p>
            </div>
        </body>
        </html>
        """

        # Load the HTML and force multiple verification attempts
        self.page_preview.update_preview(html)

        # Force multiple fit_to_page calls in quick succession to test stability
        for i in range(5):
            logger.debug(f"Fit to page attempt {i+1}")
            self.page_preview.fit_to_page()

        # Check if we're still responsive after multiple attempts
        QTimer.singleShot(1000, lambda: logger.debug("Test completed successfully"))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test page preview functionality")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    window = PagePreviewTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
