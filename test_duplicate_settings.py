#!/usr/bin/env python3
"""
Test for duplicate settings save
-------------------------------
This script tests that settings are not saved multiple times.
"""

import os
import sys
import logging
from unittest.mock import patch, MagicMock

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

# Set up Qt application attribute before importing PyQt
from PyQt6.QtCore import QCoreApplication, Qt
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

def test_mdz_integration():
    """Test that MDZ integration doesn't call save_settings multiple times"""
    from PyQt6.QtWidgets import QApplication
    
    # Create QApplication instance
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create a mock for QSettings
    mock_settings = MagicMock()
    
    # Patch QSettings to use our mock
    with patch('PyQt6.QtCore.QSettings', return_value=mock_settings):
        # Import the main application
        from markdown_to_pdf_converter import AdvancedMarkdownToPDF
        
        # Create the main window
        window = AdvancedMarkdownToPDF()
        
        # Reset the mock to clear any calls during initialization
        mock_settings.setValue.reset_mock()
        
        # Set up MDZ integration
        from mdz_integration import integrate_mdz
        mdz_integration = integrate_mdz(window)
        
        # Create a temporary file for testing
        import tempfile
        temp_md = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        temp_md.write(b'# Test Markdown\n\nThis is a test.')
        temp_md.close()
        
        # Test opening a file
        window.current_file = None
        with open(temp_md.name, 'r', encoding='utf-8') as file:
            window.markdown_editor.setPlainText(file.read())
        
        window.current_file = temp_md.name
        window.dialog_paths["open"] = os.path.dirname(temp_md.name)
        
        # Manually trigger save_settings
        window.save_settings()
        
        # Check that setValue was called only once for dialog_paths
        dialog_paths_calls = [call for call in mock_settings.setValue.call_args_list 
                             if call[0][0] == "dialog_paths"]
        
        print(f"Number of setValue calls for dialog_paths: {len(dialog_paths_calls)}")
        assert len(dialog_paths_calls) == 1, f"Expected 1 call to setValue for dialog_paths, got {len(dialog_paths_calls)}"
        
        # Clean up
        try:
            os.unlink(temp_md.name)
        except:
            pass
        
        # Clean up MDZ integration
        if mdz_integration:
            mdz_integration.cleanup_mdz()
            mdz_integration.restore_original_methods()
        
        # Close the window
        window.close()
        
        print("Test passed: No duplicate settings saves detected")
        return True

if __name__ == '__main__':
    try:
        success = test_mdz_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
