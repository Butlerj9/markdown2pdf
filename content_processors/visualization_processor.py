#!/usr/bin/env python3
"""
Visualization Content Processor
----------------------------
Processor for interactive visualizations (Plotly, Chart.js) in Markdown.
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional
from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class VisualizationProcessor(ContentProcessor):
    """Processor for interactive visualizations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Visualization processor
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.plotly_pattern = r'```plotly\s+(.*?)\s+```'
        self.chartjs_pattern = r'```chartjs\s+(.*?)\s+```'
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect visualization blocks in content
        
        Args:
            content: The content to scan
            
        Returns:
            List of tuples containing (start_index, end_index, metadata)
        """
        result = []
        
        # Detect Plotly blocks
        for match in re.finditer(self.plotly_pattern, content, re.DOTALL):
            start, end = match.span()
            plotly_code = match.group(1).strip()
            result.append((
                start, end, 
                {
                    'type': 'plotly',
                    'code': plotly_code
                }
            ))
        
        # Detect Chart.js blocks
        for match in re.finditer(self.chartjs_pattern, content, re.DOTALL):
            start, end = match.span()
            chartjs_code = match.group(1).strip()
            result.append((
                start, end, 
                {
                    'type': 'chartjs',
                    'code': chartjs_code
                }
            ))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process visualization for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content for preview
        """
        vis_type = metadata.get('type', '')
        code = metadata.get('code', '')
        
        if vis_type == 'plotly':
            # Create a div for Plotly with a unique ID
            div_id = f"plotly-{hash(code) & 0xFFFFFFFF}"
            
            # Create HTML for client-side rendering
            html = f"""
<div id="{div_id}" class="plotly-visualization" style="width: 100%; height: 400px;"></div>
<script>
(function() {{
    try {{
        const plotlyData = {code};
        Plotly.newPlot('{div_id}', plotlyData.data, plotlyData.layout || {{}});
    }} catch (e) {{
        console.error('Error rendering Plotly visualization:', e);
        document.getElementById('{div_id}').innerHTML = '<p>Error rendering visualization</p>';
    }}
}})();
</script>
"""
            return html
        
        elif vis_type == 'chartjs':
            # Create a canvas for Chart.js with a unique ID
            canvas_id = f"chartjs-{hash(code) & 0xFFFFFFFF}"
            
            # Create HTML for client-side rendering
            html = f"""
<div style="width: 100%; max-width: 800px; margin: 0 auto;">
    <canvas id="{canvas_id}" width="800" height="400"></canvas>
</div>
<script>
(function() {{
    try {{
        const ctx = document.getElementById('{canvas_id}').getContext('2d');
        const chartConfig = {code};
        new Chart(ctx, chartConfig);
    }} catch (e) {{
        console.error('Error rendering Chart.js visualization:', e);
        document.getElementById('{canvas_id}').insertAdjacentHTML('afterend', '<p>Error rendering visualization</p>');
    }}
}})();
</script>
"""
            return html
        
        # Default fallback
        return f'```\n{code}\n```'
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process visualization for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content for export
        """
        vis_type = metadata.get('type', '')
        code = metadata.get('code', '')
        
        if format_type in ['html', 'epub']:
            # For HTML/EPUB export, use the same format as preview
            return self.process_for_preview(content, metadata)
        
        elif format_type in ['pdf', 'latex', 'docx']:
            # For PDF/LaTeX/DOCX export, generate a static image if possible
            # This is a simplified implementation
            if vis_type == 'plotly':
                return "\n\n[Plotly Visualization]\n\n"
            elif vis_type == 'chartjs':
                return "\n\n[Chart.js Visualization]\n\n"
        
        # Default fallback
        return f'```\n{code}\n```'
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for visualizations
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        return [
            '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
        ]
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies
        
        Returns:
            List of dependency names
        """
        return []  # No external dependencies required
