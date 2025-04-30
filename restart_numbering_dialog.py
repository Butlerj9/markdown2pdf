"""
Dialog for inserting restart numbering marker in markdown
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt

class RestartNumberingDialog(QDialog):
    """Dialog for inserting restart numbering marker in markdown"""
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Insert Restart Numbering Marker")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add information label
        info_label = QLabel(
            "This will insert a special marker that restarts section numbering "
            "at the current heading level. The marker will be hidden in the final document."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add example
        example_label = QLabel(
            "<b>Example:</b><br>"
            "# Introduction<br>"
            "## Section 1.1<br>"
            "## Section 1.2<br><br>"
            "# <!-- RESTART_NUMBERING --> New Chapter<br>"
            "## Section 1.1 (numbering restarted)<br>"
        )
        example_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(example_label)
        
        # Add insert button
        insert_button = QPushButton("Insert Restart Numbering Marker")
        insert_button.clicked.connect(self.insert_marker)
        layout.addWidget(insert_button)
        
        # Add cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
    def insert_marker(self):
        """Insert the restart numbering marker at cursor position"""
        # Get cursor
        cursor = self.editor.textCursor()
        
        # Insert the marker
        cursor.insertText("<!-- RESTART_NUMBERING --> ")
        
        # Accept the dialog
        self.accept()
