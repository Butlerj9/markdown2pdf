#!/usr/bin/env python3
"""
Page Break Debugger for Markdown to PDF Converter
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QWidget, QLabel, QSplitter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QFont

from markdown_to_pdf_converter import AdvancedMarkdownToPDF

class PageBreakDebugger(QMainWindow):
    """Debug window for page breaks"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Page Break Debugger")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create splitter for editor and preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Create editor widget
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        self.editor_label = QLabel("Markdown Editor")
        self.editor_layout.addWidget(self.editor_label)
        
        # Create markdown editor
        self.markdown_editor = QTextEdit()
        self.markdown_editor.setFont(QFont("Courier New", 10))
        self.editor_layout.addWidget(self.markdown_editor)
        
        # Create editor controls
        self.editor_controls = QHBoxLayout()
        self.insert_page_break_btn = QPushButton("Insert Page Break")
        self.insert_page_break_btn.clicked.connect(self.insert_page_break)
        self.editor_controls.addWidget(self.insert_page_break_btn)
        
        self.update_preview_btn = QPushButton("Update Preview")
        self.update_preview_btn.clicked.connect(self.update_preview)
        self.editor_controls.addWidget(self.update_preview_btn)
        
        self.editor_layout.addLayout(self.editor_controls)
        
        # Create preview widget
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_label = QLabel("HTML Preview")
        self.preview_layout.addWidget(self.preview_label)
        
        # Create web view for preview
        self.web_view = QWebEngineView()
        self.preview_layout.addWidget(self.web_view)
        
        # Create debug controls
        self.debug_controls = QHBoxLayout()
        self.inspect_btn = QPushButton("Inspect Page Breaks")
        self.inspect_btn.clicked.connect(self.inspect_page_breaks)
        self.debug_controls.addWidget(self.inspect_btn)
        
        self.show_html_btn = QPushButton("Show HTML")
        self.show_html_btn.clicked.connect(self.show_html)
        self.debug_controls.addWidget(self.show_html_btn)
        
        self.preview_layout.addLayout(self.debug_controls)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.editor_widget)
        self.splitter.addWidget(self.preview_widget)
        self.splitter.setSizes([400, 800])
        
        # Create debug output
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setMaximumHeight(200)
        self.debug_output.setFont(QFont("Courier New", 10))
        self.layout.addWidget(QLabel("Debug Output"))
        self.layout.addWidget(self.debug_output)
        
        # Set up test content
        self.setup_test_content()
    
    def setup_test_content(self):
        """Set up test content with page breaks"""
        test_content = """# Test Document with Page Breaks

This is the first page of the document. It contains some text to demonstrate page breaks.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 1.1

This is a subsection on the first page.

* Bullet point 1
* Bullet point 2
* Bullet point 3

<!-- PAGE_BREAK -->

# Second Page

This is the second page of the document. It should appear after a page break.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2.1

This is a subsection on the second page.

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

<!-- PAGE_BREAK -->

# Third Page

This is the third page of the document. It should appear after another page break.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""
        self.markdown_editor.setPlainText(test_content)
        self.update_preview()
    
    def insert_page_break(self):
        """Insert a page break at the current cursor position"""
        self.markdown_editor.insertPlainText("\n\n<!-- PAGE_BREAK -->\n\n")
    
    def update_preview(self):
        """Update the preview with the current markdown content"""
        markdown_text = self.markdown_editor.toPlainText()
        
        # Convert markdown to HTML
        try:
            import markdown
            html = markdown.markdown(markdown_text)
            
            # Process page breaks
            html = self.process_page_breaks(html)
            
            # Create full HTML document
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f0f0f0;
                    }}
                    
                    .page {{
                        width: 8.5in;
                        min-height: 11in;
                        padding: 1in;
                        margin: 20px auto;
                        background-color: white;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                        box-sizing: border-box;
                        position: relative;
                        page-break-after: always;
                        break-after: page;
                    }}
                    
                    .page-break {{
                        height: 20px;
                        background-color: #ffcc00;
                        border: 2px dashed #ff9900;
                        margin: 20px 0;
                        text-align: center;
                        line-height: 20px;
                        font-weight: bold;
                        color: #000;
                    }}
                    
                    h1 {{
                        color: #333;
                        border-bottom: 1px solid #ddd;
                    }}
                    
                    h2 {{
                        color: #444;
                    }}
                    
                    pre {{
                        background-color: #f8f8f8;
                        border: 1px solid #ddd;
                        padding: 10px;
                        overflow-x: auto;
                    }}
                    
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                    }}
                    
                    th {{
                        background-color: #f2f2f2;
                    }}
                </style>
                <script>
                    function highlightPageBreaks() {{
                        // Add visible indicators for page breaks
                        var pageBreaks = document.querySelectorAll('.page-break');
                        console.log('Found ' + pageBreaks.length + ' page breaks');
                        
                        // Add page numbers
                        var pages = document.querySelectorAll('.page');
                        console.log('Found ' + pages.length + ' pages');
                        
                        pages.forEach(function(page, index) {{
                            var pageNum = document.createElement('div');
                            pageNum.style.position = 'absolute';
                            pageNum.style.bottom = '10px';
                            pageNum.style.right = '10px';
                            pageNum.style.backgroundColor = '#eee';
                            pageNum.style.padding = '5px';
                            pageNum.style.borderRadius = '5px';
                            pageNum.textContent = 'Page ' + (index + 1) + ' of ' + pages.length;
                            page.appendChild(pageNum);
                        }});
                    }}
                    
                    window.onload = function() {{
                        highlightPageBreaks();
                        console.log('Page break highlighting complete');
                    }};
                </script>
            </head>
            <body>
                {html}
                <script>
                    console.log('Document loaded');
                </script>
            </body>
            </html>
            """
            
            # Load HTML into web view
            self.web_view.setHtml(full_html)
            
            # Log success
            self.log("Preview updated successfully")
        except Exception as e:
            self.log(f"Error updating preview: {str(e)}")
    
    def process_page_breaks(self, html):
        """Process page breaks in HTML"""
        # Replace HTML comments with visible markers
        html = html.replace("<!-- PAGE_BREAK -->", '<div class="page-break">PAGE BREAK</div>')
        
        # Split content at page breaks
        pages = html.split('<div class="page-break">PAGE BREAK</div>')
        
        # Wrap each page in a div
        wrapped_html = ""
        for page in pages:
            wrapped_html += f'<div class="page">{page}</div>\n'
        
        self.log(f"Processed {len(pages)} pages")
        return wrapped_html
    
    def inspect_page_breaks(self):
        """Inspect page breaks in the preview"""
        script = """
        (function() {
            console.log('Inspecting page breaks...');
            
            // Count pages
            var pages = document.querySelectorAll('.page');
            console.log('Found ' + pages.length + ' pages');
            
            // Check for page break markers
            var pageBreaks = document.querySelectorAll('.page-break');
            console.log('Found ' + pageBreaks.length + ' page break markers');
            
            // Add colored borders to pages
            pages.forEach(function(page, index) {
                page.style.border = '5px solid ' + (index % 2 === 0 ? 'blue' : 'green');
                console.log('Added border to page ' + (index + 1));
            });
            
            // Add visible labels to page breaks
            pageBreaks.forEach(function(brk, index) {
                brk.textContent = 'PAGE BREAK ' + (index + 1);
                brk.style.backgroundColor = '#ffcc00';
                brk.style.color = '#000000';
                brk.style.padding = '10px';
                brk.style.margin = '20px 0';
                brk.style.textAlign = 'center';
                brk.style.fontWeight = 'bold';
                brk.style.border = '2px dashed #ff9900';
                console.log('Enhanced page break ' + (index + 1));
            });
            
            return {
                pageCount: pages.length,
                breakCount: pageBreaks.length
            };
        })();
        """
        
        self.web_view.page().runJavaScript(script, self.handle_inspection_result)
    
    def handle_inspection_result(self, result):
        """Handle the result of page break inspection"""
        if result:
            self.log(f"Inspection result: {result['pageCount']} pages, {result['breakCount']} breaks")
        else:
            self.log("No inspection result received")
    
    def show_html(self):
        """Show the raw HTML"""
        script = """
        (function() {
            return document.documentElement.outerHTML;
        })();
        """
        
        self.web_view.page().runJavaScript(script, self.handle_html_result)
    
    def handle_html_result(self, result):
        """Handle the HTML result"""
        if result:
            # Create a new window to show the HTML
            html_window = QMainWindow(self)
            html_window.setWindowTitle("Raw HTML")
            html_window.setGeometry(200, 200, 800, 600)
            
            html_edit = QTextEdit(html_window)
            html_edit.setPlainText(result)
            html_edit.setFont(QFont("Courier New", 10))
            html_window.setCentralWidget(html_edit)
            
            html_window.show()
            self.log(f"HTML displayed in new window ({len(result)} bytes)")
        else:
            self.log("No HTML result received")
    
    def log(self, message):
        """Add a message to the debug output"""
        timestamp = time.strftime("%H:%M:%S")
        self.debug_output.append(f"[{timestamp}] {message}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    debugger = PageBreakDebugger()
    debugger.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
