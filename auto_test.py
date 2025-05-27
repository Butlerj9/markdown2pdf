#!/usr/bin/env python3
"""
Automated test script for page preview
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer, QEventLoop
from page_preview import PagePreview

class AutoTestWindow(QMainWindow):
    """Automated test window for page preview"""
    
    def __init__(self):
        super().__init__()
        
        # Set up the window
        self.setWindowTitle("Page Preview Automated Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create the layout
        layout = QVBoxLayout(central_widget)
        
        # Create the preview
        self.preview = PagePreview()
        layout.addWidget(self.preview)
        
        # Create status label
        self.status_label = QLabel("Test not started")
        layout.addWidget(self.status_label)
        
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
        
        # Set up a timer to start the test after a delay
        QTimer.singleShot(2000, self.start_test)
    
    def start_test(self):
        """Start the automated test"""
        self.status_label.setText("Test started")
        print("Starting automated test...")
        
        # Check initial page count
        self.check_pages()
        
        # Set up test sequence
        self.test_sequence = [
            (self.test_next_page, "Testing next page navigation"),
            (self.test_next_page, "Testing next page navigation again"),
            (self.test_previous_page, "Testing previous page navigation"),
            (self.test_previous_page, "Testing previous page navigation again"),
            (lambda: self.test_go_to_page(2), "Testing navigation to page 2"),
            (lambda: self.test_go_to_page(3), "Testing navigation to page 3"),
            (lambda: self.test_go_to_page(1), "Testing navigation to page 1"),
            (self.test_page_layout, "Testing page layout")
        ]
        
        # Start the test sequence
        self.current_test = 0
        self.run_next_test()
    
    def run_next_test(self):
        """Run the next test in the sequence"""
        if self.current_test < len(self.test_sequence):
            test_func, description = self.test_sequence[self.current_test]
            self.status_label.setText(description)
            print(f"\n{description}")
            
            # Run the test after a short delay
            QTimer.singleShot(500, lambda: self.execute_test(test_func))
        else:
            self.status_label.setText("All tests completed")
            print("\nAll tests completed")
            
            # Exit after a delay
            QTimer.singleShot(2000, QApplication.quit)
    
    def execute_test(self, test_func):
        """Execute a test function and proceed to the next test"""
        test_func()
        self.current_test += 1
        
        # Run the next test after a delay
        QTimer.singleShot(1000, self.run_next_test)
    
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
    
    def test_next_page(self):
        """Test navigation to next page"""
        print("Going to next page...")
        self.preview.go_to_next_page()
        
        # Check current page after navigation
        QTimer.singleShot(500, self.check_pages)
    
    def test_previous_page(self):
        """Test navigation to previous page"""
        print("Going to previous page...")
        self.preview.go_to_previous_page()
        
        # Check current page after navigation
        QTimer.singleShot(500, self.check_pages)
    
    def test_go_to_page(self, page_number):
        """Test navigation to a specific page"""
        print(f"Going to page {page_number}...")
        self.preview.go_to_page(page_number)
        
        # Check current page after navigation
        QTimer.singleShot(500, self.check_pages)
    
    def test_page_layout(self):
        """Test page layout"""
        print("Testing page layout...")
        
        # Check page dimensions
        self.preview.web_page.runJavaScript(
            """
            (function() {
                var pages = document.querySelectorAll('.page');
                if (pages.length > 0) {
                    var firstPage = pages[0];
                    return {
                        width: firstPage.offsetWidth,
                        height: firstPage.offsetHeight,
                        padding: getComputedStyle(firstPage).padding
                    };
                }
                return null;
            })();
            """,
            lambda result: print(f"Page dimensions: {result}")
        )
        
        # Check if pages container exists
        self.preview.web_page.runJavaScript(
            "document.querySelector('.pages-container') ? true : false",
            lambda result: print(f"Pages container exists: {result}")
        )
        
        # Check if page numbers are displayed
        self.preview.web_page.runJavaScript(
            "document.querySelector('.page-number') ? true : false",
            lambda result: print(f"Page numbers displayed: {result}")
        )

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Create the auto test window
    window = AutoTestWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
