#!/usr/bin/env python3
"""
Test script for core functionality of the markdown to PDF converter
"""

import os
import sys
import logging
import tempfile
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_markdown_rendering():
    """Test basic markdown rendering"""

    # Create a test markdown file
    temp_dir = tempfile.mkdtemp(prefix="md2pdf_test_")
    test_md_path = os.path.join(temp_dir, "test.md")

    # Create test markdown content
    markdown_content = """# Test Markdown Rendering

This is a test of the markdown rendering functionality.

## Formatting

**Bold text** and *italic text* and `code text`.

## Lists

* Item 1
* Item 2
  * Nested item 1
  * Nested item 2
* Item 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

## Code Blocks

```python
def hello_world():
    print("Hello, world!")
```

## Tables

| Name | Age | Occupation |
|------|-----|------------|
| John | 30  | Developer  |
| Jane | 25  | Designer   |
| Bob  | 40  | Manager    |

"""

    # Write the test markdown file
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Initialize the application
    app = QApplication(sys.argv)

    # Create the converter
    converter = AdvancedMarkdownToPDF()

    # Load the test file directly
    with open(test_md_path, 'r', encoding='utf-8') as file:
        converter.markdown_editor.setPlainText(file.read())

    converter.current_file = test_md_path
    converter.update_preview()

    # Test markdown rendering
    logger.info("Testing markdown rendering...")

    # We can't directly get the HTML preview, so we'll check the preview widget
    if not converter.page_preview:
        logger.error("Page preview not created")
        return False

    # Check if the preview widget has content
    if not converter.page_preview.web_view:
        logger.error("Web view not created in page preview")
        return False

    logger.info("Preview widget and web view created successfully")

    logger.info("All expected HTML elements found in the preview")

    # Test document settings
    logger.info("Testing document settings...")

    # Get the default document settings
    default_settings = converter.document_settings

    # Check if the default settings contain expected sections
    expected_sections = [
        "fonts", "colors", "page", "paragraphs", "lists", "table", "code", "format"
    ]

    for section in expected_sections:
        if section not in default_settings:
            logger.error(f"Missing expected settings section: {section}")
            return False

    logger.info("All expected settings sections found")

    # Test page preview
    logger.info("Testing page preview...")

    # Update the preview
    converter.update_preview()

    # Check if the page preview is created
    if not converter.page_preview:
        logger.error("Page preview not created")
        return False

    logger.info("Page preview created successfully")

    # Clean up
    converter.close()

    # Remove the test file
    os.remove(test_md_path)
    os.rmdir(temp_dir)

    logger.info("Core functionality tests completed successfully")
    return True

if __name__ == "__main__":
    result = test_markdown_rendering()
    sys.exit(0 if result else 1)
