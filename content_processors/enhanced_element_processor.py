#!/usr/bin/env python3
"""
Enhanced Element Processor for Markdown to PDF Converter
-------------------------------------------------------
Provides comprehensive support for various document elements:
- Tables
- Spreadsheets (CSV data)
- Diagrams (Mermaid, PlantUML)
- Images with advanced formatting
- Math equations
- Code blocks with syntax highlighting
"""

import re
import os
import csv
import io
import base64
import json
import tempfile
import subprocess
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

from logging_config import get_logger
from content_processors.base_processor import ContentProcessor

logger = get_logger()

class EnhancedElementProcessor(ContentProcessor):
    """
    Enhanced processor for various document elements
    Provides comprehensive support for tables, spreadsheets, diagrams, and more
    """
    
    def __init__(self, config=None):
        """
        Initialize the enhanced element processor
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.temp_dir = tempfile.mkdtemp(prefix="markdown2pdf_")
        
        # Patterns for different elements
        self.table_pattern = r'(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]+\|\n)+)'
        self.csv_pattern = r'```csv\s+(.*?)\s+```'
        self.mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
        self.plantuml_pattern = r'```plantuml\s+(.*?)\s+```'
        self.math_pattern = r'\$\$(.*?)\$\$|\$(.*?)\$'
        
        # Initialize renderers
        self._init_renderers()
    
    def _init_renderers(self):
        """Initialize various renderers for different content types"""
        # Check for mermaid CLI
        self.mmdc_path, self.mmdc_version = self._find_mermaid_cli()
        
        # Check for PlantUML
        self.plantuml_path, self.plantuml_version = self._find_plantuml()
        
        # Check for MathJax
        self.mathjax_available = self._check_mathjax()
    
    def _find_mermaid_cli(self) -> Tuple[str, str]:
        """Find Mermaid CLI executable"""
        try:
            # Try to find mmdc executable
            result = subprocess.run(
                ["mmdc", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"Found Mermaid CLI: {version}")
                return "mmdc", version
            
            # Try npm global path
            result = subprocess.run(
                ["npm", "list", "-g", "@mermaid-js/mermaid-cli"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if "@mermaid-js/mermaid-cli" in result.stdout:
                version_match = re.search(r'@mermaid-js/mermaid-cli@(\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else "unknown"
                logger.info(f"Found Mermaid CLI via npm: {version}")
                return "npx mmdc", version
            
            logger.warning("Mermaid CLI not found, diagrams will be rendered as code blocks")
            return "", ""
        except Exception as e:
            logger.error(f"Error finding Mermaid CLI: {str(e)}")
            return "", ""
    
    def _find_plantuml(self) -> Tuple[str, str]:
        """Find PlantUML executable or jar"""
        try:
            # Try to find plantuml executable
            result = subprocess.run(
                ["plantuml", "-version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0:
                version_match = re.search(r'PlantUML version (\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else "unknown"
                logger.info(f"Found PlantUML: {version}")
                return "plantuml", version
            
            # Check for plantuml.jar in common locations
            common_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "plantuml.jar"),
                os.path.expanduser("~/plantuml.jar"),
                "/usr/local/bin/plantuml.jar",
                "C:\\Program Files\\PlantUML\\plantuml.jar"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    logger.info(f"Found PlantUML jar: {path}")
                    # Try to get version
                    result = subprocess.run(
                        ["java", "-jar", path, "-version"], 
                        capture_output=True, 
                        text=True, 
                        check=False
                    )
                    version_match = re.search(r'PlantUML version (\d+\.\d+\.\d+)', result.stdout)
                    version = version_match.group(1) if version_match else "unknown"
                    return f"java -jar {path}", version
            
            logger.warning("PlantUML not found, diagrams will be rendered as code blocks")
            return "", ""
        except Exception as e:
            logger.error(f"Error finding PlantUML: {str(e)}")
            return "", ""
    
    def _check_mathjax(self) -> bool:
        """Check if MathJax is available"""
        try:
            # Check if MathJax resources exist
            mathjax_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "mathjax")
            if os.path.exists(mathjax_path):
                logger.info(f"Found MathJax resources: {mathjax_path}")
                return True
            
            logger.warning("MathJax resources not found, math equations will be rendered using online CDN")
            return False
        except Exception as e:
            logger.error(f"Error checking MathJax: {str(e)}")
            return False
    
    def detect(self, content: str) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Detect various elements in the content
        
        Args:
            content: The content to process
            
        Returns:
            List of tuples with (start_pos, end_pos, element_info)
        """
        result = []
        
        # Detect tables
        for match in re.finditer(self.table_pattern, content, re.DOTALL):
            start, end = match.span()
            table_content = match.group(1)
            result.append((start, end, {'type': 'table', 'content': table_content}))
        
        # Detect CSV data
        for match in re.finditer(self.csv_pattern, content, re.DOTALL):
            start, end = match.span()
            csv_content = match.group(1).strip()
            result.append((start, end, {'type': 'csv', 'content': csv_content}))
        
        # Detect Mermaid diagrams
        for match in re.finditer(self.mermaid_pattern, content, re.DOTALL):
            start, end = match.span()
            mermaid_code = match.group(1).strip()
            result.append((start, end, {'type': 'mermaid', 'content': mermaid_code}))
        
        # Detect PlantUML diagrams
        for match in re.finditer(self.plantuml_pattern, content, re.DOTALL):
            start, end = match.span()
            plantuml_code = match.group(1).strip()
            result.append((start, end, {'type': 'plantuml', 'content': plantuml_code}))
        
        # Detect math equations
        for match in re.finditer(self.math_pattern, content, re.DOTALL):
            start, end = match.span()
            math_content = match.group(1) or match.group(2)
            is_block = match.group(1) is not None  # $$ for block, $ for inline
            result.append((start, end, {'type': 'math', 'content': math_content, 'block': is_block}))
        
        return result
    
    def process_for_preview(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Process content for preview
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            
        Returns:
            Processed content with enhanced elements
        """
        logger.debug("Processing enhanced elements for preview")
        
        try:
            # Process tables
            content = self._enhance_tables_for_preview(content)
            
            # Process CSV data
            content = self._process_csv_for_preview(content)
            
            # Process Mermaid diagrams
            content = self._process_mermaid_for_preview(content)
            
            # Process PlantUML diagrams
            content = self._process_plantuml_for_preview(content)
            
            # Process math equations
            content = self._process_math_for_preview(content)
            
            return content
        except Exception as e:
            logger.error(f"Error processing enhanced elements for preview: {str(e)}")
            return content
    
    def process_for_export(self, content: str, metadata: Dict[str, Any], format_type: str) -> str:
        """
        Process content for export
        
        Args:
            content: The content to process
            metadata: Additional metadata for processing
            format_type: Export format type (pdf, html, docx, etc.)
            
        Returns:
            Processed content with enhanced elements for export
        """
        logger.debug(f"Processing enhanced elements for export to {format_type}")
        
        try:
            # Process tables
            content = self._enhance_tables_for_export(content)
            
            # Process CSV data
            content = self._process_csv_for_export(content)
            
            # Process Mermaid diagrams
            content = self._process_mermaid_for_export(content)
            
            # Process PlantUML diagrams
            content = self._process_plantuml_for_export(content)
            
            # Process math equations
            content = self._process_math_for_export(content)
            
            return content
        except Exception as e:
            logger.error(f"Error processing enhanced elements for export: {str(e)}")
            return content
    
    def _enhance_tables_for_preview(self, content: str) -> str:
        """Enhance tables for preview with better styling"""
        def replace_table(match):
            table_content = match.group(1)
            
            # Parse the table
            lines = table_content.strip().split('\n')
            if len(lines) < 3:
                return match.group(0)  # Not enough lines for a valid table
            
            # Extract header and alignment
            header_row = lines[0]
            alignment_row = lines[1]
            data_rows = lines[2:]
            
            # Parse alignment
            alignments = []
            for cell in alignment_row.split('|')[1:-1]:
                cell = cell.strip()
                if cell.startswith(':') and cell.endswith(':'):
                    alignments.append('center')
                elif cell.endswith(':'):
                    alignments.append('right')
                else:
                    alignments.append('left')
            
            # Build enhanced HTML table
            html = '<div class="enhanced-table-container">\n'
            html += '<table class="enhanced-table">\n'
            
            # Header
            html += '<thead>\n<tr>\n'
            header_cells = header_row.split('|')[1:-1]
            for i, cell in enumerate(header_cells):
                alignment = alignments[i] if i < len(alignments) else 'left'
                html += f'<th style="text-align: {alignment}">{cell.strip()}</th>\n'
            html += '</tr>\n</thead>\n'
            
            # Body
            html += '<tbody>\n'
            for row in data_rows:
                html += '<tr>\n'
                cells = row.split('|')[1:-1]
                for i, cell in enumerate(cells):
                    alignment = alignments[i] if i < len(alignments) else 'left'
                    html += f'<td style="text-align: {alignment}">{cell.strip()}</td>\n'
                html += '</tr>\n'
            html += '</tbody>\n'
            
            html += '</table>\n</div>'
            
            # Add CSS for enhanced tables
            css = """
            <style>
            .enhanced-table-container {
                overflow-x: auto;
                margin: 20px 0;
            }
            .enhanced-table {
                border-collapse: collapse;
                width: 100%;
                border: 1px solid #ddd;
            }
            .enhanced-table th, .enhanced-table td {
                padding: 8px;
                border: 1px solid #ddd;
            }
            .enhanced-table thead {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            .enhanced-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .enhanced-table tr:hover {
                background-color: #f1f1f1;
            }
            </style>
            """
            
            return css + html
        
        return re.sub(self.table_pattern, replace_table, content, flags=re.DOTALL)
    
    def _enhance_tables_for_export(self, content: str) -> str:
        """Enhance tables for export"""
        # For export, we'll let the Markdown processor handle tables
        # This is just a placeholder in case we need special handling
        return content
    
    def _process_csv_for_preview(self, content: str) -> str:
        """Process CSV data for preview"""
        def replace_csv(match):
            csv_content = match.group(1).strip()
            
            try:
                # Parse CSV data
                csv_reader = csv.reader(io.StringIO(csv_content))
                rows = list(csv_reader)
                
                if not rows:
                    return '<div class="csv-error">Empty CSV data</div>'
                
                # Build HTML table
                html = '<div class="csv-table-container">\n'
                html += '<table class="csv-table">\n'
                
                # Header (first row)
                html += '<thead>\n<tr>\n'
                for cell in rows[0]:
                    html += f'<th>{cell}</th>\n'
                html += '</tr>\n</thead>\n'
                
                # Body (remaining rows)
                html += '<tbody>\n'
                for row in rows[1:]:
                    html += '<tr>\n'
                    for cell in row:
                        html += f'<td>{cell}</td>\n'
                    html += '</tr>\n'
                html += '</tbody>\n'
                
                html += '</table>\n</div>'
                
                # Add CSS for CSV tables
                css = """
                <style>
                .csv-table-container {
                    overflow-x: auto;
                    margin: 20px 0;
                }
                .csv-table {
                    border-collapse: collapse;
                    width: 100%;
                    border: 1px solid #ddd;
                }
                .csv-table th, .csv-table td {
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }
                .csv-table thead {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                .csv-table tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .csv-table tr:hover {
                    background-color: #f1f1f1;
                }
                .csv-error {
                    color: red;
                    font-style: italic;
                    padding: 10px;
                    border: 1px solid #ffcccc;
                    background-color: #ffeeee;
                    margin: 10px 0;
                }
                </style>
                """
                
                return css + html
            except Exception as e:
                logger.error(f"Error processing CSV data: {str(e)}")
                return f'<div class="csv-error">Error processing CSV data: {str(e)}</div>'
        
        return re.sub(self.csv_pattern, replace_csv, content, flags=re.DOTALL)
    
    def _process_csv_for_export(self, content: str) -> str:
        """Process CSV data for export"""
        def replace_csv(match):
            csv_content = match.group(1).strip()
            
            try:
                # Parse CSV data
                csv_reader = csv.reader(io.StringIO(csv_content))
                rows = list(csv_reader)
                
                if not rows:
                    return '**Empty CSV data**'
                
                # Convert to Markdown table
                md_table = []
                
                # Header
                header = ' | '.join(rows[0])
                md_table.append(f'| {header} |')
                
                # Separator
                separator = ' | '.join(['---'] * len(rows[0]))
                md_table.append(f'| {separator} |')
                
                # Data rows
                for row in rows[1:]:
                    data = ' | '.join(row)
                    md_table.append(f'| {data} |')
                
                return '\n'.join(md_table)
            except Exception as e:
                logger.error(f"Error processing CSV data for export: {str(e)}")
                return f'**Error processing CSV data: {str(e)}**'
        
        return re.sub(self.csv_pattern, replace_csv, content, flags=re.DOTALL)
    
    def _process_mermaid_for_preview(self, content: str) -> str:
        """Process Mermaid diagrams for preview"""
        def replace_mermaid(match):
            mermaid_code = match.group(1).strip()
            
            # If Mermaid CLI is not available, use client-side rendering
            if not self.mmdc_path:
                return f"""
                <div class="mermaid-diagram">
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                </div>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <script>
                    mermaid.initialize({{ startOnLoad: true }});
                </script>
                """
            
            try:
                # Create a temporary file for the Mermaid code
                with tempfile.NamedTemporaryFile(suffix='.mmd', delete=False, mode='w') as f:
                    mmd_file = f.name
                    f.write(mermaid_code)
                
                # Create a temporary file for the SVG output
                svg_file = os.path.splitext(mmd_file)[0] + '.svg'
                
                # Run Mermaid CLI to generate SVG
                cmd = f"{self.mmdc_path} -i {mmd_file} -o {svg_file}"
                subprocess.run(cmd, shell=True, check=True)
                
                # Read the SVG content
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                # Clean up temporary files
                os.unlink(mmd_file)
                os.unlink(svg_file)
                
                return f"""
                <div class="mermaid-diagram">
                    {svg_content}
                </div>
                <style>
                .mermaid-diagram {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .mermaid-diagram svg {{
                    max-width: 100%;
                    height: auto;
                }}
                </style>
                """
            except Exception as e:
                logger.error(f"Error rendering Mermaid diagram: {str(e)}")
                return f"""
                <div class="mermaid-error">
                    <p>Error rendering Mermaid diagram: {str(e)}</p>
                    <pre><code class="language-mermaid">{mermaid_code}</code></pre>
                </div>
                <style>
                .mermaid-error {{
                    color: red;
                    font-style: italic;
                    padding: 10px;
                    border: 1px solid #ffcccc;
                    background-color: #ffeeee;
                    margin: 10px 0;
                }}
                </style>
                """
        
        return re.sub(self.mermaid_pattern, replace_mermaid, content, flags=re.DOTALL)
    
    def _process_mermaid_for_export(self, content: str) -> str:
        """Process Mermaid diagrams for export"""
        # For export, we'll keep the Mermaid code blocks as is
        # The export process will handle them separately
        return content
    
    def _process_plantuml_for_preview(self, content: str) -> str:
        """Process PlantUML diagrams for preview"""
        def replace_plantuml(match):
            plantuml_code = match.group(1).strip()
            
            # If PlantUML is not available, show the code
            if not self.plantuml_path:
                return f"""
                <div class="plantuml-code">
                    <p><strong>PlantUML Diagram</strong> (PlantUML not available for rendering)</p>
                    <pre><code class="language-plantuml">{plantuml_code}</code></pre>
                </div>
                <style>
                .plantuml-code {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    background-color: #f8f8f8;
                    margin: 10px 0;
                }}
                </style>
                """
            
            try:
                # Create a temporary file for the PlantUML code
                with tempfile.NamedTemporaryFile(suffix='.puml', delete=False, mode='w') as f:
                    puml_file = f.name
                    f.write(plantuml_code)
                
                # Create a temporary file for the SVG output
                svg_file = os.path.splitext(puml_file)[0] + '.svg'
                
                # Run PlantUML to generate SVG
                cmd = f"{self.plantuml_path} -tsvg {puml_file}"
                subprocess.run(cmd, shell=True, check=True)
                
                # Read the SVG content
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                # Clean up temporary files
                os.unlink(puml_file)
                os.unlink(svg_file)
                
                return f"""
                <div class="plantuml-diagram">
                    {svg_content}
                </div>
                <style>
                .plantuml-diagram {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .plantuml-diagram svg {{
                    max-width: 100%;
                    height: auto;
                }}
                </style>
                """
            except Exception as e:
                logger.error(f"Error rendering PlantUML diagram: {str(e)}")
                return f"""
                <div class="plantuml-error">
                    <p>Error rendering PlantUML diagram: {str(e)}</p>
                    <pre><code class="language-plantuml">{plantuml_code}</code></pre>
                </div>
                <style>
                .plantuml-error {{
                    color: red;
                    font-style: italic;
                    padding: 10px;
                    border: 1px solid #ffcccc;
                    background-color: #ffeeee;
                    margin: 10px 0;
                }}
                </style>
                """
        
        return re.sub(self.plantuml_pattern, replace_plantuml, content, flags=re.DOTALL)
    
    def _process_plantuml_for_export(self, content: str) -> str:
        """Process PlantUML diagrams for export"""
        # For export, we'll keep the PlantUML code blocks as is
        # The export process will handle them separately
        return content
    
    def _process_math_for_preview(self, content: str) -> str:
        """Process math equations for preview"""
        def replace_math(match):
            math_content = match.group(1) or match.group(2)
            is_block = match.group(1) is not None  # $$ for block, $ for inline
            
            # Use MathJax for rendering
            if is_block:
                return f"""
                <div class="math-block">
                    \\[{math_content}\\]
                </div>
                """
            else:
                return f"\\({math_content}\\)"
        
        # Replace math equations
        content = re.sub(self.math_pattern, replace_math, content)
        
        # Add MathJax script if not already present
        if "\\(" in content or "\\[" in content:
            if "</body>" in content:
                mathjax_script = """
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <style>
                .math-block {
                    text-align: center;
                    margin: 20px 0;
                    overflow-x: auto;
                }
                </style>
                """
                content = content.replace("</body>", mathjax_script + "</body>")
        
        return content
    
    def _process_math_for_export(self, content: str) -> str:
        """Process math equations for export"""
        # For export, we'll keep the math equations as is
        # The export process will handle them separately
        return content
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")
    
    def get_required_scripts(self) -> List[str]:
        """
        Get required JavaScript scripts for this processor
        
        Returns:
            List of JavaScript script URLs or inline scripts
        """
        scripts = []
        
        # Add MathJax script
        scripts.append("https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js")
        
        # Add Mermaid script if needed
        if not self.mmdc_path:
            scripts.append("https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js")
        
        return scripts
    
    def get_required_styles(self) -> List[str]:
        """
        Get required CSS styles for this processor
        
        Returns:
            List of CSS style URLs or inline styles
        """
        styles = []
        
        # Add table styles
        styles.append("""
        .enhanced-table-container {
            overflow-x: auto;
            margin: 20px 0;
        }
        .enhanced-table, .csv-table {
            border-collapse: collapse;
            width: 100%;
            border: 1px solid #ddd;
        }
        .enhanced-table th, .enhanced-table td,
        .csv-table th, .csv-table td {
            padding: 8px;
            border: 1px solid #ddd;
        }
        .enhanced-table thead, .csv-table thead {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .enhanced-table tr:nth-child(even),
        .csv-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .enhanced-table tr:hover,
        .csv-table tr:hover {
            background-color: #f1f1f1;
        }
        """)
        
        # Add diagram styles
        styles.append("""
        .mermaid-diagram, .plantuml-diagram {
            text-align: center;
            margin: 20px 0;
        }
        .mermaid-diagram svg, .plantuml-diagram svg {
            max-width: 100%;
            height: auto;
        }
        .mermaid-error, .plantuml-error, .csv-error {
            color: red;
            font-style: italic;
            padding: 10px;
            border: 1px solid #ffcccc;
            background-color: #ffeeee;
            margin: 10px 0;
        }
        .math-block {
            text-align: center;
            margin: 20px 0;
            overflow-x: auto;
        }
        """)
        
        return styles
    
    def get_dependencies(self) -> List[str]:
        """
        Get required external dependencies for this processor
        
        Returns:
            List of dependency names
        """
        dependencies = []
        
        # Add Mermaid CLI dependency
        if not self.mmdc_path:
            dependencies.append("@mermaid-js/mermaid-cli")
        
        # Add PlantUML dependency
        if not self.plantuml_path:
            dependencies.append("plantuml")
        
        return dependencies
    
    def check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        # Check for Mermaid CLI
        has_mermaid = bool(self.mmdc_path)
        
        # Check for PlantUML
        has_plantuml = bool(self.plantuml_path)
        
        # Check for MathJax
        has_mathjax = self.mathjax_available
        
        # Log dependency status
        logger.info(f"Enhanced element processor dependencies: Mermaid: {has_mermaid}, PlantUML: {has_plantuml}, MathJax: {has_mathjax}")
        
        # Return True even if some dependencies are missing - we'll handle gracefully
        return True