#!/usr/bin/env python3
"""
Code Block Content Processor
--------------------------
Processor for code blocks with syntax highlighting in Markdown.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class CodeBlockProcessor(ContentProcessor):
    """Processor for code blocks with syntax highlighting"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Code Block processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.code_block_pattern = r'```(\w+)?\s*\n(.*?)\n```'
        self.highlighter = self.config.get('highlighter', 'highlight.js')
        
        if self.highlighter not in ['highlight.js', 'prism.js']:
            logger.warning(f"Unknown syntax highlighter: {self.highlighter}, defaulting to highlight.js")
            self.highlighter = 'highlight.js'
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect code blocks in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        
        # Skip Mermaid code blocks (handled by MermaidContentProcessor)
        for match in re.finditer(self.code_block_pattern, content, re.DOTALL):
            start, end = match.span()
            language = match.group(1) or ''
            code = match.group(2)
            
            # Skip Mermaid code blocks
            if language.lower() == 'mermaid':
                continue
            
            result.append((
                start, end, 
                {
                    'language': language,
                    'code': code
                }
            ))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process code block for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        language = metadata.get('language', '')
        code = metadata.get('code', '')
        
        # Escape HTML entities
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Create HTML for syntax highlighting
        if language:
            return f'<pre><code class="language-{language}">{code}</code></pre>'
        else:
            return f'<pre><code>{code}</code></pre>'
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process code block for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        language = metadata.get('language', '')
        code = metadata.get('code', '')
        
        if format_type in ['html', 'epub']:
            # For HTML/EPUB export, use the same format as preview
            return self.process_for_preview(content, metadata)
        
        elif format_type in ['pdf', 'latex', 'docx']:
            # For PDF/LaTeX/DOCX export, use Markdown format
            if language:
                return f'```{language}\n{code}\n```'
            else:
                return f'```\n{code}\n```'
        
        # Default fallback
        if language:
            return f'```{language}\n{code}\n```'
        else:
            return f'```\n{code}\n```'
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for syntax highlighting
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        if self.highlighter == 'highlight.js':
            return [
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/styles/default.min.css">',
                '<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.7.0/lib/highlight.min.js"></script>',
                '<script>hljs.highlightAll();</script>'
            ]
        else:  # prism.js
            return [
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css">',
                '<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>'
            ]
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies
        
        Returns:
            List of dependency names
        """
        return []  # No external dependencies required
