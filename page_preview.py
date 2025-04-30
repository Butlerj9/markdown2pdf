#!/usr/bin/env python3
"""
PagePreview Class
----------------
Web-based preview component for the Markdown to PDF Converter with print-like layout.
File: src--page_preview.py
"""

import os
import tempfile
from PyQt6.QtWidgets import QScrollArea, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QWidget, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineScript
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QIcon
from logging_config import get_logger

logger = get_logger()

class WebBridge(QObject):
    """Bridge between JavaScript and Python for page navigation"""
    # Signal to update page counter
    pageCountChanged = pyqtSignal(int, int)

    def __init__(self, page_preview):
        super().__init__()
        self.page_preview = page_preview

    @pyqtSlot(int, int)
    def pageCountChanged(self, current_page, total_pages):
        """Called from JavaScript when page count changes"""
        logger.debug(f"Page count changed: {current_page} of {total_pages}")
        self.page_preview.update_page_counter(current_page, total_pages)


class CustomWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage that logs JavaScript console messages"""

    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle console.log messages from JavaScript"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")

        logger.debug(f"JS Console ({level_str}): {message} [{source}:{line}]")
        super().javaScriptConsoleMessage(level, message, line, source)

class PagePreview(QScrollArea):
    """Web-based preview with print-like layout and page navigation"""
    # Signal to update page count in status bar
    page_count_changed = pyqtSignal(int, int)  # current page, total pages

    def __init__(self, parent=None):
        super().__init__(parent)

        logger.debug("Initializing PagePreview")

        # Create a container widget for the web view and navigation controls
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # Create a widget for the top controls (zoom, etc.)
        self.top_controls = QWidget()
        self.top_controls_layout = QHBoxLayout(self.top_controls)
        self.top_controls_layout.setContentsMargins(10, 5, 10, 5)

        # Add status label to top controls
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.top_controls_layout.addWidget(self.status_label)

        # Add top controls to container
        self.container_layout.addWidget(self.top_controls)

        # Create the web view for previewing HTML
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Set custom page with console logging
        self.web_page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)

        # Create web channel for JavaScript bridge
        self.web_channel = QWebChannel(self.web_page)
        self.web_page.setWebChannel(self.web_channel)

        # Create JavaScript bridge
        self.bridge = None

        # Add the web view to the container (with stretch factor to make it take up most space)
        self.container_layout.addWidget(self.web_view, 1)

        # Create navigation controls at the bottom
        self.nav_container = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(10, 5, 10, 5)

        # Previous page button
        self.prev_page_btn = QPushButton("Previous Page")
        self.prev_page_btn.setToolTip("Go to previous page (Left Arrow)")
        self.prev_page_btn.clicked.connect(self.go_to_previous_page)
        self.prev_page_btn.setEnabled(False)
        self.prev_page_btn.setShortcut("Left")

        # Page counter label
        self.page_counter = QLabel("Page 1 of 1")
        self.page_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_counter.setToolTip("Current page / Total pages (Home: First page, End: Last page)")

        # Next page button
        self.next_page_btn = QPushButton("Next Page")
        self.next_page_btn.setToolTip("Go to next page (Right Arrow)")
        self.next_page_btn.clicked.connect(self.go_to_next_page)
        self.next_page_btn.setEnabled(False)
        self.next_page_btn.setShortcut("Right")

        # Add navigation controls to layout
        self.nav_layout.addWidget(self.prev_page_btn)
        self.nav_layout.addWidget(self.page_counter)
        self.nav_layout.addWidget(self.next_page_btn)

        # Add navigation container to main layout (at the bottom)
        self.container_layout.addWidget(self.nav_container)

        # Set up the scroll area
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #e0e0e0;
                border: none;
            }

            QPushButton {
                padding: 5px 10px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }

            QPushButton:hover {
                background-color: #e0e0e0;
            }

            QPushButton:disabled {
                color: #999;
                background-color: #f5f5f5;
            }
        """)

        # Set up zoom
        self.zoom_factor = 1.0

        # Document settings
        self.document_settings = None
        self.page_width_mm = 210  # A4 default
        self.page_height_mm = 297  # A4 default
        self.margin_top_mm = 25
        self.margin_right_mm = 25
        self.margin_bottom_mm = 25
        self.margin_left_mm = 25

        # Track temporary files for cleanup
        self.temp_files = []

        # Add a label to show loading status
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")

        # Connect signals
        self.web_view.loadStarted.connect(self.on_load_started)
        self.web_view.loadFinished.connect(self.on_load_finished)

        logger.debug("PagePreview initialized")

    def on_load_started(self):
        """Handle page load started event"""
        logger.debug("Web view: load started")
        self.status_label.setText("Loading...")
        self.status_label.setStyleSheet("color: blue; font-style: italic;")

    def on_load_finished(self, success):
        """Handle page load finished event"""
        if success:
            logger.debug("Web view: load finished successfully")
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: green; font-style: italic;")

            # Apply page layout styling
            self.apply_page_layout()
        else:
            logger.warning("Web view: load failed")
            self.status_label.setText("Load Failed")
            self.status_label.setStyleSheet("color: red; font-style: italic;")

    def apply_page_layout(self):
        """Apply page layout styling to make the preview look like a printed page"""
        # Calculate page dimensions in pixels with better DPI detection
        # Default to 96 DPI, but try to get actual screen DPI if available
        try:
            screen = self.screen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                logger.debug(f"Using screen DPI: {dpi}")
            else:
                dpi = 96
                logger.debug("Using default DPI: 96")
        except Exception as e:
            dpi = 96
            logger.debug(f"Error getting screen DPI, using default 96: {str(e)}")

        mm_to_px = dpi / 25.4  # 25.4 mm = 1 inch

        page_width_px = int(self.page_width_mm * mm_to_px)
        page_height_px = int(self.page_height_mm * mm_to_px)
        margin_top_px = int(self.margin_top_mm * mm_to_px)
        margin_right_px = int(self.margin_right_mm * mm_to_px)
        margin_bottom_px = int(self.margin_bottom_mm * mm_to_px)
        margin_left_px = int(self.margin_left_mm * mm_to_px)

        # Get document settings for styling
        if not self.document_settings:
            logger.warning("No document settings available for page layout")
            return

        # Extract styling settings
        body_font_family = self.document_settings["fonts"]["body"]["family"]
        body_font_size = self.document_settings["fonts"]["body"]["size"]
        body_line_height = self.document_settings["fonts"]["body"]["line_height"]
        text_color = self.document_settings["colors"]["text"]
        bg_color = self.document_settings["colors"]["background"]
        link_color = self.document_settings["colors"]["links"]

        # Heading styles
        h1_family = self.document_settings["fonts"]["headings"]["h1"]["family"]
        h1_size = self.document_settings["fonts"]["headings"]["h1"]["size"]
        h1_color = self.document_settings["fonts"]["headings"]["h1"]["color"]
        h1_spacing = self.document_settings["fonts"]["headings"]["h1"]["spacing"]
        h1_margin_top = self.document_settings["fonts"]["headings"]["h1"]["margin_top"]
        h1_margin_bottom = self.document_settings["fonts"]["headings"]["h1"]["margin_bottom"]

        h2_family = self.document_settings["fonts"]["headings"]["h2"]["family"]
        h2_size = self.document_settings["fonts"]["headings"]["h2"]["size"]
        h2_color = self.document_settings["fonts"]["headings"]["h2"]["color"]
        h2_spacing = self.document_settings["fonts"]["headings"]["h2"]["spacing"]
        h2_margin_top = self.document_settings["fonts"]["headings"]["h2"]["margin_top"]
        h2_margin_bottom = self.document_settings["fonts"]["headings"]["h2"]["margin_bottom"]

        h3_family = self.document_settings["fonts"]["headings"]["h3"]["family"]
        h3_size = self.document_settings["fonts"]["headings"]["h3"]["size"]
        h3_color = self.document_settings["fonts"]["headings"]["h3"]["color"]
        h3_spacing = self.document_settings["fonts"]["headings"]["h3"]["spacing"]
        h3_margin_top = self.document_settings["fonts"]["headings"]["h3"]["margin_top"]
        h3_margin_bottom = self.document_settings["fonts"]["headings"]["h3"]["margin_bottom"]

        # Paragraph styles
        p_margin_top = self.document_settings["paragraphs"]["margin_top"]
        p_margin_bottom = self.document_settings["paragraphs"]["margin_bottom"]
        p_spacing = self.document_settings["paragraphs"]["spacing"]
        p_indent = self.document_settings["paragraphs"]["first_line_indent"]
        p_align = self.document_settings["paragraphs"]["alignment"]

        # Code styles
        code_font = self.document_settings["code"]["font_family"]
        code_size = self.document_settings["code"]["font_size"]
        code_bg = self.document_settings["code"]["background"]
        code_border = self.document_settings["code"]["border_color"]

        # Table styles
        table_border = self.document_settings["table"]["border_color"]
        table_header_bg = self.document_settings["table"]["header_bg"]
        table_padding = self.document_settings["table"]["cell_padding"]

        # List styles
        list_bullet_indent = self.document_settings["lists"]["bullet_indent"]
        list_number_indent = self.document_settings["lists"]["number_indent"]
        list_spacing = self.document_settings["lists"]["item_spacing"]

        # Technical numbering settings
        tech_numbering = self.document_settings["format"]["technical_numbering"]
        numbering_start = self.document_settings["format"].get("numbering_start", 1)

        # JavaScript to apply page layout
        page_layout_script = f"""
        (function() {{
            // Make sure we have a head element and document is fully loaded
            if (!document.head || !document.body) {{
                console.log('Document not ready yet, retrying in 100ms');
                setTimeout(function() {{
                    console.log('Retrying page layout application');
                    applyPageLayout();
                }}, 100);
                return;
            }}

            function applyPageLayout() {{
                // Double check document is ready
                if (!document.head || !document.body) {{
                    console.log('Document still not ready, aborting');
                    return;
                }}

            // Add page layout styling
            var style = document.createElement('style');
            style.textContent = `
                body {{
                    background-color: #e0e0e0 !important;
                    padding: 40px !important;
                    margin: 0 !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    min-height: 100vh !important;
                }}

                .page {{
                    width: {page_width_px}px;
                    min-height: {page_height_px}px;
                    margin: 0 auto 40px auto; /* Increased bottom margin for page break indicator */
                    padding: {margin_top_px}px {margin_right_px}px {margin_bottom_px}px {margin_left_px}px;
                    background-color: {bg_color};
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                    box-sizing: border-box;
                    position: relative;
                    font-family: "{body_font_family}", Arial, sans-serif;
                    font-size: {body_font_size}pt;
                    line-height: {body_line_height};
                    color: {text_color};
                    page-break-after: always;
                    break-after: page;
                    flex: 0 0 auto;
                }}

                /* Add visual indicator for page breaks */
                .page-break-indicator {{
                    display: block;
                    position: absolute;
                    bottom: -25px;
                    left: 50%;
                    transform: translateX(-50%);
                    text-align: center;
                    font-size: 10px;
                    color: #666;
                    background-color: #f0f0f0;
                    border: 1px dashed #999;
                    border-radius: 3px;
                    padding: 2px 10px;
                    z-index: 100;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}

                /* Show page boundaries */
                .page {{
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                    transition: transform 0.2s ease;
                }}

                /* Highlight current page */
                .page.current-page {{
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    transform: translateY(-2px);
                    z-index: 10;
                }}

                /* Hide non-visible pages when in single page mode */
                .page.hidden-page {{
                    display: none;
                }}

                /* Page number indicator */
                .page-number {{
                    position: absolute;
                    bottom: 5px;
                    right: 5px;
                    background-color: rgba(0, 0, 0, 0.1);
                    color: #666;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 12px;
                    z-index: 1000;
                }}

                /* Explicit page break marker */
                .explicit-page-break {{
                    display: none; /* Hide in the final output */
                    background-color: #ffcc00;
                    color: #000;
                    text-align: center;
                    padding: 5px;
                    margin: 10px 0;
                    border: 2px dashed #ff9900;
                    font-weight: bold;
                    border-radius: 5px;
                }}

                .page::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    border: 1px solid #ccc;
                    pointer-events: none;
                }}

                /* Show margin boundaries */
                .page::after {{
                    content: '';
                    position: absolute;
                    top: {margin_top_px}px;
                    left: {margin_left_px}px;
                    right: {margin_right_px}px;
                    bottom: {margin_bottom_px}px;
                    border: 1px dashed #aaa;
                    pointer-events: none;
                }}

                /* Handle page breaks */
                .page-break-before {{
                    page-break-before: always;
                }}

                /* Make sure content is inside the page */
                .page > * {{
                    max-width: 100%;
                }}

                /* Heading styles */
                .page h1 {{
                    font-family: "{h1_family}", Arial, sans-serif;
                    font-size: {h1_size}pt;
                    color: {h1_color};
                    line-height: {h1_spacing};
                    margin-top: {h1_margin_top}pt;
                    margin-bottom: {h1_margin_bottom}pt;
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }}

                .page h2 {{
                    font-family: "{h2_family}", Arial, sans-serif;
                    font-size: {h2_size}pt;
                    color: {h2_color};
                    line-height: {h2_spacing};
                    margin-top: {h2_margin_top}pt;
                    margin-bottom: {h2_margin_bottom}pt;
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }}

                .page h3 {{
                    font-family: "{h3_family}", Arial, sans-serif;
                    font-size: {h3_size}pt;
                    color: {h3_color};
                    line-height: {h3_spacing};
                    margin-top: {h3_margin_top}pt;
                    margin-bottom: {h3_margin_bottom}pt;
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }}

                /* Paragraph styles */
                .page p {{
                    margin-top: {p_margin_top}pt;
                    margin-bottom: {p_margin_bottom}pt;
                    line-height: {p_spacing};
                    text-indent: {p_indent}pt;
                    text-align: {p_align};
                }}

                /* Link styles */
                .page a {{
                    color: {link_color};
                    text-decoration: none;
                }}

                .page a:hover {{
                    text-decoration: underline;
                }}

                /* Code block styles */
                .page pre, .page code {{
                    font-family: "{code_font}", "Courier New", monospace;
                    font-size: {code_size}pt;
                }}

                .page pre {{
                    background-color: {code_bg};
                    border: 1px solid {code_border};
                    padding: 10px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}

                /* Table styles */
                .page table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15pt 0;
                    page-break-inside: avoid;
                }}

                .page th {{
                    background-color: {table_header_bg};
                    color: {text_color};
                    border: 1px solid {table_border};
                    padding: {table_padding}pt;
                }}

                .page td {{
                    border: 1px solid {table_border};
                    padding: {table_padding}pt;
                }}

                /* List styles */
                .page ul {{
                    padding-left: {list_bullet_indent}pt;
                    margin-top: 0;
                    margin-bottom: {list_spacing}pt;
                }}

                .page ol {{
                    padding-left: {list_number_indent}pt;
                    margin-top: 0;
                    margin-bottom: {list_spacing}pt;
                }}

                .page li {{
                    margin-bottom: {list_spacing}pt;
                }}

                /* Bullet styles for different levels */
                .page ul {{
                    list-style-type: {self.get_bullet_style(self.document_settings["lists"]["bullet_style_l1"])}; /* Level 1 bullet style */
                }}

                .page ul ul {{
                    list-style-type: {self.get_bullet_style(self.document_settings["lists"]["bullet_style_l2"])}; /* Level 2 bullet style */
                    padding-left: {self.document_settings["lists"]["nested_indent"]}pt;
                }}

                .page ul ul ul {{
                    list-style-type: {self.get_bullet_style(self.document_settings["lists"]["bullet_style_l3"])}; /* Level 3 bullet style */
                    padding-left: {self.document_settings["lists"]["nested_indent"]}pt;
                }}

                /* Custom bullet styles */
                /* Apply custom bullet styles based on class names */
                .page ul.dash-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.dash-bullets > li::before {{
                    content: '\2013';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.triangle-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.triangle-bullets > li::before {{
                    content: '\25B6';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.arrow-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.arrow-bullets > li::before {{
                    content: '\27A1';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.checkmark-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.checkmark-bullets > li::before {{
                    content: '\2713';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.star-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.star-bullets > li::before {{
                    content: '\2605';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.diamond-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.diamond-bullets > li::before {{
                    content: '\25C6';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.heart-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.heart-bullets > li::before {{
                    content: '\2665';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.pointer-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.pointer-bullets > li::before {{
                    content: '\261E';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                .page ul.greater-bullets > li {{
                    list-style-type: none;
                }}
                .page ul.greater-bullets > li::before {{
                    content: '\00BB';
                    display: inline-block;
                    width: 1em;
                    margin-left: -1em;
                }}

                /* Number styles for different levels */
                .page ol {{
                    list-style-type: {self.get_number_style(self.document_settings["lists"]["number_style_l1"])}; /* Level 1 number style */
                }}

                .page ol ol {{
                    list-style-type: {self.get_number_style(self.document_settings["lists"]["number_style_l2"])}; /* Level 2 number style */
                    padding-left: {self.document_settings["lists"]["nested_indent"]}pt;
                }}

                .page ol ol ol {{
                    list-style-type: {self.get_number_style(self.document_settings["lists"]["number_style_l3"])}; /* Level 3 number style */
                    padding-left: {self.document_settings["lists"]["nested_indent"]}pt;
                }}
            `;
            document.head.appendChild(style);

            // Completely new approach to page breaks
            console.log('Applying new page break approach');

            // Save the original content
            var originalContent = document.body.innerHTML;

            // Clear the body
            document.body.innerHTML = '';

            // Create a container for all pages
            var pagesContainer = document.createElement('div');
            pagesContainer.className = 'pages-container';
            document.body.appendChild(pagesContainer);

            // First, preprocess the content to handle HTML comments
            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = originalContent;

            // Find all HTML comment nodes that contain PAGE_BREAK
            var walker = document.createTreeWalker(
                tempDiv,
                NodeFilter.SHOW_COMMENT,
                {{ acceptNode: function(node) {{ return node.nodeValue.trim() === 'PAGE_BREAK' ? 1 : 2; }} }},
                false
            );

            // Replace comment nodes with actual page break divs
            var commentNodes = [];
            while(walker.nextNode()) {{
                commentNodes.push(walker.currentNode);
            }}

            // Replace each comment with a page break div (in reverse to maintain indices)
            for (var i = commentNodes.length - 1; i >= 0; i--) {{
                var comment = commentNodes[i];
                var pageBreakDiv = document.createElement('div');
                pageBreakDiv.className = 'explicit-page-break';
                pageBreakDiv.setAttribute('data-page-break', 'true');
                pageBreakDiv.textContent = 'PAGE BREAK';
                comment.parentNode.replaceChild(pageBreakDiv, comment);
            }}

            // Now split the content at the page breaks
            var pageBreaks = tempDiv.querySelectorAll('.explicit-page-break, div[style="page-break-before: always;"]');
            console.log('Found ' + pageBreaks.length + ' page breaks');

            // If no page breaks, create a single page
            if (pageBreaks.length === 0) {{
                var singlePage = document.createElement('div');
                singlePage.className = 'page';
                singlePage.innerHTML = tempDiv.innerHTML;
                pagesContainer.appendChild(singlePage);
                console.log('Created a single page (no page breaks found)');
            }} else {{
                // Create an array to hold all content nodes
                var allNodes = Array.from(tempDiv.childNodes);
                var currentPage = document.createElement('div');
                currentPage.className = 'page';
                pagesContainer.appendChild(currentPage);

                // Process each node
                var pageCount = 1;
                console.log('Creating multiple pages from ' + allNodes.length + ' nodes');

                for (var i = 0; i < allNodes.length; i++) {{
                    var node = allNodes[i];

                    // Check if this is a page break
                    if ((node.nodeType === 1 &&
                         (node.className === 'explicit-page-break' ||
                          node.getAttribute('style') === 'page-break-before: always;'))) {{
                        // Start a new page
                        currentPage = document.createElement('div');
                        currentPage.className = 'page';
                        pagesContainer.appendChild(currentPage);
                        pageCount++;
                        console.log('Created page ' + pageCount);

                        // Skip the page break node itself
                        continue;
                    }}

                    // Add the node to the current page
                    currentPage.appendChild(node.cloneNode(true));
                }}

                console.log('Created ' + pageCount + ' pages total');
            }}

            // Get all pages
            var pages = document.querySelectorAll('.page');
            var currentPage = 1;
            var totalPages = pages.length;

            // Add page navigation functions to window object
            window.navigateToPage = function(target) {{
                console.log('Navigating to page: ' + target + ', current page: ' + currentPage + ', total pages: ' + totalPages);

                if (target === 'prev' && currentPage > 1) {{
                    currentPage--;
                }} else if (target === 'next' && currentPage < totalPages) {{
                    currentPage++;
                }} else if (typeof target === 'number' && target >= 1 && target <= totalPages) {{
                    currentPage = target;
                }}

                console.log('New current page: ' + currentPage);

                // Update page visibility
                updatePageVisibility();

                // Scroll to current page
                var currentPageElement = document.querySelector('.page.current-page');
                if (currentPageElement) {{
                    currentPageElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}

                // Send page info to Qt
                if (window.qt && typeof window.qt.pageCountChanged === 'function') {{
                    window.qt.pageCountChanged(currentPage, totalPages);
                    console.log('Sent page count to Qt: ' + currentPage + ' of ' + totalPages);
                }} else {{
                    console.log('Qt bridge not available, page count: ' + currentPage + ' of ' + totalPages);
                }}
            }};

            // Function to update page visibility based on current page
            function updatePageVisibility() {{
                console.log('Updating page visibility, current page: ' + currentPage + ', total pages: ' + totalPages);

                document.querySelectorAll('.page').forEach(function(page, index) {{
                    // Page numbers are 1-based, index is 0-based
                    var pageNum = index + 1;

                    // Update page class
                    if (pageNum === currentPage) {{
                        page.classList.add('current-page');
                        page.classList.remove('hidden-page');
                        console.log('Set page ' + pageNum + ' as current page');
                    }} else {{
                        page.classList.remove('current-page');
                        // Always show all pages in the preview
                        page.classList.remove('hidden-page');
                    }}

                    // Update or add page number indicator
                    var pageNumberEl = page.querySelector('.page-number');
                    if (!pageNumberEl) {{
                        pageNumberEl = document.createElement('div');
                        pageNumberEl.className = 'page-number';
                        page.appendChild(pageNumberEl);
                        console.log('Added page number indicator to page ' + pageNum);
                    }}
                    pageNumberEl.textContent = 'Page ' + pageNum + ' of ' + totalPages;
                }});

                // Also update the navigation buttons
                if (window.qt && typeof window.qt.pageCountChanged === 'function') {{
                    window.qt.pageCountChanged(currentPage, totalPages);
                }}
            }}

            // Create page containers
            pages.forEach(function(pageContent, index) {{
                var pageDiv = document.createElement('div');
                pageDiv.className = 'page';
                if (index === 0) {{
                    pageDiv.classList.add('current-page');
                }}
                pageDiv.innerHTML = pageContent;

                // Add unique IDs to all elements for tracking
                Array.from(pageDiv.children).forEach(function(element, elementIndex) {{
                    element.setAttribute('data-element-id', 'page-' + index + '-element-' + elementIndex);
                }});

                // Add page break indicator
                if (index < pages.length - 1) {{
                    var breakIndicator = document.createElement('div');
                    breakIndicator.className = 'page-break-indicator';
                    breakIndicator.textContent = 'PAGE BREAK';
                    pageDiv.appendChild(breakIndicator);
                }}

                document.body.appendChild(pageDiv);
            }});

            // Initialize page navigation
            updatePageVisibility();

            // Add keyboard navigation
            document.addEventListener('keydown', function(event) {{
                // Left arrow key - previous page
                if (event.key === 'ArrowLeft') {{
                    window.navigateToPage('prev');
                    event.preventDefault();
                }}
                // Right arrow key - next page
                else if (event.key === 'ArrowRight') {{
                    window.navigateToPage('next');
                    event.preventDefault();
                }}
                // Home key - first page
                else if (event.key === 'Home') {{
                    window.navigateToPage(1);
                    event.preventDefault();
                }}
                // End key - last page
                else if (event.key === 'End') {{
                    window.navigateToPage(totalPages);
                    event.preventDefault();
                }}
            }});

            // Add a load event listener to update page count after everything is loaded
            window.addEventListener('load', function() {{
                console.log('Window loaded, updating page count...');
                // Force update of page count after a short delay
                setTimeout(function() {{
                    // Count actual pages
                    var actualPages = document.querySelectorAll('.page').length;
                    console.log('Actual pages in document: ' + actualPages);
                    totalPages = Math.max(actualPages, 1);

                    // Look for additional page breaks that might be in the content
                    var additionalBreaks = document.querySelectorAll('div[style="page-break-before: always;"]');
                    if (additionalBreaks.length > 0) {{
                        console.log('Found ' + additionalBreaks.length + ' additional page breaks in content');

                        // Add visual indicators for these breaks
                        additionalBreaks.forEach(function(breakEl) {{
                            var indicator = document.createElement('div');
                            indicator.className = 'page-break-indicator';
                            indicator.textContent = 'PAGE BREAK (in content)';
                            indicator.style.backgroundColor = '#fff0f0';
                            breakEl.parentNode.insertBefore(indicator, breakEl);
                        }});

                        // Update total pages count
                        totalPages += additionalBreaks.length;
                        console.log('Updated total pages to: ' + totalPages);
                    }}

                    // Check for content that exceeds page height and add automatic page breaks
                    detectOverflowingContent();

                    // Update navigation
                    updatePageVisibility();

                    // Notify Qt
                    if (window.qt && typeof window.qt.pageCountChanged === 'function') {{
                        window.qt.pageCountChanged(currentPage, totalPages);
                    }}
                }}, 1000);
            }});

            // Function to detect content that exceeds page height and add automatic page breaks
            function detectOverflowingContent() {{
                try {{
                    console.log('Checking for content that exceeds page height...');
                    var pages = document.querySelectorAll('.page');
                    var pageHeight = {page_height_px};
                    var availableHeight = pageHeight - {margin_top_px} - {margin_bottom_px};
                    var newPages = [];
                    var overflowingPages = 0;

                    // Calculate line height in pixels based on font size and line height factor
                    var fontSizePt = {body_font_size};
                    var lineHeightFactor = {body_line_height};
                    var fontSizePx = fontSizePt * 96 / 72; // Convert pt to px (96 DPI / 72 points per inch)
                    var lineHeightPx = fontSizePx * lineHeightFactor;

                    // Calculate lines per page
                    var linesPerPage = Math.floor(availableHeight / lineHeightPx);

                    console.log('Font size: ' + fontSizePt + 'pt (' + fontSizePx + 'px), Line height: ' +
                               lineHeightPx + 'px, Lines per page: ' + linesPerPage);
                    console.log('Page height: ' + pageHeight + 'px, Available height: ' + availableHeight + 'px');

                    // Process each page
                    pages.forEach(function(page, pageIndex) {{
                        // Count lines in the page
                        var totalLines = 0;
                        var paragraphs = page.querySelectorAll('p, h1, h2, h3, h4, h5, h6, ul, ol, pre, table');

                        // Create a new page
                        var currentPageContent = document.createElement('div');
                        currentPageContent.className = 'page';
                        newPages.push(currentPageContent);

                        // Process each paragraph or block element
                        paragraphs.forEach(function(para) {{
                            // Calculate lines for this element
                            var elementLines = calculateElementLines(para);

                            // If adding this element would exceed lines per page, create a new page
                            if (totalLines + elementLines > linesPerPage && totalLines > 0) {{
                                // Add page break indicator
                                var indicator = document.createElement('div');
                                indicator.className = 'page-break-indicator';
                                indicator.textContent = 'LINE COUNT PAGE BREAK';
                                indicator.style.backgroundColor = '#ffeeee';
                                indicator.style.color = '#cc0000';
                                indicator.style.fontWeight = 'bold';
                                indicator.style.position = 'relative';
                                indicator.style.textAlign = 'center';
                                indicator.style.padding = '5px';
                                indicator.style.margin = '10px 0';
                                indicator.style.border = '1px dashed #cc0000';
                                currentPageContent.appendChild(indicator);

                                // Create a new page
                                currentPageContent = document.createElement('div');
                                currentPageContent.className = 'page';
                                newPages.push(currentPageContent);

                                // Reset line count for new page
                                totalLines = 0;
                                overflowingPages++;
                            }}

                            // Clone the element and add to current page
                            var elementClone = para.cloneNode(true);
                            currentPageContent.appendChild(elementClone);

                            // Update total lines
                            totalLines += elementLines;
                        }});
                    }});

                    // Function to calculate lines for an element
                    function calculateElementLines(element) {{
                        var tag = element.tagName.toLowerCase();
                        var text = element.textContent;
                        var lines = 0;

                        // Handle different element types
                        if (tag === 'p') {{
                            // For paragraphs, estimate based on text length and available width
                            var paraWidth = element.offsetWidth || (pageHeight - {margin_left_px} - {margin_right_px});
                            var charsPerLine = Math.floor(paraWidth / (fontSizePx * 0.6)); // Approximate chars per line
                            lines = Math.ceil(text.length / charsPerLine) || 1;

                            // Add extra line for paragraph spacing
                            lines += 0.5;
                        }} else if (tag.startsWith('h') && tag.length === 2 && tag[1] >= '1' && tag[1] <= '6') {{
                            // Headings take up more space
                            var level = parseInt(tag.substring(1));
                            lines = 2 + (7 - level) * 0.5; // H1 is bigger than H6
                        }} else if (tag === 'ul' || tag === 'ol') {{
                            // For lists, count list items
                            var items = element.querySelectorAll('li');
                            lines = items.length * 1.2; // Each item takes at least one line
                        }} else if (tag === 'pre') {{
                            // For code blocks, count actual lines
                            lines = (text.split('\n').length - 1) + 2;
                        }} else if (tag === 'table') {{
                            // For tables, count rows
                            var rows = element.querySelectorAll('tr');
                            lines = rows.length * 1.5 + 2; // Each row plus some spacing
                        }} else {{
                            // Default for other elements
                            lines = 1;
                        }}

                        return Math.max(1, Math.ceil(lines)); // Ensure at least 1 line
                    }}

                    // If we created new pages, replace the old ones
                    if (newPages.length > 1) {{
                        console.log('Created ' + newPages.length + ' pages after line counting');

                        // Clear the document body
                        document.body.innerHTML = '';

                        // Add the new pages
                        newPages.forEach(function(page, index) {{
                            // Add page number
                            var pageNumberEl = document.createElement('div');
                            pageNumberEl.className = 'page-number';
                            pageNumberEl.textContent = 'Page ' + (index + 1) + ' of ' + newPages.length;
                            page.appendChild(pageNumberEl);

                            // Add to document
                            document.body.appendChild(page);
                        }});

                        // Update total pages count
                        totalPages = newPages.length;

                        // Update page visibility
                        updatePageVisibility();

                        // Notify Qt
                        if (window.qt && typeof window.qt.pageCountChanged === 'function') {{
                            window.qt.pageCountChanged(currentPage, totalPages);
                        }}
                    }}
                }} catch (e) {{
                    console.error('Error detecting overflowing content:', e);
                }}
            }}

            // Apply custom bullet styles
            applyCustomBulletStyles();

            // Function to apply custom bullet styles
            function applyCustomBulletStyles() {{
                try {{
                    console.log('Applying custom bullet styles');

                    // Standard bullet styles don't need special handling
                    var standardStyles = ['disc', 'circle', 'square', 'none'];

                    // Get bullet style settings
                    var level1Style = '{self.document_settings["lists"]["bullet_style_l1"]}';
                    var level2Style = '{self.document_settings["lists"]["bullet_style_l2"]}';
                    var level3Style = '{self.document_settings["lists"]["bullet_style_l3"]}';

                    console.log('Bullet styles:', level1Style, level2Style, level3Style);

                    // Only process if we have custom styles
                    if (standardStyles.indexOf(level1Style.toLowerCase()) !== -1 &&
                        standardStyles.indexOf(level2Style.toLowerCase()) !== -1 &&
                        standardStyles.indexOf(level3Style.toLowerCase()) !== -1) {{
                        console.log('No custom bullet styles to apply');
                        return;
                    }}

                    // Apply custom bullet styles using inline styles for better compatibility
                    document.querySelectorAll('.page ul').forEach(function(ul) {{
                        var items = ul.querySelectorAll('li');
                        items.forEach(function(li) {{
                            // Determine the nesting level
                            var level = 0;
                            var parent = li.parentElement;
                            while (parent && parent.tagName === 'UL') {{
                                level++;
                                parent = parent.parentElement;
                                if (parent && parent.tagName === 'LI') {{
                                    parent = parent.parentElement;
                                }}
                            }}

                            // Get the appropriate style for this level
                            var style = level1Style;
                            if (level === 2) style = level2Style;
                            if (level === 3) style = level3Style;

                            // Apply the style
                            applyBulletStyle(li, style);
                        }});
                    }});

                    console.log('Successfully applied custom bullet styles');
                }} catch (e) {{
                    console.error('Error applying custom bullet styles:', e);
                }}
            }}

            // Helper function to apply a specific bullet style to a list item
            function applyBulletStyle(li, styleName) {{
                // Skip standard styles
                if (['Disc', 'Circle', 'Square', 'None'].indexOf(styleName) !== -1) {{
                    return;
                }}

                // Map of style names to Unicode characters
                var bulletChars = {{
                    'Dash': '-',
                    'Triangle': '▶',
                    'Arrow': '→',
                    'Checkmark': '✓',
                    'Star': '★',
                    'Diamond': '◆',
                    'Heart': '♥',
                    'Pointer': '☞',
                    'Greater': '»'
                }};

                // Get the bullet character
                var bulletChar = bulletChars[styleName] || '•'; // Default to standard bullet

                // Set list-style to none
                li.style.listStyleType = 'none';

                // Check if we already added a custom bullet
                if (!li.querySelector('.custom-bullet')) {{
                    // Create a custom bullet span
                    var bullet = document.createElement('span');
                    bullet.className = 'custom-bullet';
                    bullet.textContent = bulletChar + ' ';
                    bullet.style.display = 'inline-block';
                    bullet.style.width = '1.2em';
                    bullet.style.marginLeft = '-1.2em';

                    // Insert at the beginning of the list item
                    if (li.firstChild) {{
                        li.insertBefore(bullet, li.firstChild);
                    }} else {{
                        li.appendChild(bullet);
                    }}
                }}
            }}

            // Apply heading colors explicitly
            function applyHeadingColors() {{
                console.log('Applying heading colors explicitly');

                // Apply H1 color
                document.querySelectorAll('.page h1').forEach(function(h1) {{
                    h1.style.color = '{h1_color}';
                    console.log('Applied H1 color: {h1_color}');
                }});

                // Apply H2 color
                document.querySelectorAll('.page h2').forEach(function(h2) {{
                    h2.style.color = '{h2_color}';
                    console.log('Applied H2 color: {h2_color}');
                }});

                // Apply H3 color
                document.querySelectorAll('.page h3').forEach(function(h3) {{
                    h3.style.color = '{h3_color}';
                    console.log('Applied H3 color: {h3_color}');
                }});

                console.log('Heading colors applied successfully');
            }}

            // Apply technical numbering if enabled
            if ({str(tech_numbering).lower()}) {{
                console.log('Applying technical numbering, starting at heading level {numbering_start}');
                // Find the starting heading level
                var startLevel = {numbering_start};
                console.log('Start level: ' + startLevel);

                // Reset counters
                var counters = {{}};
                for (var i = 1; i <= 6; i++) {{
                    counters['h' + i] = 0;
                }}

                // First pass: remove any existing section numbers
                document.querySelectorAll('.section-number').forEach(function(span) {{
                    span.remove();
                }});

                // Second pass: process all headings
                document.querySelectorAll('.page h1, .page h2, .page h3, .page h4, .page h5, .page h6').forEach(function(heading) {{
                    var level = parseInt(heading.tagName.substring(1));
                    console.log('Processing heading level H' + level);

                    // Skip headings below the start level
                    if (level < startLevel) {{
                        console.log('Skipping H' + level + ' (below start level ' + startLevel + ')');
                        return;
                    }}

                    // Check for restart numbering marker
                    if (heading.textContent.includes('<!-- RESTART_NUMBERING -->')) {{
                        console.log('Found restart numbering marker at H' + level);
                        // Reset counters for this level and below
                        for (var i = level; i <= 6; i++) {{
                            counters['h' + i] = 0;
                        }}
                        // Remove the marker
                        heading.innerHTML = heading.innerHTML.replace('<!-- RESTART_NUMBERING -->', '');
                    }}

                    // Increment counter for this level
                    counters['h' + level]++;
                    console.log('Incremented H' + level + ' counter to ' + counters['h' + level]);

                    // Reset all lower level counters
                    for (var i = level + 1; i <= 6; i++) {{
                        counters['h' + i] = 0;
                    }}

                    // Build the section number
                    var sectionNumber = '';
                    for (var i = startLevel; i <= level; i++) {{
                        sectionNumber += counters['h' + i] + '.';
                    }}
                    console.log('Section number: ' + sectionNumber);

                    // Add the section number to the heading
                    var span = document.createElement('span');
                    span.className = 'section-number';
                    span.textContent = sectionNumber + ' ';
                    heading.insertBefore(span, heading.firstChild);
                }});

                console.log('Technical numbering applied successfully');
            }}

            // Apply heading colors after everything else
            applyHeadingColors();
            }}

                console.log('Applied page layout styling');
            }}

            // Call the function to apply page layout
            applyPageLayout();
        }})();
        """


        # Execute the script
        self.web_page.runJavaScript(page_layout_script)
        logger.debug("Applied page layout styling")

    def update_preview(self, html_content):
        """Update the preview with the given HTML content and apply page layout"""
        logger.debug("Updating preview")

        # Clean up any previous temporary files
        self.cleanup_temp_files()

        try:
            # Create JavaScript bridge for page navigation
            self.create_js_bridge()

            # Add meta tag to ensure proper content-type and charset
            if "<head>" in html_content:
                html_content = html_content.replace("<head>", '<head>\n<meta charset="UTF-8">\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
            else:
                # If no head tag found, add a basic one
                html_content = "<html><head>\n<meta charset=\"UTF-8\">\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head><body>" + html_content + "</body></html>"

            # Create a temporary HTML file
            html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
            html_file.write(html_content.encode('utf-8'))
            html_file.close()

            # Track the file for later cleanup
            self.temp_files.append(html_file.name)

            logger.debug(f"Created temporary HTML file: {html_file.name}")

            # Load the HTML file using its file URL
            file_url = QUrl.fromLocalFile(html_file.name)
            logger.debug(f"Loading URL: {file_url.toString()}")
            self.web_view.load(file_url)

            # Set zoom factor
            self.web_view.setZoomFactor(self.zoom_factor)
        except Exception as e:
            logger.error(f"Error setting up preview: {str(e)}")

            # Display error in the preview
            error_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #d9534f;">Preview Error</h2>
                <p>{str(e)}</p>
                <p>Please check the logs for more details.</p>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        logger.debug(f"Cleaning up {len(self.temp_files)} temporary files")

        for file_name in self.temp_files:
            try:
                if os.path.exists(file_name):
                    os.unlink(file_name)
                    logger.debug(f"Deleted temporary file: {file_name}")
            except Exception as e:
                logger.warning(f"Error cleaning up temporary file {file_name}: {str(e)}")

        self.temp_files = []

    def setup_zoom_controls(self, layout):
        """Set up zoom controls for the preview"""
        logger.debug("Setting up zoom controls")

        # Clear existing widgets from top controls layout
        while self.top_controls_layout.count():
            item = self.top_controls_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create zoom controls
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setToolTip("Zoom Out")

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        self.zoom_slider.setToolTip("Zoom Level")

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setToolTip("Zoom In")

        # Add label to show zoom percentage
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add reset zoom button
        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        reset_zoom_btn.setToolTip("Reset Zoom")

        # Add controls to top layout
        self.top_controls_layout.addWidget(zoom_out_btn)
        self.top_controls_layout.addWidget(self.zoom_slider)
        self.top_controls_layout.addWidget(zoom_in_btn)
        self.top_controls_layout.addWidget(self.zoom_label)
        self.top_controls_layout.addWidget(reset_zoom_btn)
        self.top_controls_layout.addStretch(1)  # Add stretch to push status label to the right
        self.top_controls_layout.addWidget(self.status_label)

        logger.debug("Zoom controls setup completed")

    def update_zoom(self, value=None):
        """Update the zoom level"""
        logger.debug(f"Updating zoom to value: {value}")

        try:
            if value is not None:
                self.zoom_factor = value / 100.0
                self.zoom_label.setText(f"{value}%")

            logger.debug(f"Setting zoom factor to {self.zoom_factor}")
            self.web_view.setZoomFactor(self.zoom_factor)
        except Exception as e:
            logger.error(f"Error updating zoom: {str(e)}")

    def zoom_in(self):
        """Zoom in by 10%"""
        logger.debug("Zoom in")
        current_value = self.zoom_slider.value()
        new_value = min(current_value + 10, 200)
        self.zoom_slider.setValue(new_value)

    def zoom_out(self):
        """Zoom out by 10%"""
        logger.debug("Zoom out")
        current_value = self.zoom_slider.value()
        new_value = max(current_value - 10, 50)
        self.zoom_slider.setValue(new_value)

    def reset_zoom(self):
        """Reset zoom to 100%"""
        logger.debug("Reset zoom")
        self.zoom_slider.setValue(100)

    def update_document_settings(self, settings):
        """Update document settings and page layout"""
        logger.debug("Updating document settings")

        # Update document settings
        self.document_settings = settings

        # Update page dimensions
        if settings and "page" in settings:
            # Get page size
            page_size = settings["page"]["size"]
            orientation = settings["page"]["orientation"]

            # Set page dimensions based on orientation
            if page_size == "A4":
                if orientation == "portrait":
                    self.page_width_mm = 210
                    self.page_height_mm = 297
                else:  # landscape
                    self.page_width_mm = 297
                    self.page_height_mm = 210
            elif page_size == "Letter":
                if orientation == "portrait":
                    self.page_width_mm = 215.9
                    self.page_height_mm = 279.4
                else:  # landscape
                    self.page_width_mm = 279.4
                    self.page_height_mm = 215.9
            elif page_size == "Legal":
                if orientation == "portrait":
                    self.page_width_mm = 215.9
                    self.page_height_mm = 355.6
                else:  # landscape
                    self.page_width_mm = 355.6
                    self.page_height_mm = 215.9

            # Get margins
            self.margin_top_mm = settings["page"]["margins"]["top"]
            self.margin_right_mm = settings["page"]["margins"]["right"]
            self.margin_bottom_mm = settings["page"]["margins"]["bottom"]
            self.margin_left_mm = settings["page"]["margins"]["left"]

            # Log page dimensions for debugging
            logger.debug(f"Page dimensions: {page_size} {orientation}, {self.page_width_mm}mm x {self.page_height_mm}mm")
            logger.debug(f"Margins: T:{self.margin_top_mm}mm R:{self.margin_right_mm}mm B:{self.margin_bottom_mm}mm L:{self.margin_left_mm}mm")

        # Verify all required settings are present
        self.verify_settings()

        # Apply page layout if a page is loaded
        if self.web_view.url().isValid():
            self.apply_page_layout()

    def verify_settings(self):
        """Verify that all required settings are present and valid"""
        if not self.document_settings:
            logger.warning("No document settings available")
            return

        # Check for required sections
        required_sections = ["fonts", "colors", "page", "paragraphs", "lists", "table", "code", "format"]
        for section in required_sections:
            if section not in self.document_settings:
                logger.warning(f"Missing required settings section: {section}")

        # Check page settings
        if "page" in self.document_settings:
            page = self.document_settings["page"]
            if "size" not in page:
                logger.warning("Missing page size setting")
            if "orientation" not in page:
                logger.warning("Missing page orientation setting")
            if "margins" not in page:
                logger.warning("Missing page margins settings")
            elif not all(m in page["margins"] for m in ["top", "right", "bottom", "left"]):
                logger.warning("Missing one or more margin settings")

        # Check font settings
        if "fonts" in self.document_settings:
            fonts = self.document_settings["fonts"]
            if "body" not in fonts:
                logger.warning("Missing body font settings")
            if "headings" not in fonts:
                logger.warning("Missing headings font settings")

        # Log verification complete
        logger.debug("Settings verification complete")

    def get_bullet_style(self, style_name):
        """Convert bullet style name to CSS list-style-type"""
        # Standard bullet styles
        style_map = {
            "Disc": "disc",
            "Circle": "circle",
            "Square": "square",
            "None": "none"
        }

        # For custom bullet styles, we'll use 'none' and handle them with CSS classes
        if style_name in ["Dash", "Triangle", "Arrow", "Checkmark", "Star", "Diamond", "Heart", "Pointer", "Greater"]:
            return "none"

        # Return the standard style or default to disc
        return style_map.get(style_name, "disc")

    # These methods are no longer needed as we're using CSS classes instead
    # Keeping them as stubs for backward compatibility
    def get_bullet_content(self, style_name):
        """Get the content property value for custom bullet styles (stub)"""
        return "none"

    def get_bullet_display(self, style_name):
        """Get the display property value for custom bullet styles (stub)"""
        return "none"

    def get_number_style(self, style_name):
        """Convert number style name to CSS list-style-type"""
        style_map = {
            "Decimal": "decimal",
            "Lower Alpha": "lower-alpha",
            "Upper Alpha": "upper-alpha",
            "Lower Roman": "lower-roman",
            "Upper Roman": "upper-roman"
        }
        return style_map.get(style_name, "decimal")

    def go_to_previous_page(self):
        """Navigate to the previous page"""
        self.execute_js("window.navigateToPage('prev');")

    def go_to_next_page(self):
        """Navigate to the next page"""
        self.execute_js("window.navigateToPage('next');")

    def go_to_page(self, page_number):
        """Navigate to a specific page"""
        self.execute_js(f"window.navigateToPage({page_number});")

    def update_page_counter(self, current_page, total_pages):
        """Update the page counter display"""
        self.page_counter.setText(f"Page {current_page} of {total_pages}")
        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)

        # Emit signal to update status bar if needed
        self.page_count_changed.emit(current_page, total_pages)

    def create_js_bridge(self):
        """Create JavaScript bridge for page navigation"""
        try:
            # Create bridge object if it doesn't exist
            if not self.bridge:
                self.bridge = WebBridge(self)

            # Add the bridge object to the page's JavaScript world
            self.web_page.runJavaScript("""
                window.qt = window.qt || {};
                window.qt.pageCountChanged = function(current, total) {
                    // This function will be replaced by the actual bridge
                    console.log('Page count changed: ' + current + ' of ' + total);

                    // Update navigation buttons directly
                    var prevBtn = document.getElementById('prev-page-btn');
                    var nextBtn = document.getElementById('next-page-btn');
                    var pageCounter = document.getElementById('page-counter');

                    if (prevBtn) {
                        prevBtn.disabled = current <= 1;
                    }

                    if (nextBtn) {
                        nextBtn.disabled = current >= total;
                    }

                    if (pageCounter) {
                        pageCounter.textContent = 'Page ' + current + ' of ' + total;
                    }
                };
            """)

            # Connect the bridge to the web page
            self.web_page.setWebChannel(self.web_channel)
            self.web_channel.registerObject("bridge", self.bridge)

            # Add a script to detect page load completion and count pages
            self.web_page.runJavaScript("""
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('DOM loaded, counting pages...');
                    setTimeout(function() {
                        // Count page breaks
                        var pageBreaks = document.querySelectorAll('div[style="page-break-before: always;"]');
                        var totalPages = pageBreaks.length + 1; // +1 because breaks are between pages
                        console.log('Found ' + pageBreaks.length + ' page breaks, total pages: ' + totalPages);

                        if (window.qt && window.qt.pageCountChanged) {
                            window.qt.pageCountChanged(1, totalPages);
                        }
                    }, 500); // Small delay to ensure everything is rendered
                });
            """)

            logger.debug("JavaScript bridge created")
        except Exception as e:
            logger.error(f"Error creating JavaScript bridge: {str(e)}")

    def execute_js(self, script):
        """Execute JavaScript in the web view"""
        try:
            logger.debug(f"Executing JavaScript: {script[:100]}...")
            self.web_page.runJavaScript(script, lambda result:
                logger.debug(f"JavaScript execution result: {result}"))
        except Exception as e:
            logger.error(f"Error executing JavaScript: {str(e)}")

    def test_page_navigation(self):
        """Test page navigation functionality"""
        try:
            # Test script to verify page navigation
            test_script = """
            (function() {
                console.log('Testing page navigation...');

                // Test page count
                var pages = document.querySelectorAll('.page');
                console.log('Found ' + pages.length + ' pages');

                // Test navigation to each page
                for (var i = 1; i <= pages.length; i++) {
                    console.log('Testing navigation to page ' + i);
                    window.navigateToPage(i);

                    // Verify current page
                    var currentPage = document.querySelector('.page.current-page');
                    if (!currentPage) {
                        console.error('No current page found after navigation to page ' + i);
                    } else {
                        console.log('Successfully navigated to page ' + i);
                    }
                }

                // Test previous/next navigation
                console.log('Testing previous/next navigation');
                window.navigateToPage(1);
                window.navigateToPage('next');
                window.navigateToPage('prev');

                // Return to first page
                window.navigateToPage(1);
                console.log('Page navigation test complete');

                return 'Page navigation test complete';
            })();
            """

            # Execute the test script
            self.execute_js(test_script)
            logger.debug("Page navigation test initiated")
            return True
        except Exception as e:
            logger.error(f"Error testing page navigation: {str(e)}")
            return False

    def test_page_breaks(self):
        """Test page break detection and visualization"""
        try:
            # Test script to verify page break detection
            test_script = """
            (function() {
                console.log('Testing page break detection...');

                // Test explicit page breaks
                var explicitBreaks = document.querySelectorAll('div[style="page-break-before: always;"]');
                console.log('Found ' + explicitBreaks.length + ' explicit page breaks');

                // Test page break indicators
                var breakIndicators = document.querySelectorAll('.page-break-indicator');
                console.log('Found ' + breakIndicators.length + ' page break indicators');

                // Test content overflow detection
                var pages = document.querySelectorAll('.page');
                var pageHeight = parseFloat(getComputedStyle(pages[0]).height);
                var marginTop = parseFloat(getComputedStyle(pages[0]).paddingTop);
                var marginBottom = parseFloat(getComputedStyle(pages[0]).paddingBottom);
                var contentHeight, pageContentHeight;
                var overflowingPages = 0;

                pages.forEach(function(page, index) {
                    // Get the content height of the page
                    contentHeight = 0;
                    Array.from(page.children).forEach(function(child) {
                        if (!child.classList.contains('page-break-indicator') &&
                            !child.classList.contains('page-number')) {
                            contentHeight += child.offsetHeight;
                        }
                    });

                    // Get the available height for content (accounting for padding)
                    pageContentHeight = pageHeight - marginTop - marginBottom;

                    console.log('Page ' + (index + 1) + ' content height: ' +
                                contentHeight + 'px, available: ' + pageContentHeight + 'px');

                    if (contentHeight > pageContentHeight) {
                        overflowingPages++;
                        console.log('Page ' + (index + 1) + ' has overflowing content');
                    }
                });

                console.log('Found ' + overflowingPages + ' pages with overflowing content');
                console.log('Page break test complete');

                return {
                    explicitBreaks: explicitBreaks.length,
                    breakIndicators: breakIndicators.length,
                    overflowingPages: overflowingPages,
                    totalPages: pages.length
                };
            })();
            """

            # Execute the test script
            self.execute_js(test_script)
            logger.debug("Page break test initiated")
            return True
        except Exception as e:
            logger.error(f"Error testing page breaks: {str(e)}")
            return False