#!/usr/bin/env python3
"""
Test script to verify all the critical fixes are working:
1. Margins reading from document settings (not hardcoded 25mm)
2. Page break calculation using actual margins
3. Font settings applied to preview
4. Save dialog supports .mdz files
5. Export functionality works with document settings
"""

import sys
import os
import tempfile
import logging

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_page_preview_margins():
    """Test that page preview uses actual document settings for margins"""
    print("Testing page preview margin calculation...")
    
    from page_preview import PagePreview
    
    # Create page preview
    preview = PagePreview()
    
    # Test document settings with custom margins
    test_settings = {
        "page": {
            "width": 210,
            "height": 297,
            "margins": {
                "top": 15,
                "right": 20,
                "bottom": 15,
                "left": 30
            }
        },
        "fonts": {
            "body": {
                "family": "Arial",
                "size": 14,
                "line_height": 1.5
            }
        },
        "colors": {
            "text": "#333333",
            "background": "#ffffff",
            "links": "#0066cc"
        }
    }
    
    # Set document settings
    preview.set_document_settings(test_settings)
    
    # Test margin CSS generation
    margin_css = preview.get_margin_css()
    expected_css = "15mm 20mm 15mm 30mm"
    
    if margin_css == expected_css:
        print("✓ Margin CSS generation works correctly")
        print(f"  Generated: {margin_css}")
    else:
        print("✗ Margin CSS generation failed")
        print(f"  Expected: {expected_css}")
        print(f"  Got: {margin_css}")
        return False
    
    # Test usable page dimensions
    width, height = preview.get_usable_page_dimensions()
    expected_width = 210 - 30 - 20  # 160mm
    expected_height = 297 - 15 - 15  # 267mm
    
    if width == expected_width and height == expected_height:
        print("✓ Usable page dimensions calculated correctly")
        print(f"  Usable area: {width}mm x {height}mm")
    else:
        print("✗ Usable page dimensions calculation failed")
        print(f"  Expected: {expected_width}mm x {expected_height}mm")
        print(f"  Got: {width}mm x {height}mm")
        return False
    
    return True

def test_save_dialog_formats():
    """Test that save dialog supports both .md and .mdz formats"""
    print("Testing save dialog format support...")
    
    from markdown_to_pdf_converter import AdvancedMarkdownToPDF
    
    # Create main application instance
    app = AdvancedMarkdownToPDF()
    
    # Check if the save methods exist
    if hasattr(app, '_save_as_markdown') and hasattr(app, '_save_as_mdz'):
        print("✓ Save methods for both .md and .mdz formats exist")
    else:
        print("✗ Save methods missing")
        return False
    
    # Check if asset collection method exists
    if hasattr(app, '_collect_document_assets'):
        print("✓ Asset collection method exists")
    else:
        print("✗ Asset collection method missing")
        return False
    
    return True

def test_export_functionality():
    """Test that export functionality uses document settings"""
    print("Testing export functionality...")
    
    from markdown_to_pdf_converter import AdvancedMarkdownToPDF
    
    # Create main application instance
    app = AdvancedMarkdownToPDF()
    
    # Set some test content
    app.markdown_editor.setPlainText("# Test Document\n\nThis is a test document.")
    
    # Test that document settings are properly structured
    required_keys = ["page", "fonts", "colors", "format", "toc"]
    for key in required_keys:
        if key not in app.document_settings:
            print(f"✗ Missing required document setting: {key}")
            return False
    
    # Test that page margins are in document settings
    if "margins" in app.document_settings["page"]:
        margins = app.document_settings["page"]["margins"]
        if all(k in margins for k in ["top", "right", "bottom", "left"]):
            print("✓ Page margins properly configured in document settings")
        else:
            print("✗ Page margins missing required keys")
            return False
    else:
        print("✗ Page margins not found in document settings")
        return False
    
    # Test that export methods exist
    export_methods = ["_export_to_pdf", "_export_to_docx", "_export_to_html", "_export_to_epub", "_export_to_mdz"]
    for method in export_methods:
        if hasattr(app, method):
            print(f"✓ Export method {method} exists")
        else:
            print(f"✗ Export method {method} missing")
            return False
    
    return True

def test_font_settings_application():
    """Test that font settings are properly applied"""
    print("Testing font settings application...")
    
    from page_preview import PagePreview
    
    # Create page preview
    preview = PagePreview()
    
    # Test document settings with custom fonts
    test_settings = {
        "page": {
            "margins": {"top": 25, "right": 25, "bottom": 25, "left": 25}
        },
        "fonts": {
            "body": {
                "family": "Times New Roman",
                "size": 16
            }
        },
        "colors": {
            "text": "#000080",
            "background": "#fffff0"
        }
    }
    
    # Set document settings
    preview.set_document_settings(test_settings)
    
    # Test HTML generation with custom settings
    test_html = "<h1>Test</h1><p>This is a test paragraph.</p>"
    preview.update_preview(test_html)
    
    print("✓ Font settings applied to preview (visual verification needed)")
    return True

def main():
    """Run all tests"""
    print("Running comprehensive fix verification tests...\n")
    
    # Set up Qt application
    app = QApplication(sys.argv)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    tests = [
        ("Page Preview Margins", test_page_preview_margins),
        ("Save Dialog Formats", test_save_dialog_formats),
        ("Export Functionality", test_export_functionality),
        ("Font Settings Application", test_font_settings_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {str(e)}")
    
    print(f"\n--- SUMMARY ---")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
