#!/usr/bin/env python3
"""
Mermaid Content Processor
------------------------
Processor for Mermaid diagrams in Markdown.
"""

import re
import os
import tempfile
import subprocess
from typing import Dict, Any, List, Tuple, Optional
from shutil import which
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class MermaidContentProcessor(ContentProcessor):
    """Processor for Mermaid diagrams"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Mermaid processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
        self.mmdc_path, self.mmdc_version = self._find_mermaid_cli()
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect Mermaid diagrams in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        for match in re.finditer(self.mermaid_pattern, content, re.DOTALL):
            start, end = match.span()
            mermaid_code = match.group(1).strip()
            result.append((start, end, {'code': mermaid_code}))
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process Mermaid diagram for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        mermaid_code = metadata.get('code', '')
        
        # Create HTML for client-side rendering
        html = f"""
<div class="mermaid-wrapper" style="text-align: center; margin: 20px auto; width: 100%;">
  <div class="mermaid" style="display: inline-block; max-width: 100%; text-align: center;">
{mermaid_code}
  </div>
</div>
"""
        return html
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process Mermaid diagram for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        mermaid_code = metadata.get('code', '')
        
        if format_type in ['pdf', 'latex']:
            # For PDF/LaTeX export, render to SVG
            svg_content = self.render_mermaid_to_svg(mermaid_code)
            if svg_content:
                return f"\n\n{svg_content}\n\n"
            else:
                return "\n\n[Diagram Placeholder]\n\n"
        
        elif format_type in ['html', 'epub']:
            # For HTML/EPUB export, use client-side rendering
            return self.process_for_preview(content, metadata)
        
        elif format_type == 'docx':
            # For DOCX export, render to SVG and convert to PNG
            svg_content = self.render_mermaid_to_svg(mermaid_code)
            if svg_content:
                # In a real implementation, convert SVG to PNG here
                return f"\n\n[Diagram Image]\n\n"
            else:
                return "\n\n[Diagram Placeholder]\n\n"
        
        # Default fallback
        return "\n\n```\n[Diagram code removed]\n```\n\n"
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for Mermaid
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        return [
            '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>',
            '<script>mermaid.initialize({startOnLoad:true});</script>'
        ]
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies for Mermaid
        
        Returns:
            List of dependency names
        """
        return ['mermaid-cli']
    
    def check_dependencies(self) -> bool:
        """
        Check if Mermaid CLI is available
        
        Returns:
            True if Mermaid CLI is available, False otherwise
        """
        return self.mmdc_path is not None
    
    def _find_mermaid_cli(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Find the Mermaid CLI executable
        
        Returns:
            Tuple of (path, version) or (None, None) if not found
        """
        # Check for mmdc in PATH
        mmdc_path = which('mmdc')
        if mmdc_path:
            try:
                result = subprocess.run(
                    [mmdc_path, '--version'],
                    check=True,
                    capture_output=True,
                    text=True
                )
                version = result.stdout.strip()
                logger.info(f"Found Mermaid CLI: {mmdc_path}, version: {version}")
                return mmdc_path, version
            except Exception as e:
                logger.debug(f"Error checking Mermaid CLI version: {str(e)}")
        
        # Check for npx mmdc
        try:
            result = subprocess.run(
                ['npx', 'mmdc', '--version'],
                check=True,
                capture_output=True,
                text=True
            )
            version = result.stdout.strip()
            logger.info(f"Found Mermaid CLI via npx, version: {version}")
            return 'npx mmdc', version
        except Exception as e:
            logger.debug(f"Error checking npx Mermaid CLI: {str(e)}")
        
        logger.warning("Mermaid CLI not found")
        return None, None
    
    def render_mermaid_to_svg(self, mermaid_code: str, timeout: int = 15) -> Optional[str]:
        """
        Render a Mermaid diagram to SVG
        
        Args:
            mermaid_code: Mermaid diagram code
            timeout: Timeout in seconds
            
        Returns:
            SVG content or None if rendering failed
        """
        if not self.mmdc_path:
            logger.warning("Mermaid CLI not found, cannot render SVG")
            return None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.mmd', delete=False) as mmd_file:
                mmd_file.write(mermaid_code)
                mmd_path = mmd_file.name
            
            svg_path = mmd_path + '.svg'
            
            try:
                # Build the command
                if self.mmdc_path == 'npx mmdc':
                    cmd = [
                        'npx',
                        'mmdc',
                        '-i', mmd_path,
                        '-o', svg_path,
                        '-b', 'transparent',
                        '-w', '800',
                        '-H', '600'
                    ]
                else:
                    cmd = [
                        self.mmdc_path,
                        '-i', mmd_path,
                        '-o', svg_path,
                        '-b', 'transparent',
                        '-w', '800',
                        '-H', '600'
                    ]
                
                # Run the command
                process = subprocess.run(
                    cmd,
                    check=False,
                    capture_output=True,
                    timeout=timeout,
                    text=True
                )
                
                # Check for success
                if process.returncode == 0 and os.path.exists(svg_path):
                    # Read SVG content
                    with open(svg_path, 'r', encoding='utf-8') as svg_file:
                        svg_content = svg_file.read()
                    
                    if "<svg" in svg_content and "</svg>" in svg_content:
                        logger.debug("Successfully generated SVG with Mermaid CLI")
                        return svg_content
                
                logger.error(f"Mermaid CLI failed: {process.stderr}")
                return None
                
            finally:
                # Clean up temporary files
                try:
                    if os.path.exists(mmd_path):
                        os.unlink(mmd_path)
                    if os.path.exists(svg_path):
                        os.unlink(svg_path)
                except Exception as e:
                    logger.debug(f"Error cleaning up temporary files: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error rendering Mermaid diagram: {str(e)}")
            return None
