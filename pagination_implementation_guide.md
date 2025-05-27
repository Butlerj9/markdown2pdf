# Pagination Implementation Guide

## Overview

This document provides a guide for implementing the pagination functionality in the Markdown to PDF converter application. The pagination module (`pagination.py`) provides a clean, modular approach to handling pagination in the application.

## Components

### 1. PaginationManager Class

The `PaginationManager` class is responsible for managing pagination in a `QWebEngineView`. It provides the following functionality:

- Page navigation (previous, next, go to specific page)
- Page count detection
- Callback system for UI updates

### 2. HTML Generation

The `create_pagination_html` function generates HTML with proper pagination structure:

- Creates a container for all pages
- Adds navigation scripts
- Applies proper styling for page layout

## Implementation Steps

### 1. Import the Pagination Module

```python
from pagination import PaginationManager, create_pagination_html
```

### 2. Create a Pagination Manager

```python
# Create a pagination manager for your web view
pagination_manager = PaginationManager(web_view)

# Add a callback for UI updates
pagination_manager.add_page_change_callback(update_ui_function)
```

### 3. Generate Paginated HTML

```python
# Create content blocks for each page
content_blocks = [
    "<h1>Page 1</h1><p>Content for page 1</p>",
    "<h1>Page 2</h1><p>Content for page 2</p>",
    "<h1>Page 3</h1><p>Content for page 3</p>"
]

# Create HTML with pagination
html = create_pagination_html(content_blocks)

# Load the HTML content
web_view.setHtml(html)

# Update pagination information
pagination_manager.update_page_info()
```

### 4. Handle Page Navigation

```python
# Go to the previous page
pagination_manager.go_to_prev_page()

# Go to the next page
pagination_manager.go_to_next_page()

# Go to a specific page
pagination_manager.go_to_page(page_number)
```

### 5. Update UI Based on Page Changes

```python
def update_ui(current_page, total_pages):
    # Update page label
    page_label.setText(f"Page {current_page} of {total_pages}")
    
    # Update button states
    prev_btn.setEnabled(current_page > 1)
    next_btn.setEnabled(current_page < total_pages)
```

## Integration with Page Preview

To integrate the pagination module with the `PagePreview` class:

1. Import the pagination module
2. Create a pagination manager in the `PagePreview` class
3. Use the `create_pagination_html` function to generate HTML content
4. Connect the pagination manager to the UI controls

```python
from pagination import PaginationManager, create_pagination_html

class PagePreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Create pagination manager
        self.pagination_manager = PaginationManager(self.web_view)
        self.pagination_manager.add_page_change_callback(self.update_page_counter)
        
        # Set up UI
        self.setup_ui()
    
    def update_preview(self, html_content):
        # Split content into pages
        content_blocks = self.split_content_into_pages(html_content)
        
        # Create HTML with pagination
        html = create_pagination_html(content_blocks)
        
        # Load the HTML content
        self.web_view.setHtml(html)
        
        # Update pagination information
        self.pagination_manager.update_page_info()
    
    def go_to_previous_page(self):
        self.pagination_manager.go_to_prev_page()
    
    def go_to_next_page(self):
        self.pagination_manager.go_to_next_page()
    
    def go_to_page(self, page_number):
        self.pagination_manager.go_to_page(page_number)
    
    def update_page_counter(self, current_page, total_pages):
        # Update page counter display
        self.page_entry.setValue(current_page)
        self.total_pages_label.setText(str(total_pages))
        
        # Update button states
        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)
```

## JavaScript Functions

The pagination module adds the following JavaScript functions to the HTML:

- `goToPage(pageNum)`: Navigate to a specific page
- `nextPage()`: Navigate to the next page
- `prevPage()`: Navigate to the previous page
- `getCurrentPage()`: Get the current page number
- `getTotalPages()`: Get the total number of pages

## CSS Styling

The pagination module applies the following CSS styling to the pages:

```css
.page {
    width: 210mm;
    min-height: 297mm;
    padding: 25mm;
    margin: 10mm auto;
    background: white;
    box-sizing: border-box;
    position: relative;
    border: 1px solid #ccc;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
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
```

## Testing

The pagination functionality can be tested using the following test files:

1. `test_pagination_module.py`: Tests the pagination module independently
2. `basic_pagination_test.py`: A simple test for basic pagination functionality
3. `test_pagination_fix.py`: A more comprehensive test for pagination

## Troubleshooting

If you encounter issues with the pagination functionality:

1. Check the JavaScript console for errors
2. Verify that the HTML structure is correct
3. Ensure that the pagination manager is properly initialized
4. Check that the callbacks are properly connected

## Future Improvements

1. Add support for different page sizes
2. Improve page break detection
3. Add support for custom page templates
4. Implement page thumbnails for easier navigation
