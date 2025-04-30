#!/usr/bin/env python3
"""
Debug visual test for heading colors and page breaks
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from visual_test import VisualTester

class DebugVisualTest:
    """Class for debugging visual issues"""
    
    def __init__(self):
        """Initialize the test"""
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.tester = None
    
    def setup(self):
        """Set up the test environment"""
        # Create main window
        self.main_window = AdvancedMarkdownToPDF()
        self.main_window.show()
        
        # Create visual tester
        self.tester = VisualTester(self.app)
        
        # Maximize window for consistent screenshots
        self.main_window.showMaximized()
    
    def test_heading_colors(self):
        """Test heading colors in the preview"""
        self.setup()
        
        # Set up test content with colored headings
        test_content = """# Heading 1 (Should be colored)

This is a paragraph under heading 1.

## Heading 2 (Should be colored)

This is a paragraph under heading 2.

### Heading 3 (Should be colored)

This is a paragraph under heading 3.
"""
        
        # Set the content in the editor
        self.main_window.markdown_editor.setPlainText(test_content)
        
        # Set distinct colors for each heading level
        self.set_heading_colors()
        
        # Update the preview
        self.main_window.update_preview()
        QTest.qWait(2000)
        
        # Take a screenshot
        screenshot_path = self.tester.take_screenshot("heading_colors_test")
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Add JavaScript to inspect heading colors
        self.inspect_heading_colors()
        
        # Run the application
        QTimer.singleShot(10000, self.app.quit)  # Quit after 10 seconds
        self.app.exec()
    
    def test_page_breaks(self):
        """Test page breaks in the preview"""
        self.setup()
        
        # Set up test content with explicit page breaks
        test_content = """# Page 1

This is content on page 1.

<!-- PAGE_BREAK -->

# Page 2

This is content on page 2.

<!-- PAGE_BREAK -->

# Page 3

This is content on page 3.
"""
        
        # Set the content in the editor
        self.main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        self.main_window.update_preview()
        QTest.qWait(2000)
        
        # Take a screenshot
        screenshot_path = self.tester.take_screenshot("page_breaks_test")
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Add JavaScript to inspect page breaks
        self.inspect_page_breaks()
        
        # Run the application
        QTimer.singleShot(10000, self.app.quit)  # Quit after 10 seconds
        self.app.exec()
    
    def set_heading_colors(self):
        """Set distinct colors for each heading level"""
        # Set H1 color to red
        self.main_window.document_settings["fonts"]["headings"]["h1"]["color"] = "#FF0000"
        
        # Set H2 color to blue
        self.main_window.document_settings["fonts"]["headings"]["h2"]["color"] = "#0000FF"
        
        # Set H3 color to green
        self.main_window.document_settings["fonts"]["headings"]["h3"]["color"] = "#00FF00"
        
        print("Set heading colors: H1=Red, H2=Blue, H3=Green")
    
    def inspect_heading_colors(self):
        """Add JavaScript to inspect heading colors"""
        script = """
        (function() {
            console.log('Inspecting heading colors...');
            
            // Check H1 color
            var h1 = document.querySelector('.page h1');
            if (h1) {
                var h1Color = window.getComputedStyle(h1).color;
                console.log('H1 color: ' + h1Color);
            } else {
                console.log('No H1 found');
            }
            
            // Check H2 color
            var h2 = document.querySelector('.page h2');
            if (h2) {
                var h2Color = window.getComputedStyle(h2).color;
                console.log('H2 color: ' + h2Color);
            } else {
                console.log('No H2 found');
            }
            
            // Check H3 color
            var h3 = document.querySelector('.page h3');
            if (h3) {
                var h3Color = window.getComputedStyle(h3).color;
                console.log('H3 color: ' + h3Color);
            } else {
                console.log('No H3 found');
            }
            
            // Add colored borders to headings to make colors more visible
            document.querySelectorAll('.page h1').forEach(function(h) {
                h.style.border = '2px solid red';
            });
            
            document.querySelectorAll('.page h2').forEach(function(h) {
                h.style.border = '2px solid blue';
            });
            
            document.querySelectorAll('.page h3').forEach(function(h) {
                h.style.border = '2px solid green';
            });
            
            return 'Heading color inspection complete';
        })();
        """
        
        self.main_window.page_preview.execute_js(script)
    
    def inspect_page_breaks(self):
        """Add JavaScript to inspect page breaks"""
        script = """
        (function() {
            console.log('Inspecting page breaks...');
            
            // Count pages
            var pages = document.querySelectorAll('.page');
            console.log('Found ' + pages.length + ' pages');
            
            // Check for page break markers
            var explicitBreaks = document.querySelectorAll('div[style="page-break-before: always;"]');
            console.log('Found ' + explicitBreaks.length + ' explicit page breaks');
            
            // Check for page break indicators
            var breakIndicators = document.querySelectorAll('.page-break-indicator');
            console.log('Found ' + breakIndicators.length + ' page break indicators');
            
            // Add colored borders to pages to make them more visible
            document.querySelectorAll('.page').forEach(function(page, index) {
                page.style.border = '5px solid ' + (index % 2 === 0 ? 'purple' : 'orange');
                
                // Add a visible label at the top of each page
                var label = document.createElement('div');
                label.textContent = 'PAGE ' + (index + 1);
                label.style.backgroundColor = '#ffcc00';
                label.style.color = '#000000';
                label.style.padding = '5px';
                label.style.fontWeight = 'bold';
                label.style.position = 'absolute';
                label.style.top = '0';
                label.style.left = '0';
                label.style.zIndex = '1000';
                page.insertBefore(label, page.firstChild);
            });
            
            // Check if page breaks are being processed correctly
            var pageBreakMarker = '<div style="page-break-before: always;"></div>';
            var content = document.body.innerHTML;
            if (content.indexOf(pageBreakMarker) !== -1) {
                console.log('Page break marker found in HTML');
            } else {
                console.log('No page break marker found in HTML');
            }
            
            return 'Page break inspection complete';
        })();
        """
        
        self.main_window.page_preview.execute_js(script)

if __name__ == "__main__":
    test = DebugVisualTest()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "page_breaks":
        test.test_page_breaks()
    else:
        test.test_heading_colors()
