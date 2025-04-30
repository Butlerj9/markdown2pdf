#!/usr/bin/env python3
"""
Visual Testing Framework for Markdown to PDF Converter
----------------------------------------------------
Provides automated testing of the application's UI through screenshots and simulated user interactions.
"""

import os
import sys
import time
import logging
import tempfile
from datetime import datetime
from PIL import Image, ImageChops, ImageDraw
import numpy as np
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt, QObject
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QGuiApplication, QScreen

from logging_config import get_logger

logger = get_logger()

class VisualTester:
    """Class for visual testing of the application"""

    def __init__(self, app=None):
        """Initialize the visual tester"""
        self.app = app
        self.screenshot_dir = os.path.join(tempfile.gettempdir(), "markdown2pdf_visual_tests")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.reference_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_references")
        os.makedirs(self.reference_dir, exist_ok=True)
        self.current_test = None

    def take_screenshot(self, name=None):
        """Take a screenshot of the current application window"""
        if not name:
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Ensure the app is active
        active_window = None
        if self.app:
            for window in self.app.topLevelWidgets():
                if window.isVisible():
                    window.activateWindow()
                    window.raise_()
                    active_window = window
                    break

        # Allow time for window to activate
        QTest.qWait(500)

        # Take screenshot using Qt
        if active_window:
            # Screenshot of just the active window
            screenshot = active_window.grab()
        else:
            # Screenshot of the entire screen
            screen = QGuiApplication.primaryScreen()
            screenshot = screen.grabWindow(0)

        # Save the screenshot
        filename = os.path.join(self.screenshot_dir, f"{name}.png")
        screenshot.save(filename)
        logger.info(f"Screenshot saved to {filename}")

        return filename

    def compare_screenshots(self, reference_path, current_path):
        """Compare two screenshots and return the difference percentage"""
        try:
            # Open images
            reference_img = Image.open(reference_path)
            current_img = Image.open(current_path)

            # Ensure same size
            if reference_img.size != current_img.size:
                current_img = current_img.resize(reference_img.size)

            # Calculate difference
            diff = ImageChops.difference(reference_img, current_img)

            # Create a diff image with highlighted differences
            diff_img = Image.new("RGB", reference_img.size)
            draw = ImageDraw.Draw(diff_img)

            # Copy reference image
            diff_img.paste(reference_img)

            # Highlight differences in red
            for y in range(diff_img.height):
                for x in range(diff_img.width):
                    pixel = diff.getpixel((x, y))
                    if sum(pixel) > 30:  # Threshold for difference
                        draw.point((x, y), fill=(255, 0, 0))

            # Save diff image
            diff_path = os.path.join(self.screenshot_dir, f"diff_{os.path.basename(current_path)}")
            diff_img.save(diff_path)

            # Calculate difference percentage
            diff_array = np.array(diff)
            total_pixels = diff_array.size / 3  # RGB image
            different_pixels = np.sum(diff_array > 30) / 3  # Threshold
            diff_percentage = (different_pixels / total_pixels) * 100

            logger.info(f"Difference: {diff_percentage:.2f}% - Diff image saved to {diff_path}")

            return diff_percentage, diff_path
        except Exception as e:
            logger.error(f"Error comparing screenshots: {str(e)}")
            return 100, None  # Return 100% difference on error

    def find_widget(self, widget_name, parent=None):
        """Find a widget by name in the application"""
        if parent is None and self.app:
            # Search in all top-level widgets
            for window in self.app.topLevelWidgets():
                if window.isVisible():
                    widget = self._find_widget_recursive(window, widget_name)
                    if widget:
                        return widget
        elif parent:
            # Search in the specified parent widget
            return self._find_widget_recursive(parent, widget_name)

        logger.warning(f"Widget not found: {widget_name}")
        return None

    def _find_widget_recursive(self, parent, widget_name):
        """Recursively search for a widget by name"""
        # Check if this widget matches
        if parent.objectName() == widget_name:
            return parent

        # Check all children
        for child in parent.findChildren(QObject):
            if child.objectName() == widget_name:
                return child

        # Not found
        return None

    def click_widget(self, widget_name, parent=None):
        """Click on a widget by name"""
        widget = self.find_widget(widget_name, parent)
        if widget:
            QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
            logger.info(f"Clicked on widget: {widget_name}")
            return True
        return False

    def type_text(self, text, widget_name=None, parent=None):
        """Type text into a widget"""
        if widget_name:
            widget = self.find_widget(widget_name, parent)
            if not widget:
                logger.warning(f"Widget not found for typing: {widget_name}")
                return False
        else:
            # Type into the currently focused widget
            widget = QApplication.focusWidget()
            if not widget:
                logger.warning("No widget has focus for typing")
                return False

        # Type the text character by character
        for char in text:
            QTest.keyClick(widget, char)
            QTest.qWait(50)  # Small delay between keystrokes

        logger.info(f"Typed text: {text}")
        return True

    def press_key(self, key, widget_name=None, parent=None):
        """Press a keyboard key on a widget"""
        if widget_name:
            widget = self.find_widget(widget_name, parent)
            if not widget:
                logger.warning(f"Widget not found for key press: {widget_name}")
                return False
        else:
            # Press key on the currently focused widget
            widget = QApplication.focusWidget()
            if not widget:
                logger.warning("No widget has focus for key press")
                return False

        # Convert string key to Qt.Key
        qt_key = getattr(Qt.Key, f"Key_{key.upper()}", None)
        if qt_key is None:
            logger.warning(f"Unknown key: {key}")
            return False

        QTest.keyClick(widget, qt_key)
        logger.info(f"Pressed key: {key}")
        return True

    def press_hotkey(self, *keys, widget_name=None, parent=None):
        """Press a keyboard hotkey combination on a widget"""
        if widget_name:
            widget = self.find_widget(widget_name, parent)
            if not widget:
                logger.warning(f"Widget not found for hotkey: {widget_name}")
                return False
        else:
            # Press hotkey on the currently focused widget
            widget = QApplication.focusWidget()
            if not widget:
                logger.warning("No widget has focus for hotkey")
                return False

        # Convert string keys to Qt.Key
        qt_keys = []
        for key in keys:
            qt_key = getattr(Qt.Key, f"Key_{key.upper()}", None)
            if qt_key is None:
                logger.warning(f"Unknown key in hotkey: {key}")
                return False
            qt_keys.append(qt_key)

        # Press all keys
        for key in qt_keys[:-1]:
            QTest.keyPress(widget, key, Qt.KeyboardModifier.NoModifier)

        # Press and release the last key
        QTest.keyClick(widget, qt_keys[-1], Qt.KeyboardModifier.NoModifier)

        # Release all other keys
        for key in reversed(qt_keys[:-1]):
            QTest.keyRelease(widget, key, Qt.KeyboardModifier.NoModifier)

        logger.info(f"Pressed hotkey: {' + '.join(keys)}")
        return True

    def start_test(self, test_name):
        """Start a new test"""
        self.current_test = test_name
        logger.info(f"Starting visual test: {test_name}")

        # Take initial screenshot
        self.take_screenshot(f"{test_name}_start")

    def end_test(self):
        """End the current test"""
        if self.current_test:
            # Take final screenshot
            self.take_screenshot(f"{self.current_test}_end")
            logger.info(f"Ended visual test: {self.current_test}")
            self.current_test = None

    def create_reference(self, test_name):
        """Create a reference screenshot for a test"""
        filename = self.take_screenshot(test_name)
        reference_path = os.path.join(self.reference_dir, f"{test_name}.png")

        # Copy the screenshot to the reference directory
        img = Image.open(filename)
        img.save(reference_path)

        logger.info(f"Created reference screenshot: {reference_path}")
        return reference_path

    def verify_against_reference(self, test_name, threshold=5.0):
        """Verify a screenshot against a reference image"""
        current_path = self.take_screenshot(test_name)
        reference_path = os.path.join(self.reference_dir, f"{test_name}.png")

        if not os.path.exists(reference_path):
            logger.warning(f"Reference image not found: {reference_path}")
            return False

        diff_percentage, diff_path = self.compare_screenshots(reference_path, current_path)

        if diff_percentage <= threshold:
            logger.info(f"Visual test passed: {test_name} - Difference: {diff_percentage:.2f}%")
            return True
        else:
            logger.warning(f"Visual test failed: {test_name} - Difference: {diff_percentage:.2f}%")
            return False

# Simple test function to verify the visual testing framework
def test_visual_framework():
    """Test the visual testing framework with a simple example"""
    app = QApplication.instance() or QApplication(sys.argv)

    # Create a message box for testing
    msg = QMessageBox()
    msg.setWindowTitle("Visual Test")
    msg.setText("This is a test of the visual testing framework.")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    # Create visual tester
    tester = VisualTester(app)

    # Start test
    tester.start_test("message_box_test")

    # Show message box
    QTimer.singleShot(1000, lambda: msg.show())

    # Take screenshot after message box appears
    QTimer.singleShot(2000, lambda: tester.take_screenshot("message_box"))

    # Close message box
    QTimer.singleShot(3000, lambda: msg.accept())

    # End test
    QTimer.singleShot(4000, lambda: tester.end_test())

    # Exit application
    QTimer.singleShot(5000, lambda: app.quit())

    # Run the application
    app.exec()

if __name__ == "__main__":
    # Run the test when the script is executed directly
    test_visual_framework()
