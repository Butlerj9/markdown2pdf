import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from page_preview import PagePreview
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimpleTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Page Preview Test")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create page preview
        self.page_preview = PagePreview()
        layout.addWidget(self.page_preview)

        # Create load button
        load_button = QPushButton("Load File")
        load_button.clicked.connect(self.load_file)
        layout.addWidget(load_button)

        # Set up default document settings
        self.document_settings = {
            "page": {
                "width": 210,
                "height": 297,
                "margins": {
                    "top": 25,
                    "right": 25,
                    "bottom": 25,
                    "left": 25
                }
            },
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 11
                },
                "headings": {
                    "h1": {
                        "family": "Arial",
                        "size": 18,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 12,
                        "margin_bottom": 6
                    }
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#FFFFFF",
                "links": "#0000FF"
            }
        }

        # Apply document settings to page preview
        self.page_preview.set_document_settings(self.document_settings)

        # Show sample content
        self.show_sample_content()

    def show_sample_content(self):
        """Show sample content in the page preview"""
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Sample Document</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .page {
                    width: 210mm;
                    min-height: 297mm;
                    padding: 25mm;
                    margin: 0 auto;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    border: 1px solid #ccc;
                    box-sizing: border-box;
                    position: relative;
                }
                h1 {
                    font-size: 18pt;
                    margin-top: 0;
                }
                p {
                    font-size: 11pt;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            <div class="page">
                <h1>Sample Document</h1>
                <p>This is a sample document to test the page preview functionality.</p>
                <p>The page preview should show this content with proper page edges and apply the document settings.</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget ultricies nisl nisl eget nisl.</p>
            </div>
        </body>
        </html>
        """
        self.page_preview.update_preview(sample_html)

    def load_file(self):
        """Load a Markdown file and display it in the page preview"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md *.markdown);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Convert Markdown to HTML (simplified for testing)
                # Create HTML content
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{file_path}</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                        }
                        .page {
                            width: 210mm;
                            min-height: 297mm;
                            padding: 25mm;
                            margin: 0 auto;
                            background-color: white;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                            border: 1px solid #ccc;
                            box-sizing: border-box;
                            position: relative;
                        }
                        h1 {
                            font-size: 18pt;
                            margin-top: 0;
                        }
                        p {
                            font-size: 11pt;
                            line-height: 1.5;
                        }
                    </style>
                </head>
                <body>
                    <div class="page">
                        <h1>{file_path}</h1>
                        <p>{content.replace(chr(10), '<br>')}</p>
                    </div>
                </body>
                </html>
                """

                # Update document settings first
                self.page_preview.update_document_settings(self.document_settings)

                # Update the preview
                self.page_preview.update_preview(html_content)

            except Exception as e:
                logger.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTestWindow()
    window.show()
    sys.exit(app.exec())
