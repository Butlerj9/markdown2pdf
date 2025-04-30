"""
Style management for the Markdown to PDF converter
"""

import os
import json
import copy
import logging
from typing import Dict, Any, Optional, List

# Get the logger
logger = logging.getLogger(__name__)

class StyleManager:
    """
    Manages document styles for the Markdown to PDF converter.

    Features:
    - Load and save styles
    - Track unsaved changes
    - Maintain a temporary style for last used settings
    - Provide default styles
    """

    def __init__(self):
        """Initialize the style manager"""
        # Directory for storing styles
        self.styles_dir = os.path.join(os.path.expanduser("~"), ".markdown_presets")
        os.makedirs(self.styles_dir, exist_ok=True)

        # Temporary style file for storing last used settings
        self.temp_style_path = os.path.join(self.styles_dir, "_temp_style.json")

        # Track if current settings have unsaved changes
        self.has_unsaved_changes = False

        # Current style name
        self.current_style_name = "Custom"

        # Default styles
        self.default_styles = ["Business Professional", "Technical Document", "Academic", "Minimal", "Custom"]

        # Available styles (will be populated when loading)
        self.available_styles = []

        # Load available styles
        self.load_available_styles()

    def load_available_styles(self) -> List[str]:
        """
        Load all available style names

        Returns:
            List of style names
        """
        self.available_styles = self.default_styles.copy()

        # Add user-defined styles
        if os.path.exists(self.styles_dir):
            preset_files = [f for f in os.listdir(self.styles_dir)
                           if f.endswith('.json') and not f.startswith('_')]

            for preset_file in preset_files:
                preset_name = os.path.splitext(preset_file)[0]
                if preset_name not in self.available_styles:
                    self.available_styles.append(preset_name)

        logger.debug(f"Available styles: {self.available_styles}")
        return self.available_styles

    def load_style(self, style_name: str, document_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load a style and apply it to the document settings

        Args:
            style_name: Name of the style to load
            document_settings: Current document settings

        Returns:
            Updated document settings
        """
        # Check if we need to prompt for unsaved changes
        if self.has_unsaved_changes:
            # This will be handled by the UI
            pass

        # Make a copy of the settings to avoid modifying the original
        settings_copy = copy.deepcopy(document_settings)

        # Check if it's a default style
        if style_name in self.default_styles:
            # Default styles are handled by the main application
            # Just update the current style name and reset unsaved changes
            self.current_style_name = style_name
            self.has_unsaved_changes = False
            # Return the settings as is - the main app will apply the default style
            return settings_copy

        # Try to load a user-defined style
        style_path = os.path.join(self.styles_dir, f"{style_name}.json")
        if os.path.exists(style_path):
            try:
                with open(style_path, 'r', encoding='utf-8') as f:
                    loaded_style = json.load(f)

                # Update settings with loaded style
                settings_copy.update(loaded_style)

                # Update current style
                self.current_style_name = style_name
                self.has_unsaved_changes = False

                logger.info(f"Loaded style: {style_name}")
                return settings_copy
            except Exception as e:
                logger.error(f"Error loading style {style_name}: {str(e)}")
                # Return unchanged settings
                return settings_copy

        # If style not found, return unchanged settings
        logger.warning(f"Style not found: {style_name}")
        return settings_copy

    def save_style(self, style_name: str, document_settings: Dict[str, Any]) -> bool:
        """
        Save current settings as a style

        Args:
            style_name: Name of the style to save
            document_settings: Current document settings

        Returns:
            True if saved successfully, False otherwise
        """
        # Make a copy of the settings to avoid modifying the original
        settings_copy = copy.deepcopy(document_settings)

        # Save the style
        style_path = os.path.join(self.styles_dir, f"{style_name}.json")
        try:
            with open(style_path, 'w', encoding='utf-8') as f:
                json.dump(settings_copy, f, indent=2)

            # Update current style
            self.current_style_name = style_name
            self.has_unsaved_changes = False

            # Update available styles if it's a new style
            if style_name not in self.available_styles:
                self.available_styles.append(style_name)

            logger.info(f"Saved style: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving style {style_name}: {str(e)}")
            return False

    def save_temp_style(self, document_settings: Dict[str, Any]) -> bool:
        """
        Save current settings as a temporary style

        Args:
            document_settings: Current document settings

        Returns:
            True if saved successfully, False otherwise
        """
        # Make a copy of the settings to avoid modifying the original
        settings_copy = copy.deepcopy(document_settings)

        # Save the temporary style
        try:
            with open(self.temp_style_path, 'w', encoding='utf-8') as f:
                json.dump(settings_copy, f, indent=2)

            logger.debug("Saved temporary style")
            return True
        except Exception as e:
            logger.error(f"Error saving temporary style: {str(e)}")
            return False

    def load_temp_style(self) -> Optional[Dict[str, Any]]:
        """
        Load the temporary style

        Returns:
            Temporary style settings or None if not found
        """
        if os.path.exists(self.temp_style_path):
            try:
                with open(self.temp_style_path, 'r', encoding='utf-8') as f:
                    temp_style = json.load(f)

                logger.debug("Loaded temporary style")
                return temp_style
            except Exception as e:
                logger.error(f"Error loading temporary style: {str(e)}")
                return None

        logger.debug("No temporary style found")
        return None

    def mark_as_changed(self):
        """Mark the current style as having unsaved changes"""
        # Only mark as changed if it's not a default style (except Custom)
        if self.current_style_name not in self.default_styles or self.current_style_name == "Custom":
            self.has_unsaved_changes = True

    def check_unsaved_changes(self) -> bool:
        """
        Check if there are unsaved changes

        Returns:
            True if there are unsaved changes, False otherwise
        """
        return self.has_unsaved_changes

    def delete_style(self, style_name: str) -> bool:
        """
        Delete a style

        Args:
            style_name: Name of the style to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        # Don't allow deleting default styles
        if style_name in self.default_styles:
            logger.warning(f"Cannot delete default style: {style_name}")
            return False

        # Delete the style file
        style_path = os.path.join(self.styles_dir, f"{style_name}.json")
        if os.path.exists(style_path):
            try:
                os.remove(style_path)

                # Remove from available styles
                if style_name in self.available_styles:
                    self.available_styles.remove(style_name)

                logger.info(f"Deleted style: {style_name}")
                return True
            except Exception as e:
                logger.error(f"Error deleting style {style_name}: {str(e)}")
                return False

        logger.warning(f"Style not found: {style_name}")
        return False
