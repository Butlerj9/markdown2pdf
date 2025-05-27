#!/usr/bin/env python3
"""
Test script to verify font locking and heading spacing fixes
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

logger = get_logger()

class FontAndHeadingTester:
    """Test font locking and heading spacing functionality"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = AdvancedMarkdownToPDF()
        self.test_results = []
        
    def run_tests(self):
        """Run all tests"""
        logger.info("Starting font locking and heading spacing tests...")
        
        # Show the main window
        self.main_window.show()
        
        # Set up test content
        self.setup_test_content()
        
        # Test 1: Verify font locking only affects font family
        QTimer.singleShot(1000, self.test_font_locking_preserves_sizes)
        
        # Test 2: Verify heading spacing is reflected in page preview
        QTimer.singleShot(3000, self.test_heading_spacing_in_preview)
        
        # Test 3: Verify master font changes only font family
        QTimer.singleShot(5000, self.test_master_font_family_only)
        
        # Test 4: Verify heading margins are applied
        QTimer.singleShot(7000, self.test_heading_margins_applied)
        
        # Finish tests
        QTimer.singleShot(9000, self.finish_tests)
        
        # Start the application
        self.app.exec()
        
    def setup_test_content(self):
        """Set up test markdown content with various headings"""
        test_markdown = """# Main Heading (H1)

This is a paragraph under the main heading.

## Secondary Heading (H2)

Another paragraph with some content.

### Tertiary Heading (H3)

More content here.

#### Fourth Level Heading (H4)

Even more content.

##### Fifth Level Heading (H5)

Content continues.

###### Sixth Level Heading (H6)

Final heading level content.

## Another H2

Final paragraph to test spacing.
"""
        
        self.main_window.markdown_editor.setPlainText(test_markdown)
        logger.info("Test content loaded")
        
    def test_font_locking_preserves_sizes(self):
        """Test that font locking preserves individual heading sizes"""
        logger.info("Testing font locking preserves sizes...")
        
        # Get original heading sizes
        original_h1_size = self.main_window.document_settings["fonts"]["headings"]["h1"]["size"]
        original_h2_size = self.main_window.document_settings["fonts"]["headings"]["h2"]["size"]
        original_h3_size = self.main_window.document_settings["fonts"]["headings"]["h3"]["size"]
        original_body_size = self.main_window.document_settings["fonts"]["body"]["size"]
        
        logger.info(f"Original sizes - H1: {original_h1_size}, H2: {original_h2_size}, H3: {original_h3_size}, Body: {original_body_size}")
        
        # Enable master font
        self.main_window.use_master_font.setChecked(True)
        self.main_window.toggle_master_font(True)
        
        # Check that sizes are preserved
        new_h1_size = self.main_window.document_settings["fonts"]["headings"]["h1"]["size"]
        new_h2_size = self.main_window.document_settings["fonts"]["headings"]["h2"]["size"]
        new_h3_size = self.main_window.document_settings["fonts"]["headings"]["h3"]["size"]
        new_body_size = self.main_window.document_settings["fonts"]["body"]["size"]
        
        logger.info(f"New sizes - H1: {new_h1_size}, H2: {new_h2_size}, H3: {new_h3_size}, Body: {new_body_size}")
        
        # Verify sizes are preserved
        sizes_preserved = (
            original_h1_size == new_h1_size and
            original_h2_size == new_h2_size and
            original_h3_size == new_h3_size and
            original_body_size == new_body_size
        )
        
        if sizes_preserved:
            logger.info("✅ PASS: Font locking preserves individual sizes")
            self.test_results.append("Font locking preserves sizes: PASS")
        else:
            logger.error("❌ FAIL: Font locking changed individual sizes")
            self.test_results.append("Font locking preserves sizes: FAIL")
            
        # Verify font families are unified
        master_font = self.main_window.document_settings["format"]["master_font"]["family"]
        h1_font = self.main_window.document_settings["fonts"]["headings"]["h1"]["family"]
        h2_font = self.main_window.document_settings["fonts"]["headings"]["h2"]["family"]
        body_font = self.main_window.document_settings["fonts"]["body"]["family"]
        
        fonts_unified = (master_font == h1_font == h2_font == body_font)
        
        if fonts_unified:
            logger.info("✅ PASS: Font families are unified")
            self.test_results.append("Font families unified: PASS")
        else:
            logger.error("❌ FAIL: Font families are not unified")
            self.test_results.append("Font families unified: FAIL")
            
    def test_heading_spacing_in_preview(self):
        """Test that heading spacing is reflected in page preview"""
        logger.info("Testing heading spacing in page preview...")
        
        # Modify heading spacing settings
        self.main_window.document_settings["fonts"]["headings"]["h1"]["margin_top"] = 30
        self.main_window.document_settings["fonts"]["headings"]["h1"]["margin_bottom"] = 15
        self.main_window.document_settings["fonts"]["headings"]["h2"]["margin_top"] = 20
        self.main_window.document_settings["fonts"]["headings"]["h2"]["margin_bottom"] = 10
        
        # Update the preview
        self.main_window.update_preview()
        
        # Check if the page preview has the get_heading_css method
        if hasattr(self.main_window.page_preview, 'get_heading_css'):
            heading_css = self.main_window.page_preview.get_heading_css()
            
            # Check if the CSS contains the margin settings
            has_h1_margins = "margin-top: 30pt" in heading_css and "margin-bottom: 15pt" in heading_css
            has_h2_margins = "margin-top: 20pt" in heading_css and "margin-bottom: 10pt" in heading_css
            
            if has_h1_margins and has_h2_margins:
                logger.info("✅ PASS: Heading spacing is reflected in page preview CSS")
                self.test_results.append("Heading spacing in preview: PASS")
            else:
                logger.error("❌ FAIL: Heading spacing not found in page preview CSS")
                logger.error(f"CSS content: {heading_css[:500]}...")
                self.test_results.append("Heading spacing in preview: FAIL")
        else:
            logger.error("❌ FAIL: get_heading_css method not found")
            self.test_results.append("Heading spacing in preview: FAIL")
            
    def test_master_font_family_only(self):
        """Test that changing master font only affects font family"""
        logger.info("Testing master font changes only font family...")
        
        # Change master font
        original_master_font = self.main_window.document_settings["format"]["master_font"]["family"]
        new_master_font = "Times New Roman" if original_master_font != "Times New Roman" else "Helvetica"
        
        self.main_window.document_settings["format"]["master_font"]["family"] = new_master_font
        self.main_window.toggle_master_font(True)
        
        # Check that all font families changed but sizes remained
        all_fonts_changed = (
            self.main_window.document_settings["fonts"]["body"]["family"] == new_master_font and
            self.main_window.document_settings["fonts"]["headings"]["h1"]["family"] == new_master_font and
            self.main_window.document_settings["fonts"]["headings"]["h2"]["family"] == new_master_font
        )
        
        if all_fonts_changed:
            logger.info("✅ PASS: Master font change affects all font families")
            self.test_results.append("Master font family change: PASS")
        else:
            logger.error("❌ FAIL: Master font change did not affect all font families")
            self.test_results.append("Master font family change: FAIL")
            
    def test_heading_margins_applied(self):
        """Test that heading margins are properly applied in CSS"""
        logger.info("Testing heading margins are applied...")
        
        # Set specific margin values
        test_margins = {
            "h1": {"margin_top": 25, "margin_bottom": 12},
            "h2": {"margin_top": 18, "margin_bottom": 8},
            "h3": {"margin_top": 14, "margin_bottom": 6}
        }
        
        for heading, margins in test_margins.items():
            self.main_window.document_settings["fonts"]["headings"][heading].update(margins)
            
        # Update preview and get CSS
        self.main_window.update_preview()
        
        if hasattr(self.main_window.page_preview, 'get_heading_css'):
            heading_css = self.main_window.page_preview.get_heading_css()
            
            # Check if all margins are present
            margins_found = True
            for heading, margins in test_margins.items():
                level = heading[1]  # Extract number from h1, h2, etc.
                expected_top = f"h{level} {{" in heading_css and f"margin-top: {margins['margin_top']}pt" in heading_css
                expected_bottom = f"margin-bottom: {margins['margin_bottom']}pt" in heading_css
                
                if not (expected_top and expected_bottom):
                    margins_found = False
                    logger.error(f"Missing margins for {heading}: top={expected_top}, bottom={expected_bottom}")
                    
            if margins_found:
                logger.info("✅ PASS: All heading margins are applied in CSS")
                self.test_results.append("Heading margins applied: PASS")
            else:
                logger.error("❌ FAIL: Some heading margins are missing from CSS")
                self.test_results.append("Heading margins applied: FAIL")
        else:
            logger.error("❌ FAIL: get_heading_css method not available")
            self.test_results.append("Heading margins applied: FAIL")
            
    def finish_tests(self):
        """Finish tests and show results"""
        logger.info("=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        for result in self.test_results:
            logger.info(result)
            
        passed_tests = len([r for r in self.test_results if "PASS" in r])
        total_tests = len(self.test_results)
        
        logger.info("=" * 60)
        logger.info(f"PASSED: {passed_tests}/{total_tests} tests")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Font locking and heading spacing fixes are working correctly.")
        else:
            logger.warning(f"⚠️  {total_tests - passed_tests} tests failed. Please review the issues above.")
            
        # Close the application
        QTimer.singleShot(2000, self.app.quit)

def main():
    """Main function"""
    tester = FontAndHeadingTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
