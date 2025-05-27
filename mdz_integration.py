#!/usr/bin/env python3
"""
MDZ Integration
-------------
This module integrates the MDZ bundle format into the main application.

File: mdz_integration.py
"""

import os
import re
import sys
import tempfile
import logging
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSettings

# Import unified MDZ module and renderer
from unified_mdz import UnifiedMDZ, CompressionMethod, get_mdz_info
from mdz_renderer import MDZRenderer

# Import page preview improvements
try:
    from page_preview_improvements import apply_consolidated_improvements
except ImportError:
    # If the improvements module is not available, create a dummy function
    def apply_consolidated_improvements(page_preview):
        return page_preview

# Configure logger
logger = logging.getLogger(__name__)

class MDZIntegration:
    """
    Class for integrating MDZ bundle format into the main application
    """

    def __init__(self, main_window):
        """
        Initialize the MDZ integration

        Args:
            main_window: The main application window
        """
        self.main_window = main_window
        self.current_mdz_bundle = None
        self.temp_dir = None
        self.extracted_assets = {}
        self.mdz_renderer = MDZRenderer()

        # Add MDZ file format to open/save dialogs
        self.extend_file_dialogs()

        # Add MDZ-specific menu items
        self.add_mdz_menu_items()

        # Store original methods for later restoration
        self.original_open_file = main_window.open_file
        self.original_save_file = main_window.save_file
        self.original_save_file_as = main_window.save_file_as

        # Override file handling methods
        main_window.open_file = self.open_file
        main_window.save_file = self.save_file
        main_window.save_file_as = self.save_file_as

        # Add MDZ-specific export methods
        main_window.export_to_mdz = self.export_to_mdz
        main_window.import_from_mdz = self.import_from_mdz

        # Note: Page preview improvements are now applied only in the integrate_mdz function
        # to prevent duplicate application of improvements

        logger.info("MDZ integration initialized")

    def extend_file_dialogs(self):
        """
        Extend file dialogs to include MDZ format
        """
        # Store the original open file dialog filter
        self.original_open_filter = 'Markdown Files (*.md *.markdown);;All Files (*)'

        # Extended filter including MDZ format
        self.extended_open_filter = 'All Supported Files (*.md *.markdown *.mdz);;Markdown Files (*.md *.markdown);;MDZ Bundles (*.mdz);;All Files (*)'

        # Extended save filter including MDZ format
        self.extended_save_filter = 'Markdown Files (*.md);;MDZ Bundles (*.mdz);;All Files (*)'

    def add_mdz_menu_items(self):
        """
        Add MDZ-specific menu items to the application
        """
        # Add MDZ export option to the File menu
        file_menu = None
        for action in self.main_window.menuBar().actions():
            if action.text() == '&File':
                file_menu = action.menu()
                break

        if file_menu:
            # Find the position to insert MDZ actions (after other export actions)
            export_actions = []
            for action in file_menu.actions():
                if action.text().startswith('Export to'):
                    export_actions.append(action)

            if export_actions:
                # Get the last export action
                last_export = export_actions[-1]

                # Add MDZ export action after the last export action
                export_mdz_action = QAction('Export to MD&Z...', self.main_window)
                export_mdz_action.triggered.connect(self.export_to_mdz)
                file_menu.insertAction(last_export.menuAction().menu().actions()[0], export_mdz_action)

                # Add MDZ import action
                import_mdz_action = QAction('Import from MD&Z...', self.main_window)
                import_mdz_action.triggered.connect(self.import_from_mdz)
                file_menu.insertAction(export_mdz_action, import_mdz_action)

                # Add MDZ viewer action
                mdz_viewer_action = QAction('Open MDZ Viewer...', self.main_window)
                mdz_viewer_action.triggered.connect(self.launch_mdz_viewer)
                file_menu.insertAction(import_mdz_action, mdz_viewer_action)

                # Add separator
                file_menu.insertSeparator(import_mdz_action)

    def open_file(self):
        """
        Override of the open_file method to handle MDZ files
        """
        if self.main_window.markdown_editor.toPlainText() and self.main_window.current_file is not None:
            # Ask to save changes
            reply = QMessageBox.question(
                self.main_window, 'Save Changes',
                'Do you want to save changes to the current document?',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        # Get start directory from saved paths
        start_dir = self.main_window.dialog_paths.get("open", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.main_window, 'Open File', start_dir, self.extended_open_filter
        )

        if file_path:
            # Check if it's an MDZ file
            if file_path.lower().endswith('.mdz'):
                self.open_mdz_file(file_path)
            else:
                # Use the original method for non-MDZ files
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.main_window.markdown_editor.setPlainText(file.read())

                    self.main_window.current_file = file_path
                    self.main_window.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

                    # Save the directory for next time
                    self.main_window.dialog_paths["open"] = os.path.dirname(file_path)
                    # Don't call save_settings here, it will be called by the main application

                    self.main_window.update_preview()
                except Exception as e:
                    QMessageBox.critical(self.main_window, 'Error', f'Could not open the file: {str(e)}')

    def open_mdz_file(self, file_path):
        """
        Open an MDZ file

        Args:
            file_path: Path to the MDZ file
        """
        try:
            # Clean up any previous MDZ bundle
            self.cleanup_mdz()

            # Create a new MDZ bundle
            self.current_mdz_bundle = UnifiedMDZ()

            # Load the MDZ bundle
            self.current_mdz_bundle.load(file_path)

            # Extract to a temporary directory
            self.extracted_assets = self.current_mdz_bundle.extract_to_temp()
            self.temp_dir = self.current_mdz_bundle.temp_dir

            # Get the main content
            main_content = self.current_mdz_bundle.get_main_content()

            # Set the content in the editor
            self.main_window.markdown_editor.setPlainText(main_content)

            # Set the current file
            self.main_window.current_file = file_path
            self.main_window.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

            # Save the directory for next time
            self.main_window.dialog_paths["open"] = os.path.dirname(file_path)
            # Don't call save_settings here, it will be called by the main application

            # Update the preview with special handling for MDZ assets
            self.update_preview_with_mdz_assets()

            logger.info(f"Opened MDZ file: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, 'Error', f'Could not open the MDZ file: {str(e)}')
            logger.error(f"Error opening MDZ file: {str(e)}")

    def update_preview_with_mdz_assets(self):
        """
        Update the preview with special handling for MDZ assets

        This method modifies the editor content temporarily and then uses the main
        window's update_preview method to avoid creating duplicate preview instances.
        """
        # Get the current markdown content
        markdown_content = self.main_window.markdown_editor.toPlainText()

        # Process image references to use extracted paths
        processed_content = self.process_image_references(markdown_content)

        # Store the original content
        original_content = markdown_content

        try:
            # Clear any existing content in the page preview first
            if hasattr(self.main_window, 'page_preview') and self.main_window.page_preview is not None:
                try:
                    # Use a blank page to clear any existing content
                    self.main_window.page_preview.web_view.setHtml("")
                    logger.debug("Cleared previous web view content before MDZ preview update")
                except Exception as e:
                    logger.warning(f"Error clearing web view content: {str(e)}")

            # Temporarily set the processed content in the editor
            self.main_window.markdown_editor.blockSignals(True)
            self.main_window.markdown_editor.setPlainText(processed_content)

            # Use the main window's update_preview method to avoid duplication
            self.main_window.update_preview()

            logger.debug("Updated preview with MDZ assets using main window's update_preview")
        except Exception as e:
            logger.error(f"Error updating preview with MDZ assets: {str(e)}")
        finally:
            # Restore the original content
            self.main_window.markdown_editor.setPlainText(original_content)
            self.main_window.markdown_editor.blockSignals(False)
            logger.debug("Restored original content after MDZ preview update")

    def process_image_references(self, markdown_content):
        """
        Process image references to use extracted paths with enhanced asset resolution

        Args:
            markdown_content: Markdown content

        Returns:
            Processed markdown content
        """
        # Find all image references
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # Skip URLs
            if image_path.startswith(('http://', 'https://')):
                return match.group(0)

            # Check if we have a mapping for this image path
            for internal_path, extracted_path in self.extracted_assets.items():
                # Try different matching strategies
                if (internal_path.endswith(image_path) or
                    image_path.endswith(internal_path) or
                    os.path.basename(internal_path) == os.path.basename(image_path)):
                    # Replace with the extracted path and add MDZ asset class for styling
                    return f'![{alt_text}]({extracted_path}){{.mdz-asset}}'

                # Try to match by directory structure
                if 'images/' in internal_path and os.path.basename(internal_path) == os.path.basename(image_path):
                    return f'![{alt_text}]({extracted_path}){{.mdz-asset}}'

            # If no exact match found, try to find a match by filename only
            image_filename = os.path.basename(image_path)
            for internal_path, extracted_path in self.extracted_assets.items():
                if os.path.basename(internal_path) == image_filename:
                    return f'![{alt_text}]({extracted_path}){{.mdz-asset}}'

            # Keep the original path if no mapping is found
            logger.warning(f"No asset mapping found for image: {image_path}")
            return match.group(0)

        # Replace image paths
        processed_content = re.sub(image_pattern, replace_image_path, markdown_content)

        # Add a note about MDZ assets at the beginning of the document
        if self.extracted_assets:
            asset_count = len(self.extracted_assets)
            mdz_note = f"\n\n> **Note**: This document contains {asset_count} embedded MDZ assets that will be properly displayed in the preview and PDF export.\n\n"
            processed_content = mdz_note + processed_content

        return processed_content

    def save_file(self):
        """
        Override of the save_file method to handle MDZ files
        """
        if self.main_window.current_file:
            # Check if it's an MDZ file
            if self.main_window.current_file.lower().endswith('.mdz'):
                return self.save_mdz_file(self.main_window.current_file)
            else:
                # Use the original method for non-MDZ files
                try:
                    with open(self.main_window.current_file, 'w', encoding='utf-8') as file:
                        file.write(self.main_window.markdown_editor.toPlainText())
                    return True
                except Exception as e:
                    QMessageBox.critical(self.main_window, 'Error', f'Could not save the file: {str(e)}')
                    return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        """
        Override of the save_file_as method to handle MDZ files
        """
        # Get start directory from saved paths
        start_dir = self.main_window.dialog_paths.get("save", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.main_window, 'Save File', start_dir, self.extended_save_filter
        )

        if file_path:
            # Check the selected filter to determine the file type
            if selected_filter == 'MDZ Bundles (*.mdz)' and not file_path.lower().endswith('.mdz'):
                file_path += '.mdz'
            elif selected_filter == 'Markdown Files (*.md)' and not file_path.lower().endswith(('.md', '.markdown')):
                file_path += '.md'

            # Check if it's an MDZ file
            if file_path.lower().endswith('.mdz'):
                return self.save_mdz_file(file_path)
            else:
                # Use the original method for non-MDZ files
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(self.main_window.markdown_editor.toPlainText())

                    self.main_window.current_file = file_path
                    self.main_window.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

                    # Save the directory for next time
                    self.main_window.dialog_paths["save"] = os.path.dirname(file_path)
                    # Don't call save_settings here, it will be called by the main application

                    return True
                except Exception as e:
                    QMessageBox.critical(self.main_window, 'Error', f'Could not save the file: {str(e)}')
                    return False

        return False

    def save_mdz_file(self, file_path):
        """
        Save an MDZ file

        Args:
            file_path: Path to save the MDZ file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a new MDZ bundle
            bundle = UnifiedMDZ()

            # Get the current markdown content
            markdown_content = self.main_window.markdown_editor.toPlainText()

            # Extract front matter
            markdown_without_front_matter, front_matter = bundle.extract_front_matter(markdown_content)

            # Create the bundle from the markdown content
            bundle.create_from_markdown(markdown_content, front_matter)

            # Include referenced images
            self.include_referenced_images(bundle, markdown_content)

            # Include Mermaid diagrams
            self.include_mermaid_diagrams(bundle, markdown_content)

            # Save the bundle
            bundle.save(file_path)

            # Update the current file
            self.main_window.current_file = file_path
            self.main_window.setWindowTitle(f'Advanced Markdown to PDF Converter - {os.path.basename(file_path)}')

            # Save the directory for next time
            self.main_window.dialog_paths["save"] = os.path.dirname(file_path)
            # Don't call save_settings here, it will be called by the main application

            # Update the current MDZ bundle
            self.current_mdz_bundle = bundle

            logger.info(f"Saved MDZ file: {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self.main_window, 'Error', f'Could not save the MDZ file: {str(e)}')
            logger.error(f"Error saving MDZ file: {str(e)}")
            return False

    def include_referenced_images(self, bundle, markdown_content):
        """
        Include referenced images in the MDZ bundle

        Args:
            bundle: MDZ bundle
            markdown_content: Markdown content
        """
        # Find all image references
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        image_references = re.findall(image_pattern, markdown_content)

        for _, image_path in image_references:
            # Skip URLs
            if image_path.startswith(('http://', 'https://')):
                continue

            # Check if the image exists
            if os.path.exists(image_path):
                # Add the image to the bundle
                try:
                    with open(image_path, 'rb') as f:
                        image_content = f.read()

                    bundle.add_file(image_path, image_content)
                except Exception as e:
                    logger.warning(f"Error adding image {image_path}: {str(e)}")
            elif self.temp_dir:
                # Check if the image exists in the extracted assets
                for internal_path, extracted_path in self.extracted_assets.items():
                    if internal_path.endswith(image_path) or os.path.basename(internal_path) == os.path.basename(image_path):
                        try:
                            with open(extracted_path, 'rb') as f:
                                image_content = f.read()

                            bundle.add_file(internal_path, image_content, internal_path)
                        except Exception as e:
                            logger.warning(f"Error adding extracted image {internal_path}: {str(e)}")

    def include_mermaid_diagrams(self, bundle, markdown_content):
        """
        Include Mermaid diagrams in the MDZ bundle

        Args:
            bundle: MDZ bundle
            markdown_content: Markdown content
        """
        # Find all Mermaid code blocks
        mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
        mermaid_blocks = re.findall(mermaid_pattern, markdown_content, re.DOTALL)

        # Add each Mermaid diagram to the bundle
        for i, mermaid_code in enumerate(mermaid_blocks):
            mermaid_code = mermaid_code.strip()

            # Create a file name for the diagram
            file_name = f"diagram_{i+1}.mmd"

            # Add the diagram to the bundle
            bundle.add_file(file_name, mermaid_code, f"mermaid/{file_name}")

            # Try to render the diagram to SVG
            try:
                svg_content = self.mdz_renderer.render_mermaid_to_svg(mermaid_code)
                if svg_content:
                    # Add the SVG to the bundle
                    bundle.add_file(f"{file_name}.svg", svg_content, f"mermaid/{file_name}.svg")
            except Exception as e:
                logger.warning(f"Error rendering Mermaid diagram: {str(e)}")

    def export_to_mdz(self):
        """
        Export the current document to an MDZ bundle
        """
        if not self.main_window.markdown_editor.toPlainText():
            QMessageBox.warning(self.main_window, 'Warning', 'No content to export.')
            return

        # Ask for the output file location
        default_filename = "document.mdz"
        if self.main_window.current_file:
            default_filename = os.path.splitext(os.path.basename(self.main_window.current_file))[0] + ".mdz"

        # Get start directory from saved paths
        start_dir = self.main_window.dialog_paths.get("export", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, 'Export to MDZ', os.path.join(start_dir, default_filename),
            'MDZ Bundles (*.mdz)'
        )

        if file_path:
            # Add .mdz extension if not present
            if not file_path.lower().endswith('.mdz'):
                file_path += '.mdz'

            # Save the MDZ file
            if self.save_mdz_file(file_path):
                QMessageBox.information(self.main_window, 'Export Successful', f'Document exported to {file_path}')

                # Save the directory for next time
                self.main_window.dialog_paths["export"] = os.path.dirname(file_path)
                # Don't call save_settings here, it will be called by the main application

    def import_from_mdz(self):
        """
        Import a document from an MDZ bundle
        """
        # Get start directory from saved paths
        start_dir = self.main_window.dialog_paths.get("open", "")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = ""

        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, 'Import from MDZ', start_dir,
            'MDZ Bundles (*.mdz)'
        )

        if file_path:
            self.open_mdz_file(file_path)

    def view_in_mdz_viewer(self):
        """
        Open the current file in the MDZ viewer
        """
        # Check if the current file is saved
        if not self.main_window.current_file:
            QMessageBox.warning(self.main_window, 'Warning', 'Please save the file first.')
            return

        # If the current file is not an MDZ file, save it as an MDZ file first
        if not self.main_window.current_file.lower().endswith('.mdz'):
            # Create a temporary MDZ file
            import tempfile
            temp_mdz = tempfile.NamedTemporaryFile(delete=False, suffix='.mdz')
            temp_mdz.close()

            # Save as MDZ
            self.save_mdz_file(temp_mdz.name)

            # Open in MDZ viewer
            self.open_in_mdz_viewer(temp_mdz.name)

            # Clean up the temporary file
            try:
                os.unlink(temp_mdz.name)
            except Exception as e:
                logger.warning(f"Error removing temporary MDZ file: {str(e)}")
        else:
            # Open the current MDZ file in the viewer
            self.open_in_mdz_viewer(self.main_window.current_file)

    def open_in_mdz_viewer(self, mdz_file):
        """
        Open an MDZ file in the MDZ viewer

        Args:
            mdz_file: Path to the MDZ file
        """
        try:
            import subprocess
            import sys

            # Get the path to the MDZ viewer
            mdz_viewer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mdz_viewer.py')

            # Launch the MDZ viewer
            subprocess.Popen([sys.executable, mdz_viewer_path, mdz_file])

            logger.info(f"Opened MDZ file in viewer: {mdz_file}")
        except Exception as e:
            QMessageBox.critical(self.main_window, 'Error', f'Could not open MDZ viewer: {str(e)}')
            logger.error(f"Error opening MDZ viewer: {str(e)}")

    def launch_mdz_viewer(self):
        """
        Launch the standalone MDZ viewer
        """
        try:
            import subprocess
            import sys

            # Get the path to the MDZ viewer
            mdz_viewer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mdz_viewer.py')

            # Check if the MDZ viewer exists
            if not os.path.exists(mdz_viewer_path):
                QMessageBox.warning(self.main_window, 'Warning', 'MDZ Viewer not found. Please make sure mdz_viewer.py is in the same directory as this application.')
                return

            # Launch the MDZ viewer
            subprocess.Popen([sys.executable, mdz_viewer_path])

            logger.info("Launched MDZ Viewer")
        except Exception as e:
            QMessageBox.critical(self.main_window, 'Error', f'Could not launch MDZ Viewer: {str(e)}')
            logger.error(f"Error launching MDZ Viewer: {str(e)}")

    def cleanup_mdz(self):
        """
        Clean up MDZ resources
        """
        if self.current_mdz_bundle:
            self.current_mdz_bundle.cleanup()
            self.current_mdz_bundle = None
            self.temp_dir = None
            self.extracted_assets = {}

    def restore_original_methods(self):
        """
        Restore original file handling methods
        """
        self.main_window.open_file = self.original_open_file
        self.main_window.save_file = self.original_save_file
        self.main_window.save_file_as = self.original_save_file_as

        # Clean up MDZ resources
        self.cleanup_mdz()

        logger.info("Restored original file handling methods")


def integrate_mdz(main_window):
    """
    Integrate MDZ format into the main application

    Args:
        main_window: The main application window

    Returns:
        MDZIntegration instance
    """
    # Check if zstandard is installed
    try:
        import zstandard
    except ImportError:
        # Ask the user if they want to install zstandard
        reply = QMessageBox.question(
            main_window, 'Missing Dependency',
            'The zstandard library is required for MDZ support. Would you like to install it now?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "zstandard"])
                logger.info("Installed zstandard library")
            except Exception as e:
                QMessageBox.critical(main_window, 'Installation Error', f'Could not install zstandard: {str(e)}')
                logger.error(f"Error installing zstandard: {str(e)}")
                return None
        else:
            logger.warning("MDZ integration aborted: zstandard library not installed")
            return None

    # Page preview improvements are now applied directly in the main application
    # We don't need to apply them here to avoid duplication
    logger.info("Page preview improvements are handled by the main application")

    # Create and return the MDZ integration
    return MDZIntegration(main_window)


if __name__ == "__main__":
    # This module should not be run directly
    print("This module should be imported, not run directly.")
