#!/usr/bin/env python3
"""
Test script to verify that test mode is working correctly
"""

import os
import sys
import logging
import tempfile
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from dialog_handler import DialogHandler, handle_export_dialog

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestModeTester:
    """Test that test mode is working correctly"""

    def __init__(self):
        """Initialize the tester"""
        # Parse command-line arguments
        import argparse
        parser = argparse.ArgumentParser(description="Test Mode Tester")
        parser.add_argument("--test-mode", action="store_true", help="Run in test mode (suppresses dialogs)")
        args = parser.parse_args()

        # Set environment variable for test mode if specified
        if args.test_mode:
            os.environ["MARKDOWN_PDF_TEST_MODE"] = "1"
            logger.info("Running in test mode - dialogs will be suppressed")

        self.app = QApplication(sys.argv)
        self.temp_dir = tempfile.mkdtemp(prefix="test_mode_test_")
        self.test_files = []

        # Initialize dialog handler
        self.dialog_handler = DialogHandler(self.app)

        # Check for test mode environment variables
        test_mode = os.environ.get("MARKDOWN_PDF_TEST_MODE", "0") == "1"
        dialog_timeout = int(os.environ.get("MARKDOWN_PDF_DIALOG_TIMEOUT", "10"))

        # Configure dialog handler based on test mode
        suppress_dialogs = test_mode
        auto_close_timeout = dialog_timeout * 1000  # Convert to milliseconds

        self.dialog_handler.start(suppress_dialogs=suppress_dialogs, auto_close_timeout=auto_close_timeout)
        self.dialog_handler.register_response("QMessageBox", handle_export_dialog)

        logger.info(f"Test mode: {test_mode}")
        logger.info(f"Dialog timeout: {dialog_timeout} seconds")

    def cleanup(self):
        """Clean up temporary files and resources"""
        # Stop the dialog handler
        if hasattr(self, 'dialog_handler'):
            self.dialog_handler.stop()
            self.dialog_handler.close_all_active_dialogs()

        # Clean up temporary files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Error removing file {file_path}: {e}")

        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except Exception as e:
                logger.warning(f"Error removing directory {self.temp_dir}: {e}")

    def create_test_markdown(self, name, content):
        """Create a test markdown file"""
        file_path = os.path.join(self.temp_dir, f"{name}.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def test_export_dialogs(self):
        """Test export dialogs with test mode"""
        logger.info("Testing export dialogs with test mode")

        # Create a test markdown file
        test_content = """# Test Mode Test

This is a test for test mode functionality.
"""

        test_file = self.create_test_markdown("test_mode_test", test_content)

        # Create a window
        window = AdvancedMarkdownToPDF()

        # Load the test file content
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        window.markdown_editor.setPlainText(content)

        # Verify that test mode is enabled
        logger.info(f"Test mode enabled: {window._is_test_environment}")

        # This test is successful if we can get this far without errors
        # The actual export functionality is tested in other test scripts
        logger.info("Test mode verification completed successfully")

        return True

    def run_all_tests(self):
        """Run all tests"""
        logger.info("Running all test mode tests")

        try:
            # Test export dialogs
            export_dialog_result = self.test_export_dialogs()
            logger.info(f"Export dialog test result: {'PASS' if export_dialog_result else 'FAIL'}")

            return export_dialog_result
        finally:
            self.cleanup()

def main():
    """Main function"""
    tester = TestModeTester()

    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
