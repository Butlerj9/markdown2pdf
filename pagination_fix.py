"""
This module contains the pagination fix for the page preview component.
It provides a simplified implementation of the pagination functionality.
"""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class PaginationManager:
    """Manages pagination for the page preview component"""
    
    def __init__(self, web_view, page_entry, prev_btn, next_btn, total_pages_label):
        """Initialize the pagination manager
        
        Args:
            web_view: The QWebEngineView to manage pagination for
            page_entry: The QSpinBox for entering page numbers
            prev_btn: The QPushButton for going to the previous page
            next_btn: The QPushButton for going to the next page
            total_pages_label: The QLabel for displaying the total number of pages
        """
        self.web_view = web_view
        self.page_entry = page_entry
        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self.total_pages_label = total_pages_label
        
        # Initialize variables
        self.current_page = 1
        self.total_pages = 1
        
        # Connect signals
        self.page_entry.valueChanged.connect(self.go_to_entered_page)
        self.prev_btn.clicked.connect(self.go_to_prev_page)
        self.next_btn.clicked.connect(self.go_to_next_page)
    
    def update_page_info(self):
        """Update page information"""
        # Get total pages
        self.web_view.page().runJavaScript("getTotalPages()", self.handle_total_pages)
        
        # Get current page
        self.web_view.page().runJavaScript("getCurrentPage()", self.handle_current_page)
    
    def handle_total_pages(self, result):
        """Handle the result of getting total pages"""
        try:
            self.total_pages = int(result) if result else 1
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
            self.current_page = int(result) if result else 1
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
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
    
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

def create_pagination_controls():
    """Create pagination controls
    
    Returns:
        tuple: (layout, page_entry, prev_btn, next_btn, total_pages_label)
    """
    # Create layout
    layout = QHBoxLayout()
    
    # Previous page button
    prev_btn = QPushButton("Previous Page")
    layout.addWidget(prev_btn)
    
    # Page number input
    page_entry = QSpinBox()
    page_entry.setMinimum(1)
    page_entry.setMaximum(1)
    layout.addWidget(page_entry)
    
    # Page count label
    page_label = QLabel("of")
    layout.addWidget(page_label)
    
    # Total pages label
    total_pages_label = QLabel("1")
    layout.addWidget(total_pages_label)
    
    # Next page button
    next_btn = QPushButton("Next Page")
    layout.addWidget(next_btn)
    
    return layout, page_entry, prev_btn, next_btn, total_pages_label

def setup_pagination(web_view, layout=None):
    """Set up pagination for a web view
    
    Args:
        web_view: The QWebEngineView to set up pagination for
        layout: Optional layout to add pagination controls to
        
    Returns:
        PaginationManager: The pagination manager
    """
    # Create pagination controls if layout is provided
    if layout:
        pagination_layout, page_entry, prev_btn, next_btn, total_pages_label = create_pagination_controls()
        layout.addLayout(pagination_layout)
    else:
        # Create controls without adding to a layout
        _, page_entry, prev_btn, next_btn, total_pages_label = create_pagination_controls()
    
    # Create pagination manager
    pagination_manager = PaginationManager(
        web_view, page_entry, prev_btn, next_btn, total_pages_label
    )
    
    # Initialize pagination
    QTimer.singleShot(500, pagination_manager.update_page_info)
    
    return pagination_manager
