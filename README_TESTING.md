# Testing Framework for Markdown to PDF Converter

This document describes the testing framework for the Markdown to PDF Converter application. The framework includes unit tests, functional tests, and visual tests to ensure the application works correctly.

## Test Types

### Unit Tests

Unit tests verify that individual components of the application work correctly in isolation. These tests focus on specific functionality and are designed to be fast and reliable.

### Functional Tests

Functional tests verify that the application works correctly as a whole. These tests focus on user workflows and interactions between different components.

### Visual Tests

Visual tests verify that the application's user interface looks correct. These tests take screenshots of the application and compare them to reference screenshots.

## Running Tests

### Using the Test Dialog

The easiest way to run tests is to use the built-in test dialog:

1. Open the application
2. Go to Tools > Run Tests
3. Select the tests you want to run
4. Click "Run Selected Tests" or "Run All Tests"

### Using the Command Line

You can also run tests from the command line using the `run_tests.py` script:

```bash
# Run all tests
python run_tests.py --all

# Run only unit tests
python run_tests.py --unit

# Run only export tests
python run_tests.py --export

# Run only settings tests
python run_tests.py --settings

# Run only visual tests
python run_tests.py --visual

# Run tests with verbose output
python run_tests.py --verbose

# Create reference screenshots for visual tests
python run_tests.py --visual --create-reference
```

## Test Files

- `test_framework.py`: Main test framework implementation
- `unit_tests.py`: Unit tests for the application
- `export_tests.py`: Specific tests for export functionality
- `settings_tests.py`: Specific tests for settings functionality
- `visual_test.py`: Visual testing framework
- `visual_test_runner.py`: Runner for visual tests
- `run_tests.py`: Command-line interface for running tests

## Adding New Tests

### Adding Unit Tests

To add a new unit test:

1. Open the appropriate test file (`unit_tests.py`, `export_tests.py`, or `settings_tests.py`)
2. Add a new test method to the appropriate test class
3. The method name should start with `test_`
4. Use assertions to verify that the code works correctly

Example:

```python
def test_new_feature(self):
    """Test a new feature"""
    # Set up test
    self.window.some_setting = "test value"
    
    # Call the method being tested
    result = self.window.some_method()
    
    # Verify the result
    self.assertTrue(result, "Method should return True")
    self.assertEqual(self.window.some_property, "expected value", "Property should be updated")
```

### Adding Visual Tests

To add a new visual test:

1. Open `visual_test_runner.py`
2. Add a new test function
3. Use the `VisualTester` class to take screenshots and compare them to reference screenshots

Example:

```python
def test_new_feature():
    """Test a new feature visually"""
    runner = VisualTestRunner()
    
    def test_func():
        # Set up test content
        test_content = """# Test Content"""
        runner.main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        runner.main_window.update_preview()
        QTest.qWait(1000)
        
        # Take a screenshot
        runner.tester.take_screenshot("new_feature")
        
        # Verify against reference if it exists
        runner.tester.verify_against_reference("new_feature")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "new_feature")
    runner.run_tests()
```

## Troubleshooting

### Tests Fail with "No parent application available"

This error occurs when a test tries to access the parent application but it's not available. Make sure you're running the tests from the test dialog or using the `run_tests.py` script.

### Visual Tests Fail with "Reference image not found"

This error occurs when a visual test tries to compare a screenshot to a reference screenshot, but the reference doesn't exist. Run the test with the `--create-reference` flag to create the reference screenshot.

### Tests Hang or Crash

If tests hang or crash, try running them with the `--verbose` flag to get more information about what's happening. You can also try running individual tests instead of all tests at once.

## Best Practices

1. **Write focused tests**: Each test should focus on a specific piece of functionality.
2. **Use descriptive names**: Test names should describe what they're testing.
3. **Clean up after tests**: Make sure tests clean up any resources they use.
4. **Don't rely on test order**: Tests should be independent and not rely on the order they're run in.
5. **Test edge cases**: Make sure to test edge cases and error conditions, not just the happy path.
6. **Keep tests fast**: Tests should run quickly to encourage frequent testing.
7. **Use assertions effectively**: Use the most specific assertion for each check.
