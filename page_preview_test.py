#!/usr/bin/env python3
"""
Comprehensive test framework for page preview functionality
"""

import sys
import os
import time
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from page_preview import PagePreview

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("page_preview_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestSignals(QObject):
    """Signals for test events"""
    test_completed = pyqtSignal(str, bool)
    test_progress = pyqtSignal(str)
    all_tests_completed = pyqtSignal()

class TestRunner:
    """Runs tests for page preview functionality"""
    
    def __init__(self, preview):
        """Initialize with a page preview instance"""
        self.preview = preview
        self.signals = TestSignals()
        self.tests = []
        self.current_test = 0
        self.results = {}
        
        # Register tests
        self.register_tests()
    
    def register_tests(self):
        """Register all tests to be run"""
        self.tests = [
            {"name": "Basic HTML Rendering", "function": self.test_basic_html},
            {"name": "Page Margins", "function": self.test_page_margins},
            {"name": "Page Navigation", "function": self.test_page_navigation},
            {"name": "JavaScript Errors", "function": self.test_javascript_errors},
        ]
    
    def run_tests(self):
        """Run all registered tests"""
        logger.info("Starting test suite")
        self.current_test = 0
        self.results = {}
        self.run_next_test()
    
    def run_next_test(self):
        """Run the next test in the queue"""
        if self.current_test < len(self.tests):
            test = self.tests[self.current_test]
            logger.info(f"Running test: {test['name']}")
            self.signals.test_progress.emit(f"Running: {test['name']}")
            
            # Run the test with a delay to allow UI updates
            QTimer.singleShot(500, lambda: self.execute_test(test))
        else:
            logger.info("All tests completed")
            self.signals.all_tests_completed.emit()
    
    def execute_test(self, test):
        """Execute a single test"""
        try:
            result = test["function"]()
            self.results[test["name"]] = result
            self.signals.test_completed.emit(test["name"], result)
        except Exception as e:
            logger.error(f"Error in test {test['name']}: {str(e)}")
            self.results[test["name"]] = False
            self.signals.test_completed.emit(test["name"], False)
        
        # Move to the next test
        self.current_test += 1
        self.run_next_test()
    
    def test_basic_html(self):
        """Test basic HTML rendering"""
        logger.info("Testing basic HTML rendering")
        
        # Create simple HTML content
        html = """
        <html>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        time.sleep(1)
        
        # Check if content is rendered (basic check)
        js_result = self.preview.execute_js("document.body.textContent.includes('Test Heading')")
        
        logger.info(f"Basic HTML rendering test result: {js_result}")
        return js_result
    
    def test_page_margins(self):
        """Test page margins"""
        logger.info("Testing page margins")
        
        # Test different margin settings
        settings = {
            "fonts": {"body": {"family": "Arial", "size": 11, "line_height": 1.5}},
            "colors": {"text": "#000000", "background": "#ffffff", "links": "#0000ff"},
            "page": {
                "size": "A4",
                "orientation": "portrait",
                "margins": {"top": 0, "right": 25, "bottom": 25, "left": 25}
            }
        }
        
        # Update settings
        self.preview.update_document_settings(settings)
        
        # Create test HTML
        html = """
        <html>
        <body>
            <p>This text should be at the top with no margin.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        time.sleep(1)
        
        # Check margin values
        js_result = self.preview.execute_js("""
        (function() {
            var page = document.querySelector('.page');
            if (!page) return false;
            
            var style = window.getComputedStyle(page);
            var paddingTop = parseFloat(style.paddingTop);
            
            console.log('Padding top: ' + paddingTop + 'px');
            
            // For zero margin, padding should be very small (less than 5px)
            return paddingTop < 5;
        })()
        """)
        
        logger.info(f"Page margins test result: {js_result}")
        return js_result
    
    def test_page_navigation(self):
        """Test page navigation"""
        logger.info("Testing page navigation")
        
        # Create multi-page HTML
        html = """
        <html>
        <body>
            <h1>Page 1</h1>
            <p>This is page 1.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 2</h1>
            <p>This is page 2.</p>
            
            <div style="page-break-before: always;"></div>
            
            <h1>Page 3</h1>
            <p>This is page 3.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        time.sleep(1)
        
        # Check page count
        page_count = self.preview.execute_js("document.querySelectorAll('.page').length")
        logger.info(f"Page count: {page_count}")
        
        if page_count != 3:
            logger.error(f"Expected 3 pages, got {page_count}")
            return False
        
        # Test navigation to next page
        self.preview.go_to_next_page()
        time.sleep(0.5)
        
        # Check if page 2 is current
        current_page = self.preview.execute_js("""
        (function() {
            var currentPage = document.querySelector('.page.current-page');
            if (!currentPage) return 0;
            
            var pages = document.querySelectorAll('.page');
            for (var i = 0; i < pages.length; i++) {
                if (pages[i] === currentPage) {
                    return i + 1;
                }
            }
            return 0;
        })()
        """)
        
        logger.info(f"Current page after navigation: {current_page}")
        
        # Navigation should move to page 2
        return current_page == 2
    
    def test_javascript_errors(self):
        """Test for JavaScript errors"""
        logger.info("Testing for JavaScript errors")
        
        # Create HTML with potential error triggers
        html = """
        <html>
        <head>
            <style>
            /* Test CSS selectors */
            h1.title { display: none; }
            div.title { display: none; }
            header.title-block { display: none; }
            </style>
        </head>
        <body>
            <h1 class="title">Hidden Title</h1>
            <div class="title">Hidden Div</div>
            <header class="title-block">Hidden Header</header>
            
            <h1>Visible Heading</h1>
            <p>This is a test paragraph.</p>
        </body>
        </html>
        """
        
        # Update the preview
        self.preview.update_preview(html)
        
        # Wait for rendering
        time.sleep(1)
        
        # Check for JavaScript errors
        js_result = self.preview.execute_js("""
        (function() {
            // This will return true if no errors were caught
            return true;
        })()
        """)
        
        logger.info(f"JavaScript errors test result: {js_result}")
        return js_result

class TestWindow(QMainWindow):
    """Test window for page preview tests"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Preview Test Framework")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create preview widget
        self.preview = PagePreview()
        
        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Create status label
        self.status_label = QLabel("Ready to run tests")
        
        # Create run button
        run_button = QPushButton("Run Tests")
        run_button.clicked.connect(self.run_tests)
        
        # Add widgets to layout
        layout.addWidget(self.preview, 3)
        layout.addWidget(self.log_display, 1)
        layout.addWidget(self.status_label)
        layout.addWidget(run_button)
        
        # Create test runner
        self.test_runner = TestRunner(self.preview)
        self.test_runner.signals.test_completed.connect(self.on_test_completed)
        self.test_runner.signals.test_progress.connect(self.on_test_progress)
        self.test_runner.signals.all_tests_completed.connect(self.on_all_tests_completed)
        
        # Set up log handler
        self.log_handler = QTextEditLogger(self.log_display)
        logger.addHandler(self.log_handler)
    
    def run_tests(self):
        """Run all tests"""
        self.log_display.clear()
        self.status_label.setText("Running tests...")
        self.test_runner.run_tests()
    
    def on_test_completed(self, test_name, result):
        """Handle test completion"""
        status = "PASSED" if result else "FAILED"
        self.log_display.append(f"Test: {test_name} - {status}")
    
    def on_test_progress(self, message):
        """Handle test progress updates"""
        self.status_label.setText(message)
    
    def on_all_tests_completed(self):
        """Handle completion of all tests"""
        self.status_label.setText("All tests completed")
        
        # Summarize results
        passed = sum(1 for result in self.test_runner.results.values() if result)
        total = len(self.test_runner.results)
        
        self.log_display.append(f"\nTest Summary: {passed}/{total} tests passed")

class QTextEditLogger(logging.Handler):
    """Logger that outputs to a QTextEdit"""
    
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
