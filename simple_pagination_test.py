import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QSpinBox
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class SimplePaginationTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Pagination Test")
        self.setGeometry(100, 100, 1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)
        
        # Create navigation controls
        nav_layout = QHBoxLayout()
        
        # Previous page button
        self.prev_page_btn = QPushButton("Previous Page")
        self.prev_page_btn.clicked.connect(self.go_to_prev_page)
        nav_layout.addWidget(self.prev_page_btn)
        
        # Page number input
        self.page_entry = QSpinBox()
        self.page_entry.setMinimum(1)
        self.page_entry.setMaximum(1)
        self.page_entry.valueChanged.connect(self.go_to_entered_page)
        nav_layout.addWidget(self.page_entry)
        
        # Page count label
        self.page_label = QLabel("of")
        nav_layout.addWidget(self.page_label)
        
        # Total pages label
        self.total_pages_label = QLabel("1")
        nav_layout.addWidget(self.total_pages_label)
        
        # Next page button
        self.next_page_btn = QPushButton("Next Page")
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        nav_layout.addWidget(self.next_page_btn)
        
        # Add navigation layout to main layout
        main_layout.addLayout(nav_layout)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Initialize variables
        self.current_page = 1
        self.total_pages = 1
        
        # Load HTML content
        self.load_html_content()
        
        # Update UI after a delay to ensure page is loaded
        QTimer.singleShot(1000, self.update_page_info)
    
    def load_html_content(self):
        """Load HTML content with multiple pages"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Pagination Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .page {
                    width: 210mm;
                    min-height: 297mm;
                    padding: 25mm;
                    margin: 0 auto;
                    background-color: white;
                    box-sizing: border-box;
                    position: relative;
                    border: 1px solid #ccc;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    margin-bottom: 20px;
                }
                .current-page {
                    border: 2px solid blue;
                }
                .page-number {
                    position: absolute;
                    bottom: 10mm;
                    right: 10mm;
                    font-size: 12px;
                    color: #666;
                }
            </style>
            <script>
                // Function to navigate to a specific page
                function goToPage(pageNumber) {
                    // Get all pages
                    var pages = document.querySelectorAll('.page');
                    
                    // Validate page number
                    if (pageNumber < 1 || pageNumber > pages.length) {
                        console.error('Invalid page number:', pageNumber);
                        return false;
                    }
                    
                    // Remove current-page class from all pages
                    pages.forEach(function(page) {
                        page.classList.remove('current-page');
                    });
                    
                    // Add current-page class to the selected page
                    pages[pageNumber - 1].classList.add('current-page');
                    
                    // Scroll to the page
                    pages[pageNumber - 1].scrollIntoView({behavior: 'smooth'});
                    
                    console.log('Navigated to page', pageNumber);
                    return true;
                }
                
                // Function to get the total number of pages
                function getTotalPages() {
                    return document.querySelectorAll('.page').length;
                }
                
                // Function to get the current page number
                function getCurrentPage() {
                    var currentPage = document.querySelector('.page.current-page');
                    if (!currentPage) {
                        return 1;
                    }
                    
                    var pages = document.querySelectorAll('.page');
                    for (var i = 0; i < pages.length; i++) {
                        if (pages[i] === currentPage) {
                            return i + 1;
                        }
                    }
                    
                    return 1;
                }
            </script>
        </head>
        <body>
            <div id="pages-container">
                <div class="page current-page">
                    <h1>Page 1: First Page</h1>
                    <p>This is the first page of the document.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <div class="page-number">1</div>
                </div>
                
                <div class="page">
                    <h1>Page 2: Second Page</h1>
                    <p>This is the second page of the document.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <div class="page-number">2</div>
                </div>
                
                <div class="page">
                    <h1>Page 3: Third Page</h1>
                    <p>This is the third page of the document.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                    <div class="page-number">3</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Load the HTML content
        self.web_view.setHtml(html_content)
    
    def update_page_info(self):
        """Update page information"""
        # Get total pages
        self.web_view.page().runJavaScript("getTotalPages()", self.handle_total_pages)
        
        # Get current page
        self.web_view.page().runJavaScript("getCurrentPage()", self.handle_current_page)
    
    def handle_total_pages(self, result):
        """Handle the result of getting total pages"""
        try:
            self.total_pages = int(result)
            logger.debug(f"Total pages: {self.total_pages}")
            
            # Update UI
            self.total_pages_label.setText(str(self.total_pages))
            self.page_entry.setMaximum(self.total_pages)
            
            # Update button states
            self.update_button_states()
        except Exception as e:
            logger.error(f"Error handling total pages: {str(e)}")
    
    def handle_current_page(self, result):
        """Handle the result of getting current page"""
        try:
            self.current_page = int(result)
            logger.debug(f"Current page: {self.current_page}")
            
            # Update UI
            if self.page_entry.value() != self.current_page:
                self.page_entry.blockSignals(True)
                self.page_entry.setValue(self.current_page)
                self.page_entry.blockSignals(False)
            
            # Update button states
            self.update_button_states()
        except Exception as e:
            logger.error(f"Error handling current page: {str(e)}")
    
    def update_button_states(self):
        """Update button states based on current page"""
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def go_to_prev_page(self):
        """Go to the previous page"""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)
    
    def go_to_next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)
    
    def go_to_entered_page(self, page_number):
        """Go to the entered page number"""
        self.go_to_page(page_number)
    
    def go_to_page(self, page_number):
        """Go to a specific page"""
        logger.debug(f"Going to page {page_number}")
        
        # Execute JavaScript to navigate to the page
        script = f"goToPage({page_number})"
        self.web_view.page().runJavaScript(script, self.handle_page_navigation)
    
    def handle_page_navigation(self, result):
        """Handle the result of page navigation"""
        if result:
            # Update page information after navigation
            QTimer.singleShot(100, self.update_page_info)
        else:
            logger.error("Failed to navigate to page")

def main():
    app = QApplication(sys.argv)
    window = SimplePaginationTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
