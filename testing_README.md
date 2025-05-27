# Markdown to PDF Converter Testing Framework

This testing framework provides comprehensive testing for the Markdown to PDF Converter application, including the MDZ format support, page preview functionality, and core functionality.

## Test Categories

The testing framework is organized into the following categories:

1. **Core Functionality Tests**: Tests for basic operations of the application
2. **Page Preview Tests**: Tests for the page preview functionality
3. **MDZ Format Tests**: Tests for the MDZ format support

## Running Tests

### Running All Tests

To run all tests, use the `run_all_tests.py` script:

```bash
python run_all_tests.py
```

### Running Tests by Category

To run tests for a specific category, use the `--category` option:

```bash
python run_all_tests.py --category core
python run_all_tests.py --category page_preview
python run_all_tests.py --category mdz
```

### Setting Test Timeout

To set a custom timeout for tests, use the `--timeout` option (in seconds):

```bash
python run_all_tests.py --timeout 300
```

## Test Files

### Core Functionality Tests

- `test_core_functionality.py`: Tests for basic operations of the application

### Page Preview Tests

- `test_page_preview_breaks.py`: Tests for page breaks in the page preview
- `test_page_preview_comprehensive.py`: Comprehensive tests for the page preview functionality

### MDZ Format Tests

- `test_mdz_export_integration.py`: Tests for MDZ export integration with the main application
- `test_mdz_comprehensive.py`: Comprehensive tests for the MDZ format support

## Test Results

Test results are saved in the `test_results` directory with a timestamp in the filename. Each result file contains:

- Test name
- Test status (PASS/FAIL)
- Execution time
- Standard output
- Standard error
- Summary of all tests

## Adding New Tests

To add a new test, create a new Python file with the test code and add it to the appropriate category in the `TEST_CATEGORIES` dictionary in `run_all_tests.py`.

## Test Requirements

The testing framework requires the following dependencies:

- Python 3.6 or higher
- PyQt6
- Zstandard
- PyYAML
- Pandoc (for Markdown processing)

## Troubleshooting

If a test fails, check the test results file for detailed information about the failure. The test results include the standard output and standard error from the test, which can help identify the cause of the failure.

## Manual Testing

While the automated tests cover a significant portion of the application's functionality, some aspects require manual testing. See the `test_report.md` file for details on what should be tested manually.
