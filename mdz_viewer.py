#!/usr/bin/env python3
"""
MDZ Viewer and Extractor
------------------------
This module provides a standalone viewer and extractor for MDZ files.

File: mdz_viewer.py
"""

import os
import sys
import tempfile
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QSplitter, QTabWidget, QTextEdit, QMessageBox, QMenu, QToolBar,
    QStatusBar, QComboBox, QCheckBox, QGroupBox, QRadioButton,
    QProgressBar, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent, QAction
from PyQt6.QtCore import Qt, QSize, QMimeData, QUrl, QThread, pyqtSignal

# Import the unified MDZ module
from unified_mdz import UnifiedMDZ, CompressionMethod, get_mdz_info

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class FileTypeFilterDialog(QDialog):
    """Dialog for selecting file types to extract"""
    
    def __init__(self, file_types: Dict[str, int], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select File Types to Extract")
        self.setMinimumWidth(300)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create list widget
        self.list_widget = QListWidget()
        
        # Add "All Files" option
        all_item = QListWidgetItem("All Files")
        all_item.setCheckState(Qt.CheckState.Checked)
        self.list_widget.addItem(all_item)
        
        # Add file types
        for ext, count in file_types.items():
            item = QListWidgetItem(f"{ext} ({count} files)")
            item.setData(Qt.ItemDataRole.UserRole, ext)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_selected_types(self) -> List[str]:
        """Get the selected file types"""
        selected_types = []
        
        # Check if "All Files" is selected
        if self.list_widget.item(0).checkState() == Qt.CheckState.Checked:
            return []  # Empty list means all files
        
        # Get selected file types
        for i in range(1, self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_types.append(item.data(Qt.ItemDataRole.UserRole))
        
        return selected_types

class MDZViewerWindow(QMainWindow):
    """Main window for the MDZ viewer"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize variables
        self.current_mdz_file = None
        self.current_mdz_bundle = None
        self.temp_dir = None
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("MDZ Viewer")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create file tree
        self.create_file_tree(splitter)
        
        # Create content tabs
        self.create_content_tabs(splitter)
        
        # Set splitter sizes
        splitter.setSizes([200, 600])
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Set up drag and drop
        self.setAcceptDrops(True)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Open action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_mdz_file)
        toolbar.addAction(open_action)
        
        # Extract action
        extract_action = QAction("Extract All", self)
        extract_action.triggered.connect(self.extract_all)
        toolbar.addAction(extract_action)
        
        # Extract selected action
        extract_selected_action = QAction("Extract Selected", self)
        extract_selected_action.triggered.connect(self.extract_selected)
        toolbar.addAction(extract_selected_action)
        
        # Extract by type action
        extract_by_type_action = QAction("Extract by Type", self)
        extract_by_type_action.triggered.connect(self.extract_by_type)
        toolbar.addAction(extract_by_type_action)
        
        # Properties action
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(self.show_properties)
        toolbar.addAction(properties_action)
    
    def create_file_tree(self, parent):
        """Create the file tree widget"""
        # Create group box
        group_box = QGroupBox("Files")
        layout = QVBoxLayout(group_box)
        
        # Create tree widget
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size"])
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.itemDoubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.file_tree)
        
        parent.addWidget(group_box)
    
    def create_content_tabs(self, parent):
        """Create the content tabs"""
        # Create group box
        group_box = QGroupBox("Content")
        layout = QVBoxLayout(group_box)
        
        # Create tab widget
        self.content_tabs = QTabWidget()
        layout.addWidget(self.content_tabs)
        
        # Create text view tab
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.content_tabs.addTab(self.text_view, "Text View")
        
        # Create info tab
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        self.content_tabs.addTab(self.info_view, "File Info")
        
        parent.addWidget(group_box)
    
    def open_mdz_file(self):
        """Open an MDZ file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MDZ File", "", "MDZ Files (*.mdz);;All Files (*)"
        )
        
        if file_path:
            self.load_mdz_file(file_path)
    
    def load_mdz_file(self, file_path):
        """Load an MDZ file"""
        try:
            # Clean up any previous MDZ bundle
            self.cleanup_mdz()
            
            # Update status
            self.statusBar.showMessage(f"Loading {file_path}...")
            
            # Create a new MDZ bundle
            self.current_mdz_bundle = UnifiedMDZ()
            
            # Load the MDZ bundle
            self.current_mdz_bundle.load(file_path)
            
            # Extract to a temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="mdz_viewer_")
            self.current_mdz_bundle.extract_to_directory(self.temp_dir)
            
            # Update the file tree
            self.update_file_tree()
            
            # Update the window title
            self.current_mdz_file = file_path
            self.setWindowTitle(f"MDZ Viewer - {os.path.basename(file_path)}")
            
            # Show file info
            self.show_file_info()
            
            # Update status
            self.statusBar.showMessage(f"Loaded {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading MDZ file: {str(e)}")
            logger.error(f"Error loading MDZ file: {str(e)}")
            self.statusBar.showMessage("Error loading file")
    
    def update_file_tree(self):
        """Update the file tree with the contents of the MDZ bundle"""
        if not self.current_mdz_bundle:
            return
        
        # Clear the tree
        self.file_tree.clear()
        
        # Create root item
        root_item = QTreeWidgetItem(self.file_tree, ["Root"])
        root_item.setExpanded(True)
        
        # Add directories
        directories = {}
        for path in self.current_mdz_bundle.get_directory_list():
            # Create directory items
            parts = path.strip('/').split('/')
            parent = root_item
            
            # Create parent directories if needed
            current_path = ""
            for i, part in enumerate(parts):
                current_path += part + "/"
                if current_path in directories:
                    parent = directories[current_path]
                else:
                    item = QTreeWidgetItem(parent, [part])
                    directories[current_path] = item
                    parent = item
        
        # Add files
        file_sizes = self.current_mdz_bundle.get_file_sizes()
        for path in self.current_mdz_bundle.get_file_list():
            # Get the parent directory
            dir_path = os.path.dirname(path)
            if dir_path:
                dir_path += "/"
                parent = directories.get(dir_path, root_item)
            else:
                parent = root_item
            
            # Create file item
            file_name = os.path.basename(path)
            file_size = file_sizes.get(path, 0)
            item = QTreeWidgetItem(parent, [file_name, self.format_size(file_size)])
            item.setData(0, Qt.ItemDataRole.UserRole, path)
        
        # Resize columns
        self.file_tree.resizeColumnToContents(0)
        self.file_tree.resizeColumnToContents(1)
    
    def format_size(self, size_bytes):
        """Format a file size in bytes to a human-readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def show_file_info(self):
        """Show information about the MDZ file"""
        if not self.current_mdz_file or not self.current_mdz_bundle:
            return
        
        try:
            # Get file information
            info = get_mdz_info(self.current_mdz_file)
            
            # Format the information
            info_text = f"MDZ File: {self.current_mdz_file}\n"
            info_text += f"File Size: {self.format_size(info['file_size'])}\n"
            info_text += f"Compression Method: {info['compression_method']}\n"
            info_text += f"Compression Ratio: {info['compression_ratio']:.2f}x\n"
            info_text += f"Total Uncompressed Size: {self.format_size(info['total_uncompressed_size'])}\n"
            info_text += f"File Count: {info['file_count']}\n"
            info_text += f"Directory Count: {info['directory_count']}\n\n"
            
            info_text += "File Types:\n"
            for ext, count in info['file_types'].items():
                info_text += f"  {ext}: {count}\n"
            
            info_text += "\nMetadata:\n"
            for key, value in info['metadata'].items():
                info_text += f"  {key}: {value}\n"
            
            # Update the info view
            self.info_view.setPlainText(info_text)
            
            # Switch to the info tab
            self.content_tabs.setCurrentWidget(self.info_view)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting file information: {str(e)}")
            logger.error(f"Error getting file information: {str(e)}")
    
    def show_properties(self):
        """Show properties of the MDZ file"""
        self.show_file_info()
    
    def item_double_clicked(self, item, column):
        """Handle double-click on a file tree item"""
        # Get the file path
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path:
            return
        
        # Get the file content
        content = self.current_mdz_bundle.content.get(path)
        if content is None:
            return
        
        # Check if it's a text file
        if isinstance(content, str):
            # Show the content in the text view
            self.text_view.setPlainText(content)
            self.content_tabs.setCurrentWidget(self.text_view)
        else:
            # Try to open the file with the default application
            try:
                file_path = os.path.join(self.temp_dir, path)
                if os.path.exists(file_path):
                    import subprocess
                    if sys.platform == 'win32':
                        os.startfile(file_path)
                    elif sys.platform == 'darwin':
                        subprocess.call(['open', file_path])
                    else:
                        subprocess.call(['xdg-open', file_path])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error opening file: {str(e)}")
                logger.error(f"Error opening file: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for file tree items"""
        # Get the selected item
        item = self.file_tree.itemAt(position)
        if not item:
            return
        
        # Create context menu
        menu = QMenu()
        
        # Add actions
        extract_action = menu.addAction("Extract")
        extract_action.triggered.connect(lambda: self.extract_item(item))
        
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self.item_double_clicked(item, 0))
        
        # Show the menu
        menu.exec(self.file_tree.mapToGlobal(position))
    
    def extract_item(self, item):
        """Extract a file or directory"""
        # Get the file path
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path:
            # Check if it's a directory
            for i in range(item.childCount()):
                child = item.child(i)
                child_path = child.data(0, Qt.ItemDataRole.UserRole)
                if child_path:
                    self.extract_file(child_path)
        else:
            self.extract_file(path)
    
    def extract_file(self, path):
        """Extract a file to a user-selected location"""
        if not self.current_mdz_bundle:
            return
        
        # Get the file content
        content = self.current_mdz_bundle.content.get(path)
        if content is None:
            return
        
        # Get the save location
        file_name = os.path.basename(path)
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", file_name, "All Files (*)"
        )
        
        if save_path:
            try:
                # Write the file
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(save_path, mode) as f:
                    f.write(content)
                
                self.statusBar.showMessage(f"Extracted {path} to {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error extracting file: {str(e)}")
                logger.error(f"Error extracting file: {str(e)}")
    
    def extract_all(self):
        """Extract all files to a user-selected directory"""
        if not self.current_mdz_bundle:
            return
        
        # Get the save location
        save_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory for Extraction"
        )
        
        if save_dir:
            try:
                # Extract all files
                self.current_mdz_bundle.extract_to_directory(save_dir)
                
                self.statusBar.showMessage(f"Extracted all files to {save_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error extracting files: {str(e)}")
                logger.error(f"Error extracting files: {str(e)}")
    
    def extract_selected(self):
        """Extract selected files to a user-selected directory"""
        if not self.current_mdz_bundle:
            return
        
        # Get selected items
        selected_items = self.file_tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Information", "No files selected")
            return
        
        # Get the save location
        save_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory for Extraction"
        )
        
        if save_dir:
            try:
                # Extract selected files
                extracted_count = 0
                for item in selected_items:
                    path = item.data(0, Qt.ItemDataRole.UserRole)
                    if path:
                        # Get the file content
                        content = self.current_mdz_bundle.content.get(path)
                        if content is not None:
                            # Create the output file path
                            output_path = os.path.join(save_dir, path)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            
                            # Write the file
                            mode = 'wb' if isinstance(content, bytes) else 'w'
                            with open(output_path, mode) as f:
                                f.write(content)
                            
                            extracted_count += 1
                
                self.statusBar.showMessage(f"Extracted {extracted_count} files to {save_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error extracting files: {str(e)}")
                logger.error(f"Error extracting files: {str(e)}")
    
    def extract_by_type(self):
        """Extract files by type to a user-selected directory"""
        if not self.current_mdz_bundle:
            return
        
        # Get file types
        file_types = self.current_mdz_bundle.get_file_types()
        
        # Show file type selection dialog
        dialog = FileTypeFilterDialog(file_types, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Get selected file types
        selected_types = dialog.get_selected_types()
        
        # Get the save location
        save_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory for Extraction"
        )
        
        if save_dir:
            try:
                # Extract files by type
                extracted_count = 0
                for path in self.current_mdz_bundle.get_file_list():
                    # Check if the file matches the selected types
                    if not selected_types or any(path.lower().endswith(ext) for ext in selected_types):
                        # Get the file content
                        content = self.current_mdz_bundle.content.get(path)
                        if content is not None:
                            # Create the output file path
                            output_path = os.path.join(save_dir, path)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            
                            # Write the file
                            mode = 'wb' if isinstance(content, bytes) else 'w'
                            with open(output_path, mode) as f:
                                f.write(content)
                            
                            extracted_count += 1
                
                self.statusBar.showMessage(f"Extracted {extracted_count} files to {save_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error extracting files: {str(e)}")
                logger.error(f"Error extracting files: {str(e)}")
    
    def cleanup_mdz(self):
        """Clean up MDZ resources"""
        if self.current_mdz_bundle:
            self.current_mdz_bundle.cleanup()
            self.current_mdz_bundle = None
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
        
        self.current_mdz_file = None
        self.setWindowTitle("MDZ Viewer")
        self.file_tree.clear()
        self.text_view.clear()
        self.info_view.clear()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs is an MDZ file
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.mdz'):
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            # Get the first MDZ file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.mdz'):
                    self.load_mdz_file(file_path)
                    break
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.cleanup_mdz()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = MDZViewerWindow()
    window.show()
    
    # Check if a file was provided as an argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) and sys.argv[1].lower().endswith('.mdz'):
        window.load_mdz_file(sys.argv[1])
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
