import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import the pagination module
from pagination import PaginationManager, create_pagination_html

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class PaginationTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pagination Module Test")
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
        
        # Create pagination manager
        self.pagination_manager = PaginationManager(self.web_view)
        self.pagination_manager.add_page_change_callback(self.update_ui)
        
        # Load HTML content
        self.load_html_content()
    
    def load_html_content(self):
        """Load HTML content with multiple pages"""
        # Create content blocks for each page
        content_blocks = [
            """
            <h1>Page 1: First Page</h1>
            <p>This is the first page of the document.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            """,
            
            """
            <h1>Page 2: Second Page</h1>
            <p>This is the second page of the document.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            """,
            
            """
            <h1>Page 3: Third Page</h1>
            <p>This is the third page of the document.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            """
        ]
        
        # Create HTML with pagination
        html = create_pagination_html(content_blocks)
        
        # Load the HTML content
        self.web_view.setHtml(html)
        
        # Update pagination information
        self.pagination_manager.update_page_info()
    
    def go_prev(self):
        """Go to the previous page"""
        self.pagination_manager.go_to_prev_page()
    
    def go_next(self):
        """Go to the next page"""
        self.pagination_manager.go_to_next_page()
    
    def update_ui(self, current_page, total_pages):
        """Update UI based on current page and total pages"""
        # Update page label
        self.page_label.setText(f"Page {current_page} of {total_pages}")
        
        # Update button states
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

def main():
    app = QApplication(sys.argv)
    window = PaginationTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
