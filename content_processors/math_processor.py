#!/usr/bin/env python3
"""
Math Content Processor
--------------------
Processor for LaTeX math expressions in Markdown.
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class MathContentProcessor(ContentProcessor):
    """Processor for LaTeX math expressions"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Math processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.inline_math_pattern = r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)'
        self.display_math_pattern = r'\$\$(.*?)\$\$'
        self.math_engine = self.config.get('math_engine', 'mathjax')
        
        if self.math_engine not in ['mathjax', 'katex']:
            logger.warning(f"Unknown math engine: {self.math_engine}, defaulting to mathjax")
            self.math_engine = 'mathjax'
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect math expressions in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        
        # Detect inline math
        for match in re.finditer(self.inline_math_pattern, content):
            start, end = match.span()
            math_code = match.group(1)
            result.append((start, end, {'code': math_code, 'type': 'inline'}))
        
        # Detect display math
        for match in re.finditer(self.display_math_pattern, content, re.DOTALL):
            start, end = match.span()
            math_code = match.group(1)
            result.append((start, end, {'code': math_code, 'type': 'display'}))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process math expression for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        math_code = metadata.get('code', '')
        math_type = metadata.get('type', 'inline')
        
        if math_type == 'inline':
            return f"\\\\({math_code}\\\\)"
        else:  # display
            return f"\\\\[{math_code}\\\\]"
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process math expression for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        math_code = metadata.get('code', '')
        math_type = metadata.get('type', 'inline')
        
        if format_type in ['pdf', 'latex']:
            # For PDF/LaTeX export, use native LaTeX math
            if math_type == 'inline':
                return f"${math_code}$"
            else:  # display
                return f"$${math_code}$$"
        
        elif format_type in ['html', 'epub']:
            # For HTML/EPUB export, use the same format as preview
            return self.process_for_preview(content, metadata)
        
        elif format_type == 'docx':
            # For DOCX export, use MathML if possible
            # This is a simplified implementation
            if math_type == 'inline':
                return f"${math_code}$"
            else:  # display
                return f"$${math_code}$$"
        
        # Default fallback
        if math_type == 'inline':
            return f"${math_code}$"
        else:  # display
            return f"$${math_code}$$"
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for math rendering
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        if self.math_engine == 'mathjax':
            return [
                '<script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>',
                '''<script>
                window.MathJax = {
                  tex: {
                    inlineMath: [['\\\\(', '\\\\)']],
                    displayMath: [['\\\\[', '\\\\]']],
                    processEscapes: true
                  }
                };
                </script>'''
            ]
        else:  # KaTeX
            return [
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">',
                '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>',
                '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>',
                '''<script>
                document.addEventListener("DOMContentLoaded", function() {
                  renderMathInElement(document.body, {
                    delimiters: [
                      {left: '\\\\(', right: '\\\\)', display: false},
                      {left: '\\\\[', right: '\\\\]', display: true}
                    ]
                  });
                });
                </script>'''
            ]
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies for math rendering
        
        Returns:
            List of dependency names
        """
        return []  # No external dependencies required
