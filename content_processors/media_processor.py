#!/usr/bin/env python3
"""
Media Content Processor
--------------------
Processor for HTML5 media (video/audio) in Markdown.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class MediaContentProcessor(ContentProcessor):
    """Processor for HTML5 media (video/audio)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Media processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.video_pattern = r'<video\s+.*?</video>'
        self.audio_pattern = r'<audio\s+.*?</audio>'
        self.iframe_pattern = r'<iframe\s+.*?</iframe>'
        self.asset_paths = self.config.get('asset_paths', {})
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect media elements in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        
        # Detect video elements
        for match in re.finditer(self.video_pattern, content, re.DOTALL):
            start, end = match.span()
            result.append((
                start, end, 
                {
                    'type': 'video',
                    'content': match.group(0)
                }
            ))
        
        # Detect audio elements
        for match in re.finditer(self.audio_pattern, content, re.DOTALL):
            start, end = match.span()
            result.append((
                start, end, 
                {
                    'type': 'audio',
                    'content': match.group(0)
                }
            ))
        
        # Detect iframe elements
        for match in re.finditer(self.iframe_pattern, content, re.DOTALL):
            start, end = match.span()
            result.append((
                start, end, 
                {
                    'type': 'iframe',
                    'content': match.group(0)
                }
            ))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process media element for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        # For preview, just use the original HTML
        return metadata.get('content', content)
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process media element for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        content_type = metadata.get('type', '')
        
        if format_type in ['html', 'epub']:
            # For HTML/EPUB export, use the original HTML
            return metadata.get('content', content)
        
        elif format_type in ['pdf', 'latex', 'docx']:
            # For PDF/LaTeX/DOCX export, replace with a placeholder
            if content_type == 'video':
                return "\n\n[Video content]\n\n"
            elif content_type == 'audio':
                return "\n\n[Audio content]\n\n"
            elif content_type == 'iframe':
                return "\n\n[Embedded content]\n\n"
        
        # Default fallback
        return metadata.get('content', content)
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies
        
        Returns:
            List of dependency names
        """
        return []  # No external dependencies required
