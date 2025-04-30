#!/usr/bin/env python3
"""
Template Manager for Markdown to PDF Converter
---------------------------------------------
This module provides a user interface for managing custom templates.
"""

import os
import sys
import json
import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QTabWidget, QWidget, QFormLayout, QLineEdit,
    QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from logging_config import get_logger

# Get the properly configured logger
logger = get_logger()

class TemplateManager(QDialog):
    """Dialog for managing custom templates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Template Manager")
        self.setMinimumSize(600, 400)
        
        # Get the templates directory
        self.templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize UI
        self.init_ui()
        
        # Load templates
        self.load_templates()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.latex_tab = QWidget()
        self.css_tab = QWidget()
        self.docx_tab = QWidget()
        
        self.tabs.addTab(self.latex_tab, "LaTeX Templates")
        self.tabs.addTab(self.css_tab, "CSS Templates")
        self.tabs.addTab(self.docx_tab, "DOCX Templates")
        
        # Setup each tab
        self.setup_latex_tab()
        self.setup_css_tab()
        self.setup_docx_tab()
        
        # Add tabs to main layout
        main_layout.addWidget(self.tabs)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)
    
    def setup_latex_tab(self):
        """Setup the LaTeX templates tab"""
        layout = QVBoxLayout(self.latex_tab)
        
        # Template list
        self.latex_list = QListWidget()
        self.latex_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(QLabel("LaTeX Templates:"))
        layout.addWidget(self.latex_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Template")
        add_button.clicked.connect(lambda: self.add_template('latex'))
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Template")
        edit_button.clicked.connect(lambda: self.edit_template('latex'))
        button_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Template")
        remove_button.clicked.connect(lambda: self.remove_template('latex'))
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
    
    def setup_css_tab(self):
        """Setup the CSS templates tab"""
        layout = QVBoxLayout(self.css_tab)
        
        # Template list
        self.css_list = QListWidget()
        self.css_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(QLabel("CSS Templates:"))
        layout.addWidget(self.css_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Template")
        add_button.clicked.connect(lambda: self.add_template('css'))
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Template")
        edit_button.clicked.connect(lambda: self.edit_template('css'))
        button_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Template")
        remove_button.clicked.connect(lambda: self.remove_template('css'))
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
    
    def setup_docx_tab(self):
        """Setup the DOCX templates tab"""
        layout = QVBoxLayout(self.docx_tab)
        
        # Template list
        self.docx_list = QListWidget()
        self.docx_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(QLabel("DOCX Templates:"))
        layout.addWidget(self.docx_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Template")
        add_button.clicked.connect(lambda: self.add_template('docx'))
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove Template")
        remove_button.clicked.connect(lambda: self.remove_template('docx'))
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
    
    def load_templates(self):
        """Load templates from the templates directory"""
        # Clear lists
        self.latex_list.clear()
        self.css_list.clear()
        self.docx_list.clear()
        
        # Load templates
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.latex'):
                self.latex_list.addItem(filename)
            elif filename.endswith('.css'):
                self.css_list.addItem(filename)
            elif filename.endswith('.docx'):
                self.docx_list.addItem(filename)
    
    def add_template(self, template_type):
        """Add a new template"""
        if template_type == 'latex':
            # Create a new LaTeX template
            name, ok = QFileDialog.getSaveFileName(
                self, "Save LaTeX Template", self.templates_dir,
                "LaTeX Templates (*.latex)"
            )
            if ok and name:
                # Copy the default template as a starting point
                default_template = os.path.join(self.templates_dir, 'custom.latex')
                if os.path.exists(default_template):
                    shutil.copy(default_template, name)
                else:
                    # Create an empty file
                    with open(name, 'w') as f:
                        f.write("% Custom LaTeX Template\n")
                
                # Reload templates
                self.load_templates()
        
        elif template_type == 'css':
            # Create a new CSS template
            name, ok = QFileDialog.getSaveFileName(
                self, "Save CSS Template", self.templates_dir,
                "CSS Templates (*.css)"
            )
            if ok and name:
                # Copy the default template as a starting point
                default_template = os.path.join(self.templates_dir, 'custom.css')
                if os.path.exists(default_template):
                    shutil.copy(default_template, name)
                else:
                    # Create an empty file
                    with open(name, 'w') as f:
                        f.write("/* Custom CSS Template */\n")
                
                # Reload templates
                self.load_templates()
        
        elif template_type == 'docx':
            # Import a DOCX template
            name, _ = QFileDialog.getOpenFileName(
                self, "Import DOCX Template", "",
                "DOCX Files (*.docx)"
            )
            if name:
                # Copy the file to the templates directory
                dest = os.path.join(self.templates_dir, os.path.basename(name))
                shutil.copy(name, dest)
                
                # Reload templates
                self.load_templates()
    
    def edit_template(self, template_type):
        """Edit a template"""
        if template_type == 'latex':
            # Get the selected template
            selected_items = self.latex_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "No template selected")
                return
            
            template_name = selected_items[0].text()
            template_path = os.path.join(self.templates_dir, template_name)
            
            # Open the template in the default text editor
            if sys.platform == 'win32':
                os.startfile(template_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{template_path}"')
            else:  # Linux
                os.system(f'xdg-open "{template_path}"')
        
        elif template_type == 'css':
            # Get the selected template
            selected_items = self.css_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "No template selected")
                return
            
            template_name = selected_items[0].text()
            template_path = os.path.join(self.templates_dir, template_name)
            
            # Open the template in the default text editor
            if sys.platform == 'win32':
                os.startfile(template_path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{template_path}"')
            else:  # Linux
                os.system(f'xdg-open "{template_path}"')
    
    def remove_template(self, template_type):
        """Remove a template"""
        if template_type == 'latex':
            # Get the selected template
            selected_items = self.latex_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "No template selected")
                return
            
            template_name = selected_items[0].text()
            
            # Confirm deletion
            if template_name == 'custom.latex':
                QMessageBox.warning(self, "Warning", "Cannot delete the default template")
                return
            
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the template '{template_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete the template
                template_path = os.path.join(self.templates_dir, template_name)
                os.remove(template_path)
                
                # Reload templates
                self.load_templates()
        
        elif template_type == 'css':
            # Get the selected template
            selected_items = self.css_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "No template selected")
                return
            
            template_name = selected_items[0].text()
            
            # Confirm deletion
            if template_name == 'custom.css':
                QMessageBox.warning(self, "Warning", "Cannot delete the default template")
                return
            
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the template '{template_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete the template
                template_path = os.path.join(self.templates_dir, template_name)
                os.remove(template_path)
                
                # Reload templates
                self.load_templates()
        
        elif template_type == 'docx':
            # Get the selected template
            selected_items = self.docx_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "No template selected")
                return
            
            template_name = selected_items[0].text()
            
            # Confirm deletion
            if template_name == 'reference.docx':
                QMessageBox.warning(self, "Warning", "Cannot delete the default template")
                return
            
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the template '{template_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete the template
                template_path = os.path.join(self.templates_dir, template_name)
                os.remove(template_path)
                
                # Reload templates
                self.load_templates()
