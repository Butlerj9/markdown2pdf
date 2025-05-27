#!/usr/bin/env python3
"""
Test Content Processing Integration
----------------------------------
Tests the integration of all content processors to ensure they work together correctly.
"""

import os
import sys
import tempfile
import unittest
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Import the main application
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import get_logger

# Try to import content processors
try:
    from content_processors.processor_registry import ProcessorRegistry
    from content_processing_integration import get_integration
    CONTENT_PROCESSORS_AVAILABLE = True
except ImportError:
    CONTENT_PROCESSORS_AVAILABLE = False

logger = get_logger()

@unittest.skipIf(not CONTENT_PROCESSORS_AVAILABLE, "Content processors not available")
class ContentProcessingIntegrationTests(unittest.TestCase):
    """Tests for content processing integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests"""
        # Create QApplication if it doesn't exist
        cls.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create a temporary directory for test outputs
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = cls.temp_dir.name
        
        logger.info(f"Test output directory: {cls.output_dir}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Clean up temporary directory
        cls.temp_dir.cleanup()
    
    def setUp(self):
        """Set up before each test"""
        # Get the content processing integration
        self.integration = get_integration()
        
        # Create a test markdown file with various content types
        self.test_content = """# Content Processing Integration Test

This document tests the integration of all content processors.

## Mermaid Diagram

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

## Math Expressions

Inline math: $E = mc^2$

Block math:

$$
\\frac{d}{dx}\\left( \\int_{0}^{x} f(u)\\,du\\right)=f(x)
$$

## Code Blocks

```python
def hello_world():
    print("Hello, world!")
```

```javascript
function helloWorld() {
    console.log("Hello, world!");
}
```

## Images

![Test Image](test_image.png)

<img src="test_image.png" alt="HTML Image" width="300" />

## Media

<video src="test_video.mp4" controls></video>

<audio src="test_audio.mp3" controls></audio>

## Visualization

```plotly
{
    "data": [
        {
            "x": [1, 2, 3, 4],
            "y": [10, 15, 13, 17],
            "type": "scatter"
        }
    ],
    "layout": {
        "title": "Test Plot"
    }
}
```
"""
        
        # Create a test image
        self.image_path = os.path.join(self.output_dir, "test_image.png")
        with open(self.image_path, "wb") as f:
            f.write(b"This is a test image")
    
    def test_process_content_for_preview(self):
        """Test processing content for preview"""
        # Process the content for preview
        processed_content = self.integration.process_content_for_preview(self.test_content)
        
        # Check if the content was processed correctly
        self.assertIsNotNone(processed_content, "Processed content is None")
        self.assertNotEqual(processed_content, self.test_content, "Content was not processed")
        
        # Check for specific processor outputs
        self.assertIn("<div class=\"mermaid\">", processed_content, "Mermaid diagram not processed")
        self.assertIn("class=\"math\"", processed_content, "Math expressions not processed")
        self.assertIn("<pre><code", processed_content, "Code blocks not processed")
    
    def test_process_content_for_export(self):
        """Test processing content for export"""
        # Process the content for different export formats
        formats = ["pdf", "html", "docx", "epub"]
        
        for format_type in formats:
            processed_content = self.integration.process_content_for_export(self.test_content, format_type)
            
            # Check if the content was processed correctly
            self.assertIsNotNone(processed_content, f"Processed content for {format_type} is None")
            self.assertNotEqual(processed_content, self.test_content, f"Content for {format_type} was not processed")
    
    def test_get_required_scripts(self):
        """Test getting required scripts"""
        # Get required scripts
        scripts = self.integration.get_required_scripts()
        
        # Check if scripts were returned
        self.assertIsNotNone(scripts, "Required scripts is None")
        self.assertIsInstance(scripts, str, "Required scripts is not a string")
    
    def test_get_required_styles(self):
        """Test getting required styles"""
        # Get required styles
        styles = self.integration.get_required_styles()
        
        # Check if styles were returned
        self.assertIsNotNone(styles, "Required styles is None")
        self.assertIsInstance(styles, str, "Required styles is not a string")
    
    def test_check_dependencies(self):
        """Test checking dependencies"""
        # Check dependencies
        dependency_status = self.integration.check_dependencies()
        
        # Check if dependency status was returned
        self.assertIsNotNone(dependency_status, "Dependency status is None")
        self.assertIsInstance(dependency_status, bool, "Dependency status is not a boolean")
    
    def test_integration_with_main_application(self):
        """Test integration with the main application"""
        # Create a fresh instance of the application
        window = AdvancedMarkdownToPDF()
        
        # Set the test content in the editor
        window.markdown_editor.setPlainText(self.test_content)
        
        # Update the preview
        window.update_preview()
        
        # Check if the preview was updated
        self.assertIsNotNone(window.page_preview, "Page preview is None")
        
        # Close the window
        window.close()
        
        # Process events to ensure window closes
        QApplication.processEvents()

def run_tests():
    """Run all tests"""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    if CONTENT_PROCESSORS_AVAILABLE:
        for name in dir(ContentProcessingIntegrationTests):
            if name.startswith('test_'):
                suite.addTest(ContentProcessingIntegrationTests(name))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success if all tests passed
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
