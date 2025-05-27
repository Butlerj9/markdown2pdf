#!/usr/bin/env python3
"""
Dialog Handler for Testing Framework
-----------------------------------
Provides utilities to handle dialog boxes during automated testing.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Union, Callable, Any
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QFileDialog, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent, pyqtSignal

# Configure logger
logger = logging.getLogger(__name__)

class DialogHandler(QObject):
    """
    Class for handling dialog boxes during automated testing.

    This class can:
    1. Automatically close dialog boxes after a timeout
    2. Suppress dialog boxes entirely
    3. Provide custom responses to dialog boxes
    """

    dialog_detected = pyqtSignal(QDialog)
    dialog_closed = pyqtSignal(QDialog)

    def __init__(self, app: QApplication, parent=None):
        """
        Initialize the dialog handler.

        Args:
            app: The QApplication instance
            parent: The parent object
        """
        super().__init__(parent)
        self.app = app
        self.active = False
        self.suppress_dialogs = False
        self.auto_close_timeout = 10000  # 10 seconds default
        self.dialog_responses = {}  # Map of dialog class names to response functions
        self.active_dialogs = []

        # Install event filter
        self.app.installEventFilter(self)

        logger.info("Dialog handler initialized")

    def start(self, suppress_dialogs=False, auto_close_timeout=10000):
        """
        Start handling dialogs.

        Args:
            suppress_dialogs: Whether to suppress dialogs entirely
            auto_close_timeout: Timeout in milliseconds before auto-closing dialogs
        """
        self.active = True
        self.suppress_dialogs = suppress_dialogs
        self.auto_close_timeout = auto_close_timeout
        logger.info(f"Dialog handler started (suppress={suppress_dialogs}, timeout={auto_close_timeout}ms)")

    def stop(self):
        """Stop handling dialogs"""
        self.active = False
        logger.info("Dialog handler stopped")

    def register_response(self, dialog_class_name: str, response_func: Callable[[QDialog], None]):
        """
        Register a custom response function for a specific dialog class.

        Args:
            dialog_class_name: The class name of the dialog
            response_func: Function that takes a dialog and performs actions on it
        """
        self.dialog_responses[dialog_class_name] = response_func
        logger.info(f"Registered custom response for {dialog_class_name}")

    def eventFilter(self, obj, event):
        """
        Filter events to detect dialog creation.

        Args:
            obj: The object that triggered the event
            event: The event

        Returns:
            True if the event should be filtered out, False otherwise
        """
        if not self.active:
            return False

        # Check for dialog creation
        if event.type() == QEvent.Type.Show and isinstance(obj, QDialog):
            self._handle_dialog(obj)

            # If we're suppressing dialogs, filter out the event
            return self.suppress_dialogs

        return False

    def _handle_dialog(self, dialog):
        """
        Handle a detected dialog.

        Args:
            dialog: The dialog to handle
        """
        dialog_class = dialog.__class__.__name__
        logger.info(f"Dialog detected: {dialog_class} - '{dialog.windowTitle()}'")

        # Add to active dialogs
        if dialog not in self.active_dialogs:
            self.active_dialogs.append(dialog)
            self.dialog_detected.emit(dialog)

        # Check if we have a custom response
        if dialog_class in self.dialog_responses:
            logger.info(f"Applying custom response to {dialog_class}")
            try:
                self.dialog_responses[dialog_class](dialog)
            except Exception as e:
                logger.error(f"Error applying custom response to {dialog_class}: {str(e)}")
        else:
            # Apply default handling
            self._apply_default_handling(dialog)

    def _apply_default_handling(self, dialog):
        """
        Apply default handling to a dialog.

        Args:
            dialog: The dialog to handle
        """
        # Start a timer to auto-close the dialog
        if self.auto_close_timeout > 0:
            logger.info(f"Setting up auto-close timer for {dialog.__class__.__name__} ({self.auto_close_timeout}ms)")
            QTimer.singleShot(self.auto_close_timeout, lambda: self._auto_close_dialog(dialog))

    def _auto_close_dialog(self, dialog):
        """
        Automatically close a dialog after the timeout.

        Args:
            dialog: The dialog to close
        """
        if not dialog.isVisible():
            return

        logger.info(f"Auto-closing dialog: {dialog.__class__.__name__}")

        try:
            # Handle different dialog types
            if isinstance(dialog, QMessageBox):
                # For message boxes, click the default button
                default_button = dialog.defaultButton()
                if default_button:
                    default_button.click()
                else:
                    # If no default button, try to find an OK or Cancel button
                    buttons = dialog.buttons()
                    for button in buttons:
                        if dialog.buttonRole(button) in [QMessageBox.ButtonRole.AcceptRole, QMessageBox.ButtonRole.YesRole]:
                            button.click()
                            break
                    else:
                        # If no accept button, try cancel
                        for button in buttons:
                            if dialog.buttonRole(button) in [QMessageBox.ButtonRole.RejectRole, QMessageBox.ButtonRole.NoRole]:
                                button.click()
                                break
                        else:
                            # Last resort: just close the dialog
                            dialog.close()
            elif isinstance(dialog, QFileDialog):
                # For file dialogs, just reject
                dialog.reject()
            else:
                # For other dialogs, try to find and click an OK or Cancel button
                # This is a simplistic approach and might not work for all dialogs
                for child in dialog.findChildren(QPushButton):
                    if child.text() in ["OK", "Ok", "Close", "Cancel"]:
                        child.click()
                        break
                else:
                    # If no suitable button found, just close the dialog
                    dialog.close()
        except Exception as e:
            logger.error(f"Error auto-closing dialog: {str(e)}")
            # Last resort: just close the dialog
            try:
                dialog.close()
            except:
                pass

        # Remove from active dialogs
        if dialog in self.active_dialogs:
            self.active_dialogs.remove(dialog)
            self.dialog_closed.emit(dialog)

    def close_all_active_dialogs(self):
        """Close all active dialogs"""
        logger.info(f"Closing all active dialogs ({len(self.active_dialogs)})")

        # Make a copy of the list since we'll be modifying it
        dialogs = self.active_dialogs.copy()

        for dialog in dialogs:
            self._auto_close_dialog(dialog)

# Common response functions for specific dialogs
def accept_dialog(dialog):
    """Accept a dialog (click OK/Yes)"""
    logger.info(f"Accepting dialog: {dialog.__class__.__name__} - '{dialog.windowTitle()}'")

    if isinstance(dialog, QMessageBox):
        buttons = dialog.buttons()
        for button in buttons:
            if dialog.buttonRole(button) in [QMessageBox.ButtonRole.AcceptRole, QMessageBox.ButtonRole.YesRole]:
                logger.info(f"Clicking button: {button.text()}")
                QTimer.singleShot(100, button.click)
                return

    # For other dialogs, try to find and click an OK button
    for child in dialog.findChildren(QPushButton):
        if child.text() in ["OK", "Ok", "Yes"]:
            logger.info(f"Clicking button: {child.text()}")
            QTimer.singleShot(100, child.click)
            return

    # If no suitable button found, just accept the dialog
    logger.info("No suitable button found, calling accept()")
    QTimer.singleShot(100, dialog.accept)

def reject_dialog(dialog):
    """Reject a dialog (click Cancel/No)"""
    logger.info(f"Rejecting dialog: {dialog.__class__.__name__} - '{dialog.windowTitle()}'")

    if isinstance(dialog, QMessageBox):
        buttons = dialog.buttons()
        for button in buttons:
            if dialog.buttonRole(button) in [QMessageBox.ButtonRole.RejectRole, QMessageBox.ButtonRole.NoRole]:
                logger.info(f"Clicking button: {button.text()}")
                QTimer.singleShot(100, button.click)
                return

    # For other dialogs, try to find and click a Cancel button
    for child in dialog.findChildren(QPushButton):
        if child.text() in ["Cancel", "No"]:
            logger.info(f"Clicking button: {child.text()}")
            QTimer.singleShot(100, child.click)
            return

    # If no suitable button found, just reject the dialog
    logger.info("No suitable button found, calling reject()")
    QTimer.singleShot(100, dialog.reject)

def handle_export_dialog(dialog):
    """Handle export status dialogs"""
    logger.info(f"Handling export dialog: {dialog.__class__.__name__} - '{dialog.windowTitle()}'")

    # For export status dialogs, wait a bit longer to let the export complete
    if dialog.windowTitle() in ['Exporting', 'Export Successful', 'Export Error', 'Save Style', 'Delete Style']:
        logger.info(f"Export/Style dialog detected: {dialog.windowTitle()}")

        # For "Exporting" dialogs, wait for the export to complete
        if dialog.windowTitle() == 'Exporting':
            # Don't close immediately, let the export process run
            QTimer.singleShot(5000, lambda: close_dialog_if_visible(dialog))
            return

        # For "Save Style" dialogs, we need to handle input
        if dialog.windowTitle() == 'Save Style':
            # Find the line edit and set a default value
            for child in dialog.findChildren(QLineEdit):
                child.setText("TestStyle")
                break

            # Find the OK button and click it
            for child in dialog.findChildren(QPushButton):
                if child.text() in ["OK", "Ok"]:
                    QTimer.singleShot(500, child.click)
                    return

        # For "Delete Style" confirmation dialogs, click "No"
        if dialog.windowTitle() == 'Delete Style':
            for child in dialog.findChildren(QPushButton):
                if child.text() == "No":
                    QTimer.singleShot(500, child.click)
                    return

        # For success or error dialogs, close them after a short delay
        QTimer.singleShot(500, lambda: close_dialog_if_visible(dialog))
        return

    # Default to accept for other dialogs
    accept_dialog(dialog)

def close_dialog_if_visible(dialog):
    """Close a dialog if it's still visible"""
    if dialog and dialog.isVisible():
        logger.info(f"Closing dialog: {dialog.__class__.__name__} - '{dialog.windowTitle()}'")

        # Try to find and click an OK or Close button
        for child in dialog.findChildren(QPushButton):
            if child.text() in ["OK", "Ok", "Close"]:
                logger.info(f"Clicking button: {child.text()}")
                child.click()
                return

        # If no suitable button found, just accept the dialog
        logger.info("No suitable button found, calling accept()")
        dialog.accept()

# Example usage:
# dialog_handler = DialogHandler(QApplication.instance())
# dialog_handler.start(suppress_dialogs=False, auto_close_timeout=5000)
# dialog_handler.register_response("QMessageBox", accept_dialog)
# dialog_handler.register_response("SaveChangesDialog", reject_dialog)
