#!/usr/bin/env python3
"""
Unit Test Runner for Markdown to PDF Converter
---------------------------------------------
Runs unit tests for the application.
"""

import os
import sys
import time
import unittest
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

from unit_tests import ExportTests, SettingsTests, ExportWithSettingsTests, TestResult
from logging_config import get_logger

logger = get_logger()

class TestWorker(QThread):
    """Worker thread for running tests"""
    test_started = pyqtSignal(str)
    test_finished = pyqtSignal(TestResult)
    all_tests_finished = pyqtSignal(list)
    
    def __init__(self, test_classes):
        super(TestWorker, self).__init__()
        self.test_classes = test_classes
        self.results = []
    
    def run(self):
        """Run all tests"""
        # Create a test suite
        suite = unittest.TestSuite()
        
        # Add test cases
        for test_class in self.test_classes:
            suite.addTest(unittest.makeSuite(test_class))
        
        # Create a custom test runner
        class CustomTestRunner(unittest.TextTestRunner):
            def __init__(self, worker):
                super(CustomTestRunner, self).__init__(verbosity=2)
                self.worker = worker
                self.results = []
            
            def run(self, test):
                """Run the test suite"""
                result = super(CustomTestRunner, self).run(test)
                return result
            
            def _makeResult(self):
                """Create a custom test result object"""
                return CustomTestResult(self.worker)
        
        class CustomTestResult(unittest.TextTestResult):
            def __init__(self, worker):
                super(CustomTestResult, self).__init__(sys.stdout, True, 2)
                self.worker = worker
                self.successes = []
            
            def startTest(self, test):
                """Called when a test starts"""
                super(CustomTestResult, self).startTest(test)
                test_name = test.id().split('.')[-1]
                self.worker.test_started.emit(test_name)
            
            def addSuccess(self, test):
                """Called when a test succeeds"""
                super(CustomTestResult, self).addSuccess(test)
                self.successes.append(test)
                test_name = test.id().split('.')[-1]
                self.worker.test_finished.emit(TestResult(test_name, True, "Test passed"))
                self.worker.results.append(TestResult(test_name, True, "Test passed"))
            
            def addFailure(self, test, err):
                """Called when a test fails"""
                super(CustomTestResult, self).addFailure(test, err)
                test_name = test.id().split('.')[-1]
                self.worker.test_finished.emit(TestResult(test_name, False, str(err[1])))
                self.worker.results.append(TestResult(test_name, False, str(err[1])))
            
            def addError(self, test, err):
                """Called when a test errors"""
                super(CustomTestResult, self).addError(test, err)
                test_name = test.id().split('.')[-1]
                self.worker.test_finished.emit(TestResult(test_name, False, str(err[1])))
                self.worker.results.append(TestResult(test_name, False, str(err[1])))
        
        # Run tests
        runner = CustomTestRunner(self)
        runner.run(suite)
        
        # Emit signal with all results
        self.all_tests_finished.emit(self.results)

class UnitTestDialog(QDialog):
    """Dialog for running unit tests"""
    def __init__(self, parent=None):
        super(UnitTestDialog, self).__init__(parent)
        self.parent = parent
        self.test_worker = None
        self.initUI()
    
    def initUI(self):
        """Initialize the UI"""
        # Set up the dialog
        self.setWindowTitle("Unit Tests")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Add title
        title = QLabel("Markdown to PDF Converter Unit Tests")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)
        
        # Add description
        description = QLabel("Run unit tests to verify the functionality of the application.")
        layout.addWidget(description)
        
        # Add test list
        self.test_list = QListWidget()
        layout.addWidget(self.test_list)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Add output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)
        
        # Add buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.run_button = QPushButton("Run Tests")
        self.run_button.clicked.connect(self.run_tests)
        button_layout.addWidget(self.run_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        # Populate test list
        self.populate_test_list()
    
    def populate_test_list(self):
        """Populate the test list with available tests"""
        # Add export tests
        for method_name in dir(ExportTests):
            if method_name.startswith('test_'):
                test_name = method_name[5:].replace('_', ' ').title()
                self.test_list.addItem(f"Export: {test_name}")
        
        # Add settings tests
        for method_name in dir(SettingsTests):
            if method_name.startswith('test_'):
                test_name = method_name[5:].replace('_', ' ').title()
                self.test_list.addItem(f"Settings: {test_name}")
        
        # Add export with settings tests
        for method_name in dir(ExportWithSettingsTests):
            if method_name.startswith('test_'):
                test_name = method_name[5:].replace('_', ' ').title()
                self.test_list.addItem(f"Export with Settings: {test_name}")
    
    def run_tests(self):
        """Run the selected tests"""
        # Disable run button
        self.run_button.setEnabled(False)
        
        # Clear output area
        self.output_area.clear()
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Get selected tests
        selected_items = self.test_list.selectedItems()
        if not selected_items:
            # If no tests are selected, run all tests
            self.output_area.append("Running all tests...\n")
            test_classes = [ExportTests, SettingsTests, ExportWithSettingsTests]
        else:
            # Run only selected tests
            self.output_area.append("Running selected tests...\n")
            test_classes = []
            for item in selected_items:
                text = item.text()
                if text.startswith("Export: "):
                    test_classes.append(ExportTests)
                elif text.startswith("Settings: "):
                    test_classes.append(SettingsTests)
                elif text.startswith("Export with Settings: "):
                    test_classes.append(ExportWithSettingsTests)
        
        # Create and start worker thread
        self.test_worker = TestWorker(test_classes)
        self.test_worker.test_started.connect(self.on_test_started)
        self.test_worker.test_finished.connect(self.on_test_finished)
        self.test_worker.all_tests_finished.connect(self.on_all_tests_finished)
        self.test_worker.start()
    
    def on_test_started(self, test_name):
        """Called when a test starts"""
        self.output_area.append(f"Running test: {test_name}...")
        QApplication.processEvents()
    
    def on_test_finished(self, result):
        """Called when a test finishes"""
        if result.success:
            self.output_area.append(f"✓ {result.name}: {result.message}\n")
        else:
            self.output_area.append(f"✗ {result.name}: {result.message}\n")
        QApplication.processEvents()
    
    def on_all_tests_finished(self, results):
        """Called when all tests finish"""
        # Update progress bar
        self.progress_bar.setValue(100)
        
        # Count successes and failures
        successes = sum(1 for result in results if result.success)
        failures = sum(1 for result in results if not result.success)
        
        # Display summary
        self.output_area.append(f"\nTest Summary: {successes} passed, {failures} failed\n")
        
        # Re-enable run button
        self.run_button.setEnabled(True)

def run_unit_tests(parent=None):
    """Run unit tests and show the dialog"""
    dialog = UnitTestDialog(parent)
    dialog.exec()

if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    
    # Run tests
    run_unit_tests()
    
    # Exit
    sys.exit(0)
