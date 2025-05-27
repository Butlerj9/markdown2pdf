#!/usr/bin/env python3
"""
Simple test script to check if PDF export is working
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

    # Create a fresh instance of the application
    window = AdvancedMarkdownToPDF()

    # Sample markdown content for testing
    sample_markdown = """# Test Document

This is a test document for the Markdown to PDF converter.

## Features to Test

- PDF Export
- DOCX Export
- HTML Export
- EPUB Export
- Settings Panel

### Code Block

```python
def hello_world():
    print("Hello, World!")
```

## Table

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

"""

    # Set the sample markdown in the editor
    window.markdown_editor.setPlainText(sample_markdown)

    # Update the preview
    window.update_preview()

    # Process events to ensure UI updates
    QApplication.processEvents()

    # Print available engines
    print(f"Available engines: {window.found_engines.keys()}")

    # Try to export to PDF
    output_file = os.path.join(temp_dir, "test_export.pdf")
    print(f"Exporting to: {output_file}")

    result = window._export_to_pdf(output_file)

    # Check if export was successful
    if result:
        print("PDF export successful")
        if os.path.exists(output_file):
            print(f"PDF file created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("PDF file was not created")
    else:
        print("PDF export failed")

    # Try to export to HTML
    output_file = os.path.join(temp_dir, "test_export.html")
    print(f"Exporting to: {output_file}")

    result = window._export_to_html(output_file)

    # Check if export was successful
    if result:
        print("HTML export successful")
        if os.path.exists(output_file):
            print(f"HTML file created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("HTML file was not created")
    else:
        print("HTML export failed")

    # Close the window
    window.close()

    # Process events to ensure window closes
    QApplication.processEvents()

    return 0

if __name__ == "__main__":
    sys.exit(main())
