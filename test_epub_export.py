#!/usr/bin/env python3
"""
Test script for EPUB export functionality
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

    # Set test environment flag to avoid style saving prompts
    window._is_test_environment = True

    # Sample markdown content for testing
    sample_markdown = """# EPUB Export Test

This is a test document for the Markdown to PDF converter EPUB export functionality.

## Features to Test

- EPUB Export
- Table of Contents
- Page Breaks

### Code Block

```python
def test_epub_export():
    print("Testing EPUB export functionality")
```

## Table

| Feature | Status |
|---------|--------|
| EPUB    | Testing |
| TOC     | Testing |
| Breaks  | Testing |

<!-- PAGE_BREAK -->

## Second Page

This content should appear on the second page.

### Subsection

This is a subsection that should appear in the TOC.

#### Sub-subsection

This is a deeper level that may or may not appear in the TOC depending on depth settings.

<!-- PAGE_BREAK -->

## Third Page

This content should appear on the third page.
"""

    # Set the sample markdown in the editor
    window.markdown_editor.setPlainText(sample_markdown)

    # Update the preview
    window.update_preview()

    # Process events to ensure UI updates
    QApplication.processEvents()

    # Enable table of contents
    window.include_toc.setChecked(True)
    window.toc_depth.setValue(3)
    window.toc_title.setText("Contents")

    # Process events to ensure UI updates
    QApplication.processEvents()

    # Try to export to EPUB
    output_file = os.path.join(temp_dir, "test_export.epub")
    print(f"Exporting to: {output_file}")

    result = window._export_to_epub(output_file)

    # Check if export was successful
    if result:
        print("EPUB export successful")
        if os.path.exists(output_file):
            print(f"EPUB file created: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("EPUB file was not created")
    else:
        print("EPUB export failed")

    # Close the window
    window.close()

    # Process events to ensure window closes
    QApplication.processEvents()

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
