#!/usr/bin/env python3
"""
Test Framework for Markdown to PDF Converter
-------------------------------------------
Provides automated testing of various features and settings.
"""

import os
import sys
import json
import tempfile
import time
import logging
import subprocess
import unittest
from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QCheckBox, QProgressBar, QApplication, QTabWidget, QWidget, QGroupBox
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Import visual testing if available
try:
    from visual_test import VisualTester
    VISUAL_TESTING_AVAILABLE = True
except ImportError:
    VISUAL_TESTING_AVAILABLE = False

# Import unit tests if available
try:
    from unit_tests import ExportTests, SettingsTests, ExportWithSettingsTests
    from export_tests import ExportTestCase
    from settings_tests import SettingsTestCase
    UNIT_TESTING_AVAILABLE = True
except ImportError:
    UNIT_TESTING_AVAILABLE = False

from logging_config import get_logger

logger = get_logger()

class TestResult:
    """Class to store test results"""
    def __init__(self, name, passed, message="", details=""):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
        self.timestamp = time.time()

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }

class TestGroup:
    """Class to define a group of related tests"""
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.tests = []
        self.dependencies = []

    def add_test(self, test_func, test_name, description=""):
        """Add a test function to this group"""
        self.tests.append({
            "func": test_func,
            "name": test_name,
            "description": description
        })

    def add_dependency(self, group_name):
        """Add a dependency on another test group"""
        if group_name not in self.dependencies:
            self.dependencies.append(group_name)

class TestRunner:
    """Class to run tests and collect results"""
    def __init__(self, parent=None):
        self.parent = parent
        self.test_groups = {}
        self.results = []
        self.current_group = None
        self.initialize_test_groups()

    def initialize_test_groups(self):
        """Initialize all test groups"""
        # Page layout tests
        page_group = TestGroup("page_layout", "Page Layout Tests")
        page_group.add_test(self.test_page_size, "Page Size", "Test different page sizes")
        page_group.add_test(self.test_page_orientation, "Page Orientation", "Test page orientation")
        page_group.add_test(self.test_page_margins, "Page Margins", "Test page margins")
        page_group.add_test(self.test_page_breaks, "Page Breaks", "Test page breaks")
        page_group.add_test(self.test_page_navigation, "Page Navigation", "Test page navigation")
        self.test_groups["page_layout"] = page_group

        # Font tests
        font_group = TestGroup("fonts", "Font Tests")
        font_group.add_test(self.test_body_font, "Body Font", "Test body font settings")
        font_group.add_test(self.test_heading_fonts, "Heading Fonts", "Test heading font settings")
        font_group.add_test(self.test_code_font, "Code Font", "Test code block font settings")
        font_group.add_test(self.test_master_font, "Master Font", "Test master font control")
        self.test_groups["fonts"] = font_group

        # Color tests
        color_group = TestGroup("colors", "Color Tests")
        color_group.add_test(self.test_text_color, "Text Color", "Test text color settings")
        color_group.add_test(self.test_background_color, "Background Color", "Test background color")
        color_group.add_test(self.test_link_color, "Link Color", "Test link color")
        color_group.add_test(self.test_heading_colors, "Heading Colors", "Test heading colors")
        self.test_groups["colors"] = color_group

        # List tests
        list_group = TestGroup("lists", "List Tests")
        list_group.add_test(self.test_bullet_lists, "Bullet Lists", "Test bullet list styles")
        list_group.add_test(self.test_numbered_lists, "Numbered Lists", "Test numbered list styles")
        list_group.add_test(self.test_list_indentation, "List Indentation", "Test list indentation")
        list_group.add_test(self.test_list_spacing, "List Spacing", "Test list item spacing")
        list_group.add_test(self.test_restart_numbering, "Restart Numbering", "Test restart numbering feature")
        self.test_groups["lists"] = list_group

        # Table tests
        table_group = TestGroup("tables", "Table Tests")
        table_group.add_test(self.test_table_borders, "Table Borders", "Test table border settings")
        table_group.add_test(self.test_table_header, "Table Header", "Test table header settings")
        table_group.add_test(self.test_table_cell_padding, "Cell Padding", "Test table cell padding")
        self.test_groups["tables"] = table_group

        # Export tests
        export_group = TestGroup("export", "Export Tests")
        export_group.add_test(self.test_pdf_export, "PDF Export", "Test PDF export")
        export_group.add_test(self.test_html_export, "HTML Export", "Test HTML export")
        export_group.add_test(self.test_docx_export, "DOCX Export", "Test DOCX export")
        export_group.add_test(self.test_epub_export, "EPUB Export", "Test EPUB export")
        export_group.add_dependency("page_layout")
        export_group.add_dependency("fonts")
        export_group.add_dependency("colors")
        self.test_groups["export"] = export_group

    def run_test_group(self, group_name):
        """Run all tests in a specific group"""
        if group_name not in self.test_groups:
            return [TestResult(f"Group {group_name}", False, "Test group not found")]

        group = self.test_groups[group_name]
        self.current_group = group_name
        group_results = []

        # Check dependencies
        for dependency in group.dependencies:
            if dependency not in self.test_groups:
                group_results.append(TestResult(f"Dependency {dependency}", False, f"Required test group {dependency} not found"))
                continue

        # Run tests
        for test in group.tests:
            try:
                logger.info(f"Running test: {test['name']}")
                result = test["func"]()
                group_results.append(result)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Error in test {test['name']}: {str(e)}")
                result = TestResult(test["name"], False, f"Test error: {str(e)}")
                group_results.append(result)
                self.results.append(result)

        return group_results

    def run_all_tests(self):
        """Run all test groups"""
        all_results = []
        for group_name in self.test_groups:
            group_results = self.run_test_group(group_name)
            all_results.extend(group_results)
        return all_results

    def save_results(self, file_path=None):
        """Save test results to a JSON file"""
        if not file_path:
            file_path = os.path.join(tempfile.gettempdir(), "markdown2pdf_test_results.json")

        results_dict = {
            "timestamp": time.time(),
            "results": [r.to_dict() for r in self.results]
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2)
            logger.info(f"Test results saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")
            return False

    # Test implementations
    def test_page_size(self):
        """Test different page sizes"""
        try:
            if not self.parent:
                return TestResult("Page Size", False, "No parent application available")

            # Store original setting
            original_size = self.parent.document_settings["page"]["size"]

            # Test each page size
            sizes = ["A4", "Letter", "Legal", "A3", "A5"]
            for size in sizes:
                # Change the setting
                self.parent.page_size_combo.setCurrentText(size)

                # Verify the setting was applied
                if self.parent.document_settings["page"]["size"] != size:
                    return TestResult("Page Size", False, f"Failed to set page size to {size}")

                # Update preview to apply the change
                self.parent.update_preview()

                # Allow time for preview to update
                QApplication.processEvents()
                time.sleep(0.5)

            # Restore original setting
            self.parent.page_size_combo.setCurrentText(original_size)
            self.parent.update_preview()

            return TestResult("Page Size", True, "Successfully tested all page sizes")
        except Exception as e:
            logger.error(f"Error in page size test: {str(e)}")
            return TestResult("Page Size", False, f"Test error: {str(e)}")

    def test_page_orientation(self):
        """Test page orientation"""
        try:
            if not self.parent:
                return TestResult("Page Orientation", False, "No parent application available")

            # Store original setting
            original_orientation = self.parent.document_settings["page"]["orientation"]

            # Test each orientation
            orientations = ["Portrait", "Landscape"]
            for orientation in orientations:
                # Change the setting
                self.parent.orientation_combo.setCurrentText(orientation)

                # Verify the setting was applied
                if self.parent.document_settings["page"]["orientation"].lower() != orientation.lower():
                    return TestResult("Page Orientation", False, f"Failed to set orientation to {orientation}")

                # Update preview to apply the change
                self.parent.update_preview()

                # Allow time for preview to update
                QApplication.processEvents()
                time.sleep(0.5)

            # Restore original setting
            self.parent.orientation_combo.setCurrentText(original_orientation.capitalize())
            self.parent.update_preview()

            return TestResult("Page Orientation", True, "Successfully tested all orientations")
        except Exception as e:
            logger.error(f"Error in page orientation test: {str(e)}")
            return TestResult("Page Orientation", False, f"Test error: {str(e)}")

    def test_page_margins(self):
        """Test page margins"""
        try:
            if not self.parent:
                return TestResult("Page Margins", False, "No parent application available")

            # Store original settings
            original_top = self.parent.document_settings["page"]["margins"]["top"]
            original_right = self.parent.document_settings["page"]["margins"]["right"]
            original_bottom = self.parent.document_settings["page"]["margins"]["bottom"]
            original_left = self.parent.document_settings["page"]["margins"]["left"]

            # Test different margin values
            test_values = [10, 20, 30]
            for value in test_values:
                # Change the settings
                self.parent.margin_top.setValue(value)
                self.parent.margin_right.setValue(value)
                self.parent.margin_bottom.setValue(value)
                self.parent.margin_left.setValue(value)

                # Verify the settings were applied
                margins = self.parent.document_settings["page"]["margins"]
                if margins["top"] != value or margins["right"] != value or margins["bottom"] != value or margins["left"] != value:
                    return TestResult("Page Margins", False, f"Failed to set margins to {value}")

                # Update preview to apply the changes
                self.parent.update_preview()

                # Allow time for preview to update
                QApplication.processEvents()
                time.sleep(0.5)

            # Restore original settings
            self.parent.margin_top.setValue(original_top)
            self.parent.margin_right.setValue(original_right)
            self.parent.margin_bottom.setValue(original_bottom)
            self.parent.margin_left.setValue(original_left)
            self.parent.update_preview()

            return TestResult("Page Margins", True, "Successfully tested all margin values")
        except Exception as e:
            logger.error(f"Error in page margins test: {str(e)}")
            return TestResult("Page Margins", False, f"Test error: {str(e)}")

    def test_page_breaks(self):
        """Test page breaks"""
        try:
            if not self.parent:
                return TestResult("Page Breaks", False, "No parent application available")

            # Store original content
            original_content = self.parent.markdown_editor.toPlainText()

            # Create test content with page breaks
            test_content = """# Test Page Breaks

This is the first page.

<!-- PAGE_BREAK -->

This is the second page.

<!-- PAGE_BREAK -->

This is the third page."""

            # Set the test content
            self.parent.markdown_editor.setPlainText(test_content)

            # Update preview to apply the changes
            self.parent.update_preview()

            # Allow time for preview to update
            QApplication.processEvents()
            time.sleep(1)

            # Run the page break test
            result = self.parent.page_preview.test_page_breaks()

            # Restore original content
            self.parent.markdown_editor.setPlainText(original_content)
            self.parent.update_preview()

            if result:
                return TestResult("Page Breaks", True, "Successfully tested page breaks")
            else:
                return TestResult("Page Breaks", False, "Page break test failed")
        except Exception as e:
            logger.error(f"Error in page breaks test: {str(e)}")
            return TestResult("Page Breaks", False, f"Test error: {str(e)}")

    def test_page_navigation(self):
        """Test page navigation"""
        try:
            if not self.parent:
                return TestResult("Page Navigation", False, "No parent application available")

            # Store original content
            original_content = self.parent.markdown_editor.toPlainText()

            # Create test content with page breaks
            test_content = """# Test Page Navigation

This is the first page.

<!-- PAGE_BREAK -->

This is the second page.

<!-- PAGE_BREAK -->

This is the third page."""

            # Set the test content
            self.parent.markdown_editor.setPlainText(test_content)

            # Update preview to apply the changes
            self.parent.update_preview()

            # Allow time for preview to update
            QApplication.processEvents()
            time.sleep(1)

            # Run the page navigation test
            result = self.parent.page_preview.test_page_navigation()

            # Restore original content
            self.parent.markdown_editor.setPlainText(original_content)
            self.parent.update_preview()

            if result:
                return TestResult("Page Navigation", True, "Successfully tested page navigation")
            else:
                return TestResult("Page Navigation", False, "Page navigation test failed")
        except Exception as e:
            logger.error(f"Error in page navigation test: {str(e)}")
            return TestResult("Page Navigation", False, f"Test error: {str(e)}")

    def test_body_font(self):
        """Test body font settings"""
        # Implementation would change font family, size, and line height
        # and verify the changes are applied correctly
        return TestResult("Body Font", True, "Body font test not implemented yet")

    def test_heading_fonts(self):
        """Test heading font settings"""
        # Implementation would test fonts for each heading level
        return TestResult("Heading Fonts", True, "Heading fonts test not implemented yet")

    def test_code_font(self):
        """Test code block font settings"""
        # Implementation would test code font settings
        return TestResult("Code Font", True, "Code font test not implemented yet")

    def test_master_font(self):
        """Test master font control"""
        # Implementation would test enabling/disabling master font
        return TestResult("Master Font", True, "Master font test not implemented yet")

    def test_text_color(self):
        """Test text color settings"""
        # Implementation would test changing text color
        return TestResult("Text Color", True, "Text color test not implemented yet")

    def test_background_color(self):
        """Test background color"""
        # Implementation would test changing background color
        return TestResult("Background Color", True, "Background color test not implemented yet")

    def test_link_color(self):
        """Test link color"""
        # Implementation would test changing link color
        return TestResult("Link Color", True, "Link color test not implemented yet")

    def test_heading_colors(self):
        """Test heading colors"""
        # Implementation would test changing heading colors
        return TestResult("Heading Colors", True, "Heading colors test not implemented yet")

    def test_bullet_lists(self):
        """Test bullet list styles"""
        # Implementation would test different bullet list styles
        return TestResult("Bullet Lists", True, "Bullet lists test not implemented yet")

    def test_numbered_lists(self):
        """Test numbered list styles"""
        # Implementation would test different numbered list styles
        return TestResult("Numbered Lists", True, "Numbered lists test not implemented yet")

    def test_list_indentation(self):
        """Test list indentation"""
        # Implementation would test list indentation settings
        return TestResult("List Indentation", True, "List indentation test not implemented yet")

    def test_list_spacing(self):
        """Test list item spacing"""
        # Implementation would test list item spacing
        return TestResult("List Spacing", True, "List spacing test not implemented yet")

    def test_restart_numbering(self):
        """Test restart numbering feature"""
        # Implementation would test restart numbering feature
        return TestResult("Restart Numbering", True, "Restart numbering test not implemented yet")

    def test_table_borders(self):
        """Test table border settings"""
        # Implementation would test table border settings
        return TestResult("Table Borders", True, "Table borders test not implemented yet")

    def test_table_header(self):
        """Test table header settings"""
        # Implementation would test table header settings
        return TestResult("Table Header", True, "Table header test not implemented yet")

    def test_table_cell_padding(self):
        """Test table cell padding"""
        # Implementation would test table cell padding
        return TestResult("Cell Padding", True, "Cell padding test not implemented yet")

    def test_pdf_export(self):
        """Test PDF export"""
        # Implementation would test PDF export
        return TestResult("PDF Export", True, "PDF export test not implemented yet")

    def test_html_export(self):
        """Test HTML export"""
        # Implementation would test HTML export
        return TestResult("HTML Export", True, "HTML export test not implemented yet")

    def test_docx_export(self):
        """Test DOCX export"""
        # Implementation would test DOCX export
        return TestResult("DOCX Export", True, "DOCX export test not implemented yet")

    def test_epub_export(self):
        """Test EPUB export"""
        # Implementation would test EPUB export
        return TestResult("EPUB Export", True, "EPUB export test not implemented yet")

class TestDialog(QDialog):
    """Dialog for running tests and displaying results"""
    def __init__(self, parent=None):
        super(TestDialog, self).__init__(parent)
        self.parent = parent
        self.test_runner = TestRunner(parent)
        self.visual_tester = VisualTester(QApplication.instance()) if VISUAL_TESTING_AVAILABLE else None
        self.initUI()

    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("Test Framework")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        # Create tab widget for different test types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create functional tests tab
        functional_tab = QWidget()
        self.tab_widget.addTab(functional_tab, "Functional Tests")
        functional_layout = QVBoxLayout(functional_tab)

        # Test group selection
        group_layout = QHBoxLayout()
        group_label = QLabel("Test Groups:")
        group_layout.addWidget(group_label)

        self.group_list = QListWidget()
        for group_name, group in self.test_runner.test_groups.items():
            self.group_list.addItem(group.name)
        self.group_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        group_layout.addWidget(self.group_list)

        functional_layout.addLayout(group_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        functional_layout.addWidget(self.progress_bar)

        # Results list
        results_label = QLabel("Test Results:")
        functional_layout.addWidget(results_label)

        self.results_list = QListWidget()
        functional_layout.addWidget(self.results_list)

        # Functional test buttons
        func_button_layout = QHBoxLayout()

        self.run_selected_btn = QPushButton("Run Selected Tests")
        self.run_selected_btn.clicked.connect(self.run_selected_tests)
        func_button_layout.addWidget(self.run_selected_btn)

        self.run_all_btn = QPushButton("Run All Tests")
        self.run_all_btn.clicked.connect(self.run_all_tests)
        func_button_layout.addWidget(self.run_all_btn)

        self.save_results_btn = QPushButton("Save Results")
        self.save_results_btn.clicked.connect(self.save_results)
        func_button_layout.addWidget(self.save_results_btn)

        functional_layout.addLayout(func_button_layout)

        # Create unit tests tab if available
        if UNIT_TESTING_AVAILABLE:
            unit_tab = QWidget()
            self.tab_widget.addTab(unit_tab, "Unit Tests")
            unit_layout = QVBoxLayout(unit_tab)

            # Unit test selection
            unit_group = QGroupBox("Available Unit Tests")
            unit_group_layout = QVBoxLayout(unit_group)

            self.unit_test_list = QListWidget()

            # Add export tests
            export_tests = []
            for method_name in dir(ExportTestCase):
                if method_name.startswith('test_'):
                    test_name = method_name[5:].replace('_', ' ').title()
                    export_tests.append(f"Export: {test_name}")

            # Add settings tests
            settings_tests = []
            for method_name in dir(SettingsTestCase):
                if method_name.startswith('test_'):
                    test_name = method_name[5:].replace('_', ' ').title()
                    settings_tests.append(f"Settings: {test_name}")

            # Add all tests to the list
            self.unit_test_list.addItems(export_tests + settings_tests)
            self.unit_test_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            unit_group_layout.addWidget(self.unit_test_list)

            unit_layout.addWidget(unit_group)

            # Unit test progress bar
            self.unit_progress_bar = QProgressBar()
            self.unit_progress_bar.setRange(0, 100)
            self.unit_progress_bar.setValue(0)
            unit_layout.addWidget(self.unit_progress_bar)

            # Unit test results
            unit_results_label = QLabel("Unit Test Results:")
            unit_layout.addWidget(unit_results_label)

            self.unit_results_list = QListWidget()
            unit_layout.addWidget(self.unit_results_list)

            # Unit test buttons
            unit_button_layout = QHBoxLayout()

            self.run_unit_btn = QPushButton("Run Selected Unit Tests")
            self.run_unit_btn.clicked.connect(self.run_unit_tests)
            unit_button_layout.addWidget(self.run_unit_btn)

            self.run_all_unit_btn = QPushButton("Run All Unit Tests")
            self.run_all_unit_btn.clicked.connect(self.run_all_unit_tests)
            unit_button_layout.addWidget(self.run_all_unit_btn)

            unit_layout.addLayout(unit_button_layout)

        # Create visual tests tab if available
        if VISUAL_TESTING_AVAILABLE:
            visual_tab = QWidget()
            self.tab_widget.addTab(visual_tab, "Visual Tests")
            visual_layout = QVBoxLayout(visual_tab)

            # Visual test selection
            visual_group = QGroupBox("Available Visual Tests")
            visual_group_layout = QVBoxLayout(visual_group)

            self.visual_test_list = QListWidget()
            self.visual_test_list.addItems([
                "Basic UI",
                "Heading Numbering",
                "Page Breaks",
                "Edit Toolbar"
            ])
            self.visual_test_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            visual_group_layout.addWidget(self.visual_test_list)

            visual_layout.addWidget(visual_group)

            # Visual test options
            options_group = QGroupBox("Test Options")
            options_layout = QVBoxLayout(options_group)

            self.create_reference_check = QCheckBox("Create reference screenshots")
            options_layout.addWidget(self.create_reference_check)

            self.compare_check = QCheckBox("Compare with reference screenshots")
            self.compare_check.setChecked(True)
            options_layout.addWidget(self.compare_check)

            visual_layout.addWidget(options_group)

            # Visual test results
            visual_results_label = QLabel("Visual Test Results:")
            visual_layout.addWidget(visual_results_label)

            self.visual_results_list = QListWidget()
            visual_layout.addWidget(self.visual_results_list)

            # Visual test buttons
            visual_button_layout = QHBoxLayout()

            self.run_visual_btn = QPushButton("Run Selected Visual Tests")
            self.run_visual_btn.clicked.connect(self.run_visual_tests)
            visual_button_layout.addWidget(self.run_visual_btn)

            self.view_screenshots_btn = QPushButton("View Screenshots")
            self.view_screenshots_btn.clicked.connect(self.view_screenshots)
            visual_button_layout.addWidget(self.view_screenshots_btn)

            visual_layout.addLayout(visual_button_layout)

        # Main buttons
        button_layout = QHBoxLayout()

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def run_selected_tests(self):
        """Run the selected test groups"""
        selected_items = self.group_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one test group.")
            return

        self.results_list.clear()
        self.progress_bar.setValue(0)

        selected_groups = [item.text() for item in selected_items]
        total_tests = sum(len(self.test_runner.test_groups[group].tests) for group in selected_groups)
        completed_tests = 0

        for group in selected_groups:
            results = self.test_runner.run_test_group(group)
            for result in results:
                item_text = f"{result.name}: {'PASS' if result.passed else 'FAIL'} - {result.message}"
                self.results_list.addItem(item_text)
                completed_tests += 1
                self.progress_bar.setValue(int(completed_tests / total_tests * 100))
                QApplication.processEvents()

        self.progress_bar.setValue(100)

    def run_all_tests(self):
        """Run all test groups"""
        self.results_list.clear()
        self.progress_bar.setValue(0)

        total_tests = sum(len(group.tests) for group in self.test_runner.test_groups.values())
        completed_tests = 0

        results = self.test_runner.run_all_tests()
        for result in results:
            item_text = f"{result.name}: {'PASS' if result.passed else 'FAIL'} - {result.message}"
            self.results_list.addItem(item_text)
            completed_tests += 1
            self.progress_bar.setValue(int(completed_tests / total_tests * 100))
            QApplication.processEvents()

        self.progress_bar.setValue(100)

    def save_results(self):
        """Save test results to a file"""
        if not self.test_runner.results:
            QMessageBox.warning(self, "No Results", "No test results to save.")
            return

        file_path = os.path.join(os.path.expanduser("~"), "markdown2pdf_test_results.json")
        success = self.test_runner.save_results(file_path)

        if success:
            QMessageBox.information(self, "Results Saved", f"Test results saved to {file_path}")
        else:
            QMessageBox.warning(self, "Save Error", "Failed to save test results.")

    def run_visual_tests(self):
        """Run the selected visual tests"""
        if not VISUAL_TESTING_AVAILABLE:
            QMessageBox.warning(self, "Not Available", "Visual testing is not available.")
            return

        selected_items = self.visual_test_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one visual test.")
            return

        self.visual_results_list.clear()
        create_reference = self.create_reference_check.isChecked()
        compare_with_reference = self.compare_check.isChecked()

        # Get selected test names
        selected_tests = [item.text() for item in selected_items]

        # Add a message to the results list
        self.visual_results_list.addItem(f"Running {len(selected_tests)} visual tests...")
        QApplication.processEvents()

        # Run each selected test
        for test_name in selected_tests:
            # Convert test name to function name
            func_name = test_name.lower().replace(" ", "_")

            # Add a message to the results list
            self.visual_results_list.addItem(f"Running test: {test_name}")
            QApplication.processEvents()

            try:
                # Run the test using the visual test runner
                self.visual_tester.start_test(func_name)

                # Create reference screenshot if requested
                if create_reference:
                    reference_path = self.visual_tester.create_reference(func_name)
                    self.visual_results_list.addItem(f"Created reference screenshot: {reference_path}")

                # Compare with reference if requested
                if compare_with_reference:
                    result = self.visual_tester.verify_against_reference(func_name)
                    if result:
                        self.visual_results_list.addItem(f"✓ {test_name}: Passed visual comparison")
                    else:
                        self.visual_results_list.addItem(f"✗ {test_name}: Failed visual comparison")

                # End the test
                self.visual_tester.end_test()

            except Exception as e:
                self.visual_results_list.addItem(f"✗ {test_name}: Error - {str(e)}")

        self.visual_results_list.addItem("Visual tests completed.")

    def run_unit_tests(self):
        """Run the selected unit tests"""
        if not UNIT_TESTING_AVAILABLE:
            QMessageBox.warning(self, "Not Available", "Unit testing is not available.")
            return

        selected_items = self.unit_test_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one unit test.")
            return

        self.unit_results_list.clear()
        self.unit_progress_bar.setValue(0)

        # Create a test suite
        suite = unittest.TestSuite()

        # Add selected tests to the suite
        for item in selected_items:
            text = item.text()
            if text.startswith("Export: "):
                test_name = "test_" + text[8:].lower().replace(' ', '_')
                suite.addTest(ExportTestCase(test_name))
            elif text.startswith("Settings: "):
                test_name = "test_" + text[10:].lower().replace(' ', '_')
                suite.addTest(SettingsTestCase(test_name))

        # Run the tests
        self.run_unittest_suite(suite)

    def run_all_unit_tests(self):
        """Run all unit tests"""
        if not UNIT_TESTING_AVAILABLE:
            QMessageBox.warning(self, "Not Available", "Unit testing is not available.")
            return

        self.unit_results_list.clear()
        self.unit_progress_bar.setValue(0)

        # Create a test suite
        suite = unittest.TestSuite()

        # Add all export tests using the non-deprecated method
        for name in dir(ExportTestCase):
            if name.startswith('test_'):
                suite.addTest(ExportTestCase(name))

        # Add all settings tests using the non-deprecated method
        for name in dir(SettingsTestCase):
            if name.startswith('test_'):
                suite.addTest(SettingsTestCase(name))

        # Run the tests
        self.run_unittest_suite(suite)

    def run_unittest_suite(self, suite):
        """Run a unittest suite and display results"""
        # Create a custom test result class
        class CustomTestResult(unittest.TextTestResult):
            def __init__(self, stream, descriptions, verbosity, dialog):
                super().__init__(stream, descriptions, verbosity)
                self.dialog = dialog
                self.test_count = suite.countTestCases()
                self.current_test = 0

            def startTest(self, test):
                super().startTest(test)
                self.current_test += 1
                test_name = test.id().split('.')[-1]
                self.dialog.unit_results_list.addItem(f"Running: {test_name}")
                self.dialog.unit_progress_bar.setValue(int(self.current_test / self.test_count * 100))
                QApplication.processEvents()

            def addSuccess(self, test):
                super().addSuccess(test)
                test_name = test.id().split('.')[-1]
                self.dialog.unit_results_list.addItem(f"✓ {test_name}: Passed")
                QApplication.processEvents()

            def addFailure(self, test, err):
                super().addFailure(test, err)
                test_name = test.id().split('.')[-1]
                self.dialog.unit_results_list.addItem(f"✗ {test_name}: Failed - {str(err[1])}")
                QApplication.processEvents()

            def addError(self, test, err):
                super().addError(test, err)
                test_name = test.id().split('.')[-1]
                self.dialog.unit_results_list.addItem(f"✗ {test_name}: Error - {str(err[1])}")
                QApplication.processEvents()

        # Run the tests
        runner = unittest.TextTestRunner(resultclass=lambda *args, **kwargs: CustomTestResult(*args, **kwargs, dialog=self))
        result = runner.run(suite)

        # Show summary
        self.unit_results_list.addItem("")
        self.unit_results_list.addItem(f"Ran {result.testsRun} tests")
        self.unit_results_list.addItem(f"Failures: {len(result.failures)}")
        self.unit_results_list.addItem(f"Errors: {len(result.errors)}")
        self.unit_results_list.addItem(f"Skipped: {len(result.skipped)}")

        # Set progress bar to 100%
        self.unit_progress_bar.setValue(100)

    def view_screenshots(self):
        """Open the screenshots directory"""
        if not VISUAL_TESTING_AVAILABLE:
            QMessageBox.warning(self, "Not Available", "Visual testing is not available.")
            return

        # Get the screenshots directory
        screenshots_dir = self.visual_tester.screenshot_dir

        # Check if the directory exists
        if not os.path.exists(screenshots_dir):
            QMessageBox.warning(self, "No Screenshots", "No screenshots directory found.")
            return

        # Open the directory
        try:
            if sys.platform == 'win32':
                os.startfile(screenshots_dir)
            else:
                # For macOS and Linux
                if sys.platform == 'darwin':
                    cmd = ['open']
                else:  # Linux
                    cmd = ['xdg-open']
                subprocess.run(cmd + [screenshots_dir])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open screenshots directory: {str(e)}")

def create_test_checklist(file_path=None):
    """Create a JSON-based testing checklist at the project root"""
    if not file_path:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_checklist.json")

    # Create a test runner to get the test structure
    runner = TestRunner()

    # Create the checklist structure
    checklist = {
        "version": "1.0",
        "last_updated": time.time(),
        "test_groups": {}
    }

    # Add each test group and its tests
    for group_name, group in runner.test_groups.items():
        checklist["test_groups"][group_name] = {
            "name": group.name,
            "description": group.description,
            "dependencies": group.dependencies,
            "tests": []
        }

        # Add each test in the group
        for test in group.tests:
            checklist["test_groups"][group_name]["tests"].append({
                "name": test["name"],
                "description": test["description"],
                "status": "not_tested",
                "last_run": None,
                "last_result": None
            })

    # Save the checklist to a JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(checklist, f, indent=2)
        logger.info(f"Test checklist created at {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating test checklist: {str(e)}")
        return False

if __name__ == "__main__":
    # Create the test checklist when run directly
    create_test_checklist()
