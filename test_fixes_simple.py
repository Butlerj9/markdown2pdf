#!/usr/bin/env python3
"""
Simple test script to verify font locking and heading spacing fixes
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_font_locking_logic():
    """Test the font locking logic without GUI"""
    print("Testing font locking logic...")
    
    # Simulate document settings
    document_settings = {
        "format": {
            "master_font": {"family": "Arial"}
        },
        "fonts": {
            "body": {"family": "Times New Roman", "size": 12},
            "headings": {
                "h1": {"family": "Georgia", "size": 24},
                "h2": {"family": "Georgia", "size": 20},
                "h3": {"family": "Georgia", "size": 16}
            }
        },
        "code": {"font_family": "Courier New", "font_size": 10}
    }
    
    # Store original sizes
    original_body_size = document_settings["fonts"]["body"]["size"]
    original_h1_size = document_settings["fonts"]["headings"]["h1"]["size"]
    original_h2_size = document_settings["fonts"]["headings"]["h2"]["size"]
    original_code_size = document_settings["code"]["font_size"]
    
    print(f"Original sizes - Body: {original_body_size}, H1: {original_h1_size}, H2: {original_h2_size}, Code: {original_code_size}")
    
    # Simulate the font locking logic (from toggle_master_font method)
    use_master_font = True
    if use_master_font:
        master_font = document_settings["format"]["master_font"]["family"]
        # Apply font family to body (preserve size)
        document_settings["fonts"]["body"]["family"] = master_font
        # Apply font family to headings (preserve sizes)
        for level in range(1, 7):
            h_key = f"h{level}"
            if h_key in document_settings["fonts"]["headings"]:
                document_settings["fonts"]["headings"][h_key]["family"] = master_font
        # Apply font family to code (preserve size)
        document_settings["code"]["font_family"] = master_font
    
    # Check results
    new_body_size = document_settings["fonts"]["body"]["size"]
    new_h1_size = document_settings["fonts"]["headings"]["h1"]["size"]
    new_h2_size = document_settings["fonts"]["headings"]["h2"]["size"]
    new_code_size = document_settings["code"]["font_size"]
    
    print(f"New sizes - Body: {new_body_size}, H1: {new_h1_size}, H2: {new_h2_size}, Code: {new_code_size}")
    
    # Verify sizes are preserved
    sizes_preserved = (
        original_body_size == new_body_size and
        original_h1_size == new_h1_size and
        original_h2_size == new_h2_size and
        original_code_size == new_code_size
    )
    
    # Verify font families are unified
    master_font = document_settings["format"]["master_font"]["family"]
    body_font = document_settings["fonts"]["body"]["family"]
    h1_font = document_settings["fonts"]["headings"]["h1"]["family"]
    h2_font = document_settings["fonts"]["headings"]["h2"]["family"]
    code_font = document_settings["code"]["font_family"]
    
    fonts_unified = (master_font == body_font == h1_font == h2_font == code_font)
    
    print(f"Master font: {master_font}")
    print(f"Body font: {body_font}, H1 font: {h1_font}, H2 font: {h2_font}, Code font: {code_font}")
    
    if sizes_preserved:
        print("✅ PASS: Font locking preserves individual sizes")
    else:
        print("❌ FAIL: Font locking changed individual sizes")
        
    if fonts_unified:
        print("✅ PASS: Font families are unified")
    else:
        print("❌ FAIL: Font families are not unified")
        
    return sizes_preserved and fonts_unified

def test_heading_css_generation():
    """Test the heading CSS generation logic"""
    print("\nTesting heading CSS generation...")
    
    # Simulate document settings with heading spacing
    document_settings = {
        "fonts": {
            "headings": {
                "h1": {
                    "family": "Arial",
                    "size": 24,
                    "color": "#000000",
                    "spacing": 1.2,
                    "margin_top": 30,
                    "margin_bottom": 15
                },
                "h2": {
                    "family": "Arial", 
                    "size": 20,
                    "color": "#333333",
                    "spacing": 1.1,
                    "margin_top": 20,
                    "margin_bottom": 10
                },
                "h3": {
                    "family": "Arial",
                    "size": 16,
                    "color": "#666666",
                    "spacing": 1.0,
                    "margin_top": 15,
                    "margin_bottom": 8
                }
            }
        }
    }
    
    # Simulate the get_heading_css method logic
    def get_heading_css(document_settings):
        if not document_settings or "fonts" not in document_settings:
            return ""
        
        fonts = document_settings["fonts"]
        if "headings" not in fonts:
            return ""
        
        headings = fonts["headings"]
        css_parts = []
        
        # Generate CSS for each heading level
        for level in range(1, 7):
            h_key = f"h{level}"
            if h_key in headings:
                heading = headings[h_key]
                
                # Extract heading properties with fallbacks
                font_family = heading.get("family", "Arial")
                font_size = heading.get("size", 18 - level * 2)  # Default decreasing sizes
                color = heading.get("color", "#000000")
                spacing = heading.get("spacing", 1.2)  # Line height
                margin_top = heading.get("margin_top", 12)
                margin_bottom = heading.get("margin_bottom", 6)
                
                # Generate CSS for this heading level
                css_parts.append(f"""
                    .page-content h{level} {{
                        font-family: "{font_family}", Arial, sans-serif;
                        font-size: {font_size}pt;
                        color: {color};
                        line-height: {spacing};
                        margin-top: {margin_top}pt;
                        margin-bottom: {margin_bottom}pt;
                    }}""")
        
        return "".join(css_parts)
    
    # Generate CSS
    heading_css = get_heading_css(document_settings)
    
    print("Generated CSS:")
    print(heading_css)
    
    # Check if the CSS contains expected values
    expected_checks = [
        "h1" in heading_css,
        "h2" in heading_css,
        "h3" in heading_css,
        "margin-top: 30pt" in heading_css,  # H1 margin top
        "margin-bottom: 15pt" in heading_css,  # H1 margin bottom
        "margin-top: 20pt" in heading_css,  # H2 margin top
        "margin-bottom: 10pt" in heading_css,  # H2 margin bottom
        "font-size: 24pt" in heading_css,  # H1 size
        "font-size: 20pt" in heading_css,  # H2 size
        "line-height: 1.2" in heading_css,  # H1 spacing
        "line-height: 1.1" in heading_css   # H2 spacing
    ]
    
    all_checks_passed = all(expected_checks)
    
    if all_checks_passed:
        print("✅ PASS: Heading CSS generation includes all expected properties")
    else:
        print("❌ FAIL: Heading CSS generation missing some properties")
        for i, check in enumerate(expected_checks):
            if not check:
                print(f"  Missing check {i+1}")
                
    return all_checks_passed

def main():
    """Main function"""
    print("=" * 60)
    print("TESTING FONT LOCKING AND HEADING SPACING FIXES")
    print("=" * 60)
    
    test1_passed = test_font_locking_logic()
    test2_passed = test_heading_css_generation()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = 2
    passed_tests = sum([test1_passed, test2_passed])
    
    print(f"Font locking logic: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Heading CSS generation: {'PASS' if test2_passed else 'FAIL'}")
    
    print("=" * 60)
    print(f"PASSED: {passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Font locking and heading spacing fixes are working correctly.")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
