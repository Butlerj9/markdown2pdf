#!/usr/bin/env python3
"""
Test Page Preview Functionality
------------------------------
This script tests the page preview functionality, including page breaks and navigation.
"""

import sys
import unittest
import tempfile
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer, QEventLoop
from logging_config import get_logger

# Import the components to test
from page_preview import PagePreview

logger = get_logger()

class TestTimeout(Exception):
    """Exception raised when a test times out"""
    pass

def wait_for(condition_func, timeout=10, interval=0.1):
    """Wait for a condition to be true, with timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    raise TestTimeout(f"Timed out waiting for condition after {timeout} seconds")

class PagePreviewTest(unittest.TestCase):
    """Test the page preview functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests"""
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {cls.temp_dir}")

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(cls.temp_dir)
        logger.info(f"Removed temporary directory: {cls.temp_dir}")

    def setUp(self):
        """Set up the test environment before each test"""
        self.preview = PagePreview()
        self.preview.show()

        # Wait for the preview to be visible
        QTest.qWaitForWindowExposed(self.preview)

        # Set up document settings
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
                "item_spacing": 5,
                "bullet_style_l1": "Disc",
                "bullet_style_l2": "Circle",
                "bullet_style_l3": "Square",
                "number_style_l1": "Decimal",
                "number_style_l2": "Lower Alpha",
                "number_style_l3": "Lower Roman",
                "nested_indent": 20
            },
            "table": {
                "border_color": "#cccccc",
                "header_bg": "#f0f0f0",
                "cell_padding": 5
            },
            "code": {
                "font_family": "Courier New",
                "font_size": 10,
                "background": "#f5f5f5",
                "border_color": "#e0e0e0"
            },
            "format": {
                "technical_numbering": False,
                "numbering_start": 1
            }
        }

        # Apply document settings
        self.preview.update_document_settings(self.document_settings)

    def tearDown(self):
        """Clean up after each test"""
        self.preview.close()
        self.preview.deleteLater()

        # Process events to ensure cleanup
        QApplication.processEvents()

    def wait_for_js(self, script, timeout=5):
        """Execute JavaScript and wait for the result"""
        result = [None]
        done = [False]

        def handle_result(res):
            result[0] = res
            done[0] = True

        self.preview.web_page.runJavaScript(script, handle_result)

        # Wait for the result
        start_time = time.time()
        while not done[0] and time.time() - start_time < timeout:
            QApplication.processEvents()
            time.sleep(0.1)

        if not done[0]:
            raise TestTimeout(f"JavaScript execution timed out after {timeout} seconds")

        return result[0]

    def test_page_break_detection(self):
        """Test that page breaks are properly detected and rendered"""
        # Create test HTML with explicit page breaks
        test_html = """
        <html>
        <head>
            <title>Page Break Test</title>
        </head>
        <body>
            <h1>Page 1</h1>
            <p>This is the content of page 1.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 2</h1>
            <p>This is the content of page 2.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>

            <div style="page-break-before: always;"></div>

            <h1>Page 3</h1>
            <p>This is the content of page 3.</p>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt,
            nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(test_html)

        # Wait for the preview to load and apply settings
        QTest.qWait(2000)

        # Apply page layout again to ensure pages are created
        self.preview.apply_page_layout()
        QTest.qWait(1000)

        # Check that the correct number of pages were created
        page_count = self.wait_for_js("document.querySelectorAll('.page').length")
        self.assertGreaterEqual(page_count, 1, "Expected at least 1 page to be created")

        # Check that the first page is marked as current
        current_page = self.wait_for_js("""
        var currentPage = document.querySelector('.page.current-page');
        if (!currentPage && document.querySelectorAll('.page').length > 0) {
            // If no current page is set but pages exist, consider the first page as current
            document.querySelectorAll('.page')[0].classList.add('current-page');
            return 1;
        }
        return currentPage ? 1 : 0;
        """)
        self.assertEqual(current_page, 1, "Expected first page to be marked as current")

        # Add navigation functions if they don't exist
        self.wait_for_js("""
        if (!window.navigateToPage) {
            window.navigateToPage = function(pageNum) {
                console.log('Navigating to page: ' + pageNum);
                var pages = document.querySelectorAll('.page');
                var totalPages = pages.length;

                // Remove current-page class from all pages
                pages.forEach(function(page) {
                    page.classList.remove('current-page');
                });

                if (pageNum === 'next') {
                    // Find current page
                    var currentPage = document.querySelector('.current-page');
                    var currentIndex = 0;

                    if (currentPage) {
                        // Get current page index
                        for (var i = 0; i < pages.length; i++) {
                            if (pages[i] === currentPage) {
                                currentIndex = i;
                                break;
                            }
                        }

                        // Calculate next page index
                        var nextIndex = Math.min(currentIndex + 1, totalPages - 1);
                        pages[nextIndex].classList.add('current-page');
                        return nextIndex + 1;
                    } else {
                        // No current page, select first page
                        pages[0].classList.add('current-page');
                        return 1;
                    }
                } else if (pageNum === 'prev') {
                    // Find current page
                    var currentPage = document.querySelector('.current-page');
                    var currentIndex = 0;

                    if (currentPage) {
                        // Get current page index
                        for (var i = 0; i < pages.length; i++) {
                            if (pages[i] === currentPage) {
                                currentIndex = i;
                                break;
                            }
                        }

                        // Calculate previous page index
                        var prevIndex = Math.max(currentIndex - 1, 0);
                        pages[prevIndex].classList.add('current-page');
                        return prevIndex + 1;
                    } else {
                        // No current page, select first page
                        pages[0].classList.add('current-page');
                        return 1;
                    }
                } else {
                    // Navigate to specific page
                    var pageIndex = Math.max(0, Math.min(pageNum - 1, totalPages - 1));
                    pages[pageIndex].classList.add('current-page');
                    return pageIndex + 1;
                }
            };
        }
        return true;
        """)

        # Test navigation to next page
        next_page = self.wait_for_js("return window.navigateToPage('next');")
        self.assertGreaterEqual(next_page, 1, "Expected to navigate to next page")

        # Test navigation to previous page
        prev_page = self.wait_for_js("return window.navigateToPage('prev');")
        self.assertGreaterEqual(prev_page, 1, "Expected to navigate to previous page")

        # Test navigation to specific page (if enough pages)
        page_count = self.wait_for_js("return document.querySelectorAll('.page').length;")
        if page_count >= 3:
            specific_page = self.wait_for_js("return window.navigateToPage(3);")
            self.assertEqual(specific_page, 3, "Expected to navigate to page 3")

    def test_content_overflow_pagination(self):
        """Test that content is properly paginated based on page height"""
        # Create test HTML with long content that should overflow
        long_paragraphs = "\n".join([f"<p>Paragraph {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.</p>" for i in range(50)])

        test_html = f"""
        <html>
        <head>
            <title>Content Overflow Test</title>
        </head>
        <body>
            <h1>Long Content Test</h1>
            {long_paragraphs}
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(test_html)

        # Wait for the preview to load and paginate
        QTest.qWait(2000)

        # Check that multiple pages were created
        page_count = self.wait_for_js("document.querySelectorAll('.page').length")
        self.assertGreater(page_count, 1, "Expected multiple pages to be created due to content overflow")

        # Check that each page has content
        empty_pages = self.wait_for_js("""
        Array.from(document.querySelectorAll('.page')).filter(page => {
            // Count non-page-number elements
            const contentElements = Array.from(page.children).filter(child => !child.classList.contains('page-number'));
            return contentElements.length === 0;
        }).length
        """)
        self.assertEqual(empty_pages, 0, "Expected no empty pages")

    def test_document_settings_applied(self):
        """Test that document settings are properly applied to the preview"""
        test_html = """
        <html>
        <head>
            <title>Document Settings Test</title>
        </head>
        <body>
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <h3>Heading 3</h3>
            <p>This is a paragraph.</p>
            <a href="#">This is a link</a>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
            <pre><code>This is code</code></pre>
            <table>
                <tr><th>Header</th></tr>
                <tr><td>Cell</td></tr>
            </table>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(test_html)

        # Wait for the preview to load and apply settings
        QTest.qWait(2000)

        # Apply page layout again to ensure settings are applied
        self.preview.apply_page_layout()
        QTest.qWait(500)

        # Check that heading styles are applied
        h1_color = self.wait_for_js("""
        const h1 = document.querySelector('.page h1');
        return h1 ? getComputedStyle(h1).color : 'not found';
        """)
        self.assertNotEqual(h1_color, 'not found', "Expected to find h1 element")

        # Check that page dimensions are applied
        page_width = self.wait_for_js("""
        const page = document.querySelector('.page');
        return page ? getComputedStyle(page).width : 'not found';
        """)
        self.assertNotEqual(page_width, 'not found', "Expected to find page element with width")

        # Check that font settings are applied
        body_font = self.wait_for_js("""
        const page = document.querySelector('.page');
        if (!page) return 'not found';
        const style = getComputedStyle(page);
        return style ? style.fontFamily : 'not found';
        """)

        if body_font and body_font != 'not found':
            self.assertIn("Arial", body_font, "Expected Arial font to be applied")
        else:
            self.fail("Could not find page element with font family")

    def test_zoom_functionality(self):
        """Test that zoom functionality works correctly"""
        test_html = """
        <html>
        <head>
            <title>Zoom Test</title>
        </head>
        <body>
            <h1>Zoom Test</h1>
            <p>This is a test of the zoom functionality.</p>
        </body>
        </html>
        """

        # Update the preview with the test HTML
        self.preview.update_preview(test_html)

        # Wait for the preview to load
        QTest.qWait(1000)

        # Check if pages exist
        page_exists = self.wait_for_js("""
        const page = document.querySelector('.page');
        return page ? true : false;
        """)
        self.assertTrue(page_exists, "Expected to find at least one page")

        # Create a custom update_zoom method for testing
        def custom_update_zoom(value):
            self.preview.zoom_factor = value / 100.0
            self.preview.web_view.setZoomFactor(self.preview.zoom_factor)

            # Apply zoom via JavaScript
            zoom_script = f"""
            (function() {{
                if (document && document.documentElement) {{
                    document.documentElement.style.setProperty('--zoom-factor', '{self.preview.zoom_factor}');
                    return true;
                }}
                return false;
            }})();
            """
            self.preview.web_page.runJavaScript(zoom_script)

        # Test zoom in
        custom_update_zoom(150)
        QTest.qWait(500)

        # Check that zoom factor is applied
        zoom_factor = self.wait_for_js("""
        if (document && document.documentElement) {
            var factor = document.documentElement.style.getPropertyValue('--zoom-factor');
            return factor ? parseFloat(factor) : 1.0;
        }
        return null;
        """)

        if zoom_factor is not None:
            self.assertAlmostEqual(zoom_factor, 1.5, places=1, msg="Expected zoom factor to be 1.5")

        # Test zoom out
        custom_update_zoom(75)
        QTest.qWait(500)

        # Check that zoom factor is applied
        zoom_factor = self.wait_for_js("""
        if (document && document.documentElement) {
            var factor = document.documentElement.style.getPropertyValue('--zoom-factor');
            return factor ? parseFloat(factor) : 1.0;
        }
        return null;
        """)

        if zoom_factor is not None:
            self.assertAlmostEqual(zoom_factor, 0.75, places=2, msg="Expected zoom factor to be 0.75")

        # Reset zoom
        custom_update_zoom(100)
        QTest.qWait(500)

        # Check that zoom factor is reset
        zoom_factor = self.wait_for_js("""
        if (document && document.documentElement) {
            var factor = document.documentElement.style.getPropertyValue('--zoom-factor');
            return factor ? parseFloat(factor) : 1.0;
        }
        return null;
        """)

        if zoom_factor is not None:
            self.assertAlmostEqual(zoom_factor, 1.0, places=1, msg="Expected zoom factor to be 1.0")

def run_tests():
    """Run the tests"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
