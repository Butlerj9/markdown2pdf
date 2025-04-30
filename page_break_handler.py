#!/usr/bin/env python3
"""
Page Break Handler for Markdown to PDF Converter
-----------------------------------------------
Handles page breaks in the preview and export process.
"""

import re
from logging_config import get_logger

logger = get_logger()

def process_page_breaks_for_preview(html_content):
    """
    Process page breaks in HTML content for preview
    
    Args:
        html_content: The HTML content to process
        
    Returns:
        Processed HTML content with page breaks properly formatted
    """
    logger.debug("Processing page breaks for preview")
    
    try:
        # First, check if there are any page breaks in the content
        if "<!-- PAGE_BREAK -->" not in html_content and '<div style="page-break-before: always;"></div>' not in html_content:
            logger.debug("No page breaks found in content")
            return html_content
        
        # Replace HTML comment page breaks with visible div markers
        html_content = html_content.replace(
            "<!-- PAGE_BREAK -->", 
            '<div class="page-break-marker" style="page-break-before: always; border-top: 2px dashed #ff9900; margin: 20px 0; text-align: center; color: #ff9900; font-weight: bold;">PAGE BREAK</div>'
        )
        
        # Replace div style page breaks with visible markers
        html_content = html_content.replace(
            '<div style="page-break-before: always;"></div>', 
            '<div class="page-break-marker" style="page-break-before: always; border-top: 2px dashed #ff9900; margin: 20px 0; text-align: center; color: #ff9900; font-weight: bold;">PAGE BREAK</div>'
        )
        
        # Add JavaScript to enhance page breaks in the preview
        page_break_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Enhancing page breaks in preview...');
            
            // Find all page break markers
            var pageBreaks = document.querySelectorAll('.page-break-marker');
            console.log('Found ' + pageBreaks.length + ' page breaks');
            
            // Process each page break
            pageBreaks.forEach(function(breakEl, index) {
                // Add page number indicators
                var pageNum = index + 1;
                var nextPageNum = pageNum + 1;
                
                // Create a label for the page break
                var label = document.createElement('div');
                label.textContent = 'End of Page ' + pageNum + ' / Start of Page ' + nextPageNum;
                label.style.fontSize = '12px';
                label.style.fontStyle = 'italic';
                label.style.marginTop = '5px';
                
                // Add the label to the page break
                breakEl.appendChild(label);
                
                // Add a visual indicator for the page break
                breakEl.style.position = 'relative';
                breakEl.style.height = '30px';
                breakEl.style.backgroundColor = '#fffaee';
                breakEl.style.borderRadius = '5px';
                breakEl.style.padding = '5px';
                
                console.log('Enhanced page break ' + (index + 1));
            });
            
            // Split content into pages for better visualization
            var body = document.body;
            var content = body.innerHTML;
            
            // Create page containers
            var pages = content.split('<div class="page-break-marker"');
            
            if (pages.length > 1) {
                // Clear the body
                body.innerHTML = '';
                
                // Create a container for all pages
                var pagesContainer = document.createElement('div');
                pagesContainer.className = 'pages-container';
                pagesContainer.style.display = 'flex';
                pagesContainer.style.flexDirection = 'column';
                pagesContainer.style.gap = '40px';
                body.appendChild(pagesContainer);
                
                // Process the first page (doesn't start with a page break)
                var firstPage = document.createElement('div');
                firstPage.className = 'preview-page';
                firstPage.style.border = '1px solid #ccc';
                firstPage.style.borderRadius = '5px';
                firstPage.style.padding = '20px';
                firstPage.style.backgroundColor = 'white';
                firstPage.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                firstPage.style.position = 'relative';
                firstPage.innerHTML = pages[0];
                
                // Add page number indicator
                var pageNumIndicator = document.createElement('div');
                pageNumIndicator.textContent = 'Page 1';
                pageNumIndicator.style.position = 'absolute';
                pageNumIndicator.style.bottom = '5px';
                pageNumIndicator.style.right = '5px';
                pageNumIndicator.style.backgroundColor = '#f0f0f0';
                pageNumIndicator.style.padding = '3px 8px';
                pageNumIndicator.style.borderRadius = '3px';
                pageNumIndicator.style.fontSize = '12px';
                pageNumIndicator.style.color = '#666';
                firstPage.appendChild(pageNumIndicator);
                
                pagesContainer.appendChild(firstPage);
                
                // Process remaining pages (each starts with a page break)
                for (var i = 1; i < pages.length; i++) {
                    var pageContent = pages[i];
                    
                    // Create page container
                    var pageDiv = document.createElement('div');
                    pageDiv.className = 'preview-page';
                    pageDiv.style.border = '1px solid #ccc';
                    pageDiv.style.borderRadius = '5px';
                    pageDiv.style.padding = '20px';
                    pageDiv.style.backgroundColor = 'white';
                    pageDiv.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                    pageDiv.style.position = 'relative';
                    
                    // Fix the content by adding back the opening div tag
                    pageDiv.innerHTML = '<div class="page-break-marker"' + pageContent;
                    
                    // Add page number indicator
                    var pageNumIndicator = document.createElement('div');
                    pageNumIndicator.textContent = 'Page ' + (i + 1);
                    pageNumIndicator.style.position = 'absolute';
                    pageNumIndicator.style.bottom = '5px';
                    pageNumIndicator.style.right = '5px';
                    pageNumIndicator.style.backgroundColor = '#f0f0f0';
                    pageNumIndicator.style.padding = '3px 8px';
                    pageNumIndicator.style.borderRadius = '3px';
                    pageNumIndicator.style.fontSize = '12px';
                    pageNumIndicator.style.color = '#666';
                    pageDiv.appendChild(pageNumIndicator);
                    
                    pagesContainer.appendChild(pageDiv);
                }
                
                console.log('Created ' + pages.length + ' page containers');
            }
        });
        </script>
        """
        
        # Add the script to the HTML content
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", page_break_script + "</body>")
        else:
            html_content += page_break_script
        
        logger.debug("Page breaks processed successfully")
        return html_content
        
    except Exception as e:
        logger.error(f"Error processing page breaks: {str(e)}")
        return html_content  # Return original content on error

def inject_page_break_styles(css_content):
    """
    Inject page break styles into CSS content
    
    Args:
        css_content: The CSS content to modify
        
    Returns:
        Modified CSS content with page break styles
    """
    logger.debug("Injecting page break styles into CSS")
    
    # Add page break styles
    page_break_styles = """
    /* Page break styles */
    .page-break-marker {
        page-break-before: always;
        border-top: 2px dashed #ff9900;
        margin: 20px 0;
        text-align: center;
        color: #ff9900;
        font-weight: bold;
        display: block;
    }
    
    /* Hide page break markers in final output */
    @media print {
        .page-break-marker {
            display: none;
        }
    }
    
    /* Page styles for preview */
    .preview-page {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        position: relative;
        margin-bottom: 40px;
    }
    """
    
    # Add the styles to the CSS content
    css_content += page_break_styles
    
    return css_content

def find_page_breaks_in_markdown(markdown_text):
    """
    Find all page breaks in markdown text
    
    Args:
        markdown_text: The markdown text to search
        
    Returns:
        List of line numbers where page breaks occur
    """
    logger.debug("Finding page breaks in markdown")
    
    page_break_lines = []
    lines = markdown_text.split('\n')
    
    for i, line in enumerate(lines):
        if "<!-- PAGE_BREAK -->" in line:
            page_break_lines.append(i + 1)  # 1-based line numbers
    
    logger.debug(f"Found {len(page_break_lines)} page breaks at lines: {page_break_lines}")
    return page_break_lines

def insert_page_break(markdown_text, cursor_position):
    """
    Insert a page break at the cursor position
    
    Args:
        markdown_text: The markdown text to modify
        cursor_position: The position to insert the page break
        
    Returns:
        Modified markdown text with page break inserted
    """
    logger.debug(f"Inserting page break at position {cursor_position}")
    
    # Insert the page break at the cursor position
    return markdown_text[:cursor_position] + "\n\n<!-- PAGE_BREAK -->\n\n" + markdown_text[cursor_position:]

def estimate_pages(markdown_text, lines_per_page=40):
    """
    Estimate the number of pages based on line count and explicit page breaks
    
    Args:
        markdown_text: The markdown text to analyze
        lines_per_page: Estimated number of lines per page
        
    Returns:
        Estimated number of pages
    """
    logger.debug(f"Estimating pages with {lines_per_page} lines per page")
    
    # Split the text into lines
    lines = markdown_text.split('\n')
    
    # Count explicit page breaks
    explicit_breaks = markdown_text.count("<!-- PAGE_BREAK -->")
    
    # Calculate pages based on line count
    line_count = len(lines)
    pages_by_lines = (line_count + lines_per_page - 1) // lines_per_page
    
    # Total pages is at least the number of explicit breaks + 1
    # or the number of pages calculated by line count
    total_pages = max(explicit_breaks + 1, pages_by_lines)
    
    logger.debug(f"Estimated {total_pages} pages ({explicit_breaks} explicit breaks, {line_count} lines)")
    return total_pages
