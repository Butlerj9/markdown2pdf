# Markdown to PDF Converter - Export Verification

This script verifies that the settings used in the Markdown to PDF converter are correctly reflected in the output files.

## Features

- Tests multiple export formats (PDF, HTML, EPUB, DOCX)
- Tests multiple PDF engines (xelatex, weasyprint, wkhtmltopdf)
- Tests various settings combinations (TOC, page size, orientation)
- Provides concise output with progress tracking
- Includes per-file timeouts to prevent hanging
- Skips problematic engines after first failure
- Generates detailed test results

## Usage

### Basic Usage

Run all tests:

```
python test_export_verification.py
```

### Command Line Options

Run specific tests:

```
python test_export_verification.py --format pdf --engine xelatex --toc on
```

Available options:

- `--format`: Test only a specific format (pdf, html, epub, docx)
- `--engine`: Test only a specific PDF engine (xelatex, weasyprint, wkhtmltopdf)
- `--toc`: Test only with TOC on or off (on, off)
- `--page-size`: Test only with specific page size (A4, Letter)
- `--orientation`: Test only with specific orientation (portrait, landscape)
- `--debug`: Enable debug output for troubleshooting
- `--timeout`: Set total timeout in seconds (default: 300)

### Output

The script produces a concise output with one line per test:

```
Test #/Total (%) Format Engine     Settings             Time     Size     Status
```

Where:
- `Test #/Total (%)`: Test number, total tests, and percentage complete
- `Format`: Export format (PDF, HTML, EPUB, DOCX)
- `Engine`: PDF engine (xelatex, weasyprint, wkhtmltopdf) or N/A for non-PDF formats
- `Settings`: Brief description of the settings used
- `Time`: Time taken to export the file
- `Size`: Size of the output file
- `Status`: OK (success), WARN (warnings), or FAIL (failure)

### Test Results

The script generates the following files:

- `test_results.txt`: Detailed test results
- JSON file with all test results (path shown at the end of the test)

## Known Limitations

- PDF orientation detection is not reliable across different engines
- TOC detection in EPUB and DOCX formats is not 100% accurate
- Some JavaScript errors may appear in the console output (these can be ignored)

## Troubleshooting

If you encounter issues:

1. Run with the `--debug` flag to get more detailed output
2. Run specific tests to isolate the problem
3. Check the test results file for more information
4. Increase the timeout if tests are timing out
