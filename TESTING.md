# Markdown to PDF Converter Testing Framework

This document describes the comprehensive testing framework for the Markdown to PDF Converter application, including test files, test procedures, test categories, and how to run the tests.

## Overview

The testing framework consists of several components:

1. **Test Files**: A set of Markdown files that test different features of the converter
2. **Test Scripts**: Various test scripts for different aspects of the application
3. **Test Runners**: Scripts that run tests and collect results
4. **Unit Tests**: Tests for individual components and functions
5. **Integration Tests**: Tests for interactions between components
6. **Visual Tests**: Tests for the visual appearance of the output
7. **Performance Tests**: Tests for the performance of the application

## Test Files

The test files are located in the `test_files` directory and include:

| File | Description |
|------|-------------|
| `basic_test.md` | Tests basic Markdown features (headers, lists, tables, code blocks) |
| `mermaid_test.md` | Tests Mermaid diagram rendering |
| `latex_math_test.md` | Tests LaTeX math rendering |
| `svg_test.md` | Tests SVG embedding |
| `multi_page_test.md` | Tests multi-page documents and page navigation |
| `combined_features_test.md` | Tests a combination of all features |

## Test Scripts

The testing framework includes several test scripts for different aspects of the application:

| Script | Description |
|--------|-------------|
| `test_page_preview.py` | Tests the page preview functionality |
| `test_page_preview_breaks.py` | Tests page breaks in the page preview |
| `test_page_preview_comprehensive.py` | Comprehensive tests for the page preview |
| `test_js_syntax_and_page_numbers.py` | Tests JavaScript syntax and page number functionality |
| `test_page_navigation_and_export.py` | Tests page navigation and export functionality |
| `test_mdz_format.py` | Tests the MDZ format implementation |
| `test_mdz_export_integration.py` | Tests MDZ export integration |
| `test_mdz_comprehensive.py` | Comprehensive tests for the MDZ format |
| `test_core_functionality.py` | Tests core functionality of the converter |
| `unit_tests.py` | Unit tests for individual components |
| `test_export_fix.py` | Tests for export fixes |
| `test_docx_export.py` | Tests for DOCX export functionality |
| `test_epub_export.py` | Tests for EPUB export functionality |
| `test_pdf_export.py` | Tests for PDF export functionality |
| `test_js_errors.py` | Tests for JavaScript error handling |
| `test_content_processing.py` | Tests for content processing functionality |

## Test Categories

The tests are organized into the following categories:

| Category | Description | Test Scripts |
|----------|-------------|--------------|
| `core` | Core functionality tests | `test_core_functionality.py` |
| `page_preview` | Page preview tests | `test_page_preview_breaks.py`, `test_page_preview_comprehensive.py`, `test_js_syntax_and_page_numbers.py`, `test_page_navigation_and_export.py` |
| `mdz` | MDZ format tests | `test_mdz_export_integration.py`, `test_mdz_comprehensive.py` |
| `js` | JavaScript tests | `test_js_syntax_and_page_numbers.py`, `test_js_errors.py` |
| `navigation` | Page navigation tests | `test_page_navigation_and_export.py` |
| `export` | Export functionality tests | `test_page_navigation_and_export.py`, `test_export_fix.py`, `test_docx_export.py`, `test_epub_export.py`, `test_pdf_export.py` |
| `test_mode` | Test mode tests | `test_test_mode.py` |
| `unit` | Unit tests | `unit_tests.py` |
| `content` | Content processing tests | `test_content_processing.py` |
| `all` | All tests | All of the above |

## Test Runners

The testing framework includes several test runners:

| Runner | Description |
|--------|-------------|
| `test_runner.py` | Main test runner with support for individual tests and categories |
| `run_all_tests.py` | Runs all tests and saves results to the `test_results` directory |
| `run_all_tests_with_report.py` | Runs all tests and generates a comprehensive report |
| `unit_test_runner.py` | Runs unit tests with a graphical interface |
| `visual_test_runner.py` | Runs visual tests for UI components |

## Running Tests

### Main Test Runner

The `test_runner.py` script is the most flexible way to run tests. It supports running individual tests, test categories, or all tests.

#### Running All Tests

```bash
python test_runner.py
```

This will run all tests and save the results to the `test_results` directory.

#### Running a Specific Test

```bash
python test_runner.py --test PagePreview.basic
```

This will run the basic page preview test.

#### Running a Test with a Specific File

```bash
python test_runner.py --file test_files/basic_test.md --format pdf
```

This will run a conversion test on the specified file with the specified format.

#### Command Line Options

| Option | Description |
|--------|-------------|
| `--test` | Run a specific test (e.g., 'PagePreview.basic') |
| `--file` | Test a specific file |
| `--format` | Output format for conversion tests (pdf, html, docx, mdz) |
| `--timeout` | Test timeout in seconds (default: 30) |
| `--output-dir` | Output directory for test results (default: test_results) |

### Comprehensive Test Runner

The `run_all_tests.py` script is designed to run tests by category or all tests at once.

#### Running All Tests

```bash
python run_all_tests.py
```

This will run all tests and save the results to the `test_results` directory.

#### Running Tests by Category

```bash
python run_all_tests.py --category page_preview
```

This will run all tests in the `page_preview` category.

#### Command Line Options

| Option | Description |
|--------|-------------|
| `--category` | Test category to run (core, page_preview, mdz, js, navigation, export, test_mode, unit, content, all) |
| `--timeout` | Timeout for each test in seconds (default: 120) |

### Test Runner with Report

The `run_all_tests_with_report.py` script runs tests and generates a comprehensive report.

```bash
python run_all_tests_with_report.py --category export
```

This will run all export tests and generate a detailed report.

### Unit Test Runner

The `unit_test_runner.py` script provides a graphical interface for running unit tests.

```bash
python unit_test_runner.py
```

This will open a dialog where you can select and run unit tests.

### Visual Test Runner

The `visual_test_runner.py` script runs visual tests for UI components.

```bash
python visual_test_runner.py
```

This will run visual tests and generate screenshots for comparison.

## Test Results

Test results are saved in the following formats:

1. **Text Files**: Plain text files with test results in the `test_results` directory
2. **JSON Files**: Structured test results for programmatic analysis
3. **HTML Reports**: Visual reports with test results and statistics
4. **Log Files**: Detailed logs of test execution

Each result includes:

- Test name
- Pass/fail status
- Standard output and error
- Test duration
- Timestamp
- Error details (if applicable)

## Timeout Handling

All tests have a timeout to prevent them from hanging. The default timeout is 120 seconds, but it can be changed using the `--timeout` option.

If a test times out, it will be marked as failed and the process will be terminated.

## Dialog Handling

The test framework automatically closes any dialogs that appear during testing to prevent the tests from hanging. This is done by:

1. Setting a timeout for each test
2. Monitoring for dialog windows
3. Automatically closing any dialogs that appear

The dialog handling is implemented in the `dialog_handler.py` module, which provides functions to detect and close dialogs.

## Logging

The test framework logs all test activities to both the console and a log file. The log file is created in the current directory with a timestamp in the filename.

## Code Coverage

The test framework includes code coverage reporting to identify untested code. To run tests with code coverage:

```bash
python test_runner.py --coverage
```

This will generate a coverage report in the `coverage` directory.

## Adding New Tests

### Adding a New Test File

1. Create a new Markdown file in the `test_files` directory
2. Use the file in your test scripts

### Adding a New Test Script

1. Create a new test script file (e.g., `test_new_feature.py`)
2. Add the script to the appropriate category in the `TEST_CATEGORIES` dictionary in `run_all_tests.py`

### Adding a New Unit Test

1. Add a new test class or test method to `unit_tests.py`
2. Run the unit tests to verify the new test

## Troubleshooting

### Tests Hanging

If tests are hanging, check:

1. Dialog boxes that might be waiting for user input
2. Infinite loops in the code
3. Network requests that are not completing

The test framework includes timeout handling to prevent tests from hanging indefinitely, but it's still important to identify and fix the root cause of any hanging tests.

### Tests Failing

If tests are failing, check:

1. The log file for error messages
2. The test results file for details
3. The code being tested for bugs

Common issues include:

- JavaScript syntax errors in the page preview
- Page navigation not working correctly
- Export functionality not working correctly
- MDZ format implementation issues

## Performance Testing

The test framework includes performance testing to measure the execution time of different operations. To run performance tests:

```bash
python test_runner.py --performance
```

This will run performance tests and generate a report with execution times.

## Regression Testing

The test framework includes regression testing to ensure that new changes don't break existing functionality. To run regression tests:

```bash
python test_runner.py --regression
```

This will run regression tests and compare the results with previous runs.

## Continuous Integration

The test framework is designed to work with continuous integration systems. The tests can be run automatically on each commit or pull request.

## Future Improvements

- Add more test files for edge cases
- Enhance performance tests with benchmarks
- Add stress tests for large documents
- Add integration tests with editors (VSCode, Obsidian)
- Improve automated UI tests
- Enhance code coverage reporting
- Add mutation testing
- Add property-based testing
