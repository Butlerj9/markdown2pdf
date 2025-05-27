#!/usr/bin/env python3
"""
Test script for the new main.py application
------------------------------------
This script tests the main application for duplicate messages and basic functionality.
"""

import sys
import os
import logging
import unittest
from unittest.mock import patch, MagicMock
import tempfile

# Configure test environment
os.environ["MARKDOWN_PDF_TEST_MODE"] = "1"

# Import the main module
import main
from main import MessageTracker

class TestMessageTracker(unittest.TestCase):
    """Test the MessageTracker class"""

    def test_track_new_message(self):
        """Test tracking a new message"""
        tracker = MessageTracker()
        is_duplicate = tracker.track("Test message")
        self.assertFalse(is_duplicate)
        self.assertEqual(tracker.get_duplicate_count(), 0)

    def test_track_duplicate_message(self):
        """Test tracking a duplicate message"""
        tracker = MessageTracker()
        tracker.track("Test message")
        is_duplicate = tracker.track("Test message")
        self.assertTrue(is_duplicate)
        self.assertEqual(tracker.get_duplicate_count(), 1)

    def test_track_case_insensitive(self):
        """Test that tracking is case-insensitive"""
        tracker = MessageTracker()
        tracker.track("Test message")
        is_duplicate = tracker.track("TEST MESSAGE")
        self.assertTrue(is_duplicate)
        self.assertEqual(tracker.get_duplicate_count(), 1)

    def test_track_whitespace_insensitive(self):
        """Test that tracking ignores whitespace differences"""
        tracker = MessageTracker()
        tracker.track("Test message")
        is_duplicate = tracker.track("Test    message")
        self.assertTrue(is_duplicate)
        self.assertEqual(tracker.get_duplicate_count(), 1)

    def test_get_duplicate_summary(self):
        """Test getting a summary of duplicate messages"""
        tracker = MessageTracker()
        tracker.track("Message 1")
        tracker.track("Message 1")
        tracker.track("Message 2")
        tracker.track("Message 2")
        tracker.track("Message 2")

        summary = tracker.get_duplicate_summary()
        self.assertIn("2 unique messages", summary)
        self.assertIn("3 times", summary)
        # The message tracker normalizes to lowercase
        self.assertIn("message 1", summary)
        self.assertIn("message 2", summary)

class TestDependencyChecking(unittest.TestCase):
    """Test dependency checking functionality"""

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_check_dependencies_success(self, mock_run, mock_which):
        """Test successful dependency checking"""
        # Mock pandoc being found
        mock_which.return_value = "/usr/bin/pandoc"

        # Mock successful subprocess run
        mock_process = MagicMock()
        mock_process.stdout = "Pandoc 2.14.0\nCompiled with pandoc-types 1.22"
        mock_run.return_value = mock_process

        # Mock zstandard import
        with patch.dict('sys.modules', {'zstandard': MagicMock()}):
            result, error_msg = main.check_dependencies()

        self.assertTrue(result)
        self.assertIsNone(error_msg)

    @patch('shutil.which')
    def test_check_dependencies_missing_pandoc(self, mock_which):
        """Test dependency checking with missing Pandoc"""
        # Mock pandoc not being found
        mock_which.return_value = None

        # Mock zstandard import
        with patch.dict('sys.modules', {'zstandard': MagicMock()}):
            result, error_msg = main.check_dependencies()

        self.assertFalse(result)
        self.assertTrue(error_msg is not None)
        if error_msg:  # Type check for mypy
            self.assertIn("Pandoc not found", error_msg)

def run_tests():
    """Run the tests"""
    unittest.main()

if __name__ == "__main__":
    run_tests()
