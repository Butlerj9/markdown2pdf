#!/usr/bin/env python3
"""
Comprehensive test for page breaks in Markdown to PDF Converter
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = AdvancedMarkdownToPDF()
    
    # Set up test content with explicit page breaks and lots of content
    test_content = """# Comprehensive Page Break Test

This document tests page breaks in the Markdown to PDF Converter. It contains multiple pages with different types of content to ensure page breaks work correctly.

## Introduction

Page breaks are an important feature for document formatting. They allow you to control where content appears in the final document. This test will verify that page breaks are correctly displayed in the preview and properly applied in the exported document.

### Types of Content

We'll test page breaks with various types of content:

* Paragraphs
* Lists
* Tables
* Code blocks
* Images
* Headings

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

<!-- PAGE_BREAK -->

# Page 2: Lists

This page demonstrates lists with page breaks.

## Bullet Lists

* Item 1
* Item 2
* Item 3
  * Nested item 1
  * Nested item 2
* Item 4
* Item 5

## Numbered Lists

1. First item
2. Second item
3. Third item
   1. Nested item 1
   2. Nested item 2
4. Fourth item
5. Fifth item

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

<!-- PAGE_BREAK -->

# Page 3: Tables

This page demonstrates tables with page breaks.

## Simple Table

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
| Cell 7   | Cell 8   | Cell 9   |

## Complex Table

| Name     | Age | Occupation     | Salary  |
|----------|-----|----------------|---------|
| John Doe | 32  | Developer      | $85,000 |
| Jane Smith | 28 | Designer      | $75,000 |
| Bob Johnson | 45 | Manager      | $95,000 |
| Alice Brown | 37 | Product Owner | $90,000 |

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.

<!-- PAGE_BREAK -->

# Page 4: Code Blocks

This page demonstrates code blocks with page breaks.

## Python Code

```python
def hello_world():
    print("Hello, World!")
    
class Example:
    def __init__(self, name):
        self.name = name
        
    def greet(self):
        return f"Hello, {self.name}!"
        
# Create an instance
example = Example("User")
print(example.greet())
```

## JavaScript Code

```javascript
function helloWorld() {
    console.log("Hello, World!");
}

class Example {
    constructor(name) {
        this.name = name;
    }
    
    greet() {
        return `Hello, ${this.name}!`;
    }
}

// Create an instance
const example = new Example("User");
console.log(example.greet());
```

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

<!-- PAGE_BREAK -->

# Page 5: Conclusion

This page concludes the page break test.

## Summary

We've tested page breaks with:

1. Paragraphs
2. Lists
3. Tables
4. Code blocks
5. Headings

## Next Steps

- Verify that page breaks appear correctly in the preview
- Check that page breaks are properly applied in the exported document
- Test with different page sizes and orientations
- Test with different margin settings

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
"""
    
    # Set the content in the editor
    window.markdown_editor.setPlainText(test_content)
    
    # Update the preview
    window.update_preview()
    
    # Show the window
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
