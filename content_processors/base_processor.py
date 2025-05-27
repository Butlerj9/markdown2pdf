#!/usr/bin/env python3
"""
Content Processor Base Class
----------------------------
Base class for all content processors in the Markdown to PDF converter.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from logging_config import get_logger

logger = get_logger()

class ContentProcessor(ABC):
    """Base class for all content processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the content processor
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        logger.debug(f"Initializing {self.name}")
    
    @abstractmethod
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect content that this processor can handle
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        pass
    
    @abstractmethod
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process content for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        pass
    
    @abstractmethod
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process content for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        pass
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for this processor
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        return []
    
    def get_required_styles(self) -> List[str]:
        """
        Get required CSS styles for this processor
        
        Returns:
            List of CSS style URLs or inline styles
        """
        return []
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies for this processor
        
        Returns:
            List of dependency names
        """
        return []
    
    def check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        return True
