"""
Test script for recent files menu functionality
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class TestRecentFilesMenu(QMainWindow):
    """Test class for recent files menu"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recent Files Menu Test")
        self.setGeometry(100, 100, 800, 600)

        # Create a menu bar
        self.menu_bar = self.menuBar()

        # Create a File menu
        self.file_menu = self.menu_bar.addMenu("File")

        # Create a Recent Files submenu
        self.recent_files_menu = QMenu("Recent Files", self)
        self.file_menu.addMenu(self.recent_files_menu)

        # Sample recent files
        self.recent_files = [
            "C:/path/to/file1.md",
            "C:/path/to/file2.md",
            "C:/path/to/file3.md"
        ]

        # Store actions to prevent garbage collection
        self._recent_file_actions = []

        # Update the recent files menu
        self.update_recent_files_menu()

        # Add a status bar
        self.statusBar().showMessage("Ready")

    def update_recent_files_menu(self):
        """Update the recent files menu"""
        # Clear the menu
        self.recent_files_menu.clear()

        # Remove any existing recent file actions to prevent memory leaks
        if hasattr(self, '_recent_file_actions'):
            for action in self._recent_file_actions:
                if action:  # Just check if action exists
                    try:
                        action.triggered.disconnect()
                    except Exception:
                        pass  # Ignore errors if already disconnected
            self._recent_file_actions = []
        else:
            self._recent_file_actions = []

        if not self.recent_files:
            # Add a disabled action if there are no recent files
            no_files_action = QAction('No Recent Files', self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
            return

        # Add actions for each recent file
        for i, file_path in enumerate(self.recent_files):
            # Create a shorter display name (just the filename)
            display_name = file_path.split("/")[-1]

            # Create the action with the full path as data
            action = QAction(f'{i+1}. {display_name}', self)
            action.setStatusTip(file_path)

            # Store the action to prevent garbage collection
            self._recent_file_actions.append(action)

            # Connect using a direct method call with explicit receiver
            # This is more reliable than lambda functions
            action.triggered.connect(self._create_recent_file_handler(file_path))

            self.recent_files_menu.addAction(action)

        # Add separator and clear action
        self.recent_files_menu.addSeparator()
        clear_action = QAction('Clear Recent Files', self)
        clear_action.triggered.connect(self.clear_recent_files)
        self.recent_files_menu.addAction(clear_action)

    def _create_recent_file_handler(self, file_path):
        """Create a method to handle opening a specific recent file"""
        # Create a copy of the file path to avoid reference issues
        path_copy = str(file_path)

        def handler(checked=False):
            try:
                # Use the copied path, not the original reference
                self.open_recent_file(path_copy)
            except Exception as e:
                print(f"Error opening recent file: {str(e)}")
                QMessageBox.critical(self, 'Error', f'Could not open the file: {str(e)}')
        return handler

    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        print(f"Opening file: {file_path}")
        self.statusBar().showMessage(f"Opened: {file_path}")
        QMessageBox.information(self, "File Opened", f"Successfully opened: {file_path}")

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.recent_files = []
        self.update_recent_files_menu()
        self.statusBar().showMessage("Recent files cleared")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestRecentFilesMenu()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
