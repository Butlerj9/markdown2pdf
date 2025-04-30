#!/usr/bin/env python3
"""
Comprehensive test script for all export formats with different settings combinations
that also records settings and output file paths for later verification
"""

import os
import sys
import tempfile
import itertools
import json
import datetime
import signal
import threading
from PyQt6.QtWidgets import QApplication

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

def timeout_handler(timeout_sec, func, *args, **kwargs):
    """
    Run a function with a timeout and forcibly terminate any hanging processes

    Args:
        timeout_sec (int): Timeout in seconds
        func (callable): Function to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        tuple: (result, timed_out)
    """
    import psutil
    import os
    import signal
    import time

    result = [None]
    timed_out = [False]
    thread_finished = [False]

    # Get current process ID
    current_pid = os.getpid()
    start_time = time.time()

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            print(f"Error in function: {str(e)}")
            result[0] = False
        finally:
            thread_finished[0] = True

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

    # Wait for thread to finish or timeout
    while not thread_finished[0] and (time.time() - start_time) < timeout_sec:
        time.sleep(0.1)

    if not thread_finished[0]:
        print(f"Operation timed out after {timeout_sec} seconds - forcibly terminating child processes")
        timed_out[0] = True

        # Find and kill any child processes that might be hanging
        try:
            parent = psutil.Process(current_pid)
            children = parent.children(recursive=True)

            for child in children:
                try:
                    print(f"Terminating child process: {child.pid}")
                    child.terminate()
                except:
                    pass

            # Give them a moment to terminate
            time.sleep(0.5)

            # Force kill any remaining processes
            for child in children:
                try:
                    if child.is_running():
                        print(f"Force killing child process: {child.pid}")
                        child.kill()
                except:
                    pass
        except Exception as e:
            print(f"Error cleaning up processes: {str(e)}")

        return False, True

    return result[0], False

def main():
    # Get timeout from environment variable or use default
    export_timeout = int(os.environ.get("TEST_TIMEOUT", "60"))
    print(f"Using export timeout: {export_timeout} seconds per operation")

    # Create QApplication
    app = QApplication(sys.argv)

    # Create a temporary directory for test outputs
    temp_dir = tempfile.mkdtemp()
    print(f"Test output directory: {temp_dir}")

    # Create a directory for the settings records
    records_dir = os.path.join(temp_dir, "settings_records")
    os.makedirs(records_dir, exist_ok=True)

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

    # Settings records
    settings_records = []

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

        # Create settings record
        settings_record = {
            "test_id": test_count,
            "format": export_format,
            "engine": window.document_settings["format"]["preferred_engine"] if export_format == "pdf" else None,
            "output_file": output_file,
            "settings": {
                "toc": {
                    "include": toc["include"],
                    "depth": toc["depth"],
                    "title": toc["title"]
                },
                "page": {
                    "size": page["size"],
                    "orientation": page["orientation"],
                    "margins": page["margins"]
                },
                "font": {
                    "use_master_font": font["use_master_font"],
                    "master_font": font["master_font"] if font["use_master_font"] else None,
                    "body_font": {
                        "family": window.document_settings["fonts"]["body"]["family"],
                        "size": window.document_settings["fonts"]["body"]["size"],
                        "line_height": window.document_settings["fonts"]["body"]["line_height"]
                    },
                    "headings": {
                        "h1": {
                            "family": window.document_settings["fonts"]["headings"]["h1"]["family"],
                            "size": window.document_settings["fonts"]["headings"]["h1"]["size"]
                        },
                        "h2": {
                            "family": window.document_settings["fonts"]["headings"]["h2"]["family"],
                            "size": window.document_settings["fonts"]["headings"]["h2"]["size"]
                        }
                    },
                    "code": {
                        "family": window.document_settings["code"]["font_family"],
                        "size": window.document_settings["code"]["font_size"]
                    }
                },
                "format": {
                    "technical_numbering": format_setting["technical_numbering"],
                    "numbering_start": format_setting["numbering_start"]
                }
            },
            "document_settings": window.document_settings,
            "result": None
        }

        # Export based on format
        result = False
        if export_format == "pdf":
            # For PDF, test with default engine first
            print(f"  Exporting PDF with default engine (timeout: {export_timeout}s)...")
            result, timed_out = timeout_handler(export_timeout, window.export_to_pdf, output_file)

            # Record result
            if result:
                results["pdf"]["success"] += 1
                print(f"  PDF export successful: {os.path.basename(output_file)}")
                settings_record["result"] = "success"
            else:
                results["pdf"]["failure"] += 1
                issue = f"PDF export failed with default engine: {settings_desc}"
                if timed_out:
                    issue = f"PDF export timed out with default engine: {settings_desc}"
                results["pdf"]["issues"].append(issue)
                print(f"  ERROR: {issue}")
                settings_record["result"] = "failure"
                settings_record["error"] = issue

            # Save settings record
            settings_record_file = os.path.join(records_dir, f"settings_record_{test_count:03d}_{export_format}.json")
            with open(settings_record_file, 'w', encoding='utf-8') as f:
                json.dump(settings_record, f, indent=2)

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

                # Create engine-specific settings record
                engine_settings_record = {
                    "test_id": test_count,
                    "format": "pdf",
                    "engine": engine,
                    "output_file": engine_output_file,
                    "settings": settings_record["settings"],
                    "document_settings": window.document_settings,
                    "result": None
                }

                # Export with this engine
                print(f"  Exporting PDF with {engine} engine (timeout: {export_timeout}s)...")
                engine_result, timed_out = timeout_handler(export_timeout, window.export_to_pdf, engine_output_file)

                # Reset the engine
                window.document_settings["format"]["preferred_engine"] = old_engine

                # Record result
                if engine_result:
                    results["pdf"]["success"] += 1
                    print(f"  PDF export with {engine} successful: {os.path.basename(engine_output_file)}")
                    engine_settings_record["result"] = "success"
                else:
                    results["pdf"]["failure"] += 1
                    issue = f"PDF export with {engine} engine failed: {settings_desc}"
                    if timed_out:
                        issue = f"PDF export with {engine} engine timed out: {settings_desc}"
                    results["pdf"]["issues"].append(issue)
                    print(f"  ERROR: {issue}")
                    engine_settings_record["result"] = "failure"
                    engine_settings_record["error"] = issue

                # Save engine-specific settings record
                engine_settings_record_file = os.path.join(records_dir, f"settings_record_{test_count:03d}_pdf_{engine}.json")
                with open(engine_settings_record_file, 'w', encoding='utf-8') as f:
                    json.dump(engine_settings_record, f, indent=2)

        elif export_format == "html":
            print(f"  Exporting HTML (timeout: {export_timeout}s)...")
            result, timed_out = timeout_handler(export_timeout, window.export_to_html, output_file)
            if result:
                results["html"]["success"] += 1
                print(f"  HTML export successful: {os.path.basename(output_file)}")
                settings_record["result"] = "success"
            else:
                results["html"]["failure"] += 1
                issue = f"HTML export failed: {settings_desc}"
                if timed_out:
                    issue = f"HTML export timed out: {settings_desc}"
                results["html"]["issues"].append(issue)
                print(f"  ERROR: {issue}")
                settings_record["result"] = "failure"
                settings_record["error"] = issue

            # Save settings record
            settings_record_file = os.path.join(records_dir, f"settings_record_{test_count:03d}_{export_format}.json")
            with open(settings_record_file, 'w', encoding='utf-8') as f:
                json.dump(settings_record, f, indent=2)

        elif export_format == "epub":
            print(f"  Exporting EPUB (timeout: {export_timeout}s)...")
            result, timed_out = timeout_handler(export_timeout, window.export_to_epub, output_file)
            if result:
                results["epub"]["success"] += 1
                print(f"  EPUB export successful: {os.path.basename(output_file)}")
                settings_record["result"] = "success"
            else:
                results["epub"]["failure"] += 1
                issue = f"EPUB export failed: {settings_desc}"
                if timed_out:
                    issue = f"EPUB export timed out: {settings_desc}"
                results["epub"]["issues"].append(issue)
                print(f"  ERROR: {issue}")
                settings_record["result"] = "failure"
                settings_record["error"] = issue

            # Save settings record
            settings_record_file = os.path.join(records_dir, f"settings_record_{test_count:03d}_{export_format}.json")
            with open(settings_record_file, 'w', encoding='utf-8') as f:
                json.dump(settings_record, f, indent=2)

        elif export_format == "docx":
            print(f"  Exporting DOCX (timeout: {export_timeout}s)...")
            result, timed_out = timeout_handler(export_timeout, window.export_to_docx, output_file)
            if result:
                results["docx"]["success"] += 1
                print(f"  DOCX export successful: {os.path.basename(output_file)}")
                settings_record["result"] = "success"
            else:
                results["docx"]["failure"] += 1
                issue = f"DOCX export failed: {settings_desc}"
                if timed_out:
                    issue = f"DOCX export timed out: {settings_desc}"
                results["docx"]["issues"].append(issue)
                print(f"  ERROR: {issue}")
                settings_record["result"] = "failure"
                settings_record["error"] = issue

            # Save settings record
            settings_record_file = os.path.join(records_dir, f"settings_record_{test_count:03d}_{export_format}.json")
            with open(settings_record_file, 'w', encoding='utf-8') as f:
                json.dump(settings_record, f, indent=2)

        # Close the window
        window.close()

        # Process events to ensure window closes
        QApplication.processEvents()

    # Save overall test results
    overall_results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "test_directory": temp_dir,
        "total_tests": total_tests,
        "results": results,
        "settings_records_directory": records_dir
    }

    overall_results_file = os.path.join(temp_dir, "test_results.json")
    with open(overall_results_file, 'w', encoding='utf-8') as f:
        json.dump(overall_results, f, indent=2)

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
    print("Settings records directory:", records_dir)
    print("Overall results file:", overall_results_file)

    # Return success if all tests passed
    return 0 if total_failure == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
