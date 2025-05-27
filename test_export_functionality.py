#!/usr/bin/env python3
"""
Test Export Functionality
------------------------
This script tests the export functionality of the Markdown to PDF converter.
"""

import os
import sys
import logging
import tempfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt6.QtCore import QTimer, Qt, QCoreApplication

# Set the attribute before any QApplication is created
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

# Import after setting the attribute
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary modules
try:
    from markdown_to_pdf_export import MarkdownToPDFExport
    from mdz_export import MDZExporter
    from page_preview import PagePreview
except ImportError as e:
    logger.error(f"Error importing modules: {str(e)}")
    sys.exit(1)

class ExportTestWindow(QMainWindow):
    """Test window for export functionality"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Export Functionality Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create page preview
        self.preview = PagePreview()
        layout.addWidget(self.preview)

        # Create export button
        self.export_button = QPushButton("Export to PDF")
        self.export_button.clicked.connect(self.export_to_pdf)
        layout.addWidget(self.export_button)

        # Create export to MDZ button
        self.export_mdz_button = QPushButton("Export to MDZ")
        self.export_mdz_button.clicked.connect(self.export_to_mdz)
        layout.addWidget(self.export_mdz_button)

        # Set document settings
        self.document_settings = {
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 11,
                    "line_height": 1.5
                },
                "headings": {
                    "h1": {
                        "family": "Arial",
                        "size": 18,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 12,
                        "margin_bottom": 6
                    },
                    "h2": {
                        "family": "Arial",
                        "size": 16,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 10,
                        "margin_bottom": 5
                    },
                    "h3": {
                        "family": "Arial",
                        "size": 14,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 8,
                        "margin_bottom": 4
                    }
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#ffffff",
                "links": "#0000ff"
            },
            "page": {
                "size": "A4",
                "orientation": "portrait",
                "margins": {
                    "top": 25,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            },
            "paragraphs": {
                "margin_top": 0,
                "margin_bottom": 10,
                "spacing": 1.5,
                "first_line_indent": 0,
                "alignment": "left"
            },
            "lists": {
                "bullet_indent": 20,
                "number_indent": 20,
                "item_spacing": 5
            },
            "code": {
                "font_family": "Courier New",
                "font_size": 10
            }
        }

        # Update document settings
        self.preview.update_document_settings(self.document_settings)

        # Create test markdown content
        self.test_markdown = """# Export Functionality Test

This document tests the export functionality of the Markdown to PDF converter.

## Section 1: Basic Formatting

This is a paragraph with **bold** and *italic* text.

### Lists

- Item 1
- Item 2
  - Nested item 1
  - Nested item 2
- Item 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

## Section 2: Code and Tables

### Code Block

```python
def hello_world():
    print("Hello, world!")
```

### Table

| Name | Age | Occupation |
|------|-----|------------|
| John | 30  | Developer  |
| Jane | 25  | Designer   |
| Bob  | 40  | Manager    |

## Section 3: Math and Images

### Math Formula

E = mc^2

### Image

This would normally contain an image.
"""

        # Create HTML from markdown
        try:
            import markdown
            html_content = markdown.markdown(self.test_markdown, extensions=['tables', 'fenced_code'])
            self.preview.update_preview(html_content)
        except Exception as e:
            logger.error(f"Error converting markdown to HTML: {str(e)}")
            self.preview.update_preview("<h1>Error converting markdown to HTML</h1>")

        # Set up a timer to run tests after the page has loaded
        QTimer.singleShot(1000, self.run_tests)

    def run_tests(self):
        """Run export functionality tests"""
        logger.info("Running export functionality tests...")

        # Test 1: Check if the exporter can be initialized
        self.test_exporter_initialization()

    def test_exporter_initialization(self):
        """Test if the exporters can be initialized"""
        logger.info("Testing exporter initialization...")

        try:
            # Test PDF exporter
            pdf_exporter = MarkdownToPDFExport()
            logger.info("PDF exporter initialized successfully")

            # Test MDZ exporter
            mdz_exporter = MDZExporter()
            logger.info("MDZ exporter initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing exporters: {str(e)}")

    def export_to_pdf(self):
        """Export the current document to PDF"""
        logger.info("Exporting to PDF...")

        try:
            # Create a temporary file for the PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                output_path = f.name

            # Create a temporary file for the markdown content
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w', encoding='utf-8') as md_file:
                md_file.write(self.test_markdown)
                md_path = md_file.name

            # Create a simple CSS file instead of using RenderUtils
            css_content = """
            body {
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #000000;
                background-color: #ffffff;
                margin: 0;
                padding: 0;
            }

            h1, h2, h3, h4, h5, h6 {
                font-family: Arial, sans-serif;
                color: #000000;
            }

            h1 {
                font-size: 18pt;
                margin-top: 12pt;
                margin-bottom: 6pt;
            }

            h2 {
                font-size: 16pt;
                margin-top: 10pt;
                margin-bottom: 5pt;
            }

            h3 {
                font-size: 14pt;
                margin-top: 8pt;
                margin-bottom: 4pt;
            }

            p {
                margin-top: 0;
                margin-bottom: 10pt;
            }

            a {
                color: #0000ff;
                text-decoration: underline;
            }

            code, pre {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 5pt;
            }

            table {
                border-collapse: collapse;
                width: 100%;
                margin: 10pt 0;
            }

            th, td {
                border: 1px solid #cccccc;
                padding: 5pt;
            }

            th {
                background-color: #f0f0f0;
            }
            """

            # Create a temporary file for the CSS
            with tempfile.NamedTemporaryFile(suffix='.css', delete=False, mode='w', encoding='utf-8') as css_file:
                css_file.write(css_content)
                css_path = css_file.name

            # Run pandoc command to convert markdown to PDF
            import subprocess

            # Prepare pandoc command
            cmd = ['pandoc', md_path, '-o', output_path, '--standalone', '--css', css_path]

            # Add PDF engine
            cmd.append('--pdf-engine=xelatex')

            # Add title metadata to prevent warnings
            cmd.extend(['--metadata', f'title=Export Test'])

            # Add page settings
            page_settings = self.document_settings.get("page", {})
            page_size = page_settings.get("size", "A4").lower()
            margins = page_settings.get("margins", {"top": 25, "right": 25, "bottom": 25, "left": 25})

            cmd.extend([
                '-V', f'papersize={page_size}',
                '-V', f'margin-top={margins.get("top", 25)}mm',
                '-V', f'margin-right={margins.get("right", 25)}mm',
                '-V', f'margin-bottom={margins.get("bottom", 25)}mm',
                '-V', f'margin-left={margins.get("left", 25)}mm'
            ])

            # Add mathjax for math support
            cmd.append('--mathjax')

            # Log the command
            logger.info(f"Running pandoc command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )

            # Clean up temporary files
            os.unlink(md_path)
            os.unlink(css_path)

            # Check if export was successful
            if result.returncode == 0:
                logger.info(f"PDF exported successfully to {output_path}")
                # Open the PDF
                os.startfile(output_path)
                return True
            else:
                logger.error(f"PDF export failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            return False

    def export_to_mdz(self):
        """Export the current document to MDZ"""
        logger.info("Exporting to MDZ...")

        try:
            # Create a temporary file for the MDZ
            with tempfile.NamedTemporaryFile(suffix='.mdz', delete=False) as f:
                output_path = f.name

            # Create an exporter
            exporter = MDZExporter()

            # Export to MDZ
            result = exporter.export_to_mdz(
                markdown_text=self.test_markdown,
                output_file=output_path,
                document_settings=self.document_settings
            )

            if result:
                logger.info(f"MDZ exported successfully to {output_path}")
                # Open the MDZ
                os.startfile(output_path)
            else:
                logger.error("MDZ export failed")
        except Exception as e:
            logger.error(f"Error exporting to MDZ: {str(e)}")

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Create and show the test window
    window = ExportTestWindow()
    window.show()

    # Exit after 30 seconds
    QTimer.singleShot(30000, app.quit)

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
