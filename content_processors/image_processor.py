#!/usr/bin/env python3
"""
Image Content Processor
---------------------
Processor for images and SVG content in Markdown.
"""

import re
import os
import base64
from typing import Dict, Any, List, Tuple, Optional
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class ImageContentProcessor(ContentProcessor):
    """Processor for images and SVG content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Image processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.markdown_image_pattern = r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)'
        self.html_image_pattern = r'<img\s+[^>]*src="([^"]*)"[^>]*>'
        self.svg_pattern = r'<svg\s+.*?</svg>'
        self.asset_paths = self.config.get('asset_paths', {})
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect images and SVG content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        
        # Detect Markdown images
        for match in re.finditer(self.markdown_image_pattern, content):
            start, end = match.span()
            alt_text = match.group(1)
            src = match.group(2)
            title = match.group(3) if match.group(3) else ''
            
            # Resolve path if it's in asset_paths
            resolved_src = self.resolve_path(src)
            
            result.append((
                start, end, 
                {
                    'type': 'markdown_image',
                    'alt': alt_text,
                    'src': resolved_src,
                    'title': title
                }
            ))
        
        # Detect HTML images
        for match in re.finditer(self.html_image_pattern, content):
            start, end = match.span()
            src = match.group(1)
            
            # Resolve path if it's in asset_paths
            resolved_src = self.resolve_path(src)
            
            result.append((
                start, end, 
                {
                    'type': 'html_image',
                    'src': resolved_src,
                    'original': match.group(0)
                }
            ))
        
        # Detect inline SVG
        for match in re.finditer(self.svg_pattern, content, re.DOTALL):
            start, end = match.span()
            result.append((
                start, end, 
                {
                    'type': 'svg',
                    'content': match.group(0)
                }
            ))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process image or SVG for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        content_type = metadata.get('type', '')
        
        if content_type == 'markdown_image':
            alt = metadata.get('alt', '')
            src = metadata.get('src', '')
            title = metadata.get('title', '')
            
            title_attr = f' title="{title}"' if title else ''
            return f'<img src="{src}" alt="{alt}"{title_attr} class="markdown-image">'
        
        elif content_type == 'html_image':
            # For HTML images, just use the original HTML
            return metadata.get('original', content)
        
        elif content_type == 'svg':
            # For SVG, just use the original SVG
            return metadata.get('content', content)
        
        # Default fallback
        return content
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process image or SVG for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        content_type = metadata.get('type', '')
        
        if format_type in ['html', 'epub']:
            # For HTML/EPUB export, use the same format as preview
            return self.process_for_preview(content, metadata)
        
        elif format_type in ['pdf', 'latex']:
            # For PDF/LaTeX export, handle images and SVG differently
            if content_type == 'svg':
                # For SVG, convert to embedded image if possible
                svg_content = metadata.get('content', '')
                return f"\n\n{svg_content}\n\n"
            else:
                # For images, use the src directly
                src = metadata.get('src', '')
                alt = metadata.get('alt', '') if content_type == 'markdown_image' else ''
                
                # For Markdown images, use Markdown format
                if content_type == 'markdown_image':
                    title = metadata.get('title', '')
                    title_part = f' "{title}"' if title else ''
                    return f'![{alt}]({src}{title_part})'
                else:
                    # For HTML images, use HTML format
                    return metadata.get('original', content)
        
        elif format_type == 'docx':
            # For DOCX export, use Markdown format for images
            if content_type == 'markdown_image':
                alt = metadata.get('alt', '')
                src = metadata.get('src', '')
                title = metadata.get('title', '')
                title_part = f' "{title}"' if title else ''
                return f'![{alt}]({src}{title_part})'
            elif content_type == 'html_image':
                src = metadata.get('src', '')
                return f'![Image]({src})'
            elif content_type == 'svg':
                # For SVG, convert to PNG if possible
                # This is a simplified implementation
                return "\n\n[SVG Image]\n\n"
        
        # Default fallback
        return content
    
    def resolve_path(self, path: str) -> str:
        """
        Resolve a path using asset_paths
        
        Args:
            path: The path to resolve
            
        Returns:
            Resolved path
        """
        if path in self.asset_paths:
            resolved_path = self.asset_paths[path]
            logger.debug(f"Resolved path {path} to {resolved_path}")
            return resolved_path
        
        return path
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies
        
        Returns:
            List of dependency names
        """
        return []  # No external dependencies required
