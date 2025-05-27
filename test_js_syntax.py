#!/usr/bin/env python3
"""
Test JavaScript Syntax
---------------------
Simple test to verify JavaScript syntax in page_preview.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage

class CustomWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage that logs JavaScript console messages"""

    def javaScriptConsoleMessage(self, level, message, line, source):
        """Handle console.log messages from JavaScript"""
        level_str = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }.get(level, "UNKNOWN")

        print(f"JS Console ({level_str}): {message} [{source}:{line}]")

        # For errors, provide more detailed logging
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            print(f"JavaScript Error: {message}")
            print(f"  Source: {source}")
            print(f"  Line: {line}")

            # Extract the specific syntax error if possible
            if "SyntaxError" in message:
                error_parts = message.split(":")
                if len(error_parts) > 1:
                    error_type = error_parts[0].strip()
                    error_detail = ":".join(error_parts[1:]).strip()
                    print(f"  Error Type: {error_type}")
                    print(f"  Error Detail: {error_detail}")

def extract_js_from_page_preview():
    """Extract JavaScript code from page_preview.py"""
    js_code = ""

    with open('page_preview.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract JavaScript from docReady function and related code
    start_marker = "    // Ensure document is ready before accessing DOM"
    end_marker = "    });  // End of docReady function"

    start_index = content.find(start_marker)
    if start_index != -1:
        # Find the end of the docReady function
        end_index = content.find(end_marker, start_index)
        if end_index == -1:  # If exact marker not found, use a reasonable end point
            end_index = content.find("</script>", start_index)

        if end_index != -1:
            js_code = content[start_index:end_index]
            # Add a wrapper to make it valid standalone JS
            js_code = """
            // Test the docReady function and page initialization

            // Create required elements
            var contentContainer = document.createElement('div');
            contentContainer.id = 'content-container';
            document.body.appendChild(contentContainer);

            """ + js_code + """

            // Call docReady with a test function
            docReady(function() {
                console.log('docReady callback executed successfully');
                document.getElementById('output').innerHTML = 'JavaScript syntax test completed successfully.';
            });
            """

    return js_code

def main():
    """Main function to test JavaScript syntax"""
    app = QApplication(sys.argv)

    # Create a web view
    web_view = QWebEngineView()

    # Set custom page with console logging
    web_page = CustomWebEnginePage(web_view)
    web_view.setPage(web_page)

    # Extract JavaScript from page_preview.py
    js_code = extract_js_from_page_preview()

    # Simple HTML with the extracted JavaScript
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JavaScript Syntax Test</title>
    </head>
    <body>
        <h1>JavaScript Syntax Test</h1>
        <div id="output">Testing JavaScript syntax...</div>

        <script>
        // Test JavaScript from page_preview.py
        try {{
            {js_code}
        }} catch (error) {{
            console.error('JavaScript error:', error);
            document.getElementById('output').innerHTML = 'JavaScript syntax test failed: ' + error.message;
        }}
        </script>
    </body>
    </html>
    """

    # Load the HTML
    web_view.setHtml(html)

    # Show the web view
    web_view.show()
    web_view.resize(800, 600)

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
