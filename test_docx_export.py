#!/usr/bin/env python3
"""
Test script for DOCX export functionality
"""

import os
import sys
import tempfile
from PyQt6.QtWidgets import QApplication

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def main():
    # Create QApplication
    app = QApplication(sys.argv)

    # Create a temporary directory for test outputs
    temp_dir = tempfile.mkdtemp()
    print(f"Test output directory: {temp_dir}")

    # Create a window
    window = AdvancedMarkdownToPDF()

    # Set some test content
    test_content = """# Test Document

This is a test document for DOCX export.

## Section 1

This is a paragraph in section 1.

- Item 1
- Item 2
- Item 3

## Section 2

This is a paragraph in section 2.

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

### Subsection

This is a subsection with some **bold** and *italic* text.

```python
def hello_world():
    print("Hello, world!")
```

## Section 3

This is a table:

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
"""

    # Set the content in the editor
    window.markdown_editor.setPlainText(test_content)

    # Update the preview
    window.update_preview()

    # Process events to ensure UI updates
    QApplication.processEvents()

    # Try to export to DOCX
    output_file = os.path.join(temp_dir, "test_export.docx")
    print(f"Exporting to: {output_file}")

    result = window._export_to_docx(output_file)

    # Check if export was successful
    if result:
        print("DOCX export successful")
        if os.path.exists(output_file):
            print(f"DOCX file created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("DOCX file was not created")
    else:
        print("DOCX export failed")

    # Close the window
    window.close()

    # Process events to ensure window closes
    QApplication.processEvents()

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
