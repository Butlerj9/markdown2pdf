# Visual Testing Framework for Markdown to PDF Converter

This framework provides automated visual testing capabilities for the Markdown to PDF Converter application. It allows you to:

1. Take screenshots of the application
2. Compare screenshots against reference images
3. Highlight visual differences
4. Automate UI interactions for testing

## Requirements

The visual testing framework requires the following dependencies:

```
PyQt6>=6.4.0
PyQt6-WebEngine>=6.4.0
Pillow>=9.3.0
numpy>=1.23.0
pyautogui>=0.9.53
```

You can install these dependencies using pip:

```
pip install -r requirements.txt
```

## Using the Visual Testing Framework

### From the Test Dialog

1. Open the application
2. Go to Tools > Run Tests
3. Select the "Visual Tests" tab
4. Select the tests you want to run
5. Choose whether to create reference screenshots or compare with existing ones
6. Click "Run Selected Visual Tests"
7. View the results in the list
8. Click "View Screenshots" to open the screenshots directory

### Programmatically

```python
from visual_test import VisualTester
from PyQt6.QtWidgets import QApplication

# Create a tester instance
app = QApplication.instance() or QApplication([])
tester = VisualTester(app)

# Start a test
tester.start_test("my_test")

# Take a screenshot
screenshot_path = tester.take_screenshot("my_screenshot")

# Create a reference screenshot
reference_path = tester.create_reference("my_reference")

# Compare screenshots
diff_percentage, diff_path = tester.compare_screenshots(reference_path, screenshot_path)

# Find and click on UI elements
tester.click_element("path/to/button_image.png")

# Type text
tester.type_text("Hello, world!")

# End the test
tester.end_test()
```

## Available Visual Tests

The framework includes the following built-in tests:

1. **Basic UI** - Tests the basic UI elements of the application
2. **Heading Numbering** - Tests the heading numbering functionality
3. **Page Breaks** - Tests the page break functionality
4. **Edit Toolbar** - Tests the edit toolbar functionality

## Creating Custom Visual Tests

You can create custom visual tests by adding new test functions to the `visual_test_runner.py` file. Each test function should:

1. Create a `VisualTestRunner` instance
2. Define a test function that performs the test steps
3. Add the test to the runner
4. Run the tests

Example:

```python
def test_my_custom_test():
    """Test my custom functionality"""
    runner = VisualTestRunner()
    
    def test_func():
        # Set up test content
        test_content = "# My Test Content"
        
        # Set the content in the editor
        runner.main_window.markdown_editor.setPlainText(test_content)
        
        # Update the preview
        runner.main_window.update_preview()
        QTest.qWait(1000)
        
        # Take a screenshot
        runner.tester.take_screenshot("my_custom_test")
        
        # Verify against reference if it exists
        runner.tester.verify_against_reference("my_custom_test")
        
        # End the test
        runner.tester.end_test()
    
    runner.add_test(test_func, "my_custom_test")
    runner.run_tests()
```

## Reference Screenshots

Reference screenshots are stored in the `test_references` directory at the project root. When you run a test with the "Create reference screenshots" option checked, new reference screenshots will be created or existing ones will be overwritten.

## Troubleshooting

### Element Not Found

If the framework cannot find an element on the screen:

1. Check that the element is visible and not obscured
2. Try decreasing the confidence level (e.g., `confidence=0.7`)
3. Make sure the reference image is clear and distinctive

### High Difference Percentage

If the comparison shows a high difference percentage:

1. Check for dynamic content that may change between runs
2. Ensure consistent window size and positioning
3. Try increasing the threshold for acceptable differences

### Other Issues

- Make sure the application is in focus when taking screenshots
- Allow sufficient time for UI updates before taking screenshots
- Check that all dependencies are installed correctly
