"""
Pagination Manager for the Page Preview component.
"""

import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

class PaginationManager:
    """Manages pagination functionality for the page preview component."""
    
    def __init__(self):
        """Initialize the pagination manager."""
        self.current_page = 1
        self.total_pages = 1
        self.content_blocks = []
        self.page_width_mm = 210  # A4 width
        self.page_height_mm = 297  # A4 height
        self.margin_top_mm = 25
        self.margin_right_mm = 25
        self.margin_bottom_mm = 25
        self.margin_left_mm = 25
        
    def initialize(self, current_page=1):
        """Initialize the pagination manager with the current page."""
        self.current_page = current_page
        
    def split_content(self, html_content):
        """Split HTML content into pages for pagination."""
        logger.debug("Splitting content into pages")
        
        if not html_content:
            logger.warning("No content to split")
            return []
            
        try:
            # For now, we'll use a simple approach to split content
            # In a real implementation, this would be more sophisticated
            
            # Remove any standalone "Document" text
            html_content = self._remove_document_text(html_content)
            
            # Split content at page break markers
            blocks = self._split_at_page_breaks(html_content)
            
            # Store the content blocks
            self.content_blocks = blocks
            
            # Update total pages
            self.total_pages = len(blocks)
            
            logger.debug(f"Split content into {self.total_pages} pages")
            
            return blocks
        except Exception as e:
            logger.error(f"Error splitting content: {str(e)}")
            return [html_content]  # Return the original content as a single block
            
    def _remove_document_text(self, content):
        """Remove any standalone 'Document' text from the content."""
        if content is None:
            return ""
        
        # Use regex to remove standalone "Document" heading
        import re
        # Match "Document" as a standalone heading (h1-h6)
        pattern = r'<h[1-6][^>]*>\s*Document\s*</h[1-6]>'
        content = re.sub(pattern, '', content)
        
        return content
        
    def _split_at_page_breaks(self, html_content):
        """Split content at page break markers."""
        # Look for page break markers
        page_break_pattern = r'<div\s+class="page-break"[^>]*>.*?</div>'
        
        # Split the content at page breaks
        parts = re.split(page_break_pattern, html_content)
        
        # If no page breaks found, return the content as a single block
        if len(parts) == 1:
            return [html_content]
            
        # Process each part to ensure it's valid HTML
        blocks = []
        for part in parts:
            # Skip empty parts
            if not part.strip():
                continue
                
            # Ensure each part has proper HTML structure
            if '<html>' not in part:
                # If it's a fragment, wrap it in basic HTML
                part = f"""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                </head>
                <body>
                    {part}
                </body>
                </html>
                """
                
            blocks.append(part)
            
        # If no valid blocks found, return the original content
        if not blocks:
            return [html_content]
            
        return blocks
        
    def go_to_page(self, page_number):
        """Go to the specified page."""
        logger.debug(f"Going to page {page_number}")
        
        # Validate page number
        if page_number < 1:
            page_number = 1
        if page_number > self.total_pages:
            page_number = self.total_pages
            
        # Update current page
        self.current_page = page_number
        
        return True
        
    def get_current_page_content(self):
        """Get the content for the current page."""
        if not self.content_blocks:
            logger.warning("No content blocks available")
            return ""
            
        # Validate current page
        if self.current_page < 1:
            self.current_page = 1
        if self.current_page > len(self.content_blocks):
            self.current_page = len(self.content_blocks)
            
        # Return the content for the current page
        return self.content_blocks[self.current_page - 1]
        
    def get_all_pages_content(self):
        """Get the content for all pages."""
        return self.content_blocks


def create_pagination_html(content_blocks):
    """Create HTML with pagination from content blocks."""
    logger.debug(f"Creating paginated HTML from {len(content_blocks)} blocks")
    
    if not content_blocks:
        logger.warning("No content blocks provided")
        return ""
        
    try:
        # Create HTML with pagination
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }
                .page-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                }
                .page {
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    margin-bottom: 20px;
                    position: relative;
                    width: 210mm;
                    min-height: 297mm;
                    padding: 25mm;
                    box-sizing: border-box;
                    display: none;
                }
                .page.current-page {
                    display: block;
                }
                .page-content {
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                }
                .page-number {
                    position: absolute;
                    bottom: 10mm;
                    right: 10mm;
                    font-size: 10pt;
                    color: #888;
                }
                @media print {
                    body {
                        background-color: white;
                    }
                    .page {
                        box-shadow: none;
                        margin-bottom: 0;
                        page-break-after: always;
                        display: block;
                    }
                    .page:last-child {
                        page-break-after: avoid;
                    }
                }
            </style>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Initialize pagination
                    var pages = document.querySelectorAll('.page');
                    if (pages.length > 0) {
                        // Show the first page
                        pages[0].classList.add('current-page');
                        
                        // Update page counter
                        if (window.updatePageNavigation) {
                            window.updatePageNavigation(1, pages.length);
                        }
                    }
                });
            </script>
        </head>
        <body>
            <div class="page-container">
        """
        
        # Add each page
        for i, content in enumerate(content_blocks):
            # Extract the body content from the block
            body_content = extract_body_content(content)
            
            # Add the page
            html += f"""
                <div class="page" id="page-{i+1}">
                    <div class="page-content">
                        {body_content}
                    </div>
                    <div class="page-number">{i+1}</div>
                </div>
            """
            
        # Close the HTML
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    except Exception as e:
        logger.error(f"Error creating paginated HTML: {str(e)}")
        return ""


def extract_body_content(html):
    """Extract the body content from HTML."""
    if not html:
        return ""
        
    try:
        # Use regex to extract content between <body> tags
        body_pattern = r'<body[^>]*>(.*?)</body>'
        match = re.search(body_pattern, html, re.DOTALL)
        
        if match:
            return match.group(1)
        else:
            # If no body tags found, return the original content
            return html
    except Exception as e:
        logger.error(f"Error extracting body content: {str(e)}")
        return html
