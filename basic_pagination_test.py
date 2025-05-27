import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

class BasicPaginationTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic Pagination Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Create navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.go_prev)
        nav_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Page 1 of 3")
        nav_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        self.setCentralWidget(central_widget)
        
        # Initialize current page
        self.current_page = 1
        self.total_pages = 3
        
        # Load HTML content
        self.load_html()
        
    def load_html(self):
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }
                .page {
                    width: 210mm;
                    min-height: 297mm;
                    padding: 20mm;
                    margin: 10mm auto;
                    background: white;
                    border: 1px solid #ccc;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    position: relative;
                }
                .current-page {
                    border: 2px solid blue;
                }
                .page-number {
                    position: absolute;
                    bottom: 10mm;
                    right: 10mm;
                }
            </style>
            <script>
                var currentPage = 1;
                var totalPages = 3;
                
                function goToPage(pageNum) {
                    // Get all pages
                    var pages = document.querySelectorAll('.page');
                    
                    // Validate page number
                    if (pageNum < 1 || pageNum > pages.length) {
                        return false;
                    }
                    
                    // Update current page
                    currentPage = pageNum;
                    
                    // Remove current-page class from all pages
                    pages.forEach(function(page) {
                        page.classList.remove('current-page');
                    });
                    
                    // Add current-page class to the selected page
                    pages[pageNum-1].classList.add('current-page');
                    
                    // Scroll to the page
                    pages[pageNum-1].scrollIntoView({behavior: 'smooth'});
                    
                    return true;
                }
                
                function nextPage() {
                    if (currentPage < totalPages) {
                        return goToPage(currentPage + 1);
                    }
                    return false;
                }
                
                function prevPage() {
                    if (currentPage > 1) {
                        return goToPage(currentPage - 1);
                    }
                    return false;
                }
                
                function getCurrentPage() {
                    return currentPage;
                }
                
                function getTotalPages() {
                    return totalPages;
                }
            </script>
        </head>
        <body>
            <div class="page current-page">
                <h1>Page 1</h1>
                <p>This is the first page.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <div class="page-number">1</div>
            </div>
            
            <div class="page">
                <h1>Page 2</h1>
                <p>This is the second page.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <div class="page-number">2</div>
            </div>
            
            <div class="page">
                <h1>Page 3</h1>
                <p>This is the third page.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
                <div class="page-number">3</div>
            </div>
        </body>
        </html>
        '''
        self.web_view.setHtml(html)
    
    def go_prev(self):
        self.web_view.page().runJavaScript("prevPage()", self.handle_navigation)
    
    def go_next(self):
        self.web_view.page().runJavaScript("nextPage()", self.handle_navigation)
    
    def handle_navigation(self, result):
        if result:
            self.web_view.page().runJavaScript("getCurrentPage()", self.update_page_label)
    
    def update_page_label(self, page):
        self.current_page = page
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
        
        # Update button states
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)

def main():
    app = QApplication(sys.argv)
    window = BasicPaginationTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
