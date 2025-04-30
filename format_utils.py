#!/usr/bin/env python3
"""
Format Utilities for Markdown to PDF Converter
---------------------------------------------
Contains dialogs and utilities for formatting Markdown documents.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, 
    QSpinBox, QFormLayout, QLineEdit, QGroupBox, QCheckBox, QTabWidget,
    QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem, QWidget
)
from PyQt6.QtCore import Qt

class PageBreakDialog(QDialog):
    """Dialog for inserting and managing page breaks"""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Insert Page Break")
        
        layout = QVBoxLayout()
        
        # Add information label
        info_label = QLabel("Insert page break at cursor position?")
        layout.addWidget(info_label)
        
        # Add buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        
        insert_button.clicked.connect(self.insert_page_break)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def insert_page_break(self):
        """Insert a page break at the current cursor position"""
        # Insert HTML-style page break comment that will be converted correctly by pandoc
        self.editor.insertPlainText("\n\n<!-- PAGE_BREAK -->\n\n")
        self.accept()


class HorizontalLineDialog(QDialog):
    """Dialog for inserting customized horizontal lines"""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Insert Horizontal Line")
        
        layout = QVBoxLayout()
        
        # Add options
        form_layout = QFormLayout()
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Solid", "Dashed", "Dotted", "Double"])
        form_layout.addRow("Line Style:", self.style_combo)
        
        self.thickness = QSpinBox()
        self.thickness.setRange(1, 10)
        self.thickness.setValue(1)
        form_layout.addRow("Thickness (px):", self.thickness)
        
        self.width_combo = QComboBox()
        self.width_combo.addItems(["100%", "75%", "50%", "25%"])
        form_layout.addRow("Width:", self.width_combo)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        
        insert_button.clicked.connect(self.insert_horizontal_line)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def insert_horizontal_line(self):
        """Insert a horizontal line at the current cursor position"""
        style = self.style_combo.currentText().lower()
        thickness = self.thickness.value()
        width = self.width_combo.currentText()
        
        # Create HTML for the horizontal line with custom styling
        html = f"\n\n<hr style=\"border-style: {style}; border-width: {thickness}px; width: {width};\" />\n\n"
        
        # Insert the HTML at the cursor position
        self.editor.insertPlainText(html)
        self.accept()


class ColumnLayoutDialog(QDialog):
    """Dialog for creating multi-column layouts"""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Create Column Layout")
        
        layout = QVBoxLayout()
        
        # Column options
        form_layout = QFormLayout()
        
        self.num_columns = QSpinBox()
        self.num_columns.setRange(2, 4)
        self.num_columns.setValue(2)
        form_layout.addRow("Number of Columns:", self.num_columns)
        
        self.column_gap = QSpinBox()
        self.column_gap.setRange(10, 50)
        self.column_gap.setValue(20)
        form_layout.addRow("Column Gap (px):", self.column_gap)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        
        insert_button.clicked.connect(self.insert_column_layout)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def insert_column_layout(self):
        """Insert a column layout at the current cursor position"""
        num_columns = self.num_columns.value()
        gap = self.column_gap.value()
        
        # Create HTML for the column layout
        html = f"\n\n<div style=\"display: flex; column-gap: {gap}px;\">\n"
        
        for i in range(num_columns):
            html += f"<div style=\"flex: 1;\">\n"
            html += "Column " + str(i+1) + " content here\n"
            html += "</div>\n"
        
        html += "</div>\n\n"
        
        # Insert the HTML at the cursor position
        self.editor.insertPlainText(html)
        self.accept()


class TableCreationDialog(QDialog):
    """Dialog for creating and inserting tables"""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Create Table")
        
        layout = QVBoxLayout()
        
        # Table dimensions
        dimensions_layout = QFormLayout()
        
        self.rows = QSpinBox()
        self.rows.setRange(1, 20)
        self.rows.setValue(3)
        self.rows.valueChanged.connect(self.update_table_preview)
        dimensions_layout.addRow("Rows:", self.rows)
        
        self.columns = QSpinBox()
        self.columns.setRange(1, 10)
        self.columns.setValue(3)
        self.columns.valueChanged.connect(self.update_table_preview)
        dimensions_layout.addRow("Columns:", self.columns)
        
        layout.addLayout(dimensions_layout)
        
        # Table styling options
        styling_group = QGroupBox("Table Style")
        styling_layout = QFormLayout()
        
        self.header_row = QCheckBox("Include Header Row")
        self.header_row.setChecked(True)
        self.header_row.stateChanged.connect(self.update_table_preview)
        styling_layout.addRow(self.header_row)
        
        self.alignment = QComboBox()
        self.alignment.addItems(["Left", "Center", "Right"])
        self.alignment.setCurrentText("Left")
        styling_layout.addRow("Text Alignment:", self.alignment)
        
        styling_group.setLayout(styling_layout)
        layout.addWidget(styling_group)
        
        # Table preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.table_preview = QTableWidget()
        self.update_table_preview()
        
        preview_layout.addWidget(self.table_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Add buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        
        insert_button.clicked.connect(self.insert_table)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_table_preview(self):
        """Update the table preview widget"""
        rows = self.rows.value()
        cols = self.columns.value()
        has_header = self.header_row.isChecked()
        
        self.table_preview.setRowCount(rows)
        self.table_preview.setColumnCount(cols)
        
        # Set header row if enabled
        if has_header:
            for col in range(cols):
                self.table_preview.setItem(0, col, QTableWidgetItem(f"Header {col+1}"))
        
        # Set placeholder content for other cells
        start_row = 1 if has_header else 0
        for row in range(start_row, rows):
            for col in range(cols):
                self.table_preview.setItem(row, col, QTableWidgetItem(f"R{row+1}C{col+1}"))
    
    def insert_table(self):
        """Generate and insert Markdown table at the current cursor position"""
        rows = self.rows.value()
        cols = self.columns.value()
        has_header = self.header_row.isChecked()
        alignment = self.alignment.currentText().lower()
        
        # Create a Markdown table
        markdown_table = "\n\n"
        
        # Create header row if needed
        if has_header:
            header_row = "| "
            for col in range(cols):
                header_row += f"Header {col+1} | "
            markdown_table += header_row + "\n"
            
            # Add separator row with alignment
            separator = "| "
            for col in range(cols):
                if alignment == "left":
                    separator += ":--- | "
                elif alignment == "center":
                    separator += ":---: | "
                elif alignment == "right":
                    separator += "---: | "
            markdown_table += separator + "\n"
        
        # Create data rows
        start_row = 1 if has_header else 0
        for row in range(start_row, rows):
            data_row = "| "
            for col in range(cols):
                data_row += f"R{row+1}C{col+1} | "
            markdown_table += data_row + "\n"
        
        markdown_table += "\n"
        
        # Insert the markdown table at the cursor position
        self.editor.insertPlainText(markdown_table)
        self.accept()


class IndentationDialog(QDialog):
    """Dialog for inserting and managing text indentation"""
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Insert Indentation")
        
        layout = QVBoxLayout()
        
        # Indentation options
        tabs = QTabWidget()
        
        # Block indent tab
        block_widget = QWidget()
        block_layout = QFormLayout()
        
        self.block_size = QSpinBox()
        self.block_size.setRange(10, 200)
        self.block_size.setValue(40)
        block_layout.addRow("Indent Size (px):", self.block_size)
        
        self.indent_type = QComboBox()
        self.indent_type.addItems(["Left", "Right", "Both"])
        block_layout.addRow("Indent Type:", self.indent_type)
        
        block_widget.setLayout(block_layout)
        tabs.addTab(block_widget, "Block Indent")
        
        # First-line indent tab
        first_line_widget = QWidget()
        first_line_layout = QFormLayout()
        
        self.first_line_size = QSpinBox()
        self.first_line_size.setRange(10, 100)
        self.first_line_size.setValue(20)
        first_line_layout.addRow("First Line Indent (px):", self.first_line_size)
        
        first_line_widget.setLayout(first_line_layout)
        tabs.addTab(first_line_widget, "First Line Indent")
        
        layout.addWidget(tabs)
        
        # Add buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        
        insert_button.clicked.connect(lambda: self.apply_indentation(tabs.currentIndex()))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_indentation(self, tab_index):
        """Apply the selected indentation to the current selection or cursor position"""
        if tab_index == 0:  # Block indent
            size = self.block_size.value()
            indent_type = self.indent_type.currentText().lower()
            
            # Create HTML for the indented block
            margins = ""
            if indent_type == "left":
                margins = f"margin-left: {size}px;"
            elif indent_type == "right":
                margins = f"margin-right: {size}px;"
            elif indent_type == "both":
                margins = f"margin-left: {size}px; margin-right: {size}px;"
            
            html = f"\n\n<div style=\"{margins}\">\nIndented text here\n</div>\n\n"
            
        else:  # First-line indent
            size = self.first_line_size.value()
            html = f"\n\n<p style=\"text-indent: {size}px;\">\nThis paragraph has its first line indented.\n</p>\n\n"
        
        # Insert the HTML at the cursor position
        self.editor.insertPlainText(html)
        self.accept()


class MarginsDialog(QDialog):
    """Dialog for setting custom page margins"""
    def __init__(self, editor, document_settings, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.document_settings = document_settings
        self.setWindowTitle("Set Page Margins")
        
        layout = QVBoxLayout()
        
        # Margin inputs
        form_layout = QFormLayout()
        
        self.top_margin = QSpinBox()
        self.top_margin.setRange(0, 100)
        self.top_margin.setValue(int(document_settings["page"]["margins"]["top"]))
        form_layout.addRow("Top Margin (mm):", self.top_margin)
        
        self.right_margin = QSpinBox()
        self.right_margin.setRange(0, 100)
        self.right_margin.setValue(int(document_settings["page"]["margins"]["right"]))
        form_layout.addRow("Right Margin (mm):", self.right_margin)
        
        self.bottom_margin = QSpinBox()
        self.bottom_margin.setRange(0, 100)
        self.bottom_margin.setValue(int(document_settings["page"]["margins"]["bottom"]))
        form_layout.addRow("Bottom Margin (mm):", self.bottom_margin)
        
        self.left_margin = QSpinBox()
        self.left_margin.setRange(0, 100)
        self.left_margin.setValue(int(document_settings["page"]["margins"]["left"]))
        form_layout.addRow("Left Margin (mm):", self.left_margin)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply")
        cancel_button = QPushButton("Cancel")
        
        apply_button.clicked.connect(self.apply_margins)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_margins(self):
        """Apply the custom margins to the document settings"""
        # Update the document settings
        self.document_settings["page"]["margins"]["top"] = self.top_margin.value()
        self.document_settings["page"]["margins"]["right"] = self.right_margin.value()
        self.document_settings["page"]["margins"]["bottom"] = self.bottom_margin.value()
        self.document_settings["page"]["margins"]["left"] = self.left_margin.value()
        
        # Insert a comment indicating the custom margins
        margin_comment = f"\n<!-- Custom Margins: Top={self.top_margin.value()}mm, Right={self.right_margin.value()}mm, Bottom={self.bottom_margin.value()}mm, Left={self.left_margin.value()}mm -->\n"
        self.editor.insertPlainText(margin_comment)
        
        self.accept()


class FormatUtils:
    """Static methods for document formatting utilities"""
    
    @staticmethod
    def show_page_break_dialog(editor, parent=None):
        """Show the page break dialog"""
        dialog = PageBreakDialog(editor, parent)
        return dialog.exec()
    
    @staticmethod
    def show_horizontal_line_dialog(editor, parent=None):
        """Show the horizontal line dialog"""
        dialog = HorizontalLineDialog(editor, parent)
        return dialog.exec()
    
    @staticmethod
    def show_column_layout_dialog(editor, parent=None):
        """Show the column layout dialog"""
        dialog = ColumnLayoutDialog(editor, parent)
        return dialog.exec()
    
    @staticmethod
    def show_table_creation_dialog(editor, parent=None):
        """Show the table creation dialog"""
        dialog = TableCreationDialog(editor, parent)
        return dialog.exec()
    
    @staticmethod
    def show_indentation_dialog(editor, parent=None):
        """Show the indentation dialog"""
        dialog = IndentationDialog(editor, parent)
        return dialog.exec()
    
    @staticmethod
    def show_margins_dialog(editor, document_settings, parent=None):
        """Show the margins dialog"""
        dialog = MarginsDialog(editor, document_settings, parent)
        return dialog.exec()