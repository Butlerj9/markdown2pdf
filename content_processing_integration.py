#!/usr/bin/env python3
"""
Content Processing Integration
---------------------------
Integration of the content processing system with the main application.
"""

import os
from typing import Dict, Any, Optional
from logging_config import get_logger
from content_processors import registry
from plugin_system import PluginSystem

logger = get_logger()

class ContentProcessingIntegration:
    """Integration of the content processing system with the main application"""
    
    def __init__(self):
        """Initialize the integration"""
        self.plugin_system = PluginSystem()
        
        # Register plugin directories
        self._register_plugin_directories()
        
        # Discover plugins
        self.plugin_system.discover_plugins()
    
    def _register_plugin_directories(self):
        """Register plugin directories"""
        # Register the default plugin directory
        default_plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if os.path.isdir(default_plugin_dir):
            self.plugin_system.register_plugin_directory(default_plugin_dir)
        
        # Register user plugin directory
        user_plugin_dir = os.path.expanduser('~/.mdz/plugins')
        if os.path.isdir(user_plugin_dir):
            self.plugin_system.register_plugin_directory(user_plugin_dir)
    
    def process_content_for_preview(self, content: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Process content for preview
        
        Args:
            content: The content to process
            config: Optional configuration
            
        Returns:
            Processed content
        """
        logger.debug("Processing content for preview")
        return registry.process_content(content, 'preview')
    
    def process_content_for_export(self, content: str, format_type: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Process content for export
        
        Args:
            content: The content to process
            format_type: Export format type (pdf, html, docx, etc.)
            config: Optional configuration
            
        Returns:
            Processed content
        """
        logger.debug(f"Processing content for export: {format_type}")
        return registry.process_content(content, format_type)
    
    def get_required_scripts(self) -> str:
        """
        Get all required JavaScript scripts
        
        Returns:
            HTML string with script tags
        """
        scripts = registry.get_required_scripts()
        return '\n'.join(scripts)
    
    def get_required_styles(self) -> str:
        """
        Get all required CSS styles
        
        Returns:
            HTML string with style tags
        """
        styles = registry.get_required_styles()
        return '\n'.join(styles)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if all required dependencies are available
        
        Returns:
            Dictionary mapping processor names to dependency status
        """
        return registry.check_dependencies()


# Function to get the integration instance
def get_integration() -> ContentProcessingIntegration:
    """
    Get the content processing integration instance
    
    Returns:
        ContentProcessingIntegration instance
    """
    return ContentProcessingIntegration()
