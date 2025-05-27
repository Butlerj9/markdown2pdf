#!/usr/bin/env python3
"""
Debug test script for page preview
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer
from page_preview import PagePreview

class DebugWindow(QMainWindow):
    """Debug window for page preview"""
    
    def __init__(self):
        super().__init__()
        
        # Set up the window
        self.setWindowTitle("Page Preview Debug Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the layout
        layout = QVBoxLayout(central_widget)
        
        # Create the preview
        self.preview = PagePreview()
        layout.addWidget(self.preview)
        
        # Create navigation buttons
        button_layout = QVBoxLayout()
        
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.go_to_previous_page)
        button_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.next_button)
        
        self.page1_button = QPushButton("Page 1")
        self.page1_button.clicked.connect(lambda: self.go_to_page(1))
        button_layout.addWidget(self.page1_button)
        
        self.page2_button = QPushButton("Page 2")
        self.page2_button.clicked.connect(lambda: self.go_to_page(2))
        button_layout.addWidget(self.page2_button)
        
        self.page3_button = QPushButton("Page 3")
        self.page3_button.clicked.connect(lambda: self.go_to_page(3))
        button_layout.addWidget(self.page3_button)
        
        self.check_button = QPushButton("Check Current Page")
        self.check_button.clicked.connect(self.check_current_page)
        button_layout.addWidget(self.check_button)
        
        layout.addLayout(button_layout)
        
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
        
        # Apply document settings
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
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, 
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 2</h1>
            <p>This is the content of page 2.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, 
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 3</h1>
            <p>This is the content of page 3.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, 
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
        </body>
        </html>
        """
        
        # Update the preview with the test HTML
        self.preview.update_preview(self.test_html)
        
        # Set up a timer to check the page count after a delay
        QTimer.singleShot(2000, self.check_pages)
    
    def check_pages(self):
        """Check the page count"""
        # Run JavaScript to count pages
        self.preview.web_page.runJavaScript(
            "document.querySelectorAll('.page').length",
            lambda count: print(f"Page count: {count}")
        )
        
        # Run JavaScript to check if first page is marked as current
        self.preview.web_page.runJavaScript(
            "document.querySelector('.page.current-page') ? 1 : 0",
            lambda current: print(f"Current page: {current}")
        )
    
    def go_to_previous_page(self):
        """Navigate to the previous page"""
        print("Going to previous page...")
        self.preview.go_to_previous_page()
        QTimer.singleShot(500, self.check_current_page)
    
    def go_to_next_page(self):
        """Navigate to the next page"""
        print("Going to next page...")
        self.preview.go_to_next_page()
        QTimer.singleShot(500, self.check_current_page)
    
    def go_to_page(self, page_number):
        """Navigate to a specific page"""
        print(f"Going to page {page_number}...")
        self.preview.go_to_page(page_number)
        QTimer.singleShot(500, self.check_current_page)
    
    def check_current_page(self):
        """Check the current page"""
        # Check if any page has the current-page class
        self.preview.web_page.runJavaScript(
            "document.querySelector('.page.current-page') ? true : false",
            lambda has_current: print(f"Has current page class: {has_current}")
        )
        
        # Check which page has the current-page class
        self.preview.web_page.runJavaScript(
            """
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
            """,
            lambda current: print(f"Current page index: {current}")
        )
        
        # Check all page classes
        self.preview.web_page.runJavaScript(
            """
            (function() {
                var pages = document.querySelectorAll('.page');
                var classes = [];
                for (var i = 0; i < pages.length; i++) {
                    classes.push(pages[i].className);
                }
                return classes;
            })();
            """,
            lambda classes: print(f"Page classes: {classes}")
        )

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Create the debug window
    window = DebugWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
