#!/usr/bin/env python3
"""
PlantUML Plugin
------------
Plugin for processing PlantUML diagrams in Markdown.
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

class PlantUMLProcessor(ContentProcessor):
    """Processor for PlantUML diagrams"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PlantUML processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.plantuml_pattern = r'```plantuml\s+(.*?)\s+```'
        self.plantuml_path = self._find_plantuml()
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect PlantUML diagrams in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        for match in re.finditer(self.plantuml_pattern, content, re.DOTALL):
            start, end = match.span()
            plantuml_code = match.group(1).strip()
            result.append((start, end, {'code': plantuml_code}))
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process PlantUML diagram for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        plantuml_code = metadata.get('code', '')
        
        # If PlantUML is available, render to SVG
        svg_content = self.render_plantuml_to_svg(plantuml_code)
        if svg_content:
            return f"\n\n{svg_content}\n\n"
        
        # Fallback to code block
        return f'```plantuml\n{plantuml_code}\n```'
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process PlantUML diagram for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        plantuml_code = metadata.get('code', '')
        
        if format_type in ['pdf', 'latex', 'html', 'epub']:
            # For PDF/LaTeX/HTML/EPUB export, render to SVG
            svg_content = self.render_plantuml_to_svg(plantuml_code)
            if svg_content:
                return f"\n\n{svg_content}\n\n"
        
        # Fallback to code block
        return f'```plantuml\n{plantuml_code}\n```'
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies for PlantUML
        
        Returns:
            List of dependency names
        """
        return ['plantuml']
    
    def check_dependencies(self) -> bool:
        """
        Check if PlantUML is available
        
        Returns:
            True if PlantUML is available, False otherwise
        """
        return self.plantuml_path is not None
    
    def _find_plantuml(self) -> Optional[str]:
        """
        Find the PlantUML executable
        
        Returns:
            Path to PlantUML or None if not found
        """
        # Check for plantuml in PATH
        plantuml_path = which('plantuml')
        if plantuml_path:
            logger.info(f"Found PlantUML: {plantuml_path}")
            return plantuml_path
        
        # Check for plantuml.jar in common locations
        common_locations = [
            os.path.expanduser('~/plantuml.jar'),
            '/usr/local/bin/plantuml.jar',
            '/usr/bin/plantuml.jar',
            'C:\\Program Files\\PlantUML\\plantuml.jar',
            'C:\\PlantUML\\plantuml.jar'
        ]
        
        for location in common_locations:
            if os.path.isfile(location):
                logger.info(f"Found PlantUML JAR: {location}")
                return f"java -jar {location}"
        
        logger.warning("PlantUML not found")
        return None
    
    def render_plantuml_to_svg(self, plantuml_code: str, timeout: int = 15) -> Optional[str]:
        """
        Render a PlantUML diagram to SVG
        
        Args:
            plantuml_code: PlantUML diagram code
            timeout: Timeout in seconds
            
        Returns:
            SVG content or None if rendering failed
        """
        if not self.plantuml_path:
            logger.warning("PlantUML not found, cannot render SVG")
            return None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.puml', delete=False) as puml_file:
                puml_file.write(f"@startuml\n{plantuml_code}\n@enduml")
                puml_path = puml_file.name
            
            svg_path = puml_path + '.svg'
            
            try:
                # Build the command
                if self.plantuml_path.startswith('java -jar'):
                    cmd = f"{self.plantuml_path} -tsvg {puml_path}"
                    shell = True
                else:
                    cmd = [self.plantuml_path, '-tsvg', puml_path]
                    shell = False
                
                # Run the command
                process = subprocess.run(
                    cmd,
                    shell=shell,
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
                        logger.debug("Successfully generated SVG with PlantUML")
                        return svg_content
                
                logger.error(f"PlantUML failed: {process.stderr}")
                return None
                
            finally:
                # Clean up temporary files
                try:
                    if os.path.exists(puml_path):
                        os.unlink(puml_path)
                    if os.path.exists(svg_path):
                        os.unlink(svg_path)
                except Exception as e:
                    logger.debug(f"Error cleaning up temporary files: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error rendering PlantUML diagram: {str(e)}")
            return None


def register_plugin(plugin_system):
    """
    Register the plugin with the plugin system
    
    Args:
        plugin_system: Plugin system instance
    """
    plugin_system.register_processor(PlantUMLProcessor, priority=70)
