#!/usr/bin/env python3
"""
Plugin System
-----------
Plugin system for the Markdown to PDF converter.
"""

import os
import sys
import importlib.util
from typing import Dict, List, Any, Optional, Type
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor
from content_processors.processor_registry import ProcessorRegistry

logger = get_logger()

class PluginSystem:
    """Plugin system for the Markdown to PDF converter"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(PluginSystem, cls).__new__(cls)
            cls._instance._plugins = {}
            cls._instance._plugin_dirs = []
            cls._instance._registry = ProcessorRegistry()
        return cls._instance
    
    def register_plugin_directory(self, directory: str):
        """
        Register a directory to search for plugins
        
        Args:
            directory: Directory path
        """
        if os.path.isdir(directory) and directory not in self._plugin_dirs:
            logger.debug(f"Registering plugin directory: {directory}")
            self._plugin_dirs.append(directory)
    
    def discover_plugins(self):
        """
        Discover plugins in registered directories
        """
        for directory in self._plugin_dirs:
            logger.debug(f"Discovering plugins in {directory}")
            self._discover_plugins_in_directory(directory)
    
    def _discover_plugins_in_directory(self, directory: str):
        """
        Discover plugins in a directory
        
        Args:
            directory: Directory path
        """
        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_path = os.path.join(directory, filename)
                plugin_name = os.path.splitext(filename)[0]
                self._load_plugin(plugin_name, plugin_path)
    
    def _load_plugin(self, plugin_name: str, plugin_path: str):
        """
        Load a plugin from a file
        
        Args:
            plugin_name: Plugin name
            plugin_path: Plugin file path
        """
        try:
            logger.debug(f"Loading plugin: {plugin_name} from {plugin_path}")
            
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Failed to load plugin: {plugin_name}")
                return
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Check if the module has a register_plugin function
            if hasattr(module, 'register_plugin'):
                module.register_plugin(self)
                logger.info(f"Successfully registered plugin: {plugin_name}")
                self._plugins[plugin_name] = {
                    'path': plugin_path,
                    'module': module
                }
            else:
                logger.warning(f"Plugin {plugin_name} does not have a register_plugin function")
        
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
    
    def register_processor(self, processor_class: Type[ContentProcessor], priority: int = 100):
        """
        Register a content processor
        
        Args:
            processor_class: The processor class to register
            priority: Priority of the processor (lower values = higher priority)
        """
        self._registry.register_processor(processor_class, priority)
    
    def get_registry(self) -> ProcessorRegistry:
        """
        Get the processor registry
        
        Returns:
            Processor registry
        """
        return self._registry
    
    def get_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered plugins
        
        Returns:
            Dictionary of plugins
        """
        return self._plugins
    
    def get_plugin(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a plugin by name
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Plugin information or None if not found
        """
        return self._plugins.get(plugin_name)


# Example plugin file structure:
"""
# example_plugin.py

from content_processors.base_processor import ContentProcessor

class ExampleProcessor(ContentProcessor):
    # Implementation...
    pass

def register_plugin(plugin_system):
    plugin_system.register_processor(ExampleProcessor, priority=200)
"""
