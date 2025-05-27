#!/usr/bin/env python3
"""
Simple test script for the rebuilt page preview component.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

# Import the rebuilt page preview component
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('page_preview_test.log')
    ]
)
logger = logging.getLogger(__name__)

class TestWindow(QMainWindow):
    """Test window for the page preview component"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Page Preview Test")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create page preview
        self.page_preview = PagePreview()
        layout.addWidget(self.page_preview)

        # Create test controls
        controls_layout = QHBoxLayout()

        # Add a button to load a simple test document
        simple_btn = QPushButton("Load Simple Document")
        simple_btn.clicked.connect(self.load_simple_document)
        controls_layout.addWidget(simple_btn)

        # Add a button to load a multi-page test document
        multi_btn = QPushButton("Load Multi-Page Document")
        multi_btn.clicked.connect(self.load_multi_page_document)
        controls_layout.addWidget(multi_btn)

        # Add a button to load a document with images
        images_btn = QPushButton("Load Document with Images")
        images_btn.clicked.connect(self.load_document_with_images)
        controls_layout.addWidget(images_btn)

        # Add controls to layout
        layout.addLayout(controls_layout)

        # Load a simple document after a short delay if no other document is loaded
        self._loaded = False
        QTimer.singleShot(500, self._load_default_document)

    def _load_default_document(self):
        """Load the default document if no other document has been loaded"""
        if not self._loaded:
            self.load_simple_document()

    def load_simple_document(self):
        """Load a simple test document"""
        logger.info("Loading simple document")

        html_content = """
        <h1>Simple Test Document</h1>
        <p>This is a simple test document to verify the basic functionality of the page preview component.</p>
        <p>It contains only basic HTML elements like headings and paragraphs.</p>
        """

        self._loaded = True
        self.page_preview.update_preview(html_content)

    def load_multi_page_document(self):
        """Load a multi-page test document"""
        logger.info("Loading multi-page document")

        # Create HTML content with multiple pages
        html_content = """
        <div class="page">
            <h1>Page 1</h1>
            <p>This is the first page of a multi-page test document.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </div>
        <div class="page">
            <h1>Page 2</h1>
            <p>This is the second page of a multi-page test document.</p>
            <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        </div>
        <div class="page">
            <h1>Page 3</h1>
            <p>This is the third page of a multi-page test document.</p>
            <p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
        </div>
        """

        self._loaded = True
        self.page_preview.update_preview(html_content)

    def load_document_with_images(self):
        """Load a test document with images"""
        logger.info("Loading document with images")

        # Create HTML content with images
        html_content = """
        <h1>Document with Images</h1>
        <p>This document contains images to test image rendering in the page preview component.</p>
        <p>The images are embedded as data URLs to avoid external dependencies.</p>

        <h2>Sample Image 1</h2>
        <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzAwNzBmMyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjIwIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSI+SW1hZ2UgMTwvdGV4dD48L3N2Zz4=" alt="Sample Image 1" width="100" height="100">

        <h2>Sample Image 2</h2>
        <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2YwNzAzMCIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjIwIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSI+SW1hZ2UgMjwvdGV4dD48L3N2Zz4=" alt="Sample Image 2" width="100" height="100">
        """

        self._loaded = True
        self.page_preview.update_preview(html_content)

def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Set application name and organization
    app.setApplicationName("Page Preview Test")
    app.setOrganizationName("Test Organization")

    # Create and show the main window
    window = TestWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
