import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import the pagination fix
from pagination_fix import setup_pagination

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class PaginationTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pagination Fix Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set up pagination
        self.pagination_manager = setup_pagination(self.web_view, layout)
        
        # Load HTML content
        self.load_html_content()
    
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
        
        # Update pagination after a delay
        QTimer.singleShot(500, self.pagination_manager.update_page_info)

def main():
    app = QApplication(sys.argv)
    window = PaginationTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
