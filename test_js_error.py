#!/usr/bin/env python3
"""
Test JavaScript Error
-------------------
This script tests the JavaScript code in the page preview component to identify the error.
"""

import sys
import os
import logging
from PyQt6.QtCore import Qt, QCoreApplication

# Set the attribute before any QApplication is created
# This must be done before importing any Qt modules that might create a QApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
# Import QtWebEngine modules
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the application modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class CustomWebEnginePage(QWebEnginePage):
    """Custom web engine page to handle JavaScript console messages"""

    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle JavaScript console messages"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")

        logger.debug(f"JS {level_str} ({source}:{line}): {message}")

class TestWindow(QMainWindow):
    """Test window for JavaScript error"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("JavaScript Error Test")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create web view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Create custom web page
        self.web_page = CustomWebEnginePage()
        self.web_view.setPage(self.web_page)

        # Create test button
        self.test_button = QPushButton("Run Test")
        self.test_button.clicked.connect(self.run_test)
        layout.addWidget(self.test_button)

        # Create test script with the fixed version (no return statements in setTimeout callbacks)
        self.test_script = """
        (function() {
            try {
                // Create a global variable to store results from callbacks
                window.callbackResult = '';

                // Check if pages exist
                var pages = document.querySelectorAll('.page');

                if (!pages || pages.length === 0) {
                    console.log('No pages found yet, rechecking in 500ms...');

                    // Schedule a retry after a delay - FIXED PATTERN
                    setTimeout(function() {
                        var retryPages = document.querySelectorAll('.page');
                        if (!retryPages || retryPages.length === 0) {
                            console.error('Still no pages found in document after retry');
                            if (window.qt && window.qt.pageCountChanged) {
                                window.qt.pageCountChanged(1, 1);
                            }
                            // Store the result in a variable instead of returning it
                            window.callbackResult = 'No pages found after retry';
                            console.log('Result stored: ' + window.callbackResult);
                        } else {
                            console.log('Found ' + retryPages.length + ' pages after retry');
                            // Store the result in a variable instead of returning it
                            window.callbackResult = 'Found ' + retryPages.length + ' pages after retry';
                            console.log('Result stored: ' + window.callbackResult);

                            // Call a function to handle the result instead of returning it
                            handlePagesFound(retryPages);
                        }
                    }, 500);

                    // This is fine - returning from the main function
                    return 'Scheduled retry for page navigation';
                }

                // Helper function to handle found pages
                function handlePagesFound(pageElements) {
                    var totalPages = pageElements.length;
                    console.log('Handling ' + totalPages + ' pages');

                    // Do something with the pages
                    if (window.qt && window.qt.pageCountChanged) {
                        window.qt.pageCountChanged(1, totalPages);
                    }

                    // Return value is used within this function, not in setTimeout
                    return 'Handled ' + totalPages + ' pages';
                }

                // This is also fine - returning from the main function
                return 'Pages found immediately';
            } catch (e) {
                console.error('Error in test script:', e);
                return 'Error: ' + e.message;
            }
        })();
        """

        # Load a simple HTML page
        self.web_view.setHtml("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>JavaScript Error Test</title>
        </head>
        <body>
            <h1>JavaScript Error Test</h1>
            <p>This page is used to test JavaScript errors in the page preview component.</p>
        </body>
        </html>
        """)

    def run_test(self):
        """Run the JavaScript test"""
        logger.info("Running JavaScript test")

        # Execute the test script
        self.web_page.runJavaScript(self.test_script, self.handle_result)

    def handle_result(self, result):
        """Handle the result of the JavaScript test"""
        logger.info(f"JavaScript test result: {result}")

def main():
    """Main function"""
    # QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts) is now set at the top of the file

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()

    # Run the test after a short delay
    QTimer.singleShot(1000, window.run_test)

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
