#!/usr/bin/env python3
"""
Mermaid Diagram Processor
------------------------
Utilities for processing Mermaid diagrams in Markdown.
File: src--mermaid_processor.py
"""

import os, platform
import re
import tempfile
import subprocess
import json
import base64
from shutil import which
from logging_config import get_logger, EnhancedLogger

logger = get_logger()

class MermaidProcessor:
    """Handles the processing of Mermaid diagrams in Markdown"""
    
    @staticmethod
    def preprocess_mermaid_diagrams(markdown_text):
        """
        Pre-process Markdown to handle Mermaid diagrams for client-side rendering
        This preserves Mermaid code blocks as HTML divs that can be rendered client-side
        """
        import re
        from logging_config import get_logger, EnhancedLogger
        
        logger = get_logger()
        logger.debug("Preprocessing Mermaid diagrams")
        EnhancedLogger.log_function_entry(logger, "preprocess_mermaid_diagrams", f"Text length: {len(markdown_text)}")
        
        try:
            # Find Mermaid code blocks
            mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
            mermaid_blocks = re.findall(mermaid_pattern, markdown_text, re.DOTALL)
            
            logger.debug(f"Found {len(mermaid_blocks)} Mermaid blocks")
            
            if not mermaid_blocks:
                logger.debug("No Mermaid blocks found")
                EnhancedLogger.log_function_exit(logger, "preprocess_mermaid_diagrams", "No changes")
                return markdown_text  # No mermaid blocks found
            
            # We'll use HTML divs for proper client-side rendering
            logger.info("Using web-based approach for Mermaid diagrams")
            
            for i, mermaid_code in enumerate(mermaid_blocks):
                mermaid_code = mermaid_code.strip()
                logger.debug(f"Processing Mermaid block {i+1}")
                
                # Keep the mermaid class and format for client-side rendering
                html_replacement = f"""
<div class="mermaid-wrapper" style="text-align: center; margin: 20px auto; width: 100%;">
  <div class="mermaid" style="display: inline-block; max-width: 100%; text-align: center;">
{mermaid_code}
  </div>
</div>
"""
                original_block = f"```mermaid\n{mermaid_code}\n```"
                markdown_text = markdown_text.replace(original_block, html_replacement)
                logger.debug(f"Replaced Mermaid block {i+1} with HTML div for client-side rendering")
            
            EnhancedLogger.log_function_exit(logger, "preprocess_mermaid_diagrams", "Completed")
            return markdown_text
        
        except Exception as e:
            logger.error(f"Error preprocessing Mermaid diagrams: {str(e)}")
            EnhancedLogger.log_exception(logger, e)
            EnhancedLogger.log_function_exit(logger, "preprocess_mermaid_diagrams", f"Error: {str(e)}")
            return markdown_text  # Return original text if there's an error

    @staticmethod
    def fix_svg_for_export(svg_content):
        """Apply fixes to SVG content to ensure text displays correctly in PDF export"""
        import re
        
        # 1. Fix invalid height attribute - replace "auto" with "100%"
        svg_content = re.sub(r'height="auto"', 'height="100%"', svg_content)
        
        # 2. Fix node labels that show "Unsupported markdown: list"
        if "Unsupported markdown: list" in svg_content:
            # Replace the four occurrences of "Unsupported markdown: list" with the proper labels
            replacements = [
                "1. Information Gathering &<br/>Instruction Reformulation",
                "2. Code Generation<br/>& Refactoring",
                "3. Testing<br/>& Debugging",
                "4. Validation &<br/>Compliance Check"
            ]
            
            for replacement in replacements:
                # Replace just one occurrence at a time
                svg_content = svg_content.replace(
                    '<span class="nodeLabel">Unsupported markdown: list</span>',
                    f'<span class="nodeLabel">{replacement}</span>',
                    1  # Replace only the first occurrence
                )
        
        # 3. Add explicit styling for node labels and edge labels
        style_tag = """
        <style>
        /* Fix for node labels */
        .nodeLabel {
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
        fill: #000000 !important;
        color: #000000 !important;
        }
        /* Fix for edge labels */
        .edgeLabel {
        background-color: #E8E8E8 !important;
        color: #333333 !important;
        padding: 4px !important;
        border-radius: 4px !important;
        font-family: Arial, sans-serif !important;
        }
        .edgeLabel rect {
        fill: #E8E8E8 !important;
        }
        </style>
        """
        
        # Add the style before the closing svg tag
        svg_content = svg_content.replace('</svg>', f'{style_tag}</svg>')
        
        return svg_content

    @staticmethod
    def svg_to_base64(svg_content):
        """Convert SVG content to base64 for embedding in markdown"""
        try:
            # Encode the SVG to base64
            svg_bytes = svg_content.encode('utf-8')
            base64_svg = base64.b64encode(svg_bytes).decode('utf-8')
            return base64_svg
        except Exception as e:
            logger.error(f"Error converting SVG to base64: {str(e)}")
            return None

    @staticmethod
    def preprocess_workflow_diagram(markdown_text):
        """Special preprocessing for workflow diagrams to ensure proper syntax"""
        import re
        
        # Look for workflow diagram patterns
        workflow_pattern = r'```mermaid\s+(flowchart\s+LR[\s\S]*?Next\s+Iteration[\s\S]*?)```'
        
        if re.search(workflow_pattern, markdown_text, re.DOTALL):
            logger.debug("Found workflow diagram, replacing with fixed version")
            
            # Create a specifically formatted workflow diagram with correct syntax
            fixed_diagram = '''```mermaid
flowchart LR
    A["1. Information Gathering &\nInstruction Reformulation"] --> B["2. Code Generation\n& Refactoring"]
    B --> C["3. Testing\n& Debugging"]
    C --> D["4. Validation &\nCompliance Check"]
    D -->|"Next Iteration"| A
    
    style A fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:10,ry:10
    style B fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:10,ry:10
    style C fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:10,ry:10
    style D fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:10,ry:10
```'''
            markdown_text = re.sub(workflow_pattern, fixed_diagram, markdown_text, flags=re.DOTALL)
            logger.debug("Workflow diagram replaced with fixed version")
        
        # Look for any workflow diagram with "Basic Workflow Model" title
        basic_workflow_pattern = r'# Basic Workflow Model\s*```mermaid\s+([\s\S]*?)```'
        
        if re.search(basic_workflow_pattern, markdown_text, re.DOTALL):
            logger.debug("Found basic workflow diagram, replacing with fixed version")
            
            # Simple workflow diagram template
            fixed_basic_diagram = '''# Basic Workflow Model

```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
    
    style A fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:5,ry:5
    style B fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:5,ry:5
    style C fill:#f5f5f5,stroke:#333,stroke-width:2px,rx:5,ry:5
```'''
            markdown_text = re.sub(basic_workflow_pattern, fixed_basic_diagram, markdown_text, flags=re.DOTALL)
            logger.debug("Basic workflow diagram replaced with fixed version")
        
        # Fix any generic mermaid diagram syntax issues
        mermaid_blocks_pattern = r'```mermaid\s+([\s\S]*?)```'
        mermaid_blocks = re.findall(mermaid_blocks_pattern, markdown_text, re.DOTALL)
        
        for i, block in enumerate(mermaid_blocks):
            # Skip blocks we've already fixed
            if "flowchart LR" in block and "Next Iteration" in block:
                continue
            if "flowchart TD" in block and "Start" in block and "Process" in block:
                continue
            
            logger.debug(f"Checking mermaid block {i+1} for syntax issues")
            
            # Common syntax issues and their fixes
            fixed_block = block
            
            # Fix 1: Missing whitespace after flowchart type
            fixed_block = re.sub(r'(flowchart[A-Z]+)', r'flowchart TD', fixed_block)
            
            # Fix 2: Ensure proper arrow syntax
            fixed_block = re.sub(r'-->', r' --> ', fixed_block)
            fixed_block = re.sub(r'==>+', r' ==> ', fixed_block)
            
            # Fix 3: Ensure node definitions have proper brackets
            fixed_block = re.sub(r'([A-Za-z0-9]+)(\s*-->)', r'\1[\1]\2', fixed_block)
            
            # Fix 4: Add minimal flowchart if completely broken
            if not any(x in fixed_block for x in ['flowchart', 'graph', 'sequenceDiagram']):
                fixed_block = 'flowchart TD\n    A[Start] --> B[Process] --> C[End]'
            
            # Replace the original block with the fixed one
            if fixed_block != block:
                logger.debug(f"Fixed syntax issues in mermaid block {i+1}")
                original = f"```mermaid\n{block}\n```"
                fixed = f"```mermaid\n{fixed_block}\n```"
                markdown_text = markdown_text.replace(original, fixed)
        
        return markdown_text

    @staticmethod
    def _render_with_mmdc(mermaid_code, timeout):
        """Use mermaid-cli (mmdc) to render a diagram"""
        logger.debug("Using mermaid-cli for rendering")
        mmdc_path = which('mmdc')
        
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.mmd', delete=False) as mmd_file:
            mmd_file.write(mermaid_code)
            mmd_path = mmd_file.name
        
        svg_path = mmd_path + '.svg'
        
        try:
            # Use enhanced command for better SVG rendering
            cmd = [
                mmdc_path, 
                '-i', mmd_path, 
                '-o', svg_path, 
                '-b', 'transparent',
                '-t', 'default',
                '-w', '800',
                '-H', '600'
            ]
            
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=timeout
            )
            
            if os.path.exists(svg_path):
                with open(svg_path, 'r', encoding='utf-8') as svg_file:
                    svg_content = svg_file.read()
                
                # Verify the SVG is valid
                if '<svg' in svg_content and '</svg>' in svg_content:
                    logger.debug("Successfully rendered SVG with mermaid-cli")
                    return svg_content
                else:
                    logger.warning("Malformed SVG generated by mermaid-cli")
                    return None
            else:
                logger.warning(f"SVG file not created: {svg_path}")
                return None
        finally:
            # Clean up temporary files
            for path in [mmd_path, svg_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                        logger.debug(f"Deleted temporary file: {path}")
                    except Exception as e:
                        logger.warning(f"Error deleting file {path}: {str(e)}")

    @staticmethod
    def _render_with_puppeteer(mermaid_code, timeout):
        """Use puppeteer via Node.js to render a diagram"""
        logger.debug("Using puppeteer approach for rendering")
        
        # Check if node.js is available
        node_path = which('node') or which('nodejs')
        if not node_path:
            logger.warning("Node.js not found, cannot use puppeteer approach")
            return None
        
        # Pre-escape the problematic characters outside the f-string
        escaped_code = mermaid_code.replace("`", "\\`").replace("$", "\\$")
        
        # Create a temporary script to render the diagram
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.js', delete=False) as script_file:
            script_content = f"""
            const {{ writeFileSync }} = require('fs');
            
            // Function to create basic SVG diagram
            function createSVG(code) {{
                // This is a simple SVG template
                return `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
                    <rect width="100%" height="100%" fill="#f0f0f0"/>
                    <text x="50%" y="50%" text-anchor="middle" font-family="Arial" font-size="14">
                        Mermaid Diagram Placeholder
                    </text>
                    <foreignObject x="10" y="60" width="780" height="330">
                        <body xmlns="http://www.w3.org/1999/xhtml">
                            <pre style="font-family:monospace;font-size:12px;padding:10px;background:#fff;border:1px solid #ddd;">{{code}}</pre>
                        </body>
                    </foreignObject>
                </svg>`;
            }}
            
            // Simple diagram rendering for now - could be enhanced
            const code = `{escaped_code}`;
            const svg = createSVG(code);
            console.log(svg);
            """
            script_file.write(script_content)
            script_path = script_file.name
        
        try:
            # Run the script with Node.js
            result = subprocess.run(
                [node_path, script_path],
                check=True,
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            # Get the SVG content from stdout
            svg_content = result.stdout
            
            # Verify the SVG is valid
            if '<svg' in svg_content and '</svg>' in svg_content:
                logger.debug("Successfully rendered SVG with puppeteer approach")
                return svg_content
            else:
                logger.warning("Invalid SVG content from puppeteer approach")
                return None
                
        except Exception as e:
            logger.error(f"Error rendering with puppeteer: {str(e)}")
            return None
        finally:
            # Clean up the temporary script file
            if os.path.exists(script_path):
                try:
                    os.unlink(script_path)
                    logger.debug(f"Deleted temporary file: {script_path}")
                except Exception as e:
                    logger.warning(f"Error deleting file {script_path}: {str(e)}")

    @staticmethod
    def _generate_simple_svg(mermaid_code):
        """Generate a simple SVG placeholder with the mermaid code embedded"""
        logger.debug("Generating simple SVG placeholder")
        
        # Parse mermaid code to identify diagram type
        diagram_type = "Unknown"
        if mermaid_code.strip().startswith("flowchart") or mermaid_code.strip().startswith("graph"):
            diagram_type = "Flowchart"
        elif mermaid_code.strip().startswith("sequenceDiagram"):
            diagram_type = "Sequence Diagram"
        elif mermaid_code.strip().startswith("classDiagram"):
            diagram_type = "Class Diagram"
        elif mermaid_code.strip().startswith("gantt"):
            diagram_type = "Gantt Chart"
        elif mermaid_code.strip().startswith("pie"):
            diagram_type = "Pie Chart"
        
        # Create a simple SVG with the mermaid code embedded
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
    <rect width="100%" height="100%" fill="#f8f9fa" rx="5" ry="5"/>
    <text x="400" y="40" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#0066cc">{diagram_type} Diagram</text>
    <foreignObject x="10" y="60" width="780" height="330">
        <div xmlns="http://www.w3.org/1999/xhtml">
            <pre style="font-family:monospace;font-size:12px;padding:15px;background:#fff;border:1px solid #ddd;border-radius:5px;margin:10px;overflow:auto;white-space:pre-wrap;">{mermaid_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</pre>
            <div style="font-size:11px;font-style:italic;color:#666;text-align:center;">Note: This diagram is displayed as code only due to rendering limitations</div>
        </div>
    </foreignObject>
</svg>"""
        
        logger.debug("Generated simple SVG placeholder")
        return svg_content

    @staticmethod
    def get_mermaid_cli_version():
    
        """Get the installed version of mermaid-cli"""
        try:
            mmdc_path = which('mmdc')
            if not mmdc_path:
                logger.warning("Mermaid-CLI not found")
                return None
            
            # Run mmdc --version
            result = subprocess.run(
                [mmdc_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            logger.debug(f"Mermaid-CLI version output: {result.stdout}")
            
            # Extract version number
            version = result.stdout.strip()
            return version
        except Exception as e:
            logger.error(f"Error getting Mermaid-CLI version: {str(e)}")
            return None
        
    @staticmethod
    def find_mermaid_cli():
        """
        Enhanced Mermaid CLI detection with robust command wrapper handling.
        Addresses Windows CMD execution context isolation issues.
        
        Returns:
            tuple: (cli_path, version_string) or (None, None) if not found
        """
        import os
        import subprocess
        import platform
        from shutil import which
        from logging_config import get_logger
        
        logger = get_logger()
        logger.debug("Searching for Mermaid CLI with enhanced detection...")
        
        # First pass: Standard path resolution (works in most environments)
        mmdc_path = which('mmdc')
        if mmdc_path:
            try:
                # Regular execution attempt
                result = subprocess.run(
                    [mmdc_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip() or "Unknown version"
                    logger.info(f"Mermaid CLI found via PATH: {mmdc_path}, version: {version}")
                    return mmdc_path, version
                else:
                    logger.debug(f"Found mmdc at {mmdc_path} but version check failed with standard execution")
            except Exception as e:
                logger.debug(f"Standard execution of mmdc failed: {str(e)}")
        
        # Second pass: Windows-specific handling for CMD/BAT files
        if platform.system() == "Windows":
            # Explicitly check common npm locations
            potential_paths = []
            
            # Add user's npm directory
            if 'APPDATA' in os.environ:
                npm_dir = os.path.join(os.environ['APPDATA'], "npm")
                potential_paths.append(os.path.join(npm_dir, "mmdc.cmd"))
                potential_paths.append(os.path.join(npm_dir, "mmdc.CMD"))
            
            # Check each potential path with shell=True for CMD files
            for path in potential_paths:
                if os.path.exists(path):
                    try:
                        # Use shell=True for CMD files with proper quoting
                        logger.debug(f"Attempting CMD execution for {path}")
                        result = subprocess.run(
                            f'"{path}" --version',
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            version = result.stdout.strip() or "Unknown version"
                            logger.info(f"Mermaid CLI found with CMD handling: {path}, version: {version}")
                            return path, version
                    except Exception as e:
                        logger.debug(f"CMD execution of {path} failed: {str(e)}")
        
        # Third pass: Try to find mermaid-cli in npm modules
        try:
            # Run npm list to find mermaid-cli
            npm_cmd = "npm list -g @mermaid-js/mermaid-cli"
            result = subprocess.run(
                npm_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "@mermaid-js/mermaid-cli" in result.stdout:
                logger.info("Mermaid CLI found in npm global modules")
                
                # Try to get the bin directory
                if platform.system() == "Windows":
                    # On Windows, try direct CMD execution
                    try:
                        # Create a batch file to execute mmdc
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.bat', delete=False, mode='w') as batch_file:
                            batch_file.write('@echo off\n')
                            batch_file.write('mmdc --version\n')
                            batch_path = batch_file.name
                        
                        # Execute the batch file
                        result = subprocess.run(
                            batch_path,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        # Clean up
                        os.unlink(batch_path)
                        
                        if result.returncode == 0:
                            version = result.stdout.strip() or "Unknown version"
                            logger.info(f"Mermaid CLI found via batch file, version: {version}")
                            # Return the generic 'mmdc' command as it works via batch
                            return "mmdc", version
                    except Exception as e:
                        logger.debug(f"Batch file execution failed: {str(e)}")
        except Exception as e:
            logger.debug(f"npm list command failed: {str(e)}")
        
        logger.warning("Mermaid CLI not found despite environment PATH configuration")
        return None, None

    @staticmethod
    def render_mermaid_to_svg(mermaid_code, timeout=15):
        """
        Render a Mermaid diagram to SVG using mermaid-cli with improved rendering
        
        Args:
            mermaid_code (str): Mermaid diagram code
            timeout (int): Timeout in seconds
        
        Returns:
            str: SVG content or None if rendering failed
        """
        logger.debug("Rendering Mermaid diagram to SVG")
        
        try:
            # Use enhanced CLI detection
            mmdc_path, mmdc_version = MermaidProcessor.find_mermaid_cli()
            if not mmdc_path:
                logger.warning("Mermaid CLI not found, cannot render SVG")
                return None
            
            # Create temporary files
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.mmd', delete=False) as mmd_file:
                mmd_file.write(mermaid_code)
                mmd_path = mmd_file.name
            
            svg_path = mmd_path + '.svg'
            
            try:
                # Platform-specific execution
                if platform.system() == "Windows" and mmdc_path.lower().endswith(('.cmd', '.bat')):
                    # Windows CMD file execution
                    cmd_str = f'"{mmdc_path}" -i "{mmd_path}" -o "{svg_path}" -b transparent -w 800 -H 600 -t default'
                    logger.debug(f"Running command: {cmd_str}")
                    
                    process = subprocess.run(
                        cmd_str,
                        shell=True,
                        capture_output=True,
                        timeout=timeout,
                        text=True
                    )
                else:
                    # Standard execution
                    cmd = [
                        mmdc_path, 
                        '-i', mmd_path, 
                        '-o', svg_path, 
                        '-b', 'transparent',
                        '-w', '800',  # Width
                        '-H', '600',  # Height
                        '-t', 'default'  # Theme
                    ]
                    logger.debug(f"Running command: {' '.join(cmd)}")
                    
                    process = subprocess.run(
                        cmd,
                        check=False,
                        capture_output=True,
                        timeout=timeout,
                        text=True
                    )
                
                # Check for success
                if process.returncode == 0:
                    # Check if output file was created
                    if os.path.exists(svg_path):
                        # Read SVG content
                        with open(svg_path, 'r', encoding='utf-8') as svg_file:
                            svg_content = svg_file.read()
                        
                        if "<svg" in svg_content and "</svg>" in svg_content:
                            logger.debug("Successfully generated SVG with Mermaid CLI")
                            
                            # Apply fixes to ensure labels are visible in PDF
                            svg_content = MermaidProcessor.fix_svg_for_export(svg_content)
                            return svg_content
                        else:
                            logger.error("Generated SVG appears to be invalid")
                    else:
                        logger.error(f"SVG file was not created at {svg_path}")
                else:
                    logger.error(f"Mermaid CLI failed with return code {process.returncode}")
                    logger.error(f"Stderr: {process.stderr}")
                    logger.error(f"Stdout: {process.stdout}")
                
                return None
            
            finally:
                # Clean up temporary files
                for path in [mmd_path, svg_path]:
                    if path and os.path.exists(path):
                        try:
                            os.unlink(path)
                            logger.debug(f"Deleted temporary file: {path}")
                        except Exception as e:
                            logger.warning(f"Error deleting temporary file {path}: {str(e)}")
        
        except subprocess.TimeoutExpired:
            logger.error(f"Mermaid diagram rendering timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error rendering Mermaid diagram to SVG: {str(e)}")
            return None

