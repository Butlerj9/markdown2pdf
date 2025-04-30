#!/usr/bin/env python3
"""
Edit Toolbar for Markdown to PDF Converter
-----------------------------------------
Provides a vertical toolbar with text formatting options.
"""

import os
from PyQt6.QtWidgets import (
    QToolBar, QWidget, QVBoxLayout, QToolButton,
    QLabel, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QAction

from logging_config import get_logger

logger = get_logger()

class EditToolbar(QToolBar):
    """Vertical toolbar with text formatting options"""

    def __init__(self, parent=None):
        super(EditToolbar, self).__init__(parent)
        self.parent = parent
        self.setOrientation(Qt.Orientation.Vertical)
        self.setMovable(False)
        self.setIconSize(QSize(20, 20))
        self.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border-right: 1px solid #ccc;
                padding: 8px 5px;
                min-width: 120px;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px;
                margin: 3px 0;
                background-color: #ffffff;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #bbb;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
                border: 1px solid #999;
            }
            QLabel {
                color: #555;
                font-size: 10px;
                font-weight: bold;
                padding-top: 12px;
                padding-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QToolBar::separator {
                height: 1px;
                background-color: #ccc;
                margin: 8px 0;
            }
        """)

        self.init_actions()

    def init_actions(self):
        """Initialize toolbar actions"""
        # Add section label for text formatting
        self.addWidget(self.create_section_label("Text Format"))

        # Bold
        bold_action = QAction("Bold", self)
        bold_action.setToolTip("Bold (Ctrl+B)")
        bold_action.triggered.connect(self.insert_bold)
        self.addAction(bold_action)

        # Italic
        italic_action = QAction("Italic", self)
        italic_action.setToolTip("Italic (Ctrl+I)")
        italic_action.triggered.connect(self.insert_italic)
        self.addAction(italic_action)

        # Underline (using HTML since Markdown doesn't have native underline)
        underline_action = QAction("Underline", self)
        underline_action.setToolTip("Underline (Ctrl+U)")
        underline_action.triggered.connect(self.insert_underline)
        self.addAction(underline_action)

        # Strikethrough
        strikethrough_action = QAction("Strikethrough", self)
        strikethrough_action.setToolTip("Strikethrough")
        strikethrough_action.triggered.connect(self.insert_strikethrough)
        self.addAction(strikethrough_action)

        # Add separator
        self.addSeparator()

        # Add section label for headings
        self.addWidget(self.create_section_label("Headings"))

        # Heading 1
        h1_action = QAction("H1", self)
        h1_action.setToolTip("Heading 1")
        h1_action.triggered.connect(lambda: self.insert_heading(1))
        self.addAction(h1_action)

        # Heading 2
        h2_action = QAction("H2", self)
        h2_action.setToolTip("Heading 2")
        h2_action.triggered.connect(lambda: self.insert_heading(2))
        self.addAction(h2_action)

        # Heading 3
        h3_action = QAction("H3", self)
        h3_action.setToolTip("Heading 3")
        h3_action.triggered.connect(lambda: self.insert_heading(3))
        self.addAction(h3_action)

        # Add separator
        self.addSeparator()

        # Add section label for lists
        self.addWidget(self.create_section_label("Lists"))

        # Bullet list
        bullet_list_action = QAction("Bullet List", self)
        bullet_list_action.setToolTip("Bullet List")
        bullet_list_action.triggered.connect(self.insert_bullet_list)
        self.addAction(bullet_list_action)

        # Numbered list
        numbered_list_action = QAction("Numbered List", self)
        numbered_list_action.setToolTip("Numbered List")
        numbered_list_action.triggered.connect(self.insert_numbered_list)
        self.addAction(numbered_list_action)

        # Add separator
        self.addSeparator()

        # Add section label for special elements
        self.addWidget(self.create_section_label("Special"))

        # Page break
        page_break_action = QAction("Page Break", self)
        page_break_action.setToolTip("Insert Page Break")
        page_break_action.triggered.connect(self.insert_page_break)
        self.addAction(page_break_action)

        # Restart numbering
        restart_numbering_action = QAction("Restart Numbering", self)
        restart_numbering_action.setToolTip("Restart Section Numbering")
        restart_numbering_action.triggered.connect(self.insert_restart_numbering)
        self.addAction(restart_numbering_action)

        # Link
        link_action = QAction("Link", self)
        link_action.setToolTip("Insert Link")
        link_action.triggered.connect(self.insert_link)
        self.addAction(link_action)

        # Image
        image_action = QAction("Image", self)
        image_action.setToolTip("Insert Image")
        image_action.triggered.connect(self.insert_image)
        self.addAction(image_action)

        # Code block
        code_block_action = QAction("Code Block", self)
        code_block_action.setToolTip("Insert Code Block")
        code_block_action.triggered.connect(self.insert_code_block)
        self.addAction(code_block_action)

        # Table
        table_action = QAction("Table", self)
        table_action.setToolTip("Insert Table")
        table_action.triggered.connect(self.insert_table)
        self.addAction(table_action)

        # Add spacer at the bottom
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.addWidget(spacer)

    def create_section_label(self, text):
        """Create a section label for the toolbar"""
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        return label

    def insert_bold(self):
        """Insert bold markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, wrap it in bold markers
            cursor.insertText(f"**{selected_text}**")
        else:
            # If no text is selected, insert bold markers and place cursor between them
            cursor.insertText("****")
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 2)
            editor.setTextCursor(cursor)

    def insert_italic(self):
        """Insert italic markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, wrap it in italic markers
            cursor.insertText(f"*{selected_text}*")
        else:
            # If no text is selected, insert italic markers and place cursor between them
            cursor.insertText("**")
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 1)
            editor.setTextCursor(cursor)

    def insert_underline(self):
        """Insert HTML underline (not native in Markdown)"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, wrap it in underline HTML
            cursor.insertText(f"<u>{selected_text}</u>")
        else:
            # If no text is selected, insert underline HTML and place cursor between tags
            cursor.insertText("<u></u>")
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 4)
            editor.setTextCursor(cursor)

    def insert_strikethrough(self):
        """Insert strikethrough markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, wrap it in strikethrough markers
            cursor.insertText(f"~~{selected_text}~~")
        else:
            # If no text is selected, insert strikethrough markers and place cursor between them
            cursor.insertText("~~~~")
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 2)
            editor.setTextCursor(cursor)

    def insert_heading(self, level):
        """Insert heading markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()

        # Move to start of line
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.MoveAnchor)

        # Insert heading markers
        cursor.insertText("#" * level + " ")
        editor.setTextCursor(cursor)

    def insert_bullet_list(self):
        """Insert bullet list item"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()

        # Move to start of line
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.MoveAnchor)

        # Insert bullet list marker
        cursor.insertText("- ")
        editor.setTextCursor(cursor)

    def insert_numbered_list(self):
        """Insert numbered list item"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()

        # Move to start of line
        cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.MoveAnchor)

        # Insert numbered list marker
        cursor.insertText("1. ")
        editor.setTextCursor(cursor)

    def insert_page_break(self):
        """Insert page break marker"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        if hasattr(self.parent, 'insert_page_break'):
            self.parent.insert_page_break()
        else:
            editor = self.parent.markdown_editor
            cursor = editor.textCursor()
            cursor.insertText("\n\n<!-- PAGE_BREAK -->\n\n")
            editor.setTextCursor(cursor)

    def insert_restart_numbering(self):
        """Insert restart numbering marker"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        if hasattr(self.parent, 'insert_restart_numbering'):
            self.parent.insert_restart_numbering()
        else:
            editor = self.parent.markdown_editor
            cursor = editor.textCursor()
            cursor.insertText("\n<!-- RESTART_NUMBERING -->\n")
            editor.setTextCursor(cursor)

    def insert_link(self):
        """Insert link markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, use it as the link text
            cursor.insertText(f"[{selected_text}](url)")

            # Select the "url" part
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 1)
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, 3)
            editor.setTextCursor(cursor)
        else:
            # If no text is selected, insert link template and place cursor at link text
            cursor.insertText("[link text](url)")

            # Select "link text" for easy replacement
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 11)
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 9)
            editor.setTextCursor(cursor)

    def insert_image(self):
        """Insert image markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()

        # Insert image template
        cursor.insertText("![alt text](image_url)")

        # Select "image_url" for easy replacement
        cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, 1)
        cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, 9)
        editor.setTextCursor(cursor)

    def insert_code_block(self):
        """Insert code block markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            # If text is selected, wrap it in code block markers
            cursor.insertText(f"```\n{selected_text}\n```")
        else:
            # If no text is selected, insert code block markers and place cursor between them
            cursor.insertText("```\n\n```")
            cursor.movePosition(cursor.MoveOperation.Up, cursor.MoveMode.MoveAnchor, 1)
            editor.setTextCursor(cursor)

    def insert_table(self):
        """Insert table markdown"""
        if not self.parent or not hasattr(self.parent, 'markdown_editor'):
            return

        editor = self.parent.markdown_editor
        cursor = editor.textCursor()

        # Insert a simple 2x2 table template
        table_template = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        cursor.insertText(table_template)
        editor.setTextCursor(cursor)
