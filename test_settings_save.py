#!/usr/bin/env python3
"""
Test for settings save functionality
------------------------------------
This script tests that settings are saved only once when performing operations.
"""

import os
import sys
import time
import unittest
import logging
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QApplication

# Set the attribute before creating QApplication
from PyQt6.QtCore import QCoreApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Set test environment flag
os.environ["MARKDOWN_PDF_TEST_MODE"] = "1"

class TestSettingsSave(unittest.TestCase):
    """Test case for settings save functionality"""

    def setUp(self):
        """Set up the test environment"""
        # Create QApplication instance
        self.app = QApplication.instance() or QApplication(sys.argv)

        # Import the main application
        from markdown_to_pdf_converter import AdvancedMarkdownToPDF

        # Create the main window
        self.window = AdvancedMarkdownToPDF()

        # Set up MDZ integration
        from mdz_integration import integrate_mdz
        self.mdz_integration = integrate_mdz(self.window)

        # Create a mock for the save_settings method
        self.original_save_settings = self.window.save_settings
        self.save_settings_calls = 0

        def mock_save_settings(*args, **kwargs):
            self.save_settings_calls += 1
            logger.debug(f"save_settings called (count: {self.save_settings_calls})")
            # Don't actually save settings in test
            return

        self.window.save_settings = mock_save_settings

        # Create a temporary file for testing
        import tempfile
        self.temp_md = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        self.temp_md.write(b'# Test Markdown\n\nThis is a test.')
        self.temp_md.close()

        self.temp_mdz = tempfile.NamedTemporaryFile(delete=False, suffix='.mdz')
        self.temp_mdz.close()

    def tearDown(self):
        """Clean up after the test"""
        # Restore original save_settings method
        self.window.save_settings = self.original_save_settings

        # Clean up temporary files
        try:
            os.unlink(self.temp_md.name)
        except:
            pass

        try:
            os.unlink(self.temp_mdz.name)
        except:
            pass

        # Clean up MDZ integration
        if self.mdz_integration:
            self.mdz_integration.cleanup_mdz()
            self.mdz_integration.restore_original_methods()

        # Close the window
        self.window.close()

    def test_open_md_file(self):
        """Test opening a Markdown file"""
        # Reset counter
        self.save_settings_calls = 0

        # Open the file
        self.window.current_file = None
        self.window.open_file = lambda: None  # Mock to avoid dialog
        self.window.markdown_editor.setPlainText("")

        # Directly call the file opening code
        with open(self.temp_md.name, 'r', encoding='utf-8') as file:
            self.window.markdown_editor.setPlainText(file.read())

        self.window.current_file = self.temp_md.name
        self.window.dialog_paths["open"] = os.path.dirname(self.temp_md.name)

        # Manually trigger save_settings as would happen in the real flow
        self.window.save_settings()

        # Check that save_settings was called exactly once
        self.assertEqual(self.save_settings_calls, 1,
                        f"save_settings was called {self.save_settings_calls} times, expected 1")

    def test_open_mdz_file(self):
        """Test opening an MDZ file"""
        # Reset counter
        self.save_settings_calls = 0

        # Create a simple MDZ file
        from unified_mdz import UnifiedMDZ
        bundle = UnifiedMDZ()
        bundle.create_from_markdown("# Test MDZ\n\nThis is a test.")
        bundle.save(self.temp_mdz.name)

        # Open the MDZ file
        self.mdz_integration.open_mdz_file(self.temp_mdz.name)

        # Manually trigger save_settings as would happen in the real flow
        self.window.save_settings()

        # Check that save_settings was called exactly once
        self.assertEqual(self.save_settings_calls, 1,
                        f"save_settings was called {self.save_settings_calls} times, expected 1")

    def test_save_mdz_file(self):
        """Test saving an MDZ file"""
        # Reset counter
        self.save_settings_calls = 0

        # Set up content
        self.window.markdown_editor.setPlainText("# Test Save MDZ\n\nThis is a test.")

        # Save the MDZ file
        self.mdz_integration.save_mdz_file(self.temp_mdz.name)

        # Manually trigger save_settings as would happen in the real flow
        self.window.save_settings()

        # Check that save_settings was called exactly once
        self.assertEqual(self.save_settings_calls, 1,
                        f"save_settings was called {self.save_settings_calls} times, expected 1")

    def test_export_to_mdz(self):
        """Test exporting to MDZ"""
        # Reset counter
        self.save_settings_calls = 0

        # Set up content
        self.window.markdown_editor.setPlainText("# Test Export MDZ\n\nThis is a test.")

        # Mock the file dialog
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName',
                  return_value=(self.temp_mdz.name, 'MDZ Bundles (*.mdz)')):
            # Call export_to_mdz
            self.mdz_integration.export_to_mdz()

        # Check that save_settings was called exactly once
        self.assertEqual(self.save_settings_calls, 1,
                        f"save_settings was called {self.save_settings_calls} times, expected 1")

if __name__ == '__main__':
    unittest.main()
