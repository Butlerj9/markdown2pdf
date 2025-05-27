#!/usr/bin/env python3
"""
Test Improved Page Preview
----------------
Command-line tool to test the improved page preview functionality.
"""

import sys
import os
import argparse
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QComboBox, QSlider
from PyQt6.QtCore import Qt, QTimer
from page_preview import PagePreview
from improved_page_preview_fixed import apply_improved_preview
from logging_config import get_logger

logger = get_logger()

class ImprovedPreviewTestWindow(QMainWindow):
    """Test window for improved page preview functionality"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Improved Page Preview Test")
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

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(50)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        controls_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        controls_layout.addWidget(self.zoom_label)

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

        # Add controls to main layout
        main_layout.addLayout(controls_layout)

        # Create page preview
        self.page_preview = PagePreview()
        
        # Apply our improved preview fixes
        self.page_preview = apply_improved_preview(self.page_preview)
        
        # Add zoom slider reference
        self.page_preview.zoom_slider = self.zoom_slider
        self.page_preview.zoom_label = self.zoom_label
        
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

    def load_sample_html(self):
        """Load sample HTML content for testing"""
        sample_html = """
        <html>
        <head>
            <title>Improved Page Preview Test</title>
            <style>
                /* Base styles for content */
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.5;
                    color: #333;
                }
                
                h1 {
                    font-size: 24px;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                
                h2 {
                    font-size: 20px;
                    margin-top: 16px;
                    margin-bottom: 8px;
                }
                
                h3 {
                    font-size: 16px;
                    margin-top: 12px;
                    margin-bottom: 6px;
                }
                
                p {
                    margin-bottom: 10px;
                }
                
                ul, ol {
                    margin-bottom: 10px;
                    padding-left: 20px;
                }
                
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 15px;
                }
                
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                
                th {
                    background-color: #f2f2f2;
                }
                
                pre {
                    background-color: #f5f5f5;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    overflow-x: auto;
                    font-family: "Courier New", monospace;
                }
                
                /* Text alignment examples */
                .text-left {
                    text-align: left;
                }
                
                .text-center {
                    text-align: center;
                }
                
                .text-right {
                    text-align: right;
                }
                
                .text-justify {
                    text-align: justify;
                }
            </style>
        </head>
        <body>
            <h1>Improved Page Preview Test</h1>
            <p>This document tests the improved page preview functionality with multiple pages and various content types.</p>
            
            <h2>Text Alignment Test</h2>
            <p class="text-left">This paragraph is left-aligned (default). Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <p class="text-center">This paragraph is center-aligned. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <p class="text-right">This paragraph is right-aligned. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <p class="text-justify">This paragraph is justified. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            
            <h2>Lists Test</h2>
            <h3>Unordered List</h3>
            <ul>
                <li>Item 1</li>
                <li>Item 2
                    <ul>
                        <li>Subitem 2.1</li>
                        <li>Subitem 2.2</li>
                    </ul>
                </li>
                <li>Item 3</li>
            </ul>
            
            <h3>Ordered List</h3>
            <ol>
                <li>First item</li>
                <li>Second item
                    <ol type="a">
                        <li>Subitem a</li>
                        <li>Subitem b</li>
                    </ol>
                </li>
                <li>Third item</li>
            </ol>
            
            <h2>Table Test</h2>
            <table>
                <thead>
                    <tr>
                        <th>Header 1</th>
                        <th>Header 2</th>
                        <th>Header 3</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Row 1, Cell 1</td>
                        <td>Row 1, Cell 2</td>
                        <td>Row 1, Cell 3</td>
                    </tr>
                    <tr>
                        <td>Row 2, Cell 1</td>
                        <td>Row 2, Cell 2</td>
                        <td>Row 2, Cell 3</td>
                    </tr>
                    <tr>
                        <td>Row 3, Cell 1</td>
                        <td>Row 3, Cell 2</td>
                        <td>Row 3, Cell 3</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Second Page</h1>
            <p>This content should appear on the second page.</p>
            
            <h2>Code Block Example</h2>
            <pre><code>
def hello_world():
    # Print a greeting message
    print("Hello, world!")
    return True

# Call the function
result = hello_world()
            </code></pre>
            
            <h2>Image Placeholder</h2>
            <div style="width: 300px; height: 200px; background-color: #eee; border: 1px solid #ddd; display: flex; align-items: center; justify-content: center;">
                [Image would appear here]
            </div>
            
            <h2>Long Paragraph</h2>
            <p>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </p>
            <p>
                Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
            </p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Third Page</h1>
            <p>This content should appear on the third page.</p>
            
            <h2>Blockquote Example</h2>
            <blockquote style="border-left: 4px solid #ccc; padding-left: 15px; margin-left: 0; color: #666;">
                <p>This is a blockquote. It should be properly formatted and maintain its left alignment.</p>
                <p>— Author Name</p>
            </blockquote>
            
            <h2>Definition List</h2>
            <dl>
                <dt>Term 1</dt>
                <dd>Definition 1. This is a longer definition that might wrap to multiple lines depending on the width of the page and the zoom level.</dd>
                <dt>Term 2</dt>
                <dd>Definition 2</dd>
                <dt>Term 3</dt>
                <dd>Definition 3</dd>
            </dl>
            
            <h2>Horizontal Rule</h2>
            <hr>
            
            <h2>Footer Information</h2>
            <p>This is the end of the test document. The page preview should correctly display all three pages with proper navigation between them.</p>
        </body>
        </html>
        """

        self.page_preview.update_preview(sample_html)

    def change_zoom(self, value):
        """Change the zoom level"""
        logger.debug(f"Changing zoom to {value}%")
        self.zoom_label.setText(f"{value}%")
        self.page_preview.update_zoom(value)

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
        if hasattr(self.page_preview, 'debug_page_layout'):
            self.page_preview.debug_page_layout()
        else:
            logger.debug("No debug_page_layout method available")
            # Run JavaScript to get page information
            debug_script = """
            (function() {
                var pages = document.querySelectorAll('.page');
                var info = {
                    pageCount: pages.length,
                    bodyStyles: {
                        textAlign: getComputedStyle(document.body).textAlign,
                        margin: getComputedStyle(document.body).margin,
                        padding: getComputedStyle(document.body).padding,
                        backgroundColor: getComputedStyle(document.body).backgroundColor
                    },
                    pageStyles: []
                };
                
                for (var i = 0; i < Math.min(pages.length, 3); i++) {
                    var page = pages[i];
                    info.pageStyles.push({
                        width: page.offsetWidth,
                        height: page.offsetHeight,
                        textAlign: getComputedStyle(page).textAlign,
                        transform: getComputedStyle(page).transform,
                        margin: getComputedStyle(page).margin
                    });
                }
                
                return info;
            })();
            """
            self.page_preview.web_page.runJavaScript(debug_script, lambda result:
                logger.debug(f"Page debug info: {result}"))

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


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test improved page preview functionality")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    app = QApplication(sys.argv)
    window = ImprovedPreviewTestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()