#!/usr/bin/env python3
"""
Comprehensive test script for all export formats with different settings combinations
"""

import os
import sys
import tempfile
import itertools
from PyQt6.QtWidgets import QApplication

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def main():
    # Create QApplication
    app = QApplication(sys.argv)

    # Create a temporary directory for test outputs
    temp_dir = tempfile.mkdtemp()
    print(f"Test output directory: {temp_dir}")

    # Sample markdown content for testing
    sample_markdown = """# Export Test Document

This is a test document for the Markdown to PDF converter export functionality.

## Features to Test

- PDF Export
- HTML Export
- EPUB Export
- DOCX Export
- Table of Contents
- Page Breaks
- Code Blocks
- Tables
- Images
- Math Equations

### Code Block

```python
def test_export():
    print("Testing export functionality")
```

## Table

| Feature | Status |
|---------|--------|
| PDF     | Testing |
| HTML    | Testing |
| EPUB    | Testing |
| DOCX    | Testing |

<!-- PAGE_BREAK -->

## Second Page

This content should appear on the second page.

### Subsection

This is a subsection that should appear in the TOC.

#### Sub-subsection

This is a deeper level that may or may not appear in the TOC depending on depth settings.

<!-- PAGE_BREAK -->

## Third Page

This content should appear on the third page.

### Math Equations

Inline equation: $E = mc^2$

Display equation:

$$
\\frac{d}{dx}\\left( \\int_{a}^{x} f(u)\\,du\\right)=f(x)
$$
"""

    # Define settings combinations to test
    toc_settings = [
        {"include": True, "depth": 2, "title": "Contents"},
        {"include": True, "depth": 3, "title": "Table of Contents"},
        {"include": False, "depth": 2, "title": "Contents"}
    ]

    page_settings = [
        {"size": "A4", "orientation": "portrait", "margins": {"top": 25.4, "right": 25.4, "bottom": 25.4, "left": 25.4}},
        {"size": "Letter", "orientation": "landscape", "margins": {"top": 12.7, "right": 12.7, "bottom": 12.7, "left": 12.7}}
    ]

    font_settings = [
        {"use_master_font": True, "master_font": {"family": "Arial", "size": 12}},
        {"use_master_font": False}
    ]

    format_settings = [
        {"technical_numbering": True, "numbering_start": 1},
        {"technical_numbering": False, "numbering_start": 1}
    ]

    # Export formats to test
    export_formats = ["pdf", "html", "epub", "docx"]

    # PDF engines to test
    pdf_engines = ["xelatex", "pdflatex", "wkhtmltopdf", "weasyprint"]

    # Track test results
    results = {
        "pdf": {"success": 0, "failure": 0, "issues": []},
        "html": {"success": 0, "failure": 0, "issues": []},
        "epub": {"success": 0, "failure": 0, "issues": []},
        "docx": {"success": 0, "failure": 0, "issues": []}
    }

    # Test counter
    test_count = 0
    total_tests = len(toc_settings) * len(page_settings) * len(font_settings) * len(format_settings) * len(export_formats)
    if "pdf" in export_formats:
        total_tests += len(toc_settings) * len(page_settings) * len(font_settings) * len(format_settings) * (len(pdf_engines) - 1)

    print(f"Running {total_tests} export tests...")

    # Run tests with different combinations
    for toc, page, font, format_setting, export_format in itertools.product(
        toc_settings, page_settings, font_settings, format_settings, export_formats
    ):
        # Create a fresh instance of the application for each test
        window = AdvancedMarkdownToPDF()

        # Set test environment flag to avoid style saving prompts
        window._is_test_environment = True

        # Set the sample markdown in the editor
        window.markdown_editor.setPlainText(sample_markdown)

        # Apply settings
        # TOC settings
        window.include_toc.setChecked(toc["include"])
        window.toc_depth.setValue(toc["depth"])
        window.toc_title.setText(toc["title"])

        # Page settings
        window.page_size_combo.setCurrentText(page["size"])
        window.orientation_combo.setCurrentText(page["orientation"].capitalize())
        window.margin_top.setValue(page["margins"]["top"])
        window.margin_right.setValue(page["margins"]["right"])
        window.margin_bottom.setValue(page["margins"]["bottom"])
        window.margin_left.setValue(page["margins"]["left"])

        # Font settings
        window.use_master_font.setChecked(font["use_master_font"])
        if font["use_master_font"]:
            # Set master font
            window.document_settings["format"]["master_font"]["family"] = font["master_font"]["family"]
            window.document_settings["format"]["master_font"]["size"] = font["master_font"]["size"]

        # Format settings
        window.technical_numbering.setChecked(format_setting["technical_numbering"])
        window.numbering_start.setCurrentIndex(format_setting["numbering_start"] - 1)

        # Update the preview
        window.update_preview()

        # Process events to ensure UI updates
        QApplication.processEvents()

        # Test export
        test_count += 1
        print(f"\nTest {test_count}/{total_tests}:")
        print(f"  Format: {export_format.upper()}")
        print(f"  TOC: {'Enabled' if toc['include'] else 'Disabled'}, Depth: {toc['depth']}")
        print(f"  Page: {page['size']} {page['orientation']}")
        print(f"  Font: {'Master font' if font['use_master_font'] else 'Individual fonts'}")
        print(f"  Numbering: {'Technical' if format_setting['technical_numbering'] else 'Standard'}")

        # Define output file
        settings_desc = f"toc{'on' if toc['include'] else 'off'}_depth{toc['depth']}_page{page['size']}_{page['orientation']}_font{'master' if font['use_master_font'] else 'individual'}_numbering{'tech' if format_setting['technical_numbering'] else 'std'}"
        output_file = os.path.join(temp_dir, f"test_export_{export_format}_{settings_desc}.{export_format}")

        # Export based on format
        result = False
        if export_format == "pdf":
            # For PDF, test with default engine first
            result = window.export_to_pdf(output_file)

            # Record result
            if result:
                results["pdf"]["success"] += 1
                print(f"  PDF export successful: {os.path.basename(output_file)}")
            else:
                results["pdf"]["failure"] += 1
                issue = f"PDF export failed with default engine: {settings_desc}"
                results["pdf"]["issues"].append(issue)
                print(f"  ERROR: {issue}")

            # Test with specific engines
            for engine in pdf_engines:
                if engine == window.document_settings["format"]["preferred_engine"]:
                    continue  # Skip the default engine as we already tested it

                test_count += 1
                engine_output_file = os.path.join(temp_dir, f"test_export_pdf_{engine}_{settings_desc}.pdf")
                print(f"\nTest {test_count}/{total_tests}:")
                print(f"  Format: PDF with {engine} engine")
                print(f"  TOC: {'Enabled' if toc['include'] else 'Disabled'}, Depth: {toc['depth']}")
                print(f"  Page: {page['size']} {page['orientation']}")
                print(f"  Font: {'Master font' if font['use_master_font'] else 'Individual fonts'}")
                print(f"  Numbering: {'Technical' if format_setting['technical_numbering'] else 'Standard'}")

                # Set the engine
                old_engine = window.document_settings["format"]["preferred_engine"]
                window.document_settings["format"]["preferred_engine"] = engine

                # Export with this engine
                engine_result = window.export_to_pdf(engine_output_file)

                # Reset the engine
                window.document_settings["format"]["preferred_engine"] = old_engine

                # Record result
                if engine_result:
                    results["pdf"]["success"] += 1
                    print(f"  PDF export with {engine} successful: {os.path.basename(engine_output_file)}")
                else:
                    results["pdf"]["failure"] += 1
                    issue = f"PDF export with {engine} engine failed: {settings_desc}"
                    results["pdf"]["issues"].append(issue)
                    print(f"  ERROR: {issue}")

        elif export_format == "html":
            result = window.export_to_html(output_file)
            if result:
                results["html"]["success"] += 1
                print(f"  HTML export successful: {os.path.basename(output_file)}")
            else:
                results["html"]["failure"] += 1
                issue = f"HTML export failed: {settings_desc}"
                results["html"]["issues"].append(issue)
                print(f"  ERROR: {issue}")

        elif export_format == "epub":
            result = window.export_to_epub(output_file)
            if result:
                results["epub"]["success"] += 1
                print(f"  EPUB export successful: {os.path.basename(output_file)}")
            else:
                results["epub"]["failure"] += 1
                issue = f"EPUB export failed: {settings_desc}"
                results["epub"]["issues"].append(issue)
                print(f"  ERROR: {issue}")

        elif export_format == "docx":
            result = window.export_to_docx(output_file)
            if result:
                results["docx"]["success"] += 1
                print(f"  DOCX export successful: {os.path.basename(output_file)}")
            else:
                results["docx"]["failure"] += 1
                issue = f"DOCX export failed: {settings_desc}"
                results["docx"]["issues"].append(issue)
                print(f"  ERROR: {issue}")

        # Close the window
        window.close()

        # Process events to ensure window closes
        QApplication.processEvents()

    # Print summary
    print("\n" + "="*50)
    print("EXPORT TEST SUMMARY")
    print("="*50)

    total_success = sum(format_results["success"] for format_results in results.values())
    total_failure = sum(format_results["failure"] for format_results in results.values())

    print(f"Total tests: {total_success + total_failure}")
    print(f"Successful: {total_success}")
    print(f"Failed: {total_failure}")
    print("\nResults by format:")

    for format_name, format_results in results.items():
        print(f"\n{format_name.upper()}:")
        print(f"  Success: {format_results['success']}")
        print(f"  Failure: {format_results['failure']}")

        if format_results["issues"]:
            print("\n  Issues:")
            for i, issue in enumerate(format_results["issues"], 1):
                print(f"    {i}. {issue}")

    print("\nTest output directory:", temp_dir)

    # Return success if all tests passed
    return 0 if total_failure == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
