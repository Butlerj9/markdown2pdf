import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MinimalPaginationTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Pagination Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Create navigation buttons
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.go_prev)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        self.setCentralWidget(central_widget)
        
        # Load HTML content
        self.load_html()
        
    def load_html(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
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
                    return goToPage(currentPage + 1);
                }
                
                function prevPage() {
                    return goToPage(currentPage - 1);
                }
                
                function getTotalPages() {
                    return document.querySelectorAll('.page').length;
                }
                
                function getCurrentPage() {
                    return currentPage;
                }
            </script>
        </head>
        <body>
            <div class="page current-page">
                <h1>Page 1</h1>
                <p>This is the first page.</p>
                <div class="page-number">1</div>
            </div>
            
            <div class="page">
                <h1>Page 2</h1>
                <p>This is the second page.</p>
                <div class="page-number">2</div>
            </div>
            
            <div class="page">
                <h1>Page 3</h1>
                <p>This is the third page.</p>
                <div class="page-number">3</div>
            </div>
        </body>
        </html>
        """
        self.web_view.setHtml(html)
    
    def go_prev(self):
        self.web_view.page().runJavaScript("prevPage()")
    
    def go_next(self):
        self.web_view.page().runJavaScript("nextPage()")

def main():
    app = QApplication(sys.argv)
    window = MinimalPaginationTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
