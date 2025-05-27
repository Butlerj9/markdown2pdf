"""
Pagination module for handling page navigation in HTML content.
This module provides functions for navigating between pages in HTML content.
"""

import logging
from PyQt6.QtCore import QTimer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class PaginationManager:
    """Manages pagination for HTML content displayed in a QWebEngineView"""
    
    def __init__(self, web_view):
        """Initialize the pagination manager
        
        Args:
            web_view: The QWebEngineView to manage pagination for
        """
        self.web_view = web_view
        self.current_page = 1
        self.total_pages = 1
        self.page_change_callbacks = []
    
    def add_page_change_callback(self, callback):
        """Add a callback to be called when the page changes
        
        Args:
            callback: A function that takes two arguments: current_page and total_pages
        """
        self.page_change_callbacks.append(callback)
    
    def update_page_info(self):
        """Update page information"""
        # Get total pages
        self.web_view.page().runJavaScript("getTotalPages()", self._handle_total_pages)
        
        # Get current page
        self.web_view.page().runJavaScript("getCurrentPage()", self._handle_current_page)
    
    def _handle_total_pages(self, result):
        """Handle the result of getting total pages"""
        try:
            self.total_pages = int(result) if result else 1
            logger.debug(f"Total pages: {self.total_pages}")
            self._notify_page_change()
        except Exception as e:
            logger.error(f"Error handling total pages: {str(e)}")
    
    def _handle_current_page(self, result):
        """Handle the result of getting current page"""
        try:
            self.current_page = int(result) if result else 1
            logger.debug(f"Current page: {self.current_page}")
            self._notify_page_change()
        except Exception as e:
            logger.error(f"Error handling current page: {str(e)}")
    
    def _notify_page_change(self):
        """Notify all callbacks that the page has changed"""
        for callback in self.page_change_callbacks:
            try:
                callback(self.current_page, self.total_pages)
            except Exception as e:
                logger.error(f"Error in page change callback: {str(e)}")
    
    def go_to_prev_page(self):
        """Go to the previous page"""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)
    
    def go_to_next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)
    
    def go_to_page(self, page_number):
        """Go to a specific page"""
        logger.debug(f"Going to page {page_number}")
        
        # Execute JavaScript to navigate to the page
        script = f"goToPage({page_number})"
        self.web_view.page().runJavaScript(script, self._handle_page_navigation)
    
    def _handle_page_navigation(self, result):
        """Handle the result of page navigation"""
        if result:
            # Update page information after navigation
            QTimer.singleShot(100, self.update_page_info)
        else:
            logger.error("Failed to navigate to page")

def create_pagination_html(content_blocks, page_width_mm=210, page_height_mm=297, margin_mm=25):
    """Create HTML with pagination
    
    Args:
        content_blocks: A list of HTML content blocks, one for each page
        page_width_mm: Page width in mm (default: 210, A4 width)
        page_height_mm: Page height in mm (default: 297, A4 height)
        margin_mm: Page margin in mm (default: 25)
        
    Returns:
        str: HTML content with pagination
    """
    # Create HTML header with styles and scripts
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Paginated Document</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }}
            .page {{
                width: {page_width_mm}mm;
                min-height: {page_height_mm}mm;
                padding: {margin_mm}mm;
                margin: 10mm auto;
                background: white;
                box-sizing: border-box;
                position: relative;
                border: 1px solid #ccc;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .current-page {{
                border: 2px solid blue;
            }}
            .page-number {{
                position: absolute;
                bottom: 10mm;
                right: 10mm;
                font-size: 12px;
                color: #666;
            }}
        </style>
        <script>
            var currentPage = 1;
            var totalPages = {len(content_blocks)};
            
            function goToPage(pageNum) {{
                // Get all pages
                var pages = document.querySelectorAll('.page');
                
                // Validate page number
                if (pageNum < 1 || pageNum > pages.length) {{
                    return false;
                }}
                
                // Update current page
                currentPage = pageNum;
                
                // Remove current-page class from all pages
                pages.forEach(function(page) {{
                    page.classList.remove('current-page');
                }});
                
                // Add current-page class to the selected page
                pages[pageNum-1].classList.add('current-page');
                
                // Scroll to the page
                pages[pageNum-1].scrollIntoView({{behavior: 'smooth'}});
                
                return true;
            }}
            
            function nextPage() {{
                if (currentPage < totalPages) {{
                    return goToPage(currentPage + 1);
                }}
                return false;
            }}
            
            function prevPage() {{
                if (currentPage > 1) {{
                    return goToPage(currentPage - 1);
                }}
                return false;
            }}
            
            function getCurrentPage() {{
                return currentPage;
            }}
            
            function getTotalPages() {{
                return totalPages;
            }}
        </script>
    </head>
    <body>
    '''
    
    # Add content blocks as pages
    for i, content in enumerate(content_blocks):
        page_class = 'page current-page' if i == 0 else 'page'
        html += f'''
        <div class="{page_class}">
            {content}
            <div class="page-number">{i + 1}</div>
        </div>
        '''
    
    # Close HTML
    html += '''
    </body>
    </html>
    '''
    
    return html
