#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter
---------------------------------
A GUI application for converting Markdown documents to PDF with extensive formatting options.
Supports XeLaTeX and other PDF engines for high-quality output.

Requirements:
- Python 3.6+
- PyQt6
- Pandoc
- A PDF engine (XeLaTeX recommended, wkhtmltopdf, WeasyPrint, or Prince as alternatives)
"""

import sys
import os
import json
import subprocess
import tempfile
import time
import traceback
import logging
import threading
import signal
import psutil
import re
import copy

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QTabWidget,
    QFormLayout, QGroupBox, QCheckBox, QColorDialog, QFontDialog, QMessageBox,
    QSplitter, QListWidget, QListWidgetItem, QLineEdit, QScrollArea, QToolBar, QSizePolicy,
    QInputDialog, QFrame, QMenu, QDialog, QSlider
)
from PyQt6.QtGui import QFont, QColor, QIcon, QTextCursor, QTextFormat, QTextCharFormat, QAction, QPageSize, QPageLayout
from PyQt6.QtCore import Qt, QUrl, QSize, QSettings, QPoint, QRect, QRectF, QMarginsF
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewWidget
from PyQt6.QtGui import QPainter

# Import our custom modules
from page_preview import PagePreview
from format_utils import FormatUtils, PageBreakDialog
from restart_numbering_dialog import RestartNumberingDialog
from ui_improvements import UIImprovements
from render_utils import RenderUtils
from style_manager import StyleManager
from edit_toolbar import EditToolbar

from PyQt6.QtCore import QParallelAnimationGroup, QPropertyAnimation, QTimer
from PyQt6.QtWidgets import QToolButton

from logging_config import initialize_logger, get_logger, EnhancedLogger
from markdown_to_pdf_export import MarkdownToPDFExport

# Get the properly configured logger
logger = get_logger()

class CollapsibleBox(QWidget):
    """A custom collapsible box based on a QWidget"""
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QToolButton(self)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setStyleSheet("QToolButton { border: none; font-weight: bold; }")

        # Fix: Use simpler approach for tool button style
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)

        # Fix: Use correct enum for arrow type
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea(self)
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))

    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        # Fix: Use correct enum for arrow type
        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow if not checked else Qt.ArrowType.RightArrow
        )
        self.toggle_animation.setDirection(
            QParallelAnimationGroup.Direction.Forward if not checked
            else QParallelAnimationGroup.Direction.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = QVBoxLayout()
        lay.addLayout(layout)
        self.content_area.setLayout(lay)

        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height() + 25  # Add some padding

        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(300)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(300)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

        # Start expanded
        self.toggle_animation.start()
        self.toggle_animation.setCurrentTime(300)

class AdvancedMarkdownToPDF(QMainWindow):
    """Main application class for the Markdown to PDF converter"""

    def __init__(self, parent=None):
        super(AdvancedMarkdownToPDF, self).__init__(parent)

        # Initialize settings
        self.settings = QSettings("MarkdownToPDF", "AdvancedConverter")

        # Initialize style manager
        self.style_manager = StyleManager()

        # Test mode flag - used to suppress dialogs during automated testing
        self._is_test_environment = os.environ.get("MARKDOWN_PDF_TEST_MODE", "0") == "1"
        if self._is_test_environment:
            logger.info("Running in test mode - dialogs will be suppressed")

        # Set up default document settings
        self.document_settings = {
            "format": {
                "preferred_engine": "xelatex",
                "technical_numbering": False,
                "page_numbering": True,
                "page_number_format": "Page {page} of {total}",
                "use_master_font": False,
                "master_font": {
                    "family": "Arial",
                    "size": 11
                }
            },
            "fonts": {
                "body": {
                    "family": "Arial",
                    "size": 11,
                    "line_height": 1.5
                },
                "headings": {
                    "h1": {
                        "family": "Arial",
                        "size": 18,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 24,
                        "margin_bottom": 12
                    },
                    "h2": {
                        "family": "Arial",
                        "size": 16,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 18,
                        "margin_bottom": 10
                    },
                    "h3": {
                        "family": "Arial",
                        "size": 14,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 16,
                        "margin_bottom": 8
                    },
                    "h4": {
                        "family": "Arial",
                        "size": 13,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 14,
                        "margin_bottom": 8
                    },
                    "h5": {
                        "family": "Arial",
                        "size": 12,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 12,
                        "margin_bottom": 6
                    },
                    "h6": {
                        "family": "Arial",
                        "size": 11,
                        "color": "#000000",
                        "spacing": 1.2,
                        "margin_top": 12,
                        "margin_bottom": 6
                    }
                }
            },
            "colors": {
                "text": "#000000",
                "background": "#FFFFFF",
                "links": "#0000EE"
            },
            "page": {
                "size": "A4",
                "orientation": "Portrait",
                "margins": {
                    "top": 25.4,
                    "right": 25.4,
                    "bottom": 25.4,
                    "left": 25.4
                }
            },
            "paragraphs": {
                "spacing": 1.5,
                "margin_top": 0,
                "margin_bottom": 10,
                "first_line_indent": 0,
                "alignment": "left"
            },
            "lists": {
                "bullet_indent": 30,
                "number_indent": 30,
                "item_spacing": 5,
                "nested_indent": 20,
                "bullet_style_l1": "Disc",
                "bullet_style_l2": "Circle",
                "bullet_style_l3": "Square",
                "number_style_l1": "Decimal",
                "number_style_l2": "Lower Alpha",
                "number_style_l3": "Lower Roman"
            },
            "table": {
                "border_color": "#CCCCCC",
                "header_bg": "#EEEEEE",
                "cell_padding": 5
            },
            "code": {
                "font_family": "Consolas",
                "font_size": 10,
                "background": "#F5F5F5",
                "border_color": "#CCCCCC"
            },
            "toc": {
                "include": False,
                "depth": 3,
                "title": "Table of Contents"
            }
        }

        # Paths for file dialogs
        self.dialog_paths = {
            "open": "",
            "save": "",
            "export": ""
        }

        # Recent files list (max 10 files)
        self.recent_files = []
        self.max_recent_files = 10

        # Find available PDF engines
        self.found_engines = self.find_pdf_engines()

        # Current file path
        self.current_file = None

        # Check dependencies
        self.check_dependencies()

        # Load settings
        self.load_settings()

        # Initialize UI
        self.initUI()

        # Apply UI improvements
        UIImprovements.apply_all_ui_improvements(self)

        # Note: Preview will be initialized when first content is loaded

    def find_pdf_engines(self):
        """Find PDF engines with enhanced path detection, prioritizing XeLaTeX"""
        engines_to_check = ['xelatex', 'pdflatex', 'lualatex', 'wkhtmltopdf', 'weasyprint']
        found_engines = {}

        # Common paths where engines might be installed
        potential_paths = [
            "",  # Empty string to check the default PATH
            # TeX Live installation paths
            os.path.join(os.environ.get('PROGRAMFILES', ''), "texlive\\2023\\bin\\win32"),
            os.path.join(os.environ.get('PROGRAMFILES', ''), "texlive\\2022\\bin\\win32"),
            os.path.join(os.environ.get('PROGRAMFILES', ''), "texlive\\2021\\bin\\win32"),
            # MiKTeX installation paths
            os.path.join(os.environ.get('PROGRAMFILES', ''), "MiKTeX\\miktex\\bin\\x64"),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), "MiKTeX\\miktex\\bin"),
            # Other PDF engines
            os.path.join(os.environ.get('PROGRAMFILES', ''), "wkhtmltopdf\\bin"),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), "Programs\\Python\\Python310\\Scripts"),
        ]

        # Add more paths for macOS and Linux
        if sys.platform == 'darwin':  # macOS
            for year in range(2019, 2024):
                potential_paths.append(f"/usr/local/texlive/{year}/bin/universal-darwin")
        elif sys.platform.startswith('linux'):  # Linux
            for year in range(2019, 2024):
                potential_paths.append(f"/usr/local/texlive/{year}/bin/x86_64-linux")

        # Check each engine in each potential path
        for engine in engines_to_check:
            # Check if directly callable (in PATH)
            try:
                # Add timeout to prevent hanging
                result = subprocess.run([engine, '--version'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=2)  # 2 second timeout
                found_engines[engine] = engine  # Use just the name as it's in PATH
                print(f"Found {engine} in PATH")
                continue
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                # If timeout occurs, log it but continue with the next engine
                if 'TimeoutExpired' in str(sys.exc_info()[0]):
                    print(f"Timeout checking for {engine}")
                pass

            # Check in potential installation paths
            for base_path in potential_paths:
                if not base_path:
                    continue

                # Handle Windows executable extension
                ext = '.exe' if sys.platform == 'win32' else ''
                engine_path = os.path.join(base_path, engine + ext)

                if os.path.exists(engine_path):
                    found_engines[engine] = engine_path
                    print(f"Found {engine} at: {engine_path}")
                    break

        return found_engines

    def check_dependencies(self):
        """Check for required external dependencies"""
        # Check for Pandoc
        pandoc_path = r"C:\Users\joshd\AppData\Local\Pandoc\pandoc.exe"
        try:
            result = subprocess.run([pandoc_path, '--version'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
            print("Pandoc found:", result.stdout.decode('utf-8').splitlines()[0])
        except (subprocess.SubprocessError, FileNotFoundError):
            QMessageBox.warning(
                self,
                "Pandoc Not Found",
                "Pandoc is not installed or not found in PATH. Please install Pandoc."
            )

    def load_settings(self):
        """Load previously saved settings and dialog paths"""
        try:
            # First try to load temporary style if it exists
            temp_style = self.style_manager.load_temp_style()
            if temp_style:
                logger.info("Loaded temporary style")
                self.document_settings.update(temp_style)
            else:
                # Load from QSettings
                settings = self.settings
                if settings.contains("document_settings"):
                    saved_settings = settings.value("document_settings")
                    if saved_settings:
                        self.document_settings.update(saved_settings)

            # Add this check to ensure the keys exist
            if "page_numbering" not in self.document_settings["format"]:
                self.document_settings["format"]["page_numbering"] = True
            if "page_number_format" not in self.document_settings["format"]:
                self.document_settings["format"]["page_number_format"] = "Page {page} of {total}"

            # Check for engine preference
            if self.settings.contains("preferred_engine"):
                engine = self.settings.value("preferred_engine")
                if engine in self.found_engines:
                    self.document_settings["format"]["preferred_engine"] = engine

            # Load dialog paths
            if self.settings.contains("dialog_paths"):
                paths = self.settings.value("dialog_paths")
                if paths and isinstance(paths, dict):
                    self.dialog_paths.update(paths)

            # Load from dedicated paths file
            paths_file = os.path.join(os.path.expanduser("~"), ".mdpdf_paths.json")
            if os.path.exists(paths_file):
                try:
                    with open(paths_file, 'r', encoding='utf-8') as f:
                        loaded_paths = json.load(f)
                        if isinstance(loaded_paths, dict):
                            self.dialog_paths.update(loaded_paths)
                except Exception as e:
                    logger.error(f"Error loading dialog paths file: {e}")
                    print(f"Error loading dialog paths file: {e}")

            # Load recent files
            if self.settings.contains("recent_files"):
                recent_files = self.settings.value("recent_files")
                if recent_files and isinstance(recent_files, list):
                    # Filter out files that no longer exist
                    self.recent_files = [f for f in recent_files if os.path.exists(f)]
                    logger.info(f"Loaded {len(self.recent_files)} recent files")

            logger.info("Settings loaded successfully")
            print("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            print(f"Error loading settings: {e}")

    def save_settings(self, timeout=3):
        """
        Save current settings and dialog paths for future use with improved error handling

        Args:
            timeout: Maximum time in seconds to spend on saving settings (default: 3)
        """
        # Check if we're running in a test environment
        is_test_environment = hasattr(self, '_is_test_environment') and self._is_test_environment
        if is_test_environment:
            logger.debug("Skipping settings save in test environment")
            return

        try:
            # Use a timer to enforce timeout
            import threading
            import time

            # Flag to track if we've completed saving
            save_completed = False
            save_error = None

            # Function to run in a separate thread with timeout
            def save_settings_thread():
                nonlocal save_completed, save_error
                try:
                    # Make a copy of the settings to avoid modifying during save
                    settings_copy = copy.deepcopy(self.document_settings)
                    paths_copy = copy.deepcopy(self.dialog_paths)

                    # Save the settings
                    self.settings.setValue("document_settings", settings_copy)
                    self.settings.setValue("preferred_engine", settings_copy["format"]["preferred_engine"])
                    self.settings.setValue("window_geometry", self.saveGeometry())
                    self.settings.setValue("dialog_paths", paths_copy)

                    # Save recent files
                    self.settings.setValue("recent_files", self.recent_files)

                    # Force sync to ensure settings are written to disk
                    self.settings.sync()

                    # Save dialog paths to dedicated file for easier access by other instances
                    paths_file = os.path.join(os.path.expanduser("~"), ".mdpdf_paths.json")
                    try:
                        # Use a temporary file to avoid corruption if interrupted
                        temp_file = paths_file + ".tmp"
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(paths_copy, f, indent=2)

                        # Rename the temp file to the final file (atomic operation)
                        if os.path.exists(paths_file):
                            os.replace(temp_file, paths_file)
                        else:
                            os.rename(temp_file, paths_file)
                    except Exception as e:
                        logger.error(f"Error saving dialog paths file: {e}")

                    # Mark as completed
                    save_completed = True
                    logger.info("Settings saved successfully")
                except Exception as e:
                    save_error = e
                    logger.error(f"Error in save thread: {e}")

            # Start the save thread
            save_thread = threading.Thread(target=save_settings_thread)
            save_thread.daemon = True  # Allow the thread to be terminated when the main thread exits
            save_thread.start()

            # Wait for the thread to complete or timeout
            start_time = time.time()
            while not save_completed and time.time() - start_time < timeout:
                time.sleep(0.1)  # Small sleep to avoid busy waiting
                QApplication.processEvents()  # Process UI events to keep the application responsive

            if not save_completed:
                logger.warning(f"Settings save timed out after {timeout} seconds")
            elif save_error:
                logger.error(f"Settings save failed: {save_error}")
            else:
                logger.debug("Settings saved successfully within timeout")

        except Exception as e:
            logger.error(f"Error in save_settings: {e}")
            # Continue execution even if saving fails

    def initUI(self):
        """Initialize the user interface"""
        # Main window setup
        self.setWindowTitle('Advanced Markdown to PDF Converter')
        self.setGeometry(100, 100, 1280, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Create a horizontal layout for the edit toolbar and main content
        editor_layout_container = QHBoxLayout()
        main_layout.addLayout(editor_layout_container)

        # Left panel: Edit toolbar
        self.edit_toolbar = EditToolbar(self)
        editor_layout_container.addWidget(self.edit_toolbar)

        # Create main horizontal splitter for the rest of the content
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        editor_layout_container.addWidget(main_splitter)

        # Second panel: Markdown editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(5, 5, 5, 5)

        editor_header = QWidget()
        editor_header_layout = QHBoxLayout(editor_header)
        editor_header_layout.setContentsMargins(0, 0, 0, 0)

        editor_label = QLabel("Markdown Editor")
        editor_label.setStyleSheet("font-weight: bold;")
        editor_header_layout.addWidget(editor_label)

        # Add page break button
        page_break_btn = QPushButton("Insert Page Break")
        page_break_btn.clicked.connect(self.show_page_break_dialog)
        editor_header_layout.addWidget(page_break_btn)

        editor_header_layout.addStretch(1)

        self.markdown_editor = QTextEdit()
        self.markdown_editor.setPlaceholderText("Type or paste your Markdown text here...")
        self.markdown_editor.textChanged.connect(self.update_preview)

        editor_layout.addWidget(editor_header)
        editor_layout.addWidget(self.markdown_editor)

        # Middle panel: Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(5, 5, 5, 5)

        # Create page preview widget first
        self.page_preview = PagePreview()

        # Set up zoom controls at the top of the preview layout
        self.page_preview.setup_zoom_controls(preview_layout)

        # Add the page preview widget to fill the rest of the space
        preview_layout.addWidget(self.page_preview)

        # Right panel: Settings in a compact frame
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.Shape.StyledPanel)
        settings_frame.setFrameShadow(QFrame.Shadow.Raised)
        settings_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        settings_frame.setMaximumWidth(300)  # Limit width for compact display

        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setWidget(settings_frame)

        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        settings_layout.setSpacing(5)

        settings_title = QLabel("Document Settings")
        settings_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        settings_layout.addWidget(settings_title)

        # Add master toggle for settings
        self.settings_toggle = QCheckBox("Enable Custom Settings")
        self.settings_toggle.setChecked(True)
        self.settings_toggle.stateChanged.connect(self.toggle_settings_fields)
        settings_layout.addWidget(self.settings_toggle)

        # Create all the input elements first
        self.create_all_ui_elements()

        # Add collapsible settings sections
        self.format_settings_group = self.create_format_settings_group()
        self.text_settings_group = self.create_text_settings_group()
        self.page_settings_group = self.create_page_settings_group()
        self.heading_settings_group = self.create_heading_settings_group()
        self.paragraph_settings_group = self.create_paragraph_settings_group()
        self.list_settings_group = self.create_list_settings_group()
        self.table_settings_group = self.create_table_settings_group()
        self.code_settings_group = self.create_code_settings_group()
        self.toc_settings_group = self.create_toc_settings_group()

        settings_layout.addWidget(self.format_settings_group)
        settings_layout.addWidget(self.page_settings_group)
        settings_layout.addWidget(self.text_settings_group)
        settings_layout.addWidget(self.heading_settings_group)
        settings_layout.addWidget(self.paragraph_settings_group)
        settings_layout.addWidget(self.list_settings_group)
        settings_layout.addWidget(self.table_settings_group)
        settings_layout.addWidget(self.code_settings_group)
        settings_layout.addWidget(self.toc_settings_group)

        # Add stretch to push everything to the top
        settings_layout.addStretch(1)

        # Add widgets to splitter
        main_splitter.addWidget(editor_widget)
        main_splitter.addWidget(preview_widget)
        main_splitter.addWidget(settings_scroll)

        # Set initial sizes for the three panels (40%, 40%, 20%)
        main_splitter.setSizes([400, 400, 200])

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create status bar
        self.statusBar().showMessage("Ready")

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        new_action = QAction('&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Recent files submenu
        self.recent_files_menu = QMenu('&Recent Files', self)
        file_menu.addMenu(self.recent_files_menu)
        self.update_recent_files_menu()

        file_menu.addSeparator()

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction('Save &As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction('&Export...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_document)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('&Edit')

        undo_action = QAction('&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.markdown_editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction('&Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.markdown_editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction('Cu&t', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.markdown_editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction('&Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.markdown_editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction('&Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.markdown_editor.paste)
        edit_menu.addAction(paste_action)

        # Tools menu
        tools_menu = menubar.addMenu('&Tools')

        page_break_action = QAction('Insert &Page Break', self)
        page_break_action.setShortcut('Ctrl+Return')
        page_break_action.triggered.connect(self.insert_page_break)
        tools_menu.addAction(page_break_action)

        restart_numbering_action = QAction('Insert &Restart Numbering', self)
        restart_numbering_action.triggered.connect(self.insert_restart_numbering)
        tools_menu.addAction(restart_numbering_action)

        tools_menu.addSeparator()

        # Add test page navigation action
        test_page_nav_action = QAction('Test Page &Navigation', self)
        test_page_nav_action.triggered.connect(self.test_page_navigation)
        tools_menu.addAction(test_page_nav_action)

        # Add test page breaks action
        test_page_breaks_action = QAction('Test Page &Breaks', self)
        test_page_breaks_action.triggered.connect(self.test_page_breaks)
        tools_menu.addAction(test_page_breaks_action)

        # Add comprehensive test framework
        test_framework_action = QAction('&Test Framework...', self)
        test_framework_action.triggered.connect(self.open_test_framework)
        tools_menu.addAction(test_framework_action)

        tools_menu.addSeparator()

        template_manager_action = QAction('&Template Manager...', self)
        template_manager_action.triggered.connect(self.open_template_manager)
        tools_menu.addAction(template_manager_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the main toolbar with file operations and style presets"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # File actions
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        toolbar.addAction(save_as_action)

        toolbar.addSeparator()

        # Export action
        export_action = QAction("Export", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_document)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # Page break action
        page_break_action = QAction("Insert Page Break", self)
        page_break_action.setShortcut("Ctrl+Return")
        page_break_action.triggered.connect(self.show_page_break_dialog)
        toolbar.addAction(page_break_action)

        # Add restart numbering action
        restart_numbering_action = QAction("Restart Numbering", self)
        restart_numbering_action.setShortcut("Ctrl+Shift+N")
        restart_numbering_action.triggered.connect(self.show_restart_numbering_dialog)
        toolbar.addAction(restart_numbering_action)

        toolbar.addSeparator()

        # Add style presets dropdown
        preset_label = QLabel("Style Preset:")
        toolbar.addWidget(preset_label)

        self.preset_combo = QComboBox()
        # Load available styles from style manager
        self.preset_combo.addItems(self.style_manager.available_styles)
        self.preset_combo.setCurrentText(self.style_manager.current_style_name)
        self.preset_combo.currentTextChanged.connect(self.apply_style_preset)
        toolbar.addWidget(self.preset_combo)

        # Add save style buttons
        save_preset_action = QAction("Save Style", self)
        save_preset_action.triggered.connect(self.save_current_style)
        toolbar.addAction(save_preset_action)

        save_as_preset_action = QAction("Save As New Style", self)
        save_as_preset_action.triggered.connect(self.save_style_as_new)
        toolbar.addAction(save_as_preset_action)

        # Add delete style button
        delete_preset_action = QAction("Delete Style", self)
        delete_preset_action.triggered.connect(self.delete_current_style)
        toolbar.addAction(delete_preset_action)

    def create_all_ui_elements(self):
        """Create all UI input elements in advance to avoid dependency issues"""
        # Here we'd create any elements needed before the groups
        # Implementation omitted for brevity - will be created in each group
        pass

    def create_format_settings_group(self):
        """Create document format settings group with improved technical numbering handling"""
        box = CollapsibleBox("Document Format")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # PDF Engine selection
        engine_label = QLabel("PDF Engine:")
        self.engine_combo = QComboBox()
        # Populate with detected engines
        self.engine_combo.addItem("Auto-select")
        for engine_name in self.found_engines.keys():
            self.engine_combo.addItem(engine_name)
        # Set current selection
        if self.document_settings["format"]["preferred_engine"] in self.found_engines:
            self.engine_combo.setCurrentText(self.document_settings["format"]["preferred_engine"])
        elif "xelatex" in self.found_engines:
            # Prefer XeLaTeX if available
            self.engine_combo.setCurrentText("xelatex")
            self.document_settings["format"]["preferred_engine"] = "xelatex"
        self.engine_combo.currentTextChanged.connect(self.update_preferred_engine)
        layout.addRow(engine_label, self.engine_combo)

        # Technical numbering group
        numbering_group = QGroupBox("Section Numbering")
        numbering_layout = QFormLayout(numbering_group)

        # Technical numbering option
        self.technical_numbering = QCheckBox("Use technical document numbering (1.1, 1.2, etc.)")
        self.technical_numbering.setChecked(self.document_settings["format"]["technical_numbering"])
        self.technical_numbering.stateChanged.connect(self.toggle_numbering_with_restart)
        numbering_layout.addRow(self.technical_numbering)

        # Numbering start level
        self.numbering_start = QComboBox()
        self.numbering_start.addItems(["H1", "H2", "H3", "H4", "H5", "H6"])
        if "numbering_start" not in self.document_settings["format"]:
            self.document_settings["format"]["numbering_start"] = 1
        self.numbering_start.setCurrentIndex(self.document_settings["format"]["numbering_start"] - 1)
        self.numbering_start.currentIndexChanged.connect(self.update_numbering_start)
        numbering_layout.addRow("Start numbering at:", self.numbering_start)

        # Restart numbering button
        self.restart_numbering_btn = QPushButton("Insert Restart Numbering Marker")
        self.restart_numbering_btn.clicked.connect(self.show_restart_numbering_dialog)
        numbering_layout.addRow(self.restart_numbering_btn)

        # Restart numbering info
        restart_info = QLabel("Inserts a marker that restarts section numbering at the current heading level")
        restart_info.setWordWrap(True)
        restart_info.setStyleSheet("font-style: italic; color: #666;")
        numbering_layout.addRow(restart_info)

        layout.addRow(numbering_group)

        # Page numbering option
        self.page_numbering = QCheckBox("Show page numbers in footer")
        self.page_numbering.setChecked(self.document_settings["format"]["page_numbering"])
        self.page_numbering.stateChanged.connect(self.update_page_numbering)
        layout.addRow(self.page_numbering)

        # Page number format
        self.page_number_format = QLineEdit(self.document_settings["format"]["page_number_format"])
        self.page_number_format.setPlaceholderText("Use {page} and {total} as placeholders")
        self.page_number_format.textChanged.connect(self.update_page_number_format)
        layout.addRow("Page number format:", self.page_number_format)

        # Master font control
        master_font_group = QGroupBox("Master Font Control")
        master_layout = QFormLayout(master_font_group)

        # Master font checkbox
        self.use_master_font = QCheckBox("Use single font throughout document")
        self.use_master_font.setChecked(self.document_settings["format"]["use_master_font"])
        self.use_master_font.stateChanged.connect(self.toggle_master_font)
        master_layout.addRow(self.use_master_font)

        # Master font button (family only, no size)
        master_font = QFont(self.document_settings["format"]["master_font"]["family"])
        self.master_font_btn = QPushButton("Select Master Font...")
        self.master_font_btn.setFont(master_font)
        self.master_font_btn.setText(f"{master_font.family()}")
        self.master_font_btn.clicked.connect(self.select_master_font)
        self.master_font_btn.setEnabled(self.document_settings["format"]["use_master_font"])
        master_layout.addRow("Font:", self.master_font_btn)

        layout.addRow(master_font_group)

        box.setContentLayout(layout)
        return box

    def create_text_settings_group(self):
        """Create text settings group"""
        box = CollapsibleBox("Text Settings")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Body font
        self.body_font_btn = QPushButton("Select Font...")
        current_body_font = QFont(
            self.document_settings["fonts"]["body"]["family"],
            self.document_settings["fonts"]["body"]["size"]
        )
        self.body_font_btn.setFont(current_body_font)
        self.body_font_btn.setText(f"{current_body_font.family()}, {current_body_font.pointSize()}pt")
        self.body_font_btn.clicked.connect(self.select_body_font)
        self.body_font_btn.setEnabled(not self.document_settings["format"]["use_master_font"])
        layout.addRow("Body Font:", self.body_font_btn)

        # Line height
        self.line_height = QDoubleSpinBox()
        self.line_height.setRange(0.5, 3.0)
        self.line_height.setSingleStep(0.1)
        self.line_height.setValue(self.document_settings["fonts"]["body"]["line_height"])
        self.line_height.valueChanged.connect(self.update_line_height)
        layout.addRow("Line Height:", self.line_height)

        # Text color
        self.text_color_btn = QPushButton()
        self.text_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['text']}")
        self.text_color_btn.clicked.connect(self.select_text_color)
        layout.addRow("Text Color:", self.text_color_btn)

        # Background color
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['background']}")
        self.bg_color_btn.clicked.connect(self.select_bg_color)
        layout.addRow("Background:", self.bg_color_btn)

        # Link color
        self.link_color_btn = QPushButton()
        self.link_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['links']}")
        self.link_color_btn.clicked.connect(self.select_link_color)
        layout.addRow("Link Color:", self.link_color_btn)

        box.setContentLayout(layout)
        return box

    def create_page_settings_group(self):
        """Create page settings group"""
        box = CollapsibleBox("Page Settings")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Page size
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A3", "A4", "A5", "Letter", "Legal", "Executive", "Tabloid"])
        self.page_size_combo.setCurrentText(self.document_settings["page"]["size"])
        self.page_size_combo.currentTextChanged.connect(self.update_page_size)
        layout.addRow("Size:", self.page_size_combo)

        # Orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        self.orientation_combo.setCurrentText(self.document_settings["page"]["orientation"].capitalize())
        self.orientation_combo.currentTextChanged.connect(self.update_orientation)
        layout.addRow("Orientation:", self.orientation_combo)

        # Margins
        margin_group = QGroupBox("Margins (mm)")
        margin_layout = QFormLayout(margin_group)
        margin_layout.setContentsMargins(5, 10, 5, 5)

        self.margin_top = QDoubleSpinBox()
        self.margin_top.setRange(0, 100)
        self.margin_top.setValue(self.document_settings["page"]["margins"]["top"])
        self.margin_top.valueChanged.connect(lambda val: self.update_margin("top", val))
        margin_layout.addRow("Top:", self.margin_top)

        self.margin_right = QDoubleSpinBox()
        self.margin_right.setRange(0, 100)
        self.margin_right.setValue(self.document_settings["page"]["margins"]["right"])
        self.margin_right.valueChanged.connect(lambda val: self.update_margin("right", val))
        margin_layout.addRow("Right:", self.margin_right)

        self.margin_bottom = QDoubleSpinBox()
        self.margin_bottom.setRange(0, 100)
        self.margin_bottom.setValue(self.document_settings["page"]["margins"]["bottom"])
        self.margin_bottom.valueChanged.connect(lambda val: self.update_margin("bottom", val))
        margin_layout.addRow("Bottom:", self.margin_bottom)

        self.margin_left = QDoubleSpinBox()
        self.margin_left.setRange(0, 100)
        self.margin_left.setValue(self.document_settings["page"]["margins"]["left"])
        self.margin_left.valueChanged.connect(lambda val: self.update_margin("left", val))
        margin_layout.addRow("Left:", self.margin_left)

        layout.addRow(margin_group)

        box.setContentLayout(layout)
        return box

    def create_heading_settings_group(self):
        """Create heading settings group with tabs for each heading level"""
        box = CollapsibleBox("Heading Settings")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Create tabs for each heading level
        heading_tabs = QTabWidget()
        heading_tabs.setTabPosition(QTabWidget.TabPosition.North)
        heading_tabs.setDocumentMode(True)

        for level in range(1, 7):
            h_key = f"h{level}"
            tab = QWidget()
            tab_layout = QFormLayout(tab)
            tab_layout.setContentsMargins(5, 10, 5, 5)
            tab_layout.setVerticalSpacing(5)

            # Font button
            font_btn = QPushButton("Select Font...")
            current_font = QFont(
                self.document_settings["fonts"]["headings"][h_key]["family"],
                self.document_settings["fonts"]["headings"][h_key]["size"]
            )
            font_btn.setFont(current_font)
            font_btn.setText(f"{current_font.family()}, {current_font.pointSize()}pt")
            # Fix lambda to avoid potential KeyboardInterrupt issues
            font_btn.setProperty("heading_key", h_key)
            font_btn.clicked.connect(lambda: self.select_heading_font(self.sender().property("heading_key")))
            font_btn.setEnabled(not self.document_settings["format"]["use_master_font"])
            self.__setattr__(f"h{level}_font_btn", font_btn)
            tab_layout.addRow("Font:", font_btn)

            # Color button
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {self.document_settings['fonts']['headings'][h_key]['color']}")
            # Fix lambda to avoid potential KeyboardInterrupt issues
            def create_color_handler(heading_key):
                return lambda checked=False: self.select_heading_color(heading_key)
            color_btn.clicked.connect(create_color_handler(h_key))
            self.__setattr__(f"h{level}_color_btn", color_btn)
            tab_layout.addRow("Color:", color_btn)

            # Line spacing
            spacing = QDoubleSpinBox()
            spacing.setRange(0.5, 3.0)
            spacing.setSingleStep(0.1)
            spacing.setValue(self.document_settings["fonts"]["headings"][h_key]["spacing"])
            spacing.valueChanged.connect(lambda val, h=h_key: self.update_heading_spacing(h, val))
            self.__setattr__(f"h{level}_spacing", spacing)
            tab_layout.addRow("Line Spacing:", spacing)

            # Top margin
            margin_top = QSpinBox()
            margin_top.setRange(0, 100)
            margin_top.setValue(self.document_settings["fonts"]["headings"][h_key]["margin_top"])
            margin_top.valueChanged.connect(lambda val, h=h_key: self.update_heading_margin_top(h, val))
            self.__setattr__(f"h{level}_margin_top", margin_top)
            tab_layout.addRow("Top Margin:", margin_top)

            # Bottom margin
            margin_bottom = QSpinBox()
            margin_bottom.setRange(0, 100)
            margin_bottom.setValue(self.document_settings["fonts"]["headings"][h_key]["margin_bottom"])
            margin_bottom.valueChanged.connect(lambda val, h=h_key: self.update_heading_margin_bottom(h, val))
            self.__setattr__(f"h{level}_margin_bottom", margin_bottom)
            tab_layout.addRow("Bottom Margin:", margin_bottom)

            heading_tabs.addTab(tab, f"H{level}")

        layout.addWidget(heading_tabs)
        box.setContentLayout(layout)
        return box

    def create_paragraph_settings_group(self):
        """Create paragraph settings group"""
        box = CollapsibleBox("Paragraph Settings")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Spacing
        self.para_spacing = QDoubleSpinBox()
        self.para_spacing.setRange(0.5, 3.0)
        self.para_spacing.setSingleStep(0.1)
        self.para_spacing.setValue(self.document_settings["paragraphs"]["spacing"])
        self.para_spacing.valueChanged.connect(self.update_para_spacing)
        layout.addRow("Line Spacing:", self.para_spacing)

        # Top margin
        self.para_margin_top = QSpinBox()
        self.para_margin_top.setRange(0, 50)
        self.para_margin_top.setValue(self.document_settings["paragraphs"]["margin_top"])
        self.para_margin_top.valueChanged.connect(self.update_para_margin_top)
        layout.addRow("Top Margin:", self.para_margin_top)

        # Bottom margin
        self.para_margin_bottom = QSpinBox()
        self.para_margin_bottom.setRange(0, 50)
        self.para_margin_bottom.setValue(self.document_settings["paragraphs"]["margin_bottom"])
        self.para_margin_bottom.valueChanged.connect(self.update_para_margin_bottom)
        layout.addRow("Bottom Margin:", self.para_margin_bottom)

        # First line indent
        self.first_line_indent = QSpinBox()
        self.first_line_indent.setRange(0, 100)
        self.first_line_indent.setValue(self.document_settings["paragraphs"]["first_line_indent"])
        self.first_line_indent.valueChanged.connect(self.update_first_line_indent)
        layout.addRow("First Line Indent:", self.first_line_indent)

        # Alignment
        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["Left", "Center", "Right", "Justify"])
        self.alignment_combo.setCurrentText(self.document_settings["paragraphs"]["alignment"].capitalize())
        self.alignment_combo.currentTextChanged.connect(self.update_para_alignment)
        layout.addRow("Alignment:", self.alignment_combo)

        box.setContentLayout(layout)
        return box

    def create_list_settings_group(self):
        """Create list settings group"""
        box = CollapsibleBox("List Settings")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Bullet list styling group
        bullet_group = QGroupBox("Bullet List Styling")
        bullet_layout = QFormLayout(bullet_group)

        # Bullet indent
        self.bullet_indent = QSpinBox()
        self.bullet_indent.setRange(0, 100)
        self.bullet_indent.setValue(self.document_settings["lists"]["bullet_indent"])
        self.bullet_indent.valueChanged.connect(self.update_bullet_indent)
        bullet_layout.addRow("Indent:", self.bullet_indent)

        # Bullet style level 1
        self.bullet_style_l1 = QComboBox()
        bullet_styles = ["Disc", "Circle", "Square", "None", "Dash", "Triangle", "Arrow", "Checkmark", "Star", "Diamond", "Heart", "Pointer", "Greater"]
        self.bullet_style_l1.addItems(bullet_styles)
        if "bullet_style_l1" not in self.document_settings["lists"]:
            self.document_settings["lists"]["bullet_style_l1"] = "Disc"
        self.bullet_style_l1.setCurrentText(self.document_settings["lists"]["bullet_style_l1"])
        self.bullet_style_l1.currentTextChanged.connect(self.update_bullet_style_l1)
        bullet_layout.addRow("Level 1 Style:", self.bullet_style_l1)

        # Bullet style level 2
        self.bullet_style_l2 = QComboBox()
        self.bullet_style_l2.addItems(bullet_styles)
        if "bullet_style_l2" not in self.document_settings["lists"]:
            self.document_settings["lists"]["bullet_style_l2"] = "Circle"
        self.bullet_style_l2.setCurrentText(self.document_settings["lists"]["bullet_style_l2"])
        self.bullet_style_l2.currentTextChanged.connect(self.update_bullet_style_l2)
        bullet_layout.addRow("Level 2 Style:", self.bullet_style_l2)

        # Bullet style level 3
        self.bullet_style_l3 = QComboBox()
        self.bullet_style_l3.addItems(bullet_styles)
        if "bullet_style_l3" not in self.document_settings["lists"]:
            self.document_settings["lists"]["bullet_style_l3"] = "Square"
        self.bullet_style_l3.setCurrentText(self.document_settings["lists"]["bullet_style_l3"])
        self.bullet_style_l3.currentTextChanged.connect(self.update_bullet_style_l3)
        bullet_layout.addRow("Level 3 Style:", self.bullet_style_l3)

        # Custom bullet styles management
        custom_styles_layout = QHBoxLayout()

        # Add custom style button
        add_style_btn = QPushButton("Add Custom Style")
        add_style_btn.clicked.connect(self.add_custom_bullet_style)
        custom_styles_layout.addWidget(add_style_btn)

        # Delete custom style button
        delete_style_btn = QPushButton("Delete Custom Style")
        delete_style_btn.clicked.connect(self.delete_custom_bullet_style)
        custom_styles_layout.addWidget(delete_style_btn)

        bullet_layout.addRow("", custom_styles_layout)

        # Numbered list styling group
        number_group = QGroupBox("Numbered List Styling")
        number_layout = QFormLayout(number_group)

        # Number indent
        self.number_indent = QSpinBox()
        self.number_indent.setRange(0, 100)
        self.number_indent.setValue(self.document_settings["lists"]["number_indent"])
        self.number_indent.valueChanged.connect(self.update_number_indent)
        number_layout.addRow("Indent:", self.number_indent)

        # Number style level 1
        self.number_style_l1 = QComboBox()
        self.number_style_l1.addItems(["Decimal", "Lower Alpha", "Upper Alpha", "Lower Roman", "Upper Roman"])
        if "number_style_l1" not in self.document_settings["lists"]:
            self.document_settings["lists"]["number_style_l1"] = "Decimal"
        self.number_style_l1.setCurrentText(self.document_settings["lists"]["number_style_l1"])
        self.number_style_l1.currentTextChanged.connect(self.update_number_style_l1)
        number_layout.addRow("Level 1 Style:", self.number_style_l1)

        # Number style level 2
        self.number_style_l2 = QComboBox()
        self.number_style_l2.addItems(["Lower Alpha", "Decimal", "Upper Alpha", "Lower Roman", "Upper Roman"])
        if "number_style_l2" not in self.document_settings["lists"]:
            self.document_settings["lists"]["number_style_l2"] = "Lower Alpha"
        self.number_style_l2.setCurrentText(self.document_settings["lists"]["number_style_l2"])
        self.number_style_l2.currentTextChanged.connect(self.update_number_style_l2)
        number_layout.addRow("Level 2 Style:", self.number_style_l2)

        # Number style level 3
        self.number_style_l3 = QComboBox()
        self.number_style_l3.addItems(["Lower Roman", "Decimal", "Lower Alpha", "Upper Alpha", "Upper Roman"])
        if "number_style_l3" not in self.document_settings["lists"]:
            self.document_settings["lists"]["number_style_l3"] = "Lower Roman"
        self.number_style_l3.setCurrentText(self.document_settings["lists"]["number_style_l3"])
        self.number_style_l3.currentTextChanged.connect(self.update_number_style_l3)
        number_layout.addRow("Level 3 Style:", self.number_style_l3)

        # General list settings
        general_group = QGroupBox("General List Settings")
        general_layout = QFormLayout(general_group)

        # Item spacing
        self.list_item_spacing = QSpinBox()
        self.list_item_spacing.setRange(0, 30)
        self.list_item_spacing.setValue(self.document_settings["lists"]["item_spacing"])
        self.list_item_spacing.valueChanged.connect(self.update_list_item_spacing)
        general_layout.addRow("Item Spacing:", self.list_item_spacing)

        # Nested list indent
        self.nested_list_indent = QSpinBox()
        self.nested_list_indent.setRange(0, 100)
        if "nested_indent" not in self.document_settings["lists"]:
            self.document_settings["lists"]["nested_indent"] = 20
        self.nested_list_indent.setValue(self.document_settings["lists"]["nested_indent"])
        self.nested_list_indent.valueChanged.connect(self.update_nested_list_indent)
        general_layout.addRow("Nested Indent:", self.nested_list_indent)

        # Add all groups to the main layout
        main_layout.addWidget(bullet_group)
        main_layout.addWidget(number_group)
        main_layout.addWidget(general_group)

        box.setContentLayout(main_layout)
        return box

    def create_table_settings_group(self):
        """Create table settings group"""
        box = CollapsibleBox("Table Settings")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Border color
        self.table_border_color_btn = QPushButton()
        self.table_border_color_btn.setStyleSheet(f"background-color: {self.document_settings['table']['border_color']}")
        self.table_border_color_btn.clicked.connect(self.select_table_border_color)
        layout.addRow("Border Color:", self.table_border_color_btn)

        # Header background
        self.table_header_bg_btn = QPushButton()
        self.table_header_bg_btn.setStyleSheet(f"background-color: {self.document_settings['table']['header_bg']}")
        self.table_header_bg_btn.clicked.connect(self.select_table_header_bg)
        layout.addRow("Header BG:", self.table_header_bg_btn)

        # Cell padding
        self.cell_padding = QSpinBox()
        self.cell_padding.setRange(0, 30)
        self.cell_padding.setValue(self.document_settings["table"]["cell_padding"])
        self.cell_padding.valueChanged.connect(self.update_cell_padding)
        layout.addRow("Cell Padding:", self.cell_padding)

        box.setContentLayout(layout)
        return box

    def create_code_settings_group(self):
        """Create code block settings group"""
        box = CollapsibleBox("Code Block Settings")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Font family
        self.code_font_btn = QPushButton("Select Font...")
        current_code_font = QFont(
            self.document_settings["code"]["font_family"],
            self.document_settings["code"]["font_size"]
        )
        self.code_font_btn.setFont(current_code_font)
        self.code_font_btn.setText(f"{current_code_font.family()}, {current_code_font.pointSize()}pt")
        self.code_font_btn.clicked.connect(self.select_code_font)
        self.code_font_btn.setEnabled(not self.document_settings["format"]["use_master_font"])
        layout.addRow("Code Font:", self.code_font_btn)

        # Background color
        self.code_bg_color_btn = QPushButton()
        self.code_bg_color_btn.setStyleSheet(f"background-color: {self.document_settings['code']['background']}")
        self.code_bg_color_btn.clicked.connect(self.select_code_bg_color)
        layout.addRow("Background:", self.code_bg_color_btn)

        # Border color
        self.code_border_color_btn = QPushButton()
        self.code_border_color_btn.setStyleSheet(f"background-color: {self.document_settings['code']['border_color']}")
        self.code_border_color_btn.clicked.connect(self.select_code_border_color)
        layout.addRow("Border Color:", self.code_border_color_btn)

        box.setContentLayout(layout)
        return box

    def create_toc_settings_group(self):
        """Create table of contents settings group"""
        box = CollapsibleBox("Table of Contents")
        layout = QFormLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setVerticalSpacing(8)

        # Include TOC
        self.include_toc = QCheckBox()
        self.include_toc.setChecked(self.document_settings["toc"]["include"])
        self.include_toc.stateChanged.connect(self.update_include_toc)
        layout.addRow("Include TOC:", self.include_toc)

        # TOC depth
        self.toc_depth = QSpinBox()
        self.toc_depth.setRange(1, 6)
        self.toc_depth.setValue(self.document_settings["toc"]["depth"])
        self.toc_depth.valueChanged.connect(self.update_toc_depth)
        layout.addRow("TOC Depth:", self.toc_depth)

        # TOC title
        self.toc_title = QLineEdit()
        self.toc_title.setText(self.document_settings["toc"]["title"])
        self.toc_title.textChanged.connect(self.update_toc_title)
        layout.addRow("TOC Title:", self.toc_title)

        box.setContentLayout(layout)
        return box

    def toggle_settings_fields(self, state):
        """Enable or disable all settings fields based on the master toggle"""
        enabled = bool(state)

        # Enable/disable all settings groups
        for group in [
            self.format_settings_group,
            self.page_settings_group,
            self.text_settings_group,
            self.heading_settings_group,
            self.paragraph_settings_group,
            self.list_settings_group,
            self.table_settings_group,
            self.code_settings_group,
            self.toc_settings_group
        ]:
            group.setEnabled(enabled)

        # If disabled, apply the selected style
        if not enabled:
            # Get the current style
            current_style = self.preset_combo.currentText()
            self.apply_style_preset(current_style)

            # Show info message
            self.statusBar().showMessage(f"Applied '{current_style}' style template", 3000)

    def show_page_break_dialog(self):
        """Show dialog for inserting page break"""
        dialog = PageBreakDialog(self.markdown_editor, self)
        dialog.exec()

    def insert_page_break(self):
        """Insert page break marker at cursor position"""
        self.markdown_editor.insertPlainText("\n\n<!-- PAGE_BREAK -->\n\n")

    def show_restart_numbering_dialog(self):
        """Show dialog for inserting restart numbering marker"""
        dialog = RestartNumberingDialog(self.markdown_editor, self)
        dialog.exec()

    def insert_restart_numbering(self):
        """Insert restart numbering code at cursor position"""
        dialog = RestartNumberingDialog(self.markdown_editor, self)
        if dialog.exec():
            # The dialog will insert the marker directly
            pass

    def open_template_manager(self):
        """Open the template manager dialog"""
        from template_manager import TemplateManager
        dialog = TemplateManager(self)
        dialog.exec()

    def show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About Advanced Markdown to PDF Converter",
            "<h1>Advanced Markdown to PDF Converter</h1>"
            "<p>Version 1.0.0</p>"
            "<p>A powerful tool for converting Markdown to PDF, DOCX, and HTML.</p>"
            "<p>Supports multiple PDF engines, custom templates, and advanced formatting options.</p>"
            "<p>&copy; 2025 Your Name</p>"
        )

    def load_saved_presets(self):
        """Load user-saved style presets into the combobox"""
        presets_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
        if not os.path.exists(presets_dir):
            return

        preset_files = [f for f in os.listdir(presets_dir) if f.endswith('.json')]
        for preset_file in preset_files:
            preset_name = os.path.splitext(preset_file)[0]
            if self.preset_combo.findText(preset_name) == -1:
                self.preset_combo.addItem(preset_name)

    def save_current_style(self):
        """Save the current style settings"""
        # Get the current style name
        current_style = self.preset_combo.currentText()

        # Don't allow overwriting default styles
        default_styles = ["Business Professional", "Technical Document", "Academic", "Minimal", "Custom"]
        if current_style in default_styles:
            QMessageBox.warning(
                self,
                "Cannot Overwrite Default Style",
                f"'{current_style}' is a default style and cannot be overwritten. Use 'Save As New Style' instead."
            )
            return

        # Save the settings
        presets_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
        os.makedirs(presets_dir, exist_ok=True)

        preset_path = os.path.join(presets_dir, f"{current_style}.json")
        try:
            with open(preset_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_settings, f, indent=2)

            self.statusBar().showMessage(f"Style '{current_style}' saved", 3000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving Style",
                f"Failed to save style: {str(e)}"
            )

    def save_style_as_new(self):
        """Save the current style as a new preset"""
        # Ask for a new style name
        name, ok = QInputDialog.getText(
            self, 'Save Style As', 'Enter name for new style preset:'
        )

        if ok and name:
            # Save the settings with the new name
            presets_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
            os.makedirs(presets_dir, exist_ok=True)

            preset_path = os.path.join(presets_dir, f"{name}.json")
            try:
                with open(preset_path, 'w', encoding='utf-8') as f:
                    json.dump(self.document_settings, f, indent=2)

                # Add to preset combobox if not already there
                if self.preset_combo.findText(name) == -1:
                    self.preset_combo.addItem(name)
                    self.preset_combo.setCurrentText(name)

                self.statusBar().showMessage(f"Style '{name}' saved", 3000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Saving Style",
                    f"Failed to save style: {str(e)}"
                )

    # This is the old apply_style_preset method that is no longer used
    # The new method is defined at line ~2790
    def _old_apply_style_preset(self, preset_name):
        """Apply a style preset (old method, no longer used)"""
        pass

    def apply_business_preset(self):
        """Apply business professional style preset"""
        # Set up business-like styling
        self.document_settings["fonts"]["body"]["family"] = "Calibri"
        self.document_settings["fonts"]["body"]["size"] = 11
        self.document_settings["fonts"]["body"]["line_height"] = 1.5
        self.document_settings["colors"]["text"] = "#333333"
        self.document_settings["colors"]["background"] = "#FFFFFF"
        self.document_settings["colors"]["links"] = "#0563C1"

        # Format settings
        self.document_settings["format"]["technical_numbering"] = False
        self.document_settings["format"]["page_numbering"] = True
        self.document_settings["format"]["page_number_format"] = "Page {page} of {total}"
        self.document_settings["format"]["use_master_font"] = False
        self.document_settings["format"]["master_font"]["family"] = "Calibri"

        # Page settings
        self.document_settings["page"]["size"] = "A4"
        self.document_settings["page"]["orientation"] = "Portrait"
        self.document_settings["page"]["margins"]["top"] = 25.4
        self.document_settings["page"]["margins"]["right"] = 25.4
        self.document_settings["page"]["margins"]["bottom"] = 25.4
        self.document_settings["page"]["margins"]["left"] = 25.4

        # Paragraph settings
        self.document_settings["paragraphs"]["spacing"] = 1.5
        self.document_settings["paragraphs"]["margin_top"] = 0
        self.document_settings["paragraphs"]["margin_bottom"] = 10
        self.document_settings["paragraphs"]["first_line_indent"] = 0
        self.document_settings["paragraphs"]["alignment"] = "left"

        # Heading settings
        for level in range(1, 7):
            h_key = f"h{level}"
            self.document_settings["fonts"]["headings"][h_key]["family"] = "Calibri"
            self.document_settings["fonts"]["headings"][h_key]["color"] = "#2E74B5"

        # Specific heading sizes
        self.document_settings["fonts"]["headings"]["h1"]["size"] = 18
        self.document_settings["fonts"]["headings"]["h2"]["size"] = 16
        self.document_settings["fonts"]["headings"]["h3"]["size"] = 14
        self.document_settings["fonts"]["headings"]["h4"]["size"] = 13
        self.document_settings["fonts"]["headings"]["h5"]["size"] = 12
        self.document_settings["fonts"]["headings"]["h6"]["size"] = 11

        # List settings
        self.document_settings["lists"]["bullet_indent"] = 30
        self.document_settings["lists"]["number_indent"] = 30
        self.document_settings["lists"]["item_spacing"] = 5
        self.document_settings["lists"]["nested_indent"] = 20
        self.document_settings["lists"]["bullet_style_l1"] = "Disc"
        self.document_settings["lists"]["bullet_style_l2"] = "Circle"
        self.document_settings["lists"]["bullet_style_l3"] = "Square"
        self.document_settings["lists"]["number_style_l1"] = "Decimal"
        self.document_settings["lists"]["number_style_l2"] = "Lower Alpha"
        self.document_settings["lists"]["number_style_l3"] = "Lower Roman"

        # Table settings
        self.document_settings["table"]["border_color"] = "#CCCCCC"
        self.document_settings["table"]["header_bg"] = "#EEEEEE"
        self.document_settings["table"]["cell_padding"] = 5

        # Code settings
        self.document_settings["code"]["font_family"] = "Consolas"
        self.document_settings["code"]["font_size"] = 10
        self.document_settings["code"]["background"] = "#F5F5F5"
        self.document_settings["code"]["border_color"] = "#CCCCCC"

        # TOC settings
        self.document_settings["toc"]["include"] = False
        self.document_settings["toc"]["depth"] = 3
        self.document_settings["toc"]["title"] = "Table of Contents"

    def apply_technical_preset(self):
        """Apply technical document style preset"""
        # Set up technical document styling with numbered sections
        self.document_settings["fonts"]["body"]["family"] = "Arial"
        self.document_settings["fonts"]["body"]["size"] = 10
        self.document_settings["fonts"]["body"]["line_height"] = 1.4
        self.document_settings["colors"]["text"] = "#000000"
        self.document_settings["colors"]["background"] = "#FFFFFF"
        self.document_settings["colors"]["links"] = "#0000EE"

        # Format settings
        self.document_settings["format"]["technical_numbering"] = True
        self.document_settings["format"]["numbering_start"] = 2  # Start at H2
        self.document_settings["format"]["page_numbering"] = True
        self.document_settings["format"]["page_number_format"] = "Page {page}"
        self.document_settings["format"]["use_master_font"] = False
        self.document_settings["format"]["master_font"]["family"] = "Arial"

        # Page settings
        self.document_settings["page"]["size"] = "A4"
        self.document_settings["page"]["orientation"] = "Portrait"
        self.document_settings["page"]["margins"]["top"] = 25.4
        self.document_settings["page"]["margins"]["right"] = 25.4
        self.document_settings["page"]["margins"]["bottom"] = 25.4
        self.document_settings["page"]["margins"]["left"] = 25.4

        # Paragraph settings
        self.document_settings["paragraphs"]["spacing"] = 1.2
        self.document_settings["paragraphs"]["margin_top"] = 0
        self.document_settings["paragraphs"]["margin_bottom"] = 8
        self.document_settings["paragraphs"]["first_line_indent"] = 0
        self.document_settings["paragraphs"]["alignment"] = "left"

        # Heading settings
        for level in range(1, 7):
            h_key = f"h{level}"
            self.document_settings["fonts"]["headings"][h_key]["family"] = "Arial"
            self.document_settings["fonts"]["headings"][h_key]["color"] = "#000000"

        # Specific heading sizes
        self.document_settings["fonts"]["headings"]["h1"]["size"] = 16
        self.document_settings["fonts"]["headings"]["h2"]["size"] = 14
        self.document_settings["fonts"]["headings"]["h3"]["size"] = 12
        self.document_settings["fonts"]["headings"]["h4"]["size"] = 11
        self.document_settings["fonts"]["headings"]["h5"]["size"] = 10
        self.document_settings["fonts"]["headings"]["h6"]["size"] = 10

        # List settings
        self.document_settings["lists"]["bullet_indent"] = 25
        self.document_settings["lists"]["number_indent"] = 25
        self.document_settings["lists"]["item_spacing"] = 4
        self.document_settings["lists"]["nested_indent"] = 20
        self.document_settings["lists"]["bullet_style_l1"] = "Disc"
        self.document_settings["lists"]["bullet_style_l2"] = "Circle"
        self.document_settings["lists"]["bullet_style_l3"] = "Square"
        self.document_settings["lists"]["number_style_l1"] = "Decimal"
        self.document_settings["lists"]["number_style_l2"] = "Lower Alpha"
        self.document_settings["lists"]["number_style_l3"] = "Lower Roman"

        # Table settings
        self.document_settings["table"]["border_color"] = "#000000"
        self.document_settings["table"]["header_bg"] = "#DDDDDD"
        self.document_settings["table"]["cell_padding"] = 4

        # Code settings
        self.document_settings["code"]["font_family"] = "Courier New"
        self.document_settings["code"]["font_size"] = 9
        self.document_settings["code"]["background"] = "#F0F0F0"
        self.document_settings["code"]["border_color"] = "#CCCCCC"

        # TOC settings
        self.document_settings["toc"]["include"] = True
        self.document_settings["toc"]["depth"] = 3
        self.document_settings["toc"]["title"] = "Contents"

    def apply_academic_preset(self):
        """Apply academic style preset"""
        # Set up academic styling
        self.document_settings["fonts"]["body"]["family"] = "Times New Roman"
        self.document_settings["fonts"]["body"]["size"] = 12
        self.document_settings["fonts"]["body"]["line_height"] = 2.0
        self.document_settings["colors"]["text"] = "#000000"
        self.document_settings["colors"]["background"] = "#FFFFFF"
        self.document_settings["colors"]["links"] = "#000080"

        # Format settings
        self.document_settings["format"]["technical_numbering"] = False
        self.document_settings["format"]["page_numbering"] = True
        self.document_settings["format"]["page_number_format"] = "{page}"
        self.document_settings["format"]["use_master_font"] = False
        self.document_settings["format"]["master_font"]["family"] = "Times New Roman"

        # Page settings
        self.document_settings["page"]["size"] = "Letter"
        self.document_settings["page"]["orientation"] = "Portrait"
        self.document_settings["page"]["margins"]["top"] = 25.4
        self.document_settings["page"]["margins"]["right"] = 25.4
        self.document_settings["page"]["margins"]["bottom"] = 25.4
        self.document_settings["page"]["margins"]["left"] = 25.4

        # Paragraph settings
        self.document_settings["paragraphs"]["spacing"] = 2.0
        self.document_settings["paragraphs"]["margin_top"] = 0
        self.document_settings["paragraphs"]["margin_bottom"] = 12
        self.document_settings["paragraphs"]["first_line_indent"] = 20
        self.document_settings["paragraphs"]["alignment"] = "left"

        # Heading settings
        for level in range(1, 7):
            h_key = f"h{level}"
            self.document_settings["fonts"]["headings"][h_key]["family"] = "Times New Roman"
            self.document_settings["fonts"]["headings"][h_key]["color"] = "#000000"

        # Specific heading sizes
        self.document_settings["fonts"]["headings"]["h1"]["size"] = 16
        self.document_settings["fonts"]["headings"]["h2"]["size"] = 14
        self.document_settings["fonts"]["headings"]["h3"]["size"] = 13
        self.document_settings["fonts"]["headings"]["h4"]["size"] = 12
        self.document_settings["fonts"]["headings"]["h5"]["size"] = 12
        self.document_settings["fonts"]["headings"]["h6"]["size"] = 12

        # List settings
        self.document_settings["lists"]["bullet_indent"] = 30
        self.document_settings["lists"]["number_indent"] = 30
        self.document_settings["lists"]["item_spacing"] = 6
        self.document_settings["lists"]["nested_indent"] = 20
        self.document_settings["lists"]["bullet_style_l1"] = "Disc"
        self.document_settings["lists"]["bullet_style_l2"] = "Circle"
        self.document_settings["lists"]["bullet_style_l3"] = "Square"
        self.document_settings["lists"]["number_style_l1"] = "Decimal"
        self.document_settings["lists"]["number_style_l2"] = "Lower Alpha"
        self.document_settings["lists"]["number_style_l3"] = "Lower Roman"

        # Table settings
        self.document_settings["table"]["border_color"] = "#000000"
        self.document_settings["table"]["header_bg"] = "#FFFFFF"
        self.document_settings["table"]["cell_padding"] = 5

        # Code settings
        self.document_settings["code"]["font_family"] = "Courier New"
        self.document_settings["code"]["font_size"] = 10
        self.document_settings["code"]["background"] = "#F8F8F8"
        self.document_settings["code"]["border_color"] = "#DDDDDD"

        # TOC settings
        self.document_settings["toc"]["include"] = True
        self.document_settings["toc"]["depth"] = 3
        self.document_settings["toc"]["title"] = "Contents"

    def apply_minimal_preset(self):
        """Apply minimal style preset"""
        # Set up minimal styling
        self.document_settings["fonts"]["body"]["family"] = "Georgia"
        self.document_settings["fonts"]["body"]["size"] = 11
        self.document_settings["fonts"]["body"]["line_height"] = 1.5
        self.document_settings["colors"]["text"] = "#333333"
        self.document_settings["colors"]["background"] = "#FFFFFF"
        self.document_settings["colors"]["links"] = "#333333"

        # Format settings
        self.document_settings["format"]["technical_numbering"] = False
        self.document_settings["format"]["page_numbering"] = False
        self.document_settings["format"]["page_number_format"] = "{page}"
        self.document_settings["format"]["use_master_font"] = False
        self.document_settings["format"]["master_font"]["family"] = "Georgia"

        # Page settings
        self.document_settings["page"]["size"] = "A4"
        self.document_settings["page"]["orientation"] = "Portrait"
        self.document_settings["page"]["margins"]["top"] = 20
        self.document_settings["page"]["margins"]["right"] = 20
        self.document_settings["page"]["margins"]["bottom"] = 20
        self.document_settings["page"]["margins"]["left"] = 20

        # Paragraph settings
        self.document_settings["paragraphs"]["spacing"] = 1.5
        self.document_settings["paragraphs"]["margin_top"] = 0
        self.document_settings["paragraphs"]["margin_bottom"] = 10
        self.document_settings["paragraphs"]["first_line_indent"] = 0
        self.document_settings["paragraphs"]["alignment"] = "left"

        # Heading settings
        for level in range(1, 7):
            h_key = f"h{level}"
            self.document_settings["fonts"]["headings"][h_key]["family"] = "Arial"
            self.document_settings["fonts"]["headings"][h_key]["color"] = "#333333"

        # Specific heading sizes
        self.document_settings["fonts"]["headings"]["h1"]["size"] = 16
        self.document_settings["fonts"]["headings"]["h2"]["size"] = 14
        self.document_settings["fonts"]["headings"]["h3"]["size"] = 12
        self.document_settings["fonts"]["headings"]["h4"]["size"] = 11
        self.document_settings["fonts"]["headings"]["h5"]["size"] = 11
        self.document_settings["fonts"]["headings"]["h6"]["size"] = 11

        # List settings
        self.document_settings["lists"]["bullet_indent"] = 20
        self.document_settings["lists"]["number_indent"] = 20
        self.document_settings["lists"]["item_spacing"] = 5
        self.document_settings["lists"]["nested_indent"] = 20
        self.document_settings["lists"]["bullet_style_l1"] = "Disc"
        self.document_settings["lists"]["bullet_style_l2"] = "Circle"
        self.document_settings["lists"]["bullet_style_l3"] = "Square"
        self.document_settings["lists"]["number_style_l1"] = "Decimal"
        self.document_settings["lists"]["number_style_l2"] = "Lower Alpha"
        self.document_settings["lists"]["number_style_l3"] = "Lower Roman"

        # Table settings
        self.document_settings["table"]["border_color"] = "#DDDDDD"
        self.document_settings["table"]["header_bg"] = "#F5F5F5"
        self.document_settings["table"]["cell_padding"] = 5

        # Code settings
        self.document_settings["code"]["font_family"] = "Consolas"
        self.document_settings["code"]["font_size"] = 10
        self.document_settings["code"]["background"] = "#F8F8F8"
        self.document_settings["code"]["border_color"] = "#EEEEEE"

        # TOC settings
        self.document_settings["toc"]["include"] = False
        self.document_settings["toc"]["depth"] = 2
        self.document_settings["toc"]["title"] = "Contents"

    def load_user_preset(self, preset_name):
        """Load a user-defined preset"""
        presets_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
        preset_path = os.path.join(presets_dir, f"{preset_name}.json")

        if os.path.exists(preset_path):
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    preset_settings = json.load(f)

                # Update the settings
                self.document_settings.update(preset_settings)

                # Update UI to reflect loaded settings
                self.update_ui_from_settings()

                self.statusBar().showMessage(f"Loaded preset: {preset_name}", 3000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Preset",
                    f"Failed to load preset '{preset_name}': {str(e)}"
                )

    def update_ui_from_settings(self):
        """Update UI controls to reflect current settings"""
        try:
            # Block signals to prevent marking changes during UI update
            self.blockSignals(True)

            # Format settings
            if hasattr(self, 'technical_numbering') and self.technical_numbering is not None:
                self.technical_numbering.setChecked(self.document_settings["format"]["technical_numbering"])

            if "numbering_start" in self.document_settings["format"] and hasattr(self, 'numbering_start') and self.numbering_start is not None:
                self.numbering_start.setCurrentIndex(self.document_settings["format"]["numbering_start"] - 1)

            if hasattr(self, 'page_numbering') and self.page_numbering is not None:
                self.page_numbering.setChecked(self.document_settings["format"]["page_numbering"])

            if hasattr(self, 'page_number_format') and self.page_number_format is not None:
                self.page_number_format.setText(self.document_settings["format"]["page_number_format"])

            if hasattr(self, 'use_master_font') and self.use_master_font is not None:
                self.use_master_font.setChecked(self.document_settings["format"]["use_master_font"])

            # Update the preset combo box
            if hasattr(self, 'preset_combo') and self.preset_combo is not None and hasattr(self, 'style_manager') and self.style_manager is not None:
                if self.preset_combo.currentText() != self.style_manager.current_style_name:
                    self.preset_combo.setCurrentText(self.style_manager.current_style_name)

            # Page settings
            if hasattr(self, 'page_size_combo') and self.page_size_combo is not None:
                self.page_size_combo.setCurrentText(self.document_settings["page"]["size"])

            if hasattr(self, 'orientation_combo') and self.orientation_combo is not None:
                self.orientation_combo.setCurrentText(self.document_settings["page"]["orientation"].capitalize())

            if hasattr(self, 'margin_top') and self.margin_top is not None:
                self.margin_top.setValue(self.document_settings["page"]["margins"]["top"])

            if hasattr(self, 'margin_right') and self.margin_right is not None:
                self.margin_right.setValue(self.document_settings["page"]["margins"]["right"])

            if hasattr(self, 'margin_bottom') and self.margin_bottom is not None:
                self.margin_bottom.setValue(self.document_settings["page"]["margins"]["bottom"])

            if hasattr(self, 'margin_left') and self.margin_left is not None:
                self.margin_left.setValue(self.document_settings["page"]["margins"]["left"])

            # Text settings
            if hasattr(self, 'body_font_btn') and self.body_font_btn is not None:
                body_font = QFont(
                    self.document_settings["fonts"]["body"]["family"],
                    self.document_settings["fonts"]["body"]["size"]
                )
                self.body_font_btn.setFont(body_font)
                self.body_font_btn.setText(f"{body_font.family()}, {body_font.pointSize()}pt")

            if hasattr(self, 'line_height') and self.line_height is not None:
                self.line_height.setValue(self.document_settings["fonts"]["body"]["line_height"])

            if hasattr(self, 'text_color_btn') and self.text_color_btn is not None:
                self.text_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['text']}")

            if hasattr(self, 'bg_color_btn') and self.bg_color_btn is not None:
                self.bg_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['background']}")

            if hasattr(self, 'link_color_btn') and self.link_color_btn is not None:
                self.link_color_btn.setStyleSheet(f"background-color: {self.document_settings['colors']['links']}")

            # Heading settings
            for level in range(1, 7):
                h_key = f"h{level}"
                if hasattr(self, f"h{level}_font_btn"):
                    font_btn = getattr(self, f"h{level}_font_btn")
                    if font_btn is not None:
                        heading_font = QFont(
                            self.document_settings["fonts"]["headings"][h_key]["family"],
                            self.document_settings["fonts"]["headings"][h_key]["size"]
                        )
                        font_btn.setFont(heading_font)
                        font_btn.setText(f"{heading_font.family()}, {heading_font.pointSize()}pt")

                if hasattr(self, f"h{level}_color_btn"):
                    color_btn = getattr(self, f"h{level}_color_btn")
                    if color_btn is not None:
                        color_btn.setStyleSheet(f"background-color: {self.document_settings['fonts']['headings'][h_key]['color']}")

                if hasattr(self, f"h{level}_spacing"):
                    spacing = getattr(self, f"h{level}_spacing")
                    if spacing is not None:
                        spacing.setValue(self.document_settings["fonts"]["headings"][h_key]["spacing"])

                if hasattr(self, f"h{level}_margin_top"):
                    margin_top = getattr(self, f"h{level}_margin_top")
                    if margin_top is not None:
                        margin_top.setValue(self.document_settings["fonts"]["headings"][h_key]["margin_top"])

                if hasattr(self, f"h{level}_margin_bottom"):
                    margin_bottom = getattr(self, f"h{level}_margin_bottom")
                    if margin_bottom is not None:
                        margin_bottom.setValue(self.document_settings["fonts"]["headings"][h_key]["margin_bottom"])

            # Paragraph settings
            if hasattr(self, 'para_spacing') and self.para_spacing is not None:
                self.para_spacing.setValue(self.document_settings["paragraphs"]["spacing"])

            if hasattr(self, 'para_margin_top') and self.para_margin_top is not None:
                self.para_margin_top.setValue(self.document_settings["paragraphs"]["margin_top"])

            if hasattr(self, 'para_margin_bottom') and self.para_margin_bottom is not None:
                self.para_margin_bottom.setValue(self.document_settings["paragraphs"]["margin_bottom"])

            if hasattr(self, 'first_line_indent') and self.first_line_indent is not None:
                self.first_line_indent.setValue(self.document_settings["paragraphs"]["first_line_indent"])

            if hasattr(self, 'alignment_combo') and self.alignment_combo is not None:
                self.alignment_combo.setCurrentText(self.document_settings["paragraphs"]["alignment"].capitalize())

            # List settings
            if hasattr(self, 'bullet_indent') and self.bullet_indent is not None:
                self.bullet_indent.setValue(self.document_settings["lists"]["bullet_indent"])

            if hasattr(self, 'number_indent') and self.number_indent is not None:
                self.number_indent.setValue(self.document_settings["lists"]["number_indent"])

            if hasattr(self, 'list_item_spacing') and self.list_item_spacing is not None:
                self.list_item_spacing.setValue(self.document_settings["lists"]["item_spacing"])

            if "nested_indent" in self.document_settings["lists"] and hasattr(self, 'nested_list_indent') and self.nested_list_indent is not None:
                self.nested_list_indent.setValue(self.document_settings["lists"]["nested_indent"])

            # Table settings
            if hasattr(self, 'table_border_color_btn') and self.table_border_color_btn is not None:
                self.table_border_color_btn.setStyleSheet(f"background-color: {self.document_settings['table']['border_color']}")

            if hasattr(self, 'table_header_bg_btn') and self.table_header_bg_btn is not None:
                self.table_header_bg_btn.setStyleSheet(f"background-color: {self.document_settings['table']['header_bg']}")

            if hasattr(self, 'cell_padding') and self.cell_padding is not None:
                self.cell_padding.setValue(self.document_settings["table"]["cell_padding"])

            # Code settings
            if hasattr(self, 'code_font_btn') and self.code_font_btn is not None:
                code_font = QFont(
                    self.document_settings["code"]["font_family"],
                    self.document_settings["code"]["font_size"]
                )
                self.code_font_btn.setFont(code_font)
                self.code_font_btn.setText(f"{code_font.family()}, {code_font.pointSize()}pt")

            if hasattr(self, 'code_bg_color_btn') and self.code_bg_color_btn is not None:
                self.code_bg_color_btn.setStyleSheet(f"background-color: {self.document_settings['code']['background']}")

            if hasattr(self, 'code_border_color_btn') and self.code_border_color_btn is not None:
                self.code_border_color_btn.setStyleSheet(f"background-color: {self.document_settings['code']['border_color']}")

            # TOC settings
            if hasattr(self, 'include_toc') and self.include_toc is not None:
                self.include_toc.setChecked(self.document_settings["toc"]["include"])

            if hasattr(self, 'toc_depth') and self.toc_depth is not None:
                self.toc_depth.setValue(self.document_settings["toc"]["depth"])

            if hasattr(self, 'toc_title') and self.toc_title is not None:
                self.toc_title.setText(self.document_settings["toc"]["title"])

            # Enable/disable controls based on use_master_font
            self.toggle_master_font(self.document_settings["format"]["use_master_font"])

            # Unblock signals
            self.blockSignals(False)
        except Exception as e:
            logger.error(f"Error in update_ui_from_settings: {str(e)}")
            # Ensure signals are unblocked even if an error occurs
            self.blockSignals(False)

    def new_file(self):
        """Create a new empty document"""
        try:
            if self.markdown_editor.toPlainText() and self.current_file is not None:
                # Ask to save changes
                reply = QMessageBox.question(
                    self, 'Save Changes',
                    'Do you want to save changes to the current document?',
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save
                )

                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return

            # Clear editor and reset current file
            self.markdown_editor.clear()
            self.current_file = None
            self.setWindowTitle('Advanced Markdown to PDF Converter')
            self.update_preview()
        except Exception as e:
            logger.error(f"Error in new_file: {str(e)}")
            QMessageBox.critical(self, 'Error', f'An error occurred while creating a new file: {str(e)}')

    def update_recent_files_menu(self):
        """Update the recent files menu with the current list of recent files"""
        # Clear the menu
        self.recent_files_menu.clear()

        # Remove any existing recent file actions to prevent memory leaks
        if hasattr(self, '_recent_file_actions'):
            for action in self._recent_file_actions:
                if action:  # Just check if action exists, QAction doesn't have isNull method
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
            display_name = os.path.basename(file_path)

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
        """Create a method to handle opening a specific recent file

        This avoids issues with lambda functions and KeyboardInterrupt errors
        by creating a proper bound method for each file path.
        """
        # Create a copy of the file path to avoid reference issues
        path_copy = str(file_path)

        def handler(checked=False):
            try:
                # Use the copied path, not the original reference
                self.open_recent_file(path_copy)
            except Exception as e:
                logger.error(f"Error opening recent file: {str(e)}")
                QMessageBox.critical(self, 'Error', f'Could not open the file: {str(e)}')
        return handler

    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list"""
        if not file_path:
            return

        # Convert to absolute path
        file_path = os.path.abspath(file_path)

        # Remove the file if it's already in the list
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        # Add the file to the beginning of the list
        self.recent_files.insert(0, file_path)

        # Trim the list if it's too long
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]

        # Update the menu
        self.update_recent_files_menu()

        # Save settings
        self.save_settings()

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.recent_files = []
        self.update_recent_files_menu()
        self.save_settings()

    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if not os.path.exists(file_path):
            # File no longer exists, remove it from the list
            QMessageBox.warning(self, 'File Not Found', f'The file {file_path} no longer exists.')
            self.recent_files.remove(file_path)
            self.update_recent_files_menu()
            self.save_settings()
            return

        # Check for unsaved changes
        if self.markdown_editor.toPlainText() and self.current_file is not None:
            # Ask to save changes
            reply = QMessageBox.question(
                self, 'Save Changes',
                'Do you want to save changes to the current document?',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        # Open the file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.markdown_editor.setPlainText(file.read())

            self.current_file = file_path
            self.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

            # Update recent files list (moves this file to the top)
            self.add_to_recent_files(file_path)

            # Save the directory for next time
            self.dialog_paths["open"] = os.path.dirname(file_path)
            self.save_settings()

            self.update_preview()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open the file: {str(e)}')

    def open_file(self):
        """Open an existing Markdown file"""
        if self.markdown_editor.toPlainText() and self.current_file is not None:
            # Ask to save changes
            reply = QMessageBox.question(
                self, 'Save Changes',
                'Do you want to save changes to the current document?',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        # Get start directory from saved paths
        start_dir = self.dialog_paths.get("open", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Markdown File', start_dir, 'Markdown Files (*.md *.markdown);;All Files (*)'
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.markdown_editor.setPlainText(file.read())

                self.current_file = file_path
                self.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

                # Add to recent files
                self.add_to_recent_files(file_path)

                # Save the directory for next time
                self.dialog_paths["open"] = os.path.dirname(file_path)
                self.save_settings()

                self.update_preview()
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not open the file: {str(e)}')

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.markdown_editor.toPlainText())
                return True
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not save the file: {str(e)}')
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        """Save the current file with a new name"""
        # Get start directory from saved paths
        start_dir = self.dialog_paths.get("save", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        # Support both .md and .mdz formats
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 'Save File', start_dir, 'Markdown Files (*.md);;MDZ Files (*.mdz);;All Files (*)'
        )

        if file_path:
            # Determine file type based on selected filter or extension
            if selected_filter == 'MDZ Files (*.mdz)' or file_path.lower().endswith('.mdz'):
                # Save as MDZ file
                if not file_path.lower().endswith('.mdz'):
                    file_path += '.mdz'
                return self._save_as_mdz(file_path)
            else:
                # Save as regular markdown file
                if not file_path.lower().endswith(('.md', '.markdown')):
                    file_path += '.md'
                return self._save_as_markdown(file_path)

        return False

    def _save_as_markdown(self, file_path):
        """Save as regular markdown file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.markdown_editor.toPlainText())

            self.current_file = file_path
            self.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

            # Add to recent files
            self.add_to_recent_files(file_path)

            # Save the directory for next time
            self.dialog_paths["save"] = os.path.dirname(file_path)
            self.save_settings()

            return True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not save the file: {str(e)}')
            return False

    def _save_as_mdz(self, file_path):
        """Save as MDZ file with current document settings"""
        try:
            # Import the MDZ exporter
            from mdz_export import MDZExporter

            # Collect assets (images, etc.) from the document
            assets = self._collect_document_assets()

            # Create an MDZ exporter
            exporter = MDZExporter()

            # Export to MDZ
            result = exporter.export_to_mdz(
                markdown_text=self.markdown_editor.toPlainText(),
                output_file=file_path,
                document_settings=self.document_settings,
                assets=assets
            )

            if result:
                self.current_file = file_path
                self.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

                # Add to recent files
                self.add_to_recent_files(file_path)

                # Save the directory for next time
                self.dialog_paths["save"] = os.path.dirname(file_path)
                self.save_settings()

                # Show compatibility warning for MDZ format
                QMessageBox.information(
                    self, 'MDZ File Saved',
                    f'Document saved as MDZ file:\n{file_path}\n\n'
                    'Note: MDZ files include document settings and assets. '
                    'They can be opened with this application or compatible MDZ viewers.'
                )
                return True
            else:
                QMessageBox.critical(self, 'Error', 'Could not save the MDZ file. See log for details.')
                return False

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not save the MDZ file: {str(e)}')
            return False

    def _collect_document_assets(self):
        """Collect assets (images, etc.) referenced in the document"""
        assets = {}

        # Get the markdown text
        markdown_text = self.markdown_editor.toPlainText()

        # Simple regex to find image references
        import re

        # Find markdown image syntax: ![alt](path)
        image_pattern = r'!\[.*?\]\(([^)]+)\)'
        matches = re.findall(image_pattern, markdown_text)

        for match in matches:
            image_path = match.strip()
            # Skip URLs (http/https)
            if not image_path.startswith(('http://', 'https://')):
                # Try to resolve relative paths
                if self.current_file and not os.path.isabs(image_path):
                    # Resolve relative to current file directory
                    base_dir = os.path.dirname(self.current_file)
                    full_path = os.path.join(base_dir, image_path)
                    if os.path.exists(full_path):
                        assets[image_path] = full_path
                elif os.path.exists(image_path):
                    # Absolute path that exists
                    assets[image_path] = image_path

        return assets

    def preprocess_for_export(self, markdown_text, engine_type):
        """Preprocess markdown based on export engine"""
        # Use the improved markdown preprocessing from markdown_export_fix
        from markdown_export_fix import preprocess_markdown_for_engine
        return preprocess_markdown_for_engine(markdown_text, engine_type)

    def export_document(self):
        """Export the current document to various formats using a single dialog with format selection"""
        logger.info("Starting unified export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        # Define available export formats
        export_formats = {
            "MDZ File (*.mdz)": {"ext": ".mdz", "title": "Export to MDZ"},
            "PDF File (*.pdf)": {"ext": ".pdf", "title": "Export to PDF"},
            "Word Document (*.docx)": {"ext": ".docx", "title": "Export to DOCX"},
            "HTML File (*.html)": {"ext": ".html", "title": "Export to HTML"},
            "EPUB File (*.epub)": {"ext": ".epub", "title": "Export to EPUB"}
        }

        # Get default filename based on current file
        default_filename = "document.mdz"  # Default to MDZ
        if self.current_file:
            default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".mdz"

        # Get start directory from saved paths
        start_dir = self.dialog_paths.get("export", "")
        logger.debug(f"Export directory path: {start_dir}")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = default_filename
        else:
            start_dir = os.path.join(start_dir, default_filename)

        # Create filter string for file dialog
        filter_string = ";;".join(export_formats.keys())

        # Show save dialog with format selection
        output_file, selected_filter = QFileDialog.getSaveFileName(
            self, 'Export Document', start_dir, filter_string
        )
        logger.info(f"Selected output file: {output_file}")
        logger.info(f"Selected format: {selected_filter}")

        if not output_file:
            return False

        # Get the selected format info
        format_info = export_formats.get(selected_filter)
        if not format_info:
            logger.error(f"Unknown format selected: {selected_filter}")
            QMessageBox.critical(self, 'Export Error', f'Unknown format selected: {selected_filter}')
            return False

        # Add appropriate extension if not present
        if not output_file.lower().endswith(format_info["ext"]):
            output_file += format_info["ext"]

        # Save the directory for next time
        self.dialog_paths["export"] = os.path.dirname(output_file)
        self.save_settings()

        # Call the appropriate export function based on the selected format
        if format_info["ext"] == ".pdf":
            return self._export_to_pdf(output_file)
        elif format_info["ext"] == ".docx":
            return self._export_to_docx(output_file)
        elif format_info["ext"] == ".html":
            return self._export_to_html(output_file)
        elif format_info["ext"] == ".epub":
            return self._export_to_epub(output_file)
        elif format_info["ext"] == ".mdz":
            return self._export_to_mdz(output_file)
        else:
            logger.error(f"Unsupported export format: {format_info['ext']}")
            QMessageBox.critical(self, 'Export Error', f'Unsupported export format: {format_info["ext"]}')
            return False

    def _export_to_pdf(self, output_file=None):
        """Export the current document to PDF using pandoc

        Args:
            output_file: Optional path to save the output file. If not provided, a file dialog will be shown.

        Returns:
            bool: True if export was successful, False otherwise
        """
        logger.info("Starting export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            if output_file is None:  # Only show warning in interactive mode
                QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        # If output_file is not provided, ask for the output file location
        if output_file is None:
            default_filename = "document.pdf"
            if self.current_file:
                default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".pdf"

            # Get start directory from saved paths
            start_dir = self.dialog_paths.get("export", "")
            logger.debug(f"Export directory path: {start_dir}")
            if not start_dir or not os.path.exists(start_dir):
                start_dir = default_filename
            else:
                start_dir = os.path.join(start_dir, default_filename)

            output_file, _ = QFileDialog.getSaveFileName(
                self, 'Export to PDF', start_dir, 'PDF Files (*.pdf);;All Files (*)'
            )
            logger.info(f"Selected output file: {output_file}")

            if not output_file:
                return False

            # Save the directory for next time
            self.dialog_paths["export"] = os.path.dirname(output_file)
            self.save_settings()
        else:
            logger.info(f"Using provided output file: {output_file}")

        # Add .pdf extension if not present
        if isinstance(output_file, str) and not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'

        # Show a progress dialog with cancel button if not in headless mode
        progress = None
        if output_file is None or not self.isHidden():  # Interactive mode
            progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to PDF...')
            progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
            progress.show()
            QApplication.processEvents()

        # Arrange engines based on preference and reliability
        from markdown_export_fix import arrange_engines_for_export
        try_engines = arrange_engines_for_export(self.found_engines, self.document_settings["format"]["preferred_engine"])

        # If wkhtmltopdf is the preferred engine, add a fallback engine
        if try_engines and try_engines[0] == 'wkhtmltopdf':
            logger.info("wkhtmltopdf is the preferred engine, adding fallback engines")
            # Make sure we have fallback engines ready
            fallback_engines = [e for e in self.found_engines if e != 'wkhtmltopdf']
            if fallback_engines:
                logger.info(f"Added fallback engines: {fallback_engines}")
                # Keep wkhtmltopdf as first choice but ensure we have fallbacks
                try_engines = [try_engines[0]] + fallback_engines

        logger.debug(f"Will try these engines in order: {try_engines}")

        for engine in try_engines:
            try:
                # Update progress message if progress dialog exists
                if progress:
                    progress.setText(f'Trying PDF engine: {engine}...')
                    QApplication.processEvents()

                logger.info(f"Attempting export with engine: {engine}")

                # Use try-finally to ensure cleanup even if errors occur
                md_file = None
                css_file = None
                template_file = None
                no_numbers_file = None
                header_file = None

                try:
                    # Create temporary markdown file
                    markdown_text = self.markdown_editor.toPlainText()

                    # Pre-process the markdown based on engine with enhanced mermaid support
                    from markdown_export_fix import preprocess_markdown_for_engine
                    markdown_text = preprocess_markdown_for_engine(markdown_text, engine)

                    # Create temporary markdown file
                    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                        md_file.write(markdown_text)
                        md_path = md_file.name

                    logger.debug(f"Created temporary markdown file: {md_path}")

                    # Create CSS file from settings
                    css_content = RenderUtils.generate_css_from_settings(self.document_settings)
                    css_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False)
                    css_file.write(css_content)
                    css_file.close()

                    logger.debug(f"Created temporary CSS file: {css_file.name}")

                    # Prepare pandoc command
                    if not isinstance(output_file, str):
                        # If output_file is not a string, use a temporary file
                        temp_output = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                        temp_output.close()
                        output_path = temp_output.name
                    else:
                        output_path = output_file

                    cmd = ['C:\\Users\\joshd\\AppData\\Local\\Pandoc\\pandoc.exe', md_path, '-o', output_path, '--standalone']

                    # Check if we're exporting to a non-PDF format
                    output_ext = '.pdf'  # Default to PDF
                    if isinstance(output_path, str):
                        output_ext = os.path.splitext(output_path)[1].lower()
                    if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                        logger.info(f"Exporting to non-PDF format: {output_ext}")
                        # For non-PDF formats, we don't need a PDF engine
                        # Just add format-specific options if needed
                        if output_ext == '.docx':
                            # Use reference-doc if available
                            reference_docx = os.path.join(os.path.dirname(__file__), 'templates', 'reference.docx')
                            if os.path.exists(reference_docx):
                                cmd.append(f'--reference-doc={reference_docx}')
                                logger.info(f"Using reference DOCX: {reference_docx}")
                        elif output_ext == '.html':
                            # Use custom CSS if available
                            custom_css = os.path.join(os.path.dirname(__file__), 'templates', 'custom.css')
                            if os.path.exists(custom_css):
                                cmd.append(f'--css={custom_css}')
                                logger.info(f"Using custom CSS: {custom_css}")
                    else:
                        # Add PDF engine for PDF output
                        engine_path = self.found_engines.get(engine, engine)
                        cmd.append(f'--pdf-engine={engine_path}')

                        # Use custom LaTeX template if available
                        custom_template = os.path.join(os.path.dirname(__file__), 'templates', 'custom.latex')
                        if os.path.exists(custom_template):
                            cmd.append(f'--template={custom_template}')
                            logger.info(f"Using custom LaTeX template: {custom_template}")

                        # Add engine-specific options with improved mermaid support
                        from markdown_export_fix import update_pandoc_command_for_engine
                        cmd = update_pandoc_command_for_engine(engine, cmd)

                    # Add CSS and other common options
                    cmd.append(f'--css={css_file.name}')

                    # Add template for LaTeX engines
                    use_latex = engine in ["xelatex", "pdflatex", "lualatex"]
                    if use_latex:
                        # Don't use a custom template for now
                        logger.info("Using default pandoc template")

                        # Add special handling for LaTeX engines
                        logger.debug("Adding special handling for LaTeX engines")

                        # Use a simpler approach for LaTeX engines
                        cmd.append('-V')
                        cmd.append('documentclass=article')

                        # Add font packages
                        if engine == "xelatex":
                            # Use fontspec directly instead of fontfamily
                            # Remove the previous font variables
                            for i, arg in enumerate(cmd):
                                if arg == '--variable=mainfont:DejaVu Serif' or \
                                   arg == '--variable=sansfont:DejaVu Sans' or \
                                   arg == '--variable=monofont:DejaVu Sans Mono':
                                    cmd[i] = '--variable=dummy:dummy'  # Replace with dummy value

                            # Add the correct font variables
                            cmd.append('--variable')
                            cmd.append('mainfont=DejaVu Serif')
                            cmd.append('--variable')
                            cmd.append('sansfont=DejaVu Sans')
                            cmd.append('--variable')
                            cmd.append('monofont=DejaVu Sans Mono')

                    # Add basic header file for HTML styling
                    if engine not in ["xelatex", "pdflatex", "lualatex"]:
                        # Only include styling for non-LaTeX engines
                        header_content = """
                        <style>
                        /* Basic styling for HTML output */
                        body {
                            font-family: Arial, sans-serif;
                            line-height: 1.5;
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                        }
                        pre {
                            background-color: #f5f5f5;
                            padding: 10px;
                            border-radius: 5px;
                            overflow: auto;
                        }
                        table {
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }
                        th, td {
                            border: 1px solid #ddd;
                            padding: 8px;
                        }
                        th {
                            background-color: #f2f2f2;
                        }
                        </style>
                        """
                        header_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.html', delete=False)
                        header_file.write(header_content)
                        header_file.close()
                        cmd.extend(['--include-in-header', header_file.name])

                    # Add TOC if needed
                    if self.document_settings["toc"]["include"]:
                        cmd.append('--toc')
                        cmd.append(f'--toc-depth={self.document_settings["toc"]["depth"]}')
                        cmd.append('-V')
                        cmd.append(f'toc-title={self.document_settings["toc"]["title"]}')

                    # Add technical numbering options
                    if not self.document_settings["format"]["technical_numbering"]:
                        cmd.extend(['--variable', 'secnumdepth=-2'])
                        cmd.extend(['--variable', 'disable-numbering=true'])
                    else:
                        cmd.append('--number-sections')
                        # Set the heading level at which numbering starts
                        numbering_start = self.document_settings["format"].get("numbering_start", 1)
                        cmd.extend(['--variable', f'secnumdepth={7-numbering_start}'])
                        cmd.extend(['--variable', 'technical_numbering=true'])

                    # Add common variables
                    cmd.extend([
                        '-V', f'papersize={self.document_settings["page"]["size"].lower()}',
                        '-V', f'margin-top={self.document_settings["page"]["margins"]["top"]}mm',
                        '-V', f'margin-right={self.document_settings["page"]["margins"]["right"]}mm',
                        '-V', f'margin-bottom={self.document_settings["page"]["margins"]["bottom"]}mm',
                        '-V', f'margin-left={self.document_settings["page"]["margins"]["left"]}mm'
                    ])

                    # Add empty title metadata to prevent title from showing in the document
                    cmd.extend(['--metadata', 'title='])

                    # Add mathjax for math support
                    cmd.append('--mathjax')

                    # Log the command
                    logger.info(f"Running pandoc command: {' '.join(cmd)}")

                    # Run the command with increased timeout for complex mermaid diagrams
                    # Use a shorter timeout for wkhtmltopdf as it tends to hang
                    if engine == 'wkhtmltopdf':
                        process_timeout = 60  # 1 minute for wkhtmltopdf
                    else:
                        process_timeout = 180  # 3 minutes for other engines
                    logger.info(f"Using timeout of {process_timeout} seconds for engine {engine}")

                    try:
                        result = subprocess.run(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=process_timeout
                        )
                    except Exception as e:
                        logger.error(f"Exception with engine {engine}: {str(e)}")
                        continue

                    # Check if export was successful
                    if result.returncode == 0:
                        # Success!
                        output_ext = '.pdf'  # Default to PDF
                        if isinstance(output_path, str):
                            output_ext = os.path.splitext(output_path)[1].lower()
                        if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                            logger.info(f"Export to {output_ext} successful")
                        else:
                            logger.info(f"PDF export successful with engine: {engine}")

                        if progress:
                            progress.close()

                        # Show success message if not in headless mode and not in test mode
                        if (output_file is None or not self.isHidden()) and not self._is_test_environment:  # Interactive mode
                            QMessageBox.information(
                                self, 'Export Successful',
                                f'Document exported successfully to:\n{output_path}'
                            )
                        elif self._is_test_environment:
                            logger.info(f"Test mode: Suppressing success dialog for export to: {output_path}")
                        return True
                    else:
                        # This engine failed, log the error and try the next one
                        output_ext = '.pdf'  # Default to PDF
                        if isinstance(output_path, str):
                            output_ext = os.path.splitext(output_path)[1].lower()
                        if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                            logger.warning(f"Export to {output_ext} failed: {result.stderr}")
                        else:
                            logger.warning(f"Engine {engine} failed: {result.stderr}")

                        if engine == try_engines[-1]:  # Last engine to try
                            if progress:
                                progress.close()

                            # Show error message if not in headless mode and not in test mode
                            if (output_file is None or not self.isHidden()) and not self._is_test_environment:  # Interactive mode
                                if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                                    QMessageBox.critical(
                                        self, 'Export Error',
                                        f'Error exporting to {output_ext[1:].upper()}:\n{result.stderr}'
                                    )
                                else:
                                    QMessageBox.critical(
                                        self, 'Export Error',
                                        f'Error exporting to PDF:\n{result.stderr}'
                                    )
                            elif self._is_test_environment:
                                if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                                    logger.error(f"Test mode: Suppressing error dialog for export to {output_ext[1:].upper()}: {result.stderr}")
                                else:
                                    logger.error(f"Test mode: Suppressing error dialog for export to PDF: {result.stderr}")
                            return False

                except Exception as e:
                    # Error with this engine, log and try next
                    logger.error(f"Exception with engine {engine}: {str(e)}")

                    if engine == try_engines[-1]:  # Last engine to try
                        if progress:
                            progress.close()

                        # Show error message if not in headless mode and not in test mode
                        if (output_file is None or not self.isHidden()) and not self._is_test_environment:  # Interactive mode
                            QMessageBox.critical(
                                self, 'Export Error',
                                f'Error exporting to PDF:\n{str(e)}'
                            )
                        elif self._is_test_environment:
                            logger.error(f"Test mode: Suppressing error dialog for export to PDF: {str(e)}")
                        return False

                finally:
                    # Clean up temporary files
                    for file_path in [
                        getattr(md_file, 'name', None),
                        getattr(css_file, 'name', None),
                        getattr(template_file, 'name', None),
                        getattr(no_numbers_file, 'name', None),
                        getattr(header_file, 'name', None)
                    ]:
                        if file_path and os.path.exists(file_path):
                            try:
                                os.unlink(file_path)
                                logger.debug(f"Deleted temporary file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Error cleaning up temp file {file_path}: {e}")

            except Exception as e:
                logger.error(f"Serious error with engine {engine}: {str(e)}")
                if engine == try_engines[-1]:  # Last engine to try
                    if progress:
                        progress.close()

                    # Show error message if not in headless mode
                    if output_file is None or not self.isHidden():  # Interactive mode
                        QMessageBox.critical(
                            self, 'Export Error',
                            f'Error exporting to PDF:\n{str(e)}'
                        )
                    return False

        # If we've tried all engines and none worked
        if progress:
            progress.close()

        # Show error message if not in headless mode and not in test mode
        if (output_file is None or not self.isHidden()) and not self._is_test_environment:  # Interactive mode
            output_ext = '.pdf'  # Default to PDF
            if isinstance(output_file, str):
                output_ext = os.path.splitext(output_file)[1].lower()

            if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                QMessageBox.critical(
                    self, 'Export Error',
                    f'Failed to export to {output_ext[1:].upper()}.'
                )
            else:
                QMessageBox.critical(
                    self, 'Export Error',
                    'Failed to export PDF with any available engine.'
                )
        elif self._is_test_environment:
            output_ext = '.pdf'  # Default to PDF
            if isinstance(output_file, str):
                output_ext = os.path.splitext(output_file)[1].lower()

            if output_ext in ['.docx', '.html', '.epub', '.odt', '.rtf', '.txt']:
                logger.error(f"Test mode: Suppressing error dialog for export to {output_ext[1:].upper()}")
            else:
                logger.error("Test mode: Suppressing error dialog for export to PDF with any available engine")
        return False

    def update_preview(self):
        """Update the HTML preview with current settings and robust error handling"""
        # Add a debounce mechanism to prevent multiple rapid calls
        current_time = time.time()
        if hasattr(self, '_last_preview_update_time'):
            # If less than 100ms has passed since the last update, skip this update
            if current_time - self._last_preview_update_time < 0.1:
                logger.debug("Skipping duplicate preview update (debounce)")
                return

        # Update the timestamp
        self._last_preview_update_time = current_time

        # Add a counter to track how many times this method is called
        if not hasattr(self, '_update_preview_count'):
            self._update_preview_count = 0
        self._update_preview_count += 1
        logger.debug(f"Main update_preview call #{self._update_preview_count}")

        try:
            # Make sure document settings are up to date in the page preview
            if hasattr(self, 'page_preview') and self.page_preview is not None:
                # Update document settings first
                self.page_preview.update_document_settings(self.document_settings)
                logger.debug("Updated document settings in page preview")

                # We no longer need to clear the content as the page_preview component
                # now handles this properly with the _last_html_content property
                # This prevents the flickering when updating the preview

            # Update the preview
            RenderUtils.update_preview(self.markdown_editor, self.page_preview, self.document_settings)
            logger.debug(f"Preview updated successfully (call #{self._update_preview_count})")
        except Exception as e:
            logger.error(f"Error in update_preview: {str(e)}")
            # Show error in status bar
            self.statusBar().showMessage(f"Error updating preview: {str(e)}", 5000)

    def test_page_navigation(self):
        """Test page navigation functionality"""
        try:
            # Run the page navigation test in the page preview
            result = self.page_preview.test_page_navigation()
            if result:
                self.statusBar().showMessage("Page navigation test completed successfully", 5000)
            else:
                self.statusBar().showMessage("Page navigation test failed", 5000)
        except Exception as e:
            logger.error(f"Error testing page navigation: {str(e)}")
            self.statusBar().showMessage(f"Error testing page navigation: {str(e)}", 5000)

    def test_page_breaks(self):
        """Test page break detection and visualization"""
        try:
            # Run the page break test in the page preview
            result = self.page_preview.test_page_breaks()
            if result:
                self.statusBar().showMessage("Page break test completed successfully", 5000)
            else:
                self.statusBar().showMessage("Page break test failed", 5000)
        except Exception as e:
            logger.error(f"Error testing page breaks: {str(e)}")
            self.statusBar().showMessage(f"Error testing page breaks: {str(e)}", 5000)

    def open_test_framework(self):
        """Open the test framework dialog"""
        try:
            # Import the test framework
            from test_framework import TestDialog

            # Create and show the test dialog
            dialog = TestDialog(self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error opening test framework: {str(e)}")
            self.statusBar().showMessage(f"Error opening test framework: {str(e)}", 5000)

    def generate_css_from_settings(self):
        """Generate enhanced CSS from current settings"""
        return RenderUtils.generate_css_from_settings(self.document_settings)

    def generate_latex_template(self):
        """Generate an improved LaTeX template with support for styling and diagrams"""
        return RenderUtils.generate_latex_template()

    def _export_to_docx(self, output_file=None):
        """Export the current document to DOCX format using pandoc

        Args:
            output_file: Optional path to save the DOCX. If not provided, a file dialog will be shown.

        Returns:
            bool: True if export was successful, False otherwise
        """
        logger.info("Starting DOCX export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            if output_file is None:  # Only show warning in interactive mode
                QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        # If no output file provided, ask for the output file location
        if output_file is None:
            default_filename = "document.docx"
            if self.current_file:
                default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".docx"

            # Get start directory from saved paths
            start_dir = self.dialog_paths.get("export", "")
            logger.debug(f"Export directory path: {start_dir}")
            if not start_dir or not os.path.exists(start_dir):
                start_dir = default_filename
            else:
                start_dir = os.path.join(start_dir, default_filename)

            output_file, _ = QFileDialog.getSaveFileName(
                self, 'Export to DOCX', start_dir, 'Word Documents (*.docx);;All Files (*)'
            )
            logger.info(f"Selected output file: {output_file}")

            if not output_file:
                return False

            # Add .docx extension if not present
            if isinstance(output_file, str) and not output_file.lower().endswith('.docx'):
                output_file += '.docx'

            # Save the directory for next time
            self.dialog_paths["export"] = os.path.dirname(output_file)
            self.save_settings()
        else:
            logger.info(f"Using provided output file: {output_file}")

        # Show a progress dialog with cancel button if not in headless mode
        progress = None
        if output_file is None or not self.isHidden():  # Interactive mode
            progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to DOCX...')
            progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
            progress.show()
            QApplication.processEvents()

        try:
            # Create temporary markdown file
            markdown_text = self.markdown_editor.toPlainText()

            # Pre-process the markdown
            from markdown_export_fix import preprocess_markdown_for_engine
            markdown_text = preprocess_markdown_for_engine(markdown_text, "docx")

            # Create temporary markdown file
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                md_file.write(markdown_text)
                md_path = md_file.name

            logger.debug(f"Created temporary markdown file: {md_path}")

            # Create CSS file from settings
            css_content = RenderUtils.generate_css_from_settings(self.document_settings)
            css_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False)
            css_file.write(css_content)
            css_file.close()

            logger.debug(f"Created temporary CSS file: {css_file.name}")

            # Prepare pandoc command
            if not isinstance(output_file, str):
                # If output_file is not a string, use a temporary file
                temp_output = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
                temp_output.close()
                output_path = temp_output.name
            else:
                output_path = output_file

            cmd = ['C:\\Users\\joshd\\AppData\\Local\\Pandoc\\pandoc.exe', md_path, '-o', output_path, '--standalone']

            # Add CSS and other common options
            cmd.append(f'--css={css_file.name}')

            # Add title metadata to prevent warnings
            title = "Document"
            if self.current_file:
                title = os.path.splitext(os.path.basename(self.current_file))[0]
            cmd.extend(['--metadata', f'title={title}'])

            # Add TOC if needed
            if self.document_settings["toc"]["include"]:
                cmd.append('--toc')
                cmd.append(f'--toc-depth={self.document_settings["toc"]["depth"]}')

            # Add technical numbering options
            if self.document_settings["format"]["technical_numbering"]:
                cmd.append('--number-sections')
                # Set the heading level at which numbering starts
                numbering_start = self.document_settings["format"].get("numbering_start", 1)
                cmd.extend(['--variable', f'secnumdepth={7-numbering_start}'])

            # Log the command
            logger.info(f"Running pandoc command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60  # 1 minute timeout
            )

            # Check if export was successful
            if result.returncode == 0:
                # Success!
                logger.info("DOCX export successful")
                if progress:
                    progress.close()

                # Show success message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.information(
                        self, 'Export Successful',
                        f'Document exported successfully to:\n{output_path}'
                    )
                return True
            else:
                # Export failed
                if progress:
                    progress.close()

                # Show error message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.critical(
                        self, 'Export Error',
                        f'Error exporting to DOCX:\n{result.stderr}'
                    )
                return False

        except Exception as e:
            logger.error(f"Exception during DOCX export: {str(e)}")
            if progress:
                progress.close()

            # Show error message if not in headless mode
            if output_file is None or not self.isHidden():  # Interactive mode
                QMessageBox.critical(
                    self, 'Export Error',
                    f'Error exporting to DOCX:\n{str(e)}'
                )
            return False
        finally:
            # Clean up temporary files
            for file_path in [md_path, css_file.name]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.unlink(file_path)
                        logger.debug(f"Deleted temporary file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error cleaning up temp file {file_path}: {e}")

    def _export_to_epub(self, output_file=None):
        """Export the current document to EPUB format using pandoc

        Args:
            output_file: Optional path to save the EPUB. If not provided, a file dialog will be shown.

        Returns:
            bool: True if export was successful, False otherwise
        """
        logger.info("Starting EPUB export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            if output_file is None:  # Only show warning in interactive mode
                QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        # If no output file provided, ask for the output file location
        if output_file is None:
            default_filename = "document.epub"
            if self.current_file:
                default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".epub"

            # Get start directory from saved paths
            start_dir = self.dialog_paths.get("export", "")
            logger.debug(f"Export directory path: {start_dir}")
            if not start_dir or not os.path.exists(start_dir):
                start_dir = default_filename
            else:
                start_dir = os.path.join(start_dir, default_filename)

            output_file, _ = QFileDialog.getSaveFileName(
                self, 'Export to EPUB', start_dir, 'EPUB Files (*.epub);;All Files (*)'
            )
            logger.info(f"Selected output file: {output_file}")

            if not output_file:
                return False

            # Add .epub extension if not present
            if isinstance(output_file, str) and not output_file.lower().endswith('.epub'):
                output_file += '.epub'

            # Save the directory for next time
            self.dialog_paths["export"] = os.path.dirname(output_file)
            self.save_settings()
        else:
            logger.info(f"Using provided output file: {output_file}")

        # Show a progress dialog with cancel button if not in headless mode
        progress = None
        if output_file is None or not self.isHidden():  # Interactive mode
            progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to EPUB...')
            progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
            progress.show()
            QApplication.processEvents()

        try:
            # Create temporary markdown file
            markdown_text = self.markdown_editor.toPlainText()

            # Pre-process the markdown
            from markdown_export_fix import preprocess_markdown_for_engine
            markdown_text = preprocess_markdown_for_engine(markdown_text, "epub")

            # Create temporary markdown file
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                md_file.write(markdown_text)
                md_path = md_file.name

            logger.debug(f"Created temporary markdown file: {md_path}")

            # Create CSS file from settings
            css_content = RenderUtils.generate_css_from_settings(self.document_settings)
            css_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False)
            css_file.write(css_content)
            css_file.close()

            logger.debug(f"Created temporary CSS file: {css_file.name}")

            # Prepare pandoc command
            if not isinstance(output_file, str):
                # If output_file is not a string, use a temporary file
                temp_output = tempfile.NamedTemporaryFile(suffix='.epub', delete=False)
                temp_output.close()
                output_path = temp_output.name
            else:
                output_path = output_file

            cmd = ['C:\\Users\\joshd\\AppData\\Local\\Pandoc\\pandoc.exe', md_path, '-o', output_path, '--standalone']

            # Add CSS and other common options
            cmd.append(f'--css={css_file.name}')

            # Add metadata for EPUB
            title = "Document"  # Default title
            if isinstance(output_path, str):
                title = os.path.splitext(os.path.basename(output_path))[0]
            cmd.extend(['--metadata', f'title={title}'])

            # Add TOC if needed
            if self.document_settings["toc"]["include"]:
                cmd.append('--toc')
                cmd.append(f'--toc-depth={self.document_settings["toc"]["depth"]}')

            # Add technical numbering options
            if self.document_settings["format"]["technical_numbering"]:
                cmd.append('--number-sections')
                # Set the heading level at which numbering starts
                numbering_start = self.document_settings["format"].get("numbering_start", 1)
                cmd.extend(['--variable', f'secnumdepth={7-numbering_start}'])

            # Log the command
            logger.info(f"Running pandoc command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60  # 1 minute timeout
            )

            # Check if export was successful
            if result.returncode == 0:
                # Success!
                logger.info("EPUB export successful")
                if progress:
                    progress.close()

                # Show success message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.information(
                        self, 'Export Successful',
                        f'Document exported successfully to:\n{output_path}'
                    )
                return True
            else:
                # Export failed
                if progress:
                    progress.close()

                # Show error message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.critical(
                        self, 'Export Error',
                        f'Error exporting to EPUB:\n{result.stderr}'
                    )
                return False

        except Exception as e:
            logger.error(f"Exception during EPUB export: {str(e)}")
            if progress:
                progress.close()

            # Show error message if not in headless mode
            if output_file is None or not self.isHidden():  # Interactive mode
                QMessageBox.critical(
                    self, 'Export Error',
                    f'Error exporting to EPUB:\n{str(e)}'
                )
            return False
        finally:
            # Clean up temporary files
            for file_path in [md_path, css_file.name]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.unlink(file_path)
                        logger.debug(f"Deleted temporary file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error cleaning up temp file {file_path}: {e}")

    def _export_to_mdz(self, output_file):
        """Export the current document to MDZ format (Markdown with Zstandard compression)

        Args:
            output_file: Path to save the MDZ file.

        Returns:
            bool: True if export was successful, False otherwise
        """
        logger.info("Starting MDZ export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        try:
            # Show a progress dialog
            progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to MDZ...')
            progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
            progress.show()
            QApplication.processEvents()

            # Import the MDZ exporter
            from mdz_export import MDZExporter

            # Collect assets (images, etc.) from the document
            assets = self._collect_document_assets()

            # Create an MDZ exporter
            exporter = MDZExporter()

            # Export to MDZ
            result = exporter.export_to_mdz(
                markdown_text=self.markdown_editor.toPlainText(),
                output_file=output_file,
                document_settings=self.document_settings,
                assets=assets
            )

            # Close the progress dialog
            progress.close()

            if result:
                # Show success message
                QMessageBox.information(
                    self, 'Export Successful',
                    f'Document exported successfully to:\n{output_file}'
                )
                return True
            else:
                QMessageBox.critical(
                    self, 'Export Error',
                    f'Error exporting to MDZ. See log for details.'
                )
                return False

        except Exception as e:
            logger.error(f"Exception during MDZ export: {str(e)}")
            if 'progress' in locals():
                progress.close()

            QMessageBox.critical(
                self, 'Export Error',
                f'Error exporting to MDZ:\n{str(e)}'
            )
            return False

    def _show_dialog_if_not_test_mode(self, dialog_type, title, message):
        """
        Show a dialog box only if not in test mode

        Args:
            dialog_type: The type of dialog to show (QMessageBox.Information, QMessageBox.Critical, etc.)
            title: The dialog title
            message: The dialog message

        Returns:
            The result of the dialog, or None if in test mode
        """
        if self._is_test_environment:
            # In test mode, just log the message instead of showing a dialog
            if dialog_type == QMessageBox.Icon.Information:
                logger.info(f"Test mode: Suppressing dialog '{title}': {message}")
            elif dialog_type == QMessageBox.Icon.Critical:
                logger.error(f"Test mode: Suppressing dialog '{title}': {message}")
            elif dialog_type == QMessageBox.Icon.Warning:
                logger.warning(f"Test mode: Suppressing dialog '{title}': {message}")
            else:
                logger.info(f"Test mode: Suppressing dialog '{title}': {message}")
            return None
        else:
            # Not in test mode, show the dialog
            return QMessageBox(dialog_type, title, message).exec()

    def _collect_document_assets(self):
        """
        Collect assets (images, etc.) from the document

        Returns:
            List of asset dictionaries with 'path', 'data', and 'type'
        """
        assets = []

        try:
            # Extract image references from markdown
            import re
            markdown_text = self.markdown_editor.toPlainText()

            # Find all image references in the markdown
            image_pattern = r'!\[.*?\]\((.*?)\)'
            image_refs = re.findall(image_pattern, markdown_text)

            # Process each image reference
            for img_ref in image_refs:
                # Skip URLs
                if img_ref.startswith(('http://', 'https://')):
                    continue

                # Try to load the image file
                img_path = img_ref
                if not os.path.isabs(img_path) and self.current_file:
                    # Make path relative to the current file
                    img_path = os.path.join(os.path.dirname(self.current_file), img_ref)

                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        img_data = f.read()

                    assets.append({
                        'path': img_ref,
                        'data': img_data,
                        'type': 'binary'
                    })
                    logger.debug(f"Added asset: {img_ref}")

            # Find all other file references (e.g., for code includes)
            file_pattern = r'```include\s+(.*?)\s*```'
            file_refs = re.findall(file_pattern, markdown_text)

            # Process each file reference
            for file_ref in file_refs:
                file_path = file_ref.strip()
                if not os.path.isabs(file_path) and self.current_file:
                    # Make path relative to the current file
                    file_path = os.path.join(os.path.dirname(self.current_file), file_ref)

                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_data = f.read()

                    assets.append({
                        'path': file_ref,
                        'data': file_data,
                        'type': 'text'
                    })
                    logger.debug(f"Added asset: {file_ref}")

        except Exception as e:
            logger.error(f"Error collecting document assets: {str(e)}")

        return assets

    def _export_to_html(self, output_file=None):
        """Export the current document to HTML format using pandoc

        Args:
            output_file: Optional path to save the HTML. If not provided, a file dialog will be shown.

        Returns:
            bool: True if export was successful, False otherwise
        """
        logger.info("Starting HTML export process")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            if output_file is None:  # Only show warning in interactive mode
                QMessageBox.warning(self, 'Warning', 'No content to export.')
            return False

        # If no output file provided, ask for the output file location
        if output_file is None:
            default_filename = "document.html"
            if self.current_file:
                default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".html"

            # Get start directory from saved paths
            start_dir = self.dialog_paths.get("export", "")
            logger.debug(f"Export directory path: {start_dir}")
            if not start_dir or not os.path.exists(start_dir):
                start_dir = default_filename
            else:
                start_dir = os.path.join(start_dir, default_filename)

            output_file, _ = QFileDialog.getSaveFileName(
                self, 'Export to HTML', start_dir, 'HTML Files (*.html);;All Files (*)'
            )
            logger.info(f"Selected output file: {output_file}")

            if not output_file:
                return False

            # Add .html extension if not present
            if isinstance(output_file, str) and not output_file.lower().endswith('.html'):
                output_file += '.html'

            # Save the directory for next time
            self.dialog_paths["export"] = os.path.dirname(output_file)
            self.save_settings()
        else:
            logger.info(f"Using provided output file: {output_file}")

        # Show a progress dialog with cancel button if not in headless mode
        progress = None
        if output_file is None or not self.isHidden():  # Interactive mode
            progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to HTML...')
            progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
            progress.show()
            QApplication.processEvents()

        try:
            # Create temporary markdown file
            markdown_text = self.markdown_editor.toPlainText()

            # Pre-process the markdown
            from markdown_export_fix import preprocess_markdown_for_engine
            markdown_text = preprocess_markdown_for_engine(markdown_text, "html")

            # Create temporary markdown file
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                md_file.write(markdown_text)
                md_path = md_file.name

            logger.debug(f"Created temporary markdown file: {md_path}")

            # Create CSS file from settings
            css_content = RenderUtils.generate_css_from_settings(self.document_settings)
            css_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False)
            css_file.write(css_content)
            css_file.close()

            logger.debug(f"Created temporary CSS file: {css_file.name}")

            # Prepare pandoc command
            if not isinstance(output_file, str):
                # If output_file is not a string, use a temporary file
                temp_output = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
                temp_output.close()
                output_path = temp_output.name
            else:
                output_path = output_file

            cmd = ['C:\\Users\\joshd\\AppData\\Local\\Pandoc\\pandoc.exe', md_path, '-o', output_path, '--standalone', '--self-contained']

            # Add CSS and other common options
            cmd.append(f'--css={css_file.name}')

            # Add title metadata to prevent warnings
            title = "Document"
            if self.current_file:
                title = os.path.splitext(os.path.basename(self.current_file))[0]
            cmd.extend(['--metadata', f'title={title}'])

            # Add TOC if needed
            if self.document_settings["toc"]["include"]:
                cmd.append('--toc')
                cmd.append(f'--toc-depth={self.document_settings["toc"]["depth"]}')

            # Add technical numbering options
            if self.document_settings["format"]["technical_numbering"]:
                cmd.append('--number-sections')
                # Set the heading level at which numbering starts
                numbering_start = self.document_settings["format"].get("numbering_start", 1)
                cmd.extend(['--variable', f'secnumdepth={7-numbering_start}'])

            # Add basic header file for HTML styling
            header_content = """
            <style>
            /* Basic styling for HTML output */
            body {
                font-family: Arial, sans-serif;
                line-height: 1.5;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            </style>
            """
            header_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.html', delete=False)
            header_file.write(header_content)
            header_file.close()
            cmd.extend(['--include-in-header', header_file.name])

            # Log the command
            logger.info(f"Running pandoc command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60  # 1 minute timeout
            )

            # Check if export was successful
            if result.returncode == 0:
                # Success!
                logger.info("HTML export successful")
                if progress:
                    progress.close()

                # Show success message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.information(
                        self, 'Export Successful',
                        f'Document exported successfully to:\n{output_path}'
                    )
                return True
            else:
                # Export failed
                if progress:
                    progress.close()

                # Show error message if not in headless mode
                if output_file is None or not self.isHidden():  # Interactive mode
                    QMessageBox.critical(
                        self, 'Export Error',
                        f'Error exporting to HTML:\n{result.stderr}'
                    )
                return False

        except Exception as e:
            logger.error(f"Exception during HTML export: {str(e)}")
            if progress:
                progress.close()

            # Show error message if not in headless mode
            if output_file is None or not self.isHidden():  # Interactive mode
                QMessageBox.critical(
                    self, 'Export Error',
                    f'Error exporting to HTML:\n{str(e)}'
                )
            return False
        finally:
            # Clean up temporary files
            for file_path in [md_path, css_file.name, header_file.name]:
                if file_path and os.path.exists(file_path):
                    try:
                        os.unlink(file_path)
                        logger.debug(f"Deleted temporary file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error cleaning up temp file {file_path}: {e}")

    def update_preferred_engine(self, engine):
        """Update the preferred PDF engine and save the setting"""
        if engine == "Auto-select":
            # Default to weasyprint if available
            if "weasyprint" in self.found_engines:
                self.document_settings["format"]["preferred_engine"] = "weasyprint"
            elif "xelatex" in self.found_engines:
                self.document_settings["format"]["preferred_engine"] = "xelatex"
            elif len(self.found_engines) > 0:
                # Use first available engine
                self.document_settings["format"]["preferred_engine"] = next(iter(self.found_engines.keys()))
        else:
            self.document_settings["format"]["preferred_engine"] = engine

        # Mark settings as changed
        self.style_manager.mark_as_changed()

        # Save the setting
        self.save_settings()

        # Update the status bar
        self.statusBar().showMessage(f"PDF engine set to: {self.document_settings['format']['preferred_engine']}", 3000)

    def update_pandoc_command_for_engine(engine, cmd):
        """Add engine-specific options to pandoc command"""
        # Add engine-specific options
        if engine == "weasyprint":
            # No special options needed for weasyprint
            pass
        elif engine == "wkhtmltopdf":
            # Fix for wkhtmltopdf parameters
            # Remove the problematic --javascript-delay parameter
            # and use the correct format for wkhtmltopdf options
            cmd.append('--pdf-engine-opt=--enable-local-file-access')
            cmd.append('--pdf-engine-opt=--enable-javascript')
            # Instead of javascript-delay, use a script timeout option
            cmd.append('--pdf-engine-opt=--javascript-delay')
            cmd.append('--pdf-engine-opt=3000')
            cmd.append('--pdf-engine-opt=--no-stop-slow-scripts')

        return cmd

    def arrange_engines_for_export(self, preferred_engine):
        """Arrange engines in order of preference for export attempts"""
        try_engines = []

        # First try the preferred engine if specified and available
        if preferred_engine != "Auto-select" and preferred_engine in self.found_engines:
            try_engines.append(preferred_engine)

        # Then try weasyprint as it has good Mermaid support
        if "weasyprint" in self.found_engines and preferred_engine != "weasyprint":
            try_engines.append("weasyprint")

        # Then try other LaTeX engines
        for engine in ["xelatex", "pdflatex", "lualatex"]:
            if engine in self.found_engines and engine not in try_engines:
                try_engines.append(engine)

        # Then try any other available engines
        for engine in self.found_engines:
            if engine not in try_engines:
                try_engines.append(engine)

        return try_engines

    def toggle_numbering_with_restart(self, state):
        """Toggle technical numbering with automatic preview refresh"""
        self.document_settings["format"]["technical_numbering"] = bool(state)
        self.style_manager.mark_as_changed()
        self.update_preview()

    def update_numbering_start(self, index):
        """Update the heading level at which numbering starts"""
        # Index is 0-based, but we want to store 1-based heading levels
        self.document_settings["format"]["numbering_start"] = index + 1
        self.style_manager.mark_as_changed()
        self.update_preview()

    def update_page_numbering(self, state):
        """Update page numbering setting"""
        try:
            self.document_settings["format"]["page_numbering"] = bool(state)
            self.style_manager.mark_as_changed()
            # Update the preview to reflect the change
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.update_preview)
            logger.debug(f"Page numbering updated to: {bool(state)}")
        except Exception as e:
            logger.error(f"Error updating page numbering: {str(e)}")
        except KeyboardInterrupt:
            logger.warning("Page numbering update interrupted by user")

    def update_page_number_format(self, format_text):
        """Update page number format"""
        self.document_settings["format"]["page_number_format"] = format_text
        self.style_manager.mark_as_changed()

    def toggle_master_font(self, state):
        """Toggle master font control"""
        try:
            use_master_font = bool(state)
            self.document_settings["format"]["use_master_font"] = use_master_font

            # Check if style_manager exists before calling mark_as_changed
            if hasattr(self, 'style_manager') and self.style_manager is not None:
                self.style_manager.mark_as_changed()

            # Check if UI elements exist before trying to access them
            if hasattr(self, 'body_font_btn') and self.body_font_btn is not None:
                self.body_font_btn.setEnabled(not use_master_font)

            if hasattr(self, 'code_font_btn') and self.code_font_btn is not None:
                self.code_font_btn.setEnabled(not use_master_font)

            if hasattr(self, 'master_font_btn') and self.master_font_btn is not None:
                self.master_font_btn.setEnabled(use_master_font)

            # Enable/disable heading font buttons
            for level in range(1, 7):
                if hasattr(self, f"h{level}_font_btn"):
                    font_btn = getattr(self, f"h{level}_font_btn")
                    if font_btn is not None:
                        font_btn.setEnabled(not use_master_font)

            # If master font is enabled, apply the master font family to all text elements
            # but preserve their individual sizes
            if use_master_font:
                master_font = self.document_settings["format"]["master_font"]["family"]
                # Apply to body
                self.document_settings["fonts"]["body"]["family"] = master_font
                # Apply to headings
                for level in range(1, 7):
                    h_key = f"h{level}"
                    self.document_settings["fonts"]["headings"][h_key]["family"] = master_font
                # Apply to code
                self.document_settings["code"]["font_family"] = master_font

                # Update UI elements directly without calling update_ui_from_settings
                # to avoid recursive calls
                if hasattr(self, 'body_font_btn') and self.body_font_btn is not None:
                    self.body_font_btn.setText(f"{master_font}, {self.document_settings['fonts']['body']['size']}pt")
                    self.body_font_btn.setFont(QFont(master_font, self.document_settings['fonts']['body']['size']))

                if hasattr(self, 'code_font_btn') and self.code_font_btn is not None:
                    self.code_font_btn.setText(f"{master_font}, {self.document_settings['code']['font_size']}pt")
                    self.code_font_btn.setFont(QFont(master_font, self.document_settings['code']['font_size']))

                # Update heading font buttons
                for level in range(1, 7):
                    if hasattr(self, f"h{level}_font_btn"):
                        h_key = f"h{level}"
                        font_btn = getattr(self, f"h{level}_font_btn")
                        if font_btn is not None:
                            font_size = self.document_settings["fonts"]["headings"][h_key]["size"]
                            font_btn.setText(f"{master_font}, {font_size}pt")
                            font_btn.setFont(QFont(master_font, font_size))

                # Update preview
                self.update_preview()
        except Exception as e:
            logger.error(f"Error in toggle_master_font: {str(e)}")
            # Don't show a message box here as this might be called during initialization

    def select_master_font(self):
        """Select master font for the entire document"""
        current_font = QFont(self.document_settings["format"]["master_font"]["family"])
        font, ok = QFontDialog.getFont(current_font, self, "Select Master Font")

        if ok:
            self.document_settings["format"]["master_font"]["family"] = font.family()
            self.style_manager.mark_as_changed()

            # Update button text and font
            self.master_font_btn.setFont(font)
            self.master_font_btn.setText(f"{font.family()}")

            # Apply to all text elements
            self.toggle_master_font(True)

    def select_body_font(self):
        """Select body font"""
        current_font = QFont(
            self.document_settings["fonts"]["body"]["family"],
            self.document_settings["fonts"]["body"]["size"]
        )
        font, ok = QFontDialog.getFont(current_font, self, "Select Body Font")

        if ok:
            self.document_settings["fonts"]["body"]["family"] = font.family()
            self.document_settings["fonts"]["body"]["size"] = font.pointSize()
            self.style_manager.mark_as_changed()

            # Update button text and font
            self.body_font_btn.setFont(font)
            self.body_font_btn.setText(f"{font.family()}, {font.pointSize()}pt")

            # Update preview
            self.update_preview()

    def update_line_height(self, value):
        """Update body text line height"""
        self.document_settings["fonts"]["body"]["line_height"] = value
        self.style_manager.mark_as_changed()
        self.update_preview()

    def select_text_color(self):
        """Select text color"""
        current_color = QColor(self.document_settings["colors"]["text"])
        color = QColorDialog.getColor(current_color, self, "Select Text Color")

        if color.isValid():
            self.document_settings["colors"]["text"] = color.name()
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def select_bg_color(self):
        """Select background color"""
        current_color = QColor(self.document_settings["colors"]["background"])
        color = QColorDialog.getColor(current_color, self, "Select Background Color")

        if color.isValid():
            self.document_settings["colors"]["background"] = color.name()
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def select_link_color(self):
        """Select link color"""
        current_color = QColor(self.document_settings["colors"]["links"])
        color = QColorDialog.getColor(current_color, self, "Select Link Color")

        if color.isValid():
            self.document_settings["colors"]["links"] = color.name()
            self.link_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def update_page_size(self, size):
        """Update page size"""
        self.document_settings["page"]["size"] = size
        self.style_manager.mark_as_changed()
        self.save_settings()
        self.update_preview()

    def update_orientation(self, orientation):
        """Update page orientation"""
        self.document_settings["page"]["orientation"] = orientation.lower()
        self.style_manager.mark_as_changed()
        self.save_settings()
        self.update_preview()

    def update_margin(self, side, value):
        """Update page margin"""
        self.document_settings["page"]["margins"][side] = value
        self.style_manager.mark_as_changed()
        self.save_settings()
        self.update_preview()

    def select_heading_font(self, heading_key):
        """Select heading font"""
        current_font = QFont(
            self.document_settings["fonts"]["headings"][heading_key]["family"],
            self.document_settings["fonts"]["headings"][heading_key]["size"]
        )
        font, ok = QFontDialog.getFont(current_font, self, f"Select {heading_key.upper()} Font")

        if ok:
            self.document_settings["fonts"]["headings"][heading_key]["family"] = font.family()
            self.document_settings["fonts"]["headings"][heading_key]["size"] = font.pointSize()

            # Get the correct button
            level = int(heading_key[1])
            font_btn = getattr(self, f"h{level}_font_btn")

            # Update button text and font
            font_btn.setFont(font)
            font_btn.setText(f"{font.family()}, {font.pointSize()}pt")

            # Update preview
            self.update_preview()

    def select_heading_color(self, heading_key):
        """Select heading color"""
        current_color = QColor(self.document_settings["fonts"]["headings"][heading_key]["color"])
        color = QColorDialog.getColor(current_color, self, f"Select {heading_key.upper()} Color")

        if color.isValid():
            self.document_settings["fonts"]["headings"][heading_key]["color"] = color.name()

            # Get the correct button
            level = int(heading_key[1])
            color_btn = getattr(self, f"h{level}_color_btn")

            # Update button color
            color_btn.setStyleSheet(f"background-color: {color.name()}")

            # Update preview
            self.update_preview()

    def update_heading_spacing(self, heading_key, value):
        """Update heading line spacing"""
        self.document_settings["fonts"]["headings"][heading_key]["spacing"] = value
        self.update_preview()

    def update_heading_margin_top(self, heading_key, value):
        """Update heading top margin"""
        self.document_settings["fonts"]["headings"][heading_key]["margin_top"] = value
        self.update_preview()

    def update_heading_margin_bottom(self, heading_key, value):
        """Update heading bottom margin"""
        self.document_settings["fonts"]["headings"][heading_key]["margin_bottom"] = value
        self.update_preview()

    def update_para_spacing(self, value):
        """Update paragraph line spacing"""
        self.document_settings["paragraphs"]["spacing"] = value
        self.update_preview()

    def update_para_margin_top(self, value):
        """Update paragraph top margin"""
        self.document_settings["paragraphs"]["margin_top"] = value
        self.update_preview()

    def update_para_margin_bottom(self, value):
        """Update paragraph bottom margin"""
        self.document_settings["paragraphs"]["margin_bottom"] = value
        self.update_preview()

    def update_first_line_indent(self, value):
        """Update paragraph first line indent"""
        self.document_settings["paragraphs"]["first_line_indent"] = value
        self.update_preview()

    def update_para_alignment(self, alignment):
        """Update paragraph alignment"""
        self.document_settings["paragraphs"]["alignment"] = alignment.lower()
        self.update_preview()

    def update_bullet_indent(self, value):
        """Update bullet list indent"""
        self.document_settings["lists"]["bullet_indent"] = value
        self.update_preview()

    def update_bullet_style_l1(self, style):
        """Update bullet list level 1 style"""
        self.document_settings["lists"]["bullet_style_l1"] = style
        self.update_preview()

    def update_bullet_style_l2(self, style):
        """Update bullet list level 2 style"""
        self.document_settings["lists"]["bullet_style_l2"] = style
        self.update_preview()

    def update_bullet_style_l3(self, style):
        """Update bullet list level 3 style"""
        self.document_settings["lists"]["bullet_style_l3"] = style
        self.update_preview()

    def update_number_indent(self, value):
        """Update numbered list indent"""
        self.document_settings["lists"]["number_indent"] = value
        self.update_preview()

    def update_number_style_l1(self, style):
        """Update numbered list level 1 style"""
        self.document_settings["lists"]["number_style_l1"] = style
        self.update_preview()

    def update_number_style_l2(self, style):
        """Update numbered list level 2 style"""
        self.document_settings["lists"]["number_style_l2"] = style
        self.update_preview()

    def update_number_style_l3(self, style):
        """Update numbered list level 3 style"""
        self.document_settings["lists"]["number_style_l3"] = style
        self.update_preview()

    def update_list_item_spacing(self, value):
        """Update list item spacing"""
        self.document_settings["lists"]["item_spacing"] = value
        self.update_preview()

    def update_nested_list_indent(self, value):
        """Update nested list indent"""
        self.document_settings["lists"]["nested_indent"] = value
        self.update_preview()

    def add_custom_bullet_style(self):
        """Add a custom bullet style"""
        # Get the Unicode character from the user
        unicode_char, ok = QInputDialog.getText(
            self, 'Add Custom Bullet Style',
            'Enter a name for the custom bullet style:'
        )

        if ok and unicode_char:
            # Check if the style already exists
            bullet_styles = [self.bullet_style_l1.itemText(i) for i in range(self.bullet_style_l1.count())]
            if unicode_char in bullet_styles:
                QMessageBox.warning(
                    self,
                    "Style Already Exists",
                    f"A style named '{unicode_char}' already exists."
                )
                return

            # Add the style to all comboboxes
            self.bullet_style_l1.addItem(unicode_char)
            self.bullet_style_l2.addItem(unicode_char)
            self.bullet_style_l3.addItem(unicode_char)

            # Show success message
            self.statusBar().showMessage(f"Added custom bullet style: {unicode_char}", 3000)

    def delete_custom_bullet_style(self):
        """Delete a custom bullet style"""
        # Get all available styles
        bullet_styles = [self.bullet_style_l1.itemText(i) for i in range(self.bullet_style_l1.count())]

        # Remove default styles that cannot be deleted
        protected_styles = ["Disc", "Circle", "Square", "None"]
        deletable_styles = [style for style in bullet_styles if style not in protected_styles]

        if not deletable_styles:
            QMessageBox.information(
                self,
                "No Custom Styles",
                "There are no custom styles to delete. Default styles cannot be deleted."
            )
            return

        # Ask the user which style to delete
        style_to_delete, ok = QInputDialog.getItem(
            self, 'Delete Custom Style',
            'Select a custom style to delete:',
            deletable_styles, 0, False
        )

        if ok and style_to_delete:
            # Check if the style is currently in use
            in_use = False
            for level in ["bullet_style_l1", "bullet_style_l2", "bullet_style_l3"]:
                if self.document_settings["lists"][level] == style_to_delete:
                    in_use = True
                    # Reset to a default style
                    if level == "bullet_style_l1":
                        self.document_settings["lists"][level] = "Disc"
                        self.bullet_style_l1.setCurrentText("Disc")
                    elif level == "bullet_style_l2":
                        self.document_settings["lists"][level] = "Circle"
                        self.bullet_style_l2.setCurrentText("Circle")
                    elif level == "bullet_style_l3":
                        self.document_settings["lists"][level] = "Square"
                        self.bullet_style_l3.setCurrentText("Square")

            # Remove the style from all comboboxes
            for combo in [self.bullet_style_l1, self.bullet_style_l2, self.bullet_style_l3]:
                index = combo.findText(style_to_delete)
                if index >= 0:
                    combo.removeItem(index)

            # Show success message with warning if the style was in use
            if in_use:
                self.statusBar().showMessage(
                    f"Deleted custom style: {style_to_delete} (was in use and reset to default)", 3000
                )
            else:
                self.statusBar().showMessage(f"Deleted custom style: {style_to_delete}", 3000)

            # Update the preview
            self.update_preview()

    def select_table_border_color(self):
        """Select table border color"""
        current_color = QColor(self.document_settings["table"]["border_color"])
        color = QColorDialog.getColor(current_color, self, "Select Table Border Color")

        if color.isValid():
            self.document_settings["table"]["border_color"] = color.name()
            self.table_border_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def select_table_header_bg(self):
        """Select table header background color"""
        current_color = QColor(self.document_settings["table"]["header_bg"])
        color = QColorDialog.getColor(current_color, self, "Select Table Header Background")

        if color.isValid():
            self.document_settings["table"]["header_bg"] = color.name()
            self.table_header_bg_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def update_cell_padding(self, value):
        """Update table cell padding"""
        self.document_settings["table"]["cell_padding"] = value
        self.update_preview()

    def select_code_font(self):
        """Select code font"""
        current_font = QFont(
            self.document_settings["code"]["font_family"],
            self.document_settings["code"]["font_size"]
        )
        font, ok = QFontDialog.getFont(current_font, self, "Select Code Font")

        if ok:
            self.document_settings["code"]["font_family"] = font.family()
            self.document_settings["code"]["font_size"] = font.pointSize()

            # Update button text and font
            self.code_font_btn.setFont(font)
            self.code_font_btn.setText(f"{font.family()}, {font.pointSize()}pt")

            # Update preview
            self.update_preview()

    def select_code_bg_color(self):
        """Select code background color"""
        current_color = QColor(self.document_settings["code"]["background"])
        color = QColorDialog.getColor(current_color, self, "Select Code Background Color")

        if color.isValid():
            self.document_settings["code"]["background"] = color.name()
            self.code_bg_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def select_code_border_color(self):
        """Select code border color"""
        current_color = QColor(self.document_settings["code"]["border_color"])
        color = QColorDialog.getColor(current_color, self, "Select Code Border Color")

        if color.isValid():
            self.document_settings["code"]["border_color"] = color.name()
            self.code_border_color_btn.setStyleSheet(f"background-color: {color.name()}")
            self.update_preview()

    def update_include_toc(self, state):
        """Update include table of contents setting"""
        self.document_settings["toc"]["include"] = bool(state)
        self.style_manager.mark_as_changed()
        self.update_preview()

    def update_toc_depth(self, value):
        """Update table of contents depth"""
        self.document_settings["toc"]["depth"] = value
        self.style_manager.mark_as_changed()
        self.update_preview()

    def update_toc_title(self, title):
        """Update table of contents title"""
        self.document_settings["toc"]["title"] = title
        self.style_manager.mark_as_changed()
        self.update_preview()

    def closeEvent(self, event):
        """Handle application close event"""
        # Check if we're running in a test environment
        is_test_environment = hasattr(self, '_is_test_environment') and self._is_test_environment

        # Skip style saving prompt and settings save in test environment
        if is_test_environment:
            logger.debug("Closing in test environment - skipping style and settings save")
            event.accept()
            return

        # Check for unsaved style changes
        if self.style_manager.has_unsaved_changes:
            try:
                # Use a timeout for the dialog to prevent hanging
                reply = QMessageBox.question(
                    self,
                    "Unsaved Style Changes",
                    f"You have unsaved changes to the current style '{self.style_manager.current_style_name}'."
                    f"\nDo you want to save these changes before quitting?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.No  # Default to No to avoid hanging
                )

                if reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
                elif reply == QMessageBox.StandardButton.Yes:
                    # Save current style with timeout protection
                    try:
                        self.save_current_style()
                    except Exception as e:
                        logger.error(f"Error saving style during close: {str(e)}")
            except Exception as e:
                logger.error(f"Error showing style save dialog: {str(e)}")
                # Continue with close even if dialog fails

        try:
            # Save temporary style for next session with timeout protection
            try:
                self.style_manager.save_temp_style(self.document_settings)
            except Exception as e:
                logger.error(f"Error saving temp style during close: {str(e)}")

            # Save settings with timeout protection
            try:
                self.save_settings()
            except Exception as e:
                logger.error(f"Error saving settings during close: {str(e)}")
        except Exception as e:
            logger.error(f"Error during close event: {str(e)}")

        # Accept the close event - always close even if saving fails
        event.accept()

    # Style management methods
    def apply_style_preset(self, style_name):
        """Apply a style preset"""
        if not style_name or style_name == self.style_manager.current_style_name:
            return

        # Check for unsaved changes only if we're not on a default style
        # or if we're on Custom which is saveable
        current_style = self.style_manager.current_style_name
        is_current_default = current_style in self.style_manager.default_styles and current_style != "Custom"

        if self.style_manager.has_unsaved_changes and not is_current_default:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"You have unsaved changes to the current style '{current_style}'."
                f"\nDo you want to save these changes before loading '{style_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                # Revert combo box selection
                self.preset_combo.setCurrentText(current_style)
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # Save current style
                self.save_current_style()

        # First let the style manager update its state
        # This just updates the current_style_name and resets has_unsaved_changes
        self.style_manager.load_style(style_name, self.document_settings)

        # Now handle default styles with specific presets
        if style_name == "Business Professional":
            self.apply_business_preset()
        elif style_name == "Technical Document":
            self.apply_technical_preset()
        elif style_name == "Academic":
            self.apply_academic_preset()
        elif style_name == "Minimal":
            self.apply_minimal_preset()
        elif style_name == "Custom":
            # Just use the current settings
            pass
        else:
            # For user-defined styles, load from file
            presets_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
            preset_path = os.path.join(presets_dir, f"{style_name}.json")

            if os.path.exists(preset_path):
                try:
                    with open(preset_path, 'r', encoding='utf-8') as f:
                        preset_settings = json.load(f)

                    # Update the settings
                    self.document_settings.update(preset_settings)
                    logger.info(f"Loaded user style: {style_name}")
                except Exception as e:
                    logger.error(f"Error loading style {style_name}: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Error Loading Style",
                        f"Failed to load style '{style_name}': {str(e)}"
                    )

        # Update UI and preview
        self.update_ui_from_settings()
        self.update_preview()
        logger.info(f"Applied style preset: {style_name}")
        self.statusBar().showMessage(f"Applied style preset: {style_name}", 3000)

    def save_current_style(self):
        """Save the current settings to the current style"""
        style_name = self.style_manager.current_style_name

        # Don't allow saving to default styles
        if style_name in self.style_manager.default_styles and style_name != "Custom":
            # Ask for a new name
            self.save_style_as_new()
            return

        # Save the style
        if self.style_manager.save_style(style_name, self.document_settings):
            logger.info(f"Saved style: {style_name}")
            self.statusBar().showMessage(f"Saved style: {style_name}", 3000)
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Failed to save style '{style_name}'."
            )

    def save_style_as_new(self):
        """Save the current settings as a new style"""
        style_name, ok = QInputDialog.getText(
            self,
            "Save Style As",
            "Enter a name for the new style:",
            QLineEdit.EchoMode.Normal,
            self.style_manager.current_style_name
        )

        if ok and style_name:
            # Check if style already exists
            if style_name in self.style_manager.available_styles:
                reply = QMessageBox.question(
                    self,
                    "Style Already Exists",
                    f"A style named '{style_name}' already exists. Overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Save the style
            if self.style_manager.save_style(style_name, self.document_settings):
                # Update the combo box
                if style_name not in self.style_manager.available_styles:
                    self.preset_combo.addItem(style_name)
                self.preset_combo.setCurrentText(style_name)

                logger.info(f"Saved new style: {style_name}")
                self.statusBar().showMessage(f"Saved new style: {style_name}", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save style '{style_name}'."
                )

    def delete_current_style(self):
        """Delete the current style"""
        style_name = self.style_manager.current_style_name

        # Don't allow deleting default styles
        if style_name in self.style_manager.default_styles:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                f"Cannot delete default style '{style_name}'."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Style",
            f"Are you sure you want to delete the style '{style_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete the style
        if self.style_manager.delete_style(style_name):
            # Update the combo box
            index = self.preset_combo.findText(style_name)
            if index >= 0:
                self.preset_combo.removeItem(index)

            # Switch to Custom style
            self.preset_combo.setCurrentText("Custom")

            logger.info(f"Deleted style: {style_name}")
            self.statusBar().showMessage(f"Deleted style: {style_name}", 3000)
        else:
            QMessageBox.warning(
                self,
                "Delete Failed",
                f"Failed to delete style '{style_name}'."
            )

def main():
    """Main entry point for the application"""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Advanced Markdown to PDF Converter")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (suppresses dialogs)")
    args, remaining = parser.parse_known_args()

    # Set environment variable for test mode if specified
    if args.test_mode:
        os.environ["MARKDOWN_PDF_TEST_MODE"] = "1"
        logger.info("Running in test mode - dialogs will be suppressed")

    # Initialize QApplication with remaining arguments
    app = QApplication(remaining)
    app.setApplicationName("Advanced Markdown to PDF Converter")
    app.setOrganizationName("MarkdownToPDF")

    # Create and show the main window
    window = AdvancedMarkdownToPDF()

    # Restore window geometry if available
    settings = QSettings("MarkdownToPDF", "AdvancedConverter")
    if settings.contains("window_geometry"):
        window.restoreGeometry(settings.value("window_geometry"))

    # Save settings before exit
    app.aboutToQuit.connect(window.save_settings)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()