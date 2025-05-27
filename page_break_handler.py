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
    Supports multiple page break formats:
    - HTML comment: <!-- PAGE_BREAK -->
    - HTML div: <div style="page-break-before: always;"></div>
    - Markdown horizontal rule: --- (when used alone on a line with page break intent)
    - Standard page break syntax: {pagebreak} or {page-break}

    Args:
        html_content: The HTML content to process

    Returns:
        Processed HTML content with page breaks properly formatted
    """
    logger.debug("Processing page breaks for preview")

    try:
        # Check for various page break formats
        has_page_breaks = any([
            "<!-- PAGE_BREAK -->" in html_content,
            '<div style="page-break-before: always;"></div>' in html_content,
            '<p>{pagebreak}</p>' in html_content,
            '<p>{page-break}</p>' in html_content
        ])
        
        if not has_page_breaks:
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
        
        # Replace standard page break syntax
        html_content = html_content.replace(
            '<p>{pagebreak}</p>',
            '<div class="page-break-marker" style="page-break-before: always; border-top: 2px dashed #ff9900; margin: 20px 0; text-align: center; color: #ff9900; font-weight: bold;">PAGE BREAK</div>'
        )
        
        html_content = html_content.replace(
            '<p>{page-break}</p>',
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
                pagesContainer.style.padding = '20px';
                body.appendChild(pagesContainer);

                // Process the first page (doesn't start with a page break)
                var firstPage = document.createElement('div');
                firstPage.className = 'preview-page page';
                firstPage.setAttribute('data-page-num', '1');
                firstPage.style.border = '1px solid #ccc';
                firstPage.style.borderRadius = '5px';
                firstPage.style.padding = '20px';
                firstPage.style.backgroundColor = 'white';
                firstPage.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.15)';
                firstPage.style.position = 'relative';
                firstPage.style.minHeight = '297mm'; // A4 height
                firstPage.style.width = '210mm'; // A4 width
                firstPage.style.margin = '0 auto 40px auto'; // Center horizontally
                firstPage.innerHTML = pages[0];

                // Make this the current page
                firstPage.classList.add('current-page');

                // Add page controls
                var pageControls = document.createElement('div');
                pageControls.className = 'page-controls';
                pageControls.style.position = 'absolute';
                pageControls.style.top = '-30px';
                pageControls.style.right = '0';
                pageControls.style.display = 'flex';
                pageControls.style.gap = '5px';
                
                // Add page number indicator with improved styling
                var pageNumIndicator = document.createElement('div');
                pageNumIndicator.textContent = 'Page 1 of ' + pages.length;
                pageNumIndicator.style.backgroundColor = '#f0f0f0';
                pageNumIndicator.style.padding = '3px 8px';
                pageNumIndicator.style.borderRadius = '3px';
                pageNumIndicator.style.fontSize = '12px';
                pageNumIndicator.style.color = '#666';
                pageNumIndicator.style.fontWeight = 'bold';
                pageControls.appendChild(pageNumIndicator);
                
                firstPage.appendChild(pageControls);
                pagesContainer.appendChild(firstPage);

                // Process remaining pages (each starts with a page break)
                for (var i = 1; i < pages.length; i++) {
                    var pageContent = pages[i];

                    // Create page container with enhanced styling
                    var pageDiv = document.createElement('div');
                    pageDiv.className = 'preview-page page';
                    pageDiv.setAttribute('data-page-num', (i + 1).toString());
                    pageDiv.style.border = '1px solid #ccc';
                    pageDiv.style.borderRadius = '5px';
                    pageDiv.style.padding = '20px';
                    pageDiv.style.backgroundColor = 'white';
                    pageDiv.style.boxShadow = '0 4px 10px rgba(0, 0, 0, 0.15)';
                    pageDiv.style.position = 'relative';
                    pageDiv.style.minHeight = '297mm'; // A4 height
                    pageDiv.style.width = '210mm'; // A4 width
                    pageDiv.style.margin = '0 auto 40px auto'; // Center horizontally

                    // Fix the content by adding back the opening div tag
                    pageDiv.innerHTML = '<div class="page-break-marker"' + pageContent;

                    // Add page controls
                    var pageControls = document.createElement('div');
                    pageControls.className = 'page-controls';
                    pageControls.style.position = 'absolute';
                    pageControls.style.top = '-30px';
                    pageControls.style.right = '0';
                    pageControls.style.display = 'flex';
                    pageControls.style.gap = '5px';
                    
                    // Add page number indicator with improved styling
                    var pageNumIndicator = document.createElement('div');
                    pageNumIndicator.textContent = 'Page ' + (i + 1) + ' of ' + pages.length;
                    pageNumIndicator.style.backgroundColor = '#f0f0f0';
                    pageNumIndicator.style.padding = '3px 8px';
                    pageNumIndicator.style.borderRadius = '3px';
                    pageNumIndicator.style.fontSize = '12px';
                    pageNumIndicator.style.color = '#666';
                    pageNumIndicator.style.fontWeight = 'bold';
                    pageControls.appendChild(pageNumIndicator);
                    
                    pageDiv.appendChild(pageControls);
                    pagesContainer.appendChild(pageDiv);
                }

                // Add navigation controls
                var navControls = document.createElement('div');
                navControls.className = 'navigation-controls';
                navControls.style.position = 'fixed';
                navControls.style.bottom = '20px';
                navControls.style.right = '20px';
                navControls.style.display = 'flex';
                navControls.style.gap = '10px';
                navControls.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
                navControls.style.padding = '10px';
                navControls.style.borderRadius = '5px';
                navControls.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
                
                // Previous page button
                var prevButton = document.createElement('button');
                prevButton.textContent = '← Previous';
                prevButton.style.padding = '5px 10px';
                prevButton.style.border = '1px solid #ccc';
                prevButton.style.borderRadius = '3px';
                prevButton.style.backgroundColor = '#f8f8f8';
                prevButton.style.cursor = 'pointer';
                prevButton.onclick = function() {
                    var currentPage = document.querySelector('.page.current-page');
                    if (currentPage && currentPage.previousElementSibling && currentPage.previousElementSibling.classList.contains('page')) {
                        currentPage.classList.remove('current-page');
                        currentPage.previousElementSibling.classList.add('current-page');
                        currentPage.previousElementSibling.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        
                        // Update page counter
                        if (window.qt && window.qt.pageCountChanged) {
                            var newPageNum = parseInt(currentPage.previousElementSibling.getAttribute('data-page-num'));
                            window.qt.pageCountChanged(newPageNum, pages.length);
                        }
                    }
                };
                navControls.appendChild(prevButton);
                
                // Next page button
                var nextButton = document.createElement('button');
                nextButton.textContent = 'Next →';
                nextButton.style.padding = '5px 10px';
                nextButton.style.border = '1px solid #ccc';
                nextButton.style.borderRadius = '3px';
                nextButton.style.backgroundColor = '#f8f8f8';
                nextButton.style.cursor = 'pointer';
                nextButton.onclick = function() {
                    var currentPage = document.querySelector('.page.current-page');
                    if (currentPage && currentPage.nextElementSibling && currentPage.nextElementSibling.classList.contains('page')) {
                        currentPage.classList.remove('current-page');
                        currentPage.nextElementSibling.classList.add('current-page');
                        currentPage.nextElementSibling.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        
                        // Update page counter
                        if (window.qt && window.qt.pageCountChanged) {
                            var newPageNum = parseInt(currentPage.nextElementSibling.getAttribute('data-page-num'));
                            window.qt.pageCountChanged(newPageNum, pages.length);
                        }
                    }
                };
                navControls.appendChild(nextButton);
                
                body.appendChild(navControls);

                console.log('Created ' + pages.length + ' page containers with enhanced navigation');
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
        padding: 0;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        position: relative;
        margin-bottom: 40px;
    }

    /* Fix for zero margins */
    .preview-page > *:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    """

    # Add the styles to the CSS content
    css_content += page_break_styles

    return css_content

def find_page_breaks_in_markdown(markdown_text):
    """
    Find all page breaks in markdown text
    Supports multiple page break formats:
    - HTML comment: <!-- PAGE_BREAK -->
    - Standard page break syntax: {pagebreak} or {page-break}
    - Horizontal rule when used alone on a line (with empty lines before and after): ---

    Args:
        markdown_text: The markdown text to search

    Returns:
        List of line numbers where page breaks occur
    """
    logger.debug("Finding page breaks in markdown")

    page_break_lines = []
    lines = markdown_text.split('\n')

    for i, line in enumerate(lines):
        # Check for HTML comment page break
        if "<!-- PAGE_BREAK -->" in line:
            page_break_lines.append(i + 1)  # 1-based line numbers
        
        # Check for standard page break syntax
        elif line.strip() in ["{pagebreak}", "{page-break}"]:
            page_break_lines.append(i + 1)
        
        # Check for horizontal rule as page break (when alone on a line)
        elif line.strip() == "---":
            # Only consider it a page break if it's alone (empty lines before and after)
            if (i == 0 or not lines[i-1].strip()) and (i == len(lines)-1 or not lines[i+1].strip()):
                page_break_lines.append(i + 1)

    logger.debug(f"Found {len(page_break_lines)} page breaks at lines: {page_break_lines}")
    return page_break_lines

def insert_page_break(markdown_text, cursor_position):
    """
    Insert a page break at the cursor position using the standard page break syntax

    Args:
        markdown_text: The markdown text to modify
        cursor_position: The position to insert the page break

    Returns:
        Modified markdown text with page break inserted
    """
    logger.debug(f"Inserting page break at position {cursor_position}")

    # Insert the page break at the cursor position using the standard syntax
    return markdown_text[:cursor_position] + "\n\n{pagebreak}\n\n" + markdown_text[cursor_position:]

def estimate_pages(markdown_text, lines_per_page=40):
    """
    Estimate the number of pages based on line count, explicit page breaks,
    and content complexity (headings, code blocks, images)
    Accounts for all supported page break formats

    Args:
        markdown_text: The markdown text to analyze
        lines_per_page: Estimated number of lines per page

    Returns:
        Estimated number of pages
    """
    logger.debug(f"Estimating pages with {lines_per_page} lines per page")

    # Split the text into lines
    lines = markdown_text.split('\n')

    # Count all types of explicit page breaks
    explicit_breaks = 0
    
    # HTML comment page breaks
    explicit_breaks += markdown_text.count("<!-- PAGE_BREAK -->")
    
    # Standard page break syntax
    explicit_breaks += markdown_text.count("{pagebreak}")
    explicit_breaks += markdown_text.count("{page-break}")
    
    # Count horizontal rule page breaks (when alone on a line)
    for i, line in enumerate(lines):
        if line.strip() == "---":
            # Only count if it's alone (empty lines before and after)
            if (i == 0 or not lines[i-1].strip()) and (i == len(lines)-1 or not lines[i+1].strip()):
                explicit_breaks += 1
    
    # Analyze content complexity to better estimate page count
    content_complexity_factor = 1.0
    
    # Count headings (they take up more space)
    heading_count = 0
    for line in lines:
        if line.strip().startswith('#'):
            heading_count += 1
    
    # Count code blocks (they take up more space)
    code_block_count = 0
    in_code_block = False
    code_block_type = ""
    for line in lines:
        if line.strip().startswith('```'):
            if not in_code_block:
                # Start of code block, check if it's a special type
                code_block_type = line.strip()[3:].lower()
            in_code_block = not in_code_block
            if not in_code_block:  # End of a code block
                code_block_count += 1
                code_block_type = ""
    
    # Count images (they take up more space)
    image_count = 0
    for line in lines:
        if '![' in line and '](' in line:
            image_count += 1
    
    # Count tables (they take up more space)
    table_count = 0
    in_table = False
    for i, line in enumerate(lines):
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                # Check if next line is a table separator
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('|') and '-' in lines[i + 1]:
                    in_table = True
                    table_count += 1
        elif in_table and not line.strip().startswith('|'):
            in_table = False
    
    # Count diagrams (they take up more space)
    diagram_count = 0
    for i, line in enumerate(lines):
        if line.strip() == '```mermaid' or line.strip() == '```plantuml':
            diagram_count += 1
    
    # Count math equations (they take up more space)
    math_count = 0
    for line in lines:
        math_count += line.count('$$')  # Block equations
        math_count += line.count('$') - 2 * line.count('$$')  # Inline equations (subtract double-counted block equations)
    math_count = math_count // 2  # Each equation has opening and closing delimiters
    
    # Adjust complexity factor based on content
    if heading_count > 0:
        content_complexity_factor += 0.1 * min(heading_count, 10) / 10  # Max +10%
    
    if code_block_count > 0:
        content_complexity_factor += 0.2 * min(code_block_count, 5) / 5  # Max +20%
    
    if image_count > 0:
        content_complexity_factor += 0.3 * min(image_count, 5) / 5  # Max +30%
    
    if table_count > 0:
        content_complexity_factor += 0.25 * min(table_count, 5) / 5  # Max +25%
    
    if diagram_count > 0:
        content_complexity_factor += 0.35 * min(diagram_count, 3) / 3  # Max +35%
    
    if math_count > 0:
        content_complexity_factor += 0.15 * min(math_count, 10) / 10  # Max +15%
        
    logger.debug(f"Content analysis: {heading_count} headings, {code_block_count} code blocks, {image_count} images, {table_count} tables, {diagram_count} diagrams, {math_count} math equations")
    
    logger.debug(f"Content complexity factor: {content_complexity_factor:.2f}")
    
    # Calculate pages based on line count and complexity
    line_count = len(lines)
    adjusted_line_count = int(line_count * content_complexity_factor)
    pages_by_lines = (adjusted_line_count + lines_per_page - 1) // lines_per_page
    
    # Total pages is at least the number of explicit breaks + 1
    # or the number of pages calculated by line count
    total_pages = max(explicit_breaks + 1, pages_by_lines)
    
    logger.debug(f"Estimated {total_pages} pages ({explicit_breaks} explicit breaks, {line_count} lines, adjusted to {adjusted_line_count} lines)")
    return total_pages
