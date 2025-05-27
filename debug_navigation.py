#!/usr/bin/env python3
"""
Debug script for page navigation
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QTextEdit, QSpinBox
from PyQt6.QtCore import QTimer
from page_preview import PagePreview

class DebugNavigationWindow(QMainWindow):
    """Debug window for page navigation"""

    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Debug Page Navigation")
        self.setGeometry(100, 100, 1000, 800)

        # Create the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the layout
        layout = QVBoxLayout(central_widget)

        # Create the preview
        self.preview = PagePreview()

        # Hide the built-in navigation controls
        self.preview.nav_container.setVisible(False)

        layout.addWidget(self.preview, 1)  # Give it a stretch factor of 1

        # Create debug log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(200)
        layout.addWidget(self.log_area)

        # Create navigation controls
        nav_layout = QHBoxLayout()

        # Previous page button
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.go_to_previous_page)
        self.prev_button.setEnabled(False)  # Initially disabled since we start on page 1
        nav_layout.addWidget(self.prev_button)

        # Page navigation layout
        page_nav_layout = QHBoxLayout()

        # Page entry field
        self.page_entry = QSpinBox()
        self.page_entry.setMinimum(1)
        self.page_entry.setMaximum(999)
        self.page_entry.setValue(1)
        self.page_entry.setFixedWidth(50)
        self.page_entry.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)  # Hide the up/down arrows
        self.page_entry.editingFinished.connect(self.go_to_entered_page)
        page_nav_layout.addWidget(self.page_entry)

        # "of" label
        page_nav_layout.addWidget(QLabel("of"))

        # Total pages label
        self.total_pages_label = QLabel("1")
        page_nav_layout.addWidget(self.total_pages_label)

        # Add the page navigation layout to the main navigation layout
        nav_layout.addLayout(page_nav_layout)

        # Next page button
        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.go_to_next_page)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        # Create page buttons
        page_layout = QHBoxLayout()

        self.page1_button = QPushButton("Page 1")
        self.page1_button.clicked.connect(lambda: self.go_to_page(1))
        page_layout.addWidget(self.page1_button)

        self.page2_button = QPushButton("Page 2")
        self.page2_button.clicked.connect(lambda: self.go_to_page(2))
        page_layout.addWidget(self.page2_button)

        self.page3_button = QPushButton("Page 3")
        self.page3_button.clicked.connect(lambda: self.go_to_page(3))
        page_layout.addWidget(self.page3_button)

        # Add debug buttons
        self.check_button = QPushButton("Check Current Page")
        self.check_button.clicked.connect(self.check_current_page)
        page_layout.addWidget(self.check_button)

        self.debug_button = QPushButton("Debug JS")
        self.debug_button.clicked.connect(self.debug_js)
        page_layout.addWidget(self.debug_button)

        layout.addLayout(page_layout)

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
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                h1 {
                    color: #333;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }
                .page-content {
                    padding: 20px;
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Page 1</h1>
            <div class="page-content">
                <p>This is the content of page 1.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            </div>

            <div style="page-break-before: always;"></div>

            <h1>Page 2</h1>
            <div class="page-content">
                <p>This is the content of page 2.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            </div>

            <div style="page-break-before: always;"></div>

            <h1>Page 3</h1>
            <div class="page-content">
                <p>This is the content of page 3.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
                nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
            </div>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(self.test_html)

        # Connect page count changed signal
        self.preview.page_count_changed.connect(self.update_page_counter)

        # Set up a timer to check the page count after a delay
        QTimer.singleShot(2000, self.check_pages)

        # Log initialization
        self.log("Debug navigation window initialized")

    def log(self, message):
        """Add a message to the log area"""
        self.log_area.append(message)
        print(message)

    def check_pages(self):
        """Check the page count"""
        # Run JavaScript to count pages
        self.preview.web_page.runJavaScript(
            "document.querySelectorAll('.page').length",
            lambda count: self.log(f"Page count: {count}")
        )

        # Run JavaScript to check if first page is marked as current
        self.preview.web_page.runJavaScript(
            "document.querySelector('.page.current-page') ? 1 : 0",
            lambda current: self.log(f"Current page exists: {current}")
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
            lambda current: self.log(f"Current page index: {current}")
        )

        # Check the global current page index
        self.preview.web_page.runJavaScript(
            "window.currentPageIndex !== undefined ? window.currentPageIndex + 1 : 'undefined'",
            lambda index: self.log(f"Global current page index: {index}")
        )

    def go_to_previous_page(self):
        """Navigate to the previous page"""
        self.log("Going to previous page...")
        self.preview.go_to_previous_page()
        # Check the current page after a short delay to allow the navigation to complete
        QTimer.singleShot(500, self.check_current_page)

    def go_to_next_page(self):
        """Navigate to the next page"""
        self.log("Going to next page...")
        self.preview.go_to_next_page()
        # Check the current page after a short delay to allow the navigation to complete
        QTimer.singleShot(500, self.check_current_page)

    def go_to_page(self, page_number):
        """Navigate to a specific page"""
        self.log(f"Going to page {page_number}...")
        self.preview.go_to_page(page_number)
        # Check the current page after a short delay to allow the navigation to complete
        QTimer.singleShot(500, self.check_current_page)

    def go_to_entered_page(self):
        """Navigate to the page entered in the page entry field"""
        entered_page = self.page_entry.value()

        # Get the total number of pages from the preview
        self.preview.web_page.runJavaScript(
            """
            (function() {
                var pages = document.querySelectorAll('.page');
                return pages.length;
            })();
            """,
            lambda total_pages: self.validate_and_navigate(entered_page, total_pages)
        )

    def validate_and_navigate(self, entered_page, total_pages):
        """Validate the entered page number and navigate to it"""
        # Ensure page number is within valid range
        valid_page = max(1, min(entered_page, total_pages))

        # If the entered value was invalid, update the field
        if valid_page != entered_page:
            self.log(f"Correcting page number from {entered_page} to {valid_page}")
            self.page_entry.blockSignals(True)
            self.page_entry.setValue(valid_page)
            self.page_entry.blockSignals(False)

        self.log(f"Going to entered page {valid_page}...")
        self.go_to_page(valid_page)

    def check_current_page(self):
        """Check the current page"""
        self.log("Checking current page...")

        # Get comprehensive page information
        self.preview.web_page.runJavaScript(
            """
            (function() {
                var pages = document.querySelectorAll('.page');
                var totalPages = pages.length;

                // Find current page index
                var currentIndex = -1;
                for (var i = 0; i < pages.length; i++) {
                    if (pages[i].classList.contains('current-page')) {
                        currentIndex = i;
                        break;
                    }
                }

                // If no current page found, default to first page
                if (currentIndex === -1 && pages.length > 0) {
                    currentIndex = 0;
                    // Set the first page as current
                    pages[0].classList.add('current-page');
                }

                // Get all page classes for debugging
                var classes = [];
                for (var i = 0; i < pages.length; i++) {
                    classes.push(pages[i].className);
                }

                return {
                    currentPageIndex: currentIndex + 1,
                    globalCurrentPageIndex: window.currentPageIndex !== undefined ?
                        window.currentPageIndex + 1 : 'undefined',
                    totalPages: totalPages,
                    pageClasses: classes
                };
            })();
            """,
            self.process_page_info
        )

    def process_page_info(self, info):
        """Process page information"""
        if not info:
            self.log("No page information received")
            return

        self.log(f"Current page index: {info['currentPageIndex']}")
        self.log(f"Global current page index: {info['globalCurrentPageIndex']}")
        self.log(f"Total pages: {info['totalPages']}")
        self.log(f"Page classes: {info['pageClasses']}")

        # Update the page counter
        self.update_page_counter(info['currentPageIndex'], info['totalPages'])

    def debug_js(self):
        """Run JavaScript debug code"""
        self.log("Running JavaScript debug code...")

        debug_script = """
        (function() {
            console.log('Debug script running...');

            // Check if navigateToPage function exists
            if (typeof window.navigateToPage === 'function') {
                console.log('navigateToPage function exists');
            } else {
                console.log('navigateToPage function does NOT exist');
            }

            // Check current page index
            console.log('Current page index: ' + window.currentPageIndex);

            // Check all pages
            var pages = document.querySelectorAll('.page');
            console.log('Found ' + pages.length + ' pages');

            // Check which page has current-page class
            var currentPageIndex = -1;
            for (var i = 0; i < pages.length; i++) {
                if (pages[i].classList.contains('current-page')) {
                    currentPageIndex = i;
                    break;
                }
            }

            if (currentPageIndex >= 0) {
                console.log('Current page class is on page ' + (currentPageIndex + 1));
            } else {
                console.log('No page has current-page class');
            }

            // Return debug info
            return {
                navigateToPageExists: typeof window.navigateToPage === 'function',
                currentPageIndex: window.currentPageIndex,
                totalPages: pages.length,
                currentPageClassIndex: currentPageIndex
            };
        })();
        """

        self.preview.web_page.runJavaScript(debug_script, lambda result: self.log(f"Debug result: {result}"))

    def update_page_counter(self, current_page, total_pages):
        """Update the page counter"""
        self.log(f"Page counter updated: {current_page} of {total_pages}")

        # Update the page entry field (without triggering the editingFinished signal)
        self.page_entry.blockSignals(True)
        self.page_entry.setValue(current_page)
        self.page_entry.blockSignals(False)

        # Update the total pages label
        self.total_pages_label.setText(str(total_pages))

        # Update the page entry field's maximum value
        self.page_entry.setMaximum(max(1, total_pages))

        # Enable/disable navigation buttons
        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)

        # Check if the page counter was actually updated
        self.preview.web_page.runJavaScript(
            """
            (function() {
                return {
                    currentPage: window.currentPageIndex !== undefined ?
                        window.currentPageIndex + 1 : 'undefined',
                    totalPages: document.querySelectorAll('.page').length
                };
            })();
            """,
            lambda result: self.log(f"Page counter check: {result}")
        )

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create the debug window
    window = DebugNavigationWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
