# Output File Verification Plan

## Overview

This document outlines the plan for verifying that the settings used in the Markdown to PDF converter are correctly reflected in the output files. The goal is to create a comprehensive testing framework that can:

1. Generate output files with various combinations of settings
2. Record the settings used for each export
3. Analyze the actual output files to verify settings are correctly applied
4. Generate a report of any discrepancies

## Components

### 1. Settings Recorder (Implemented)

The `test_all_exports_with_settings_record.py` script has been created to:

- Run tests with various combinations of settings
- Export files in different formats (PDF, HTML, EPUB, DOCX)
- Record all settings used for each export in JSON format
- Save the output files for later analysis

The settings recorded include:
- TOC settings (include, depth, title)
- Page settings (size, orientation, margins)
- Font settings (master font, body font, heading fonts, code font)
- Format settings (technical numbering, numbering start)

### 2. File Analyzers (To Be Implemented)

We need to implement analyzers for each file format:

#### PDF Analyzer
- Use PyPDF2 or pdfminer to extract:
  - Page size and orientation
  - Font information (families, sizes)
  - Check for TOC presence and structure
  - Verify heading numbering (technical vs. standard)
  - Measure margins

#### HTML Analyzer
- Use BeautifulSoup to:
  - Parse HTML structure
  - Extract CSS styles
  - Check for TOC presence and depth
  - Verify font settings in CSS
  - Check heading numbering

#### EPUB Analyzer
- Use ebooklib to:
  - Extract EPUB content
  - Check for TOC presence and structure
  - Verify CSS styles for fonts
  - Check heading numbering

#### DOCX Analyzer
- Use python-docx to:
  - Extract document properties
  - Check page setup (size, orientation, margins)
  - Verify font settings
  - Check for TOC presence
  - Verify heading numbering

### 3. Verification Framework (To Be Implemented)

Create a verification framework that:
1. Loads the settings records from JSON files
2. Analyzes the corresponding output files
3. Compares expected settings with actual settings
4. Generates a report of discrepancies

## Implementation Plan

### Phase 1: PDF Analyzer

1. Install required libraries:
   ```
   pip install PyPDF2 pdfminer.six
   ```

2. Create `pdf_analyzer.py`:
   - Function to extract page size and orientation
   - Function to extract font information
   - Function to check for TOC presence
   - Function to verify heading numbering
   - Function to measure margins

3. Test with sample PDF files

### Phase 2: HTML Analyzer

1. Install required libraries:
   ```
   pip install beautifulsoup4 lxml
   ```

2. Create `html_analyzer.py`:
   - Function to parse HTML structure
   - Function to extract CSS styles
   - Function to check for TOC presence
   - Function to verify font settings
   - Function to check heading numbering

3. Test with sample HTML files

### Phase 3: EPUB Analyzer

1. Install required libraries:
   ```
   pip install ebooklib
   ```

2. Create `epub_analyzer.py`:
   - Function to extract EPUB content
   - Function to check for TOC presence
   - Function to verify CSS styles
   - Function to check heading numbering

3. Test with sample EPUB files

### Phase 4: DOCX Analyzer

1. Install required libraries:
   ```
   pip install python-docx
   ```

2. Create `docx_analyzer.py`:
   - Function to extract document properties
   - Function to check page setup
   - Function to verify font settings
   - Function to check for TOC presence
   - Function to verify heading numbering

3. Test with sample DOCX files

### Phase 5: Verification Framework

1. Create `verify_outputs.py`:
   - Function to load settings records
   - Function to analyze output files using the appropriate analyzer
   - Function to compare expected settings with actual settings
   - Function to generate a report of discrepancies

2. Test with the output files and settings records from `test_all_exports_with_settings_record.py`

## Sample Code Structure

```python
# verify_outputs.py

import os
import json
import argparse
from pdf_analyzer import analyze_pdf
from html_analyzer import analyze_html
from epub_analyzer import analyze_epub
from docx_analyzer import analyze_docx

def load_settings_records(records_dir):
    """Load all settings records from the records directory"""
    records = []
    for filename in os.listdir(records_dir):
        if filename.startswith("settings_record_") and filename.endswith(".json"):
            with open(os.path.join(records_dir, filename), 'r', encoding='utf-8') as f:
                record = json.load(f)
                records.append(record)
    return records

def analyze_output_file(record):
    """Analyze the output file based on its format"""
    output_file = record["output_file"]
    format_type = record["format"]
    
    if not os.path.exists(output_file):
        return {"error": f"Output file not found: {output_file}"}
    
    try:
        if format_type == "pdf":
            return analyze_pdf(output_file)
        elif format_type == "html":
            return analyze_html(output_file)
        elif format_type == "epub":
            return analyze_epub(output_file)
        elif format_type == "docx":
            return analyze_docx(output_file)
        else:
            return {"error": f"Unsupported format: {format_type}"}
    except Exception as e:
        return {"error": f"Error analyzing {format_type} file: {str(e)}"}

def compare_settings(expected, actual):
    """Compare expected settings with actual settings"""
    discrepancies = []
    
    # Compare page settings
    if expected["settings"]["page"]["size"] != actual.get("page_size"):
        discrepancies.append({
            "setting": "page_size",
            "expected": expected["settings"]["page"]["size"],
            "actual": actual.get("page_size")
        })
    
    # Compare orientation
    if expected["settings"]["page"]["orientation"] != actual.get("orientation"):
        discrepancies.append({
            "setting": "orientation",
            "expected": expected["settings"]["page"]["orientation"],
            "actual": actual.get("orientation")
        })
    
    # Compare TOC settings
    if expected["settings"]["toc"]["include"] != actual.get("has_toc", False):
        discrepancies.append({
            "setting": "toc_include",
            "expected": expected["settings"]["toc"]["include"],
            "actual": actual.get("has_toc")
        })
    
    # Compare font settings
    # ... (more detailed comparisons)
    
    return discrepancies

def main():
    parser = argparse.ArgumentParser(description='Verify output files against expected settings')
    parser.add_argument('--records-dir', required=True, help='Directory containing settings records')
    parser.add_argument('--output', help='Path to save the verification report')
    args = parser.parse_args()
    
    records = load_settings_records(args.records_dir)
    print(f"Loaded {len(records)} settings records")
    
    results = []
    for record in records:
        print(f"Analyzing {record['format']} file: {os.path.basename(record['output_file'])}")
        actual_settings = analyze_output_file(record)
        
        if "error" in actual_settings:
            results.append({
                "test_id": record["test_id"],
                "format": record["format"],
                "output_file": record["output_file"],
                "error": actual_settings["error"],
                "discrepancies": []
            })
            continue
        
        discrepancies = compare_settings(record, actual_settings)
        
        results.append({
            "test_id": record["test_id"],
            "format": record["format"],
            "output_file": record["output_file"],
            "discrepancies": discrepancies
        })
    
    # Generate summary
    total_files = len(results)
    files_with_errors = sum(1 for r in results if "error" in r)
    files_with_discrepancies = sum(1 for r in results if r["discrepancies"])
    
    print("\n===== VERIFICATION SUMMARY =====")
    print(f"Total files analyzed: {total_files}")
    print(f"Files with errors: {files_with_errors}")
    print(f"Files with discrepancies: {files_with_discrepancies}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Verification report saved to {args.output}")
    
    return 0 if files_with_errors == 0 and files_with_discrepancies == 0 else 1

if __name__ == "__main__":
    main()
```

## Required Libraries

To implement this plan, the following libraries will be needed:

```
pip install PyPDF2 pdfminer.six beautifulsoup4 lxml ebooklib python-docx
```

## Next Steps

1. Run the `test_all_exports_with_settings_record.py` script to generate output files and settings records
2. Implement the file analyzers for each format
3. Implement the verification framework
4. Run the verification and analyze the results
5. Fix any discrepancies found in the markdown to PDF converter

## Challenges and Considerations

1. **PDF Analysis**: Extracting precise font information from PDFs can be challenging, especially with embedded fonts
2. **EPUB Analysis**: EPUB files are essentially ZIP archives with HTML content, requiring careful extraction and analysis
3. **Margin Verification**: Measuring margins accurately in different formats may require format-specific approaches
4. **Font Substitution**: Some formats may substitute fonts if the specified fonts are not available
5. **Performance**: Analyzing a large number of files may be time-consuming, especially for complex PDFs

## Conclusion

This plan provides a comprehensive approach to verifying that the settings used in the Markdown to PDF converter are correctly reflected in the output files. By implementing the file analyzers and verification framework, we can systematically test the converter with multiple setting combinations and ensure that the output files align with the expected settings.
