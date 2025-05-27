#!/usr/bin/env python3
"""
MDZ Renderer
-----------
This module provides enhanced Markdown rendering capabilities for .mdz files,
supporting GitHub Flavored Markdown, YAML front matter, Mermaid diagrams,
SVG embedding, and LaTeX math.

File: mdz_renderer.py
"""

import os
import re
import json
import tempfile
import logging
import yaml
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

class MDZRenderer:
    """
    Enhanced Markdown renderer for .mdz files
    """

    def __init__(self, math_engine: str = "mathjax"):
        """
        Initialize the renderer

        Args:
            math_engine: Math rendering engine ('mathjax' or 'katex')
        """
        self.math_engine = math_engine.lower()
        if self.math_engine not in ["mathjax", "katex"]:
            logger.warning(f"Unknown math engine: {math_engine}, defaulting to mathjax")
            self.math_engine = "mathjax"

        # Import required modules
        try:
            import markdown
            from markdown.extensions.tables import TableExtension
            from markdown.extensions.fenced_code import FencedCodeExtension
            from markdown.extensions.codehilite import CodeHiliteExtension
            from markdown.extensions.toc import TocExtension
            from markdown.extensions.nl2br import Nl2BrExtension

            # Store extensions for later use
            self.markdown_extensions = [
                TableExtension(),
                FencedCodeExtension(),
                CodeHiliteExtension(),
                TocExtension(permalink=True),
                Nl2BrExtension(),
                'markdown.extensions.extra',
                'markdown.extensions.smarty'
            ]

            # Try to import PyMdown extensions for GitHub-style Markdown
            try:
                import pymdownx
                self.markdown_extensions.extend([
                    'pymdownx.tasklist',
                    'pymdownx.superfences',
                    'pymdownx.highlight',
                    'pymdownx.inlinehilite',
                    'pymdownx.magiclink',
                    'pymdownx.emoji',
                    'pymdownx.smartsymbols'
                ])
                logger.debug("PyMdown extensions loaded")
            except ImportError:
                logger.warning("PyMdown extensions not found, some GitHub Flavored Markdown features may not be available")

        except ImportError as e:
            logger.error(f"Error importing Markdown libraries: {str(e)}")
            raise ImportError("Required Markdown libraries not found. Please install them with 'pip install markdown pymdown-extensions'")

    def extract_front_matter(self, markdown_content: str) -> Tuple[str, Dict]:
        """
        Extract YAML front matter from markdown content

        Args:
            markdown_content: Markdown content with potential front matter

        Returns:
            Tuple of (markdown_without_front_matter, front_matter_dict)
        """
        # Regular expression to match YAML front matter
        front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(front_matter_pattern, markdown_content, re.DOTALL)

        if match:
            front_matter_text = match.group(1)
            try:
                front_matter = yaml.safe_load(front_matter_text)
                if not isinstance(front_matter, dict):
                    front_matter = {}
            except Exception as e:
                logger.warning(f"Error parsing front matter: {str(e)}")
                front_matter = {}

            # Remove front matter from markdown
            markdown_without_front_matter = markdown_content[match.end():]
            return markdown_without_front_matter, front_matter

        # No front matter found
        return markdown_content, {}

    def preprocess_mermaid(self, markdown_content: str, mermaid_diagrams: Optional[Dict] = None) -> str:
        """
        Preprocess Markdown content to handle Mermaid diagrams

        Args:
            markdown_content: Markdown content
            mermaid_diagrams: Optional dictionary of pre-rendered Mermaid diagrams

        Returns:
            Preprocessed Markdown content
        """
        # If no pre-rendered diagrams provided, just return the original content
        if not mermaid_diagrams:
            return markdown_content

        # Find all Mermaid code blocks
        mermaid_pattern = r'```mermaid\s+(.*?)\s+```'

        def replace_mermaid(match):
            mermaid_code = match.group(1).strip()

            # Check if we have a pre-rendered diagram for this code
            if mermaid_code in mermaid_diagrams:
                # Replace with the pre-rendered SVG
                svg_content = mermaid_diagrams[mermaid_code]
                return f'<div class="mermaid-diagram">{svg_content}</div>'

            # Keep the original code block if no pre-rendered diagram is available
            return match.group(0)

        # Replace Mermaid code blocks with pre-rendered SVGs
        processed_content = re.sub(mermaid_pattern, replace_mermaid, markdown_content, flags=re.DOTALL)

        return processed_content

    def preprocess_math(self, markdown_content: str) -> str:
        """
        Preprocess Markdown content to handle math expressions

        Args:
            markdown_content: Markdown content

        Returns:
            Preprocessed Markdown content
        """
        # Ensure math delimiters are properly handled

        # Inline math: $...$
        markdown_content = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)',
                                 r'\\\\(\1\\\\)',
                                 markdown_content)

        # Display math: $$...$$
        markdown_content = re.sub(r'\$\$(.*?)\$\$',
                                 r'\\\\[\1\\\\]',
                                 markdown_content)

        return markdown_content

    def preprocess_image_paths(self, markdown_content: str, asset_paths: Optional[Dict] = None) -> str:
        """
        Preprocess Markdown content to handle image paths with enhanced asset resolution

        Args:
            markdown_content: Markdown content
            asset_paths: Optional dictionary mapping internal paths to actual file paths

        Returns:
            Preprocessed Markdown content
        """
        # If no asset paths provided, just return the original content
        if not asset_paths:
            return markdown_content

        # Find all image references
        image_pattern = r'!\[(.*?)\]\((.*?)\)'

        def replace_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # Skip URLs
            if image_path.startswith(('http://', 'https://')):
                return match.group(0)

            # Check if we have a mapping for this image path
            for internal_path, actual_path in asset_paths.items():
                # Try different matching strategies
                if (internal_path.endswith(image_path) or 
                    image_path.endswith(internal_path) or
                    os.path.basename(internal_path) == os.path.basename(image_path)):
                    # Replace with the actual path
                    return f'![{alt_text}]({actual_path})'
                
                # Try to match by directory structure
                if 'images/' in internal_path and os.path.basename(internal_path) == os.path.basename(image_path):
                    return f'![{alt_text}]({actual_path})'

            # If no exact match found, try to find a match by filename only
            image_filename = os.path.basename(image_path)
            for internal_path, actual_path in asset_paths.items():
                if os.path.basename(internal_path) == image_filename:
                    return f'![{alt_text}]({actual_path})'

            # Keep the original path if no mapping is found
            logger.warning(f"No asset mapping found for image: {image_path}")
            return match.group(0)

        # Replace image paths
        processed_content = re.sub(image_pattern, replace_image_path, markdown_content)

        return processed_content

    def render_to_html(self, markdown_content: str,
                      front_matter: Optional[Dict] = None,
                      mermaid_diagrams: Optional[Dict] = None,
                      asset_paths: Optional[Dict] = None,
                      toc: bool = False,
                      numbering: bool = False,
                      theme: str = "default") -> str:
        """
        Render Markdown content to HTML

        Args:
            markdown_content: Markdown content
            front_matter: Optional front matter dictionary
            mermaid_diagrams: Optional dictionary of pre-rendered Mermaid diagrams
            asset_paths: Optional dictionary mapping internal paths to actual file paths
            toc: Whether to include a table of contents
            numbering: Whether to enable section numbering
            theme: Theme for the output ('default', 'light', or 'dark')

        Returns:
            HTML content
        """
        import markdown

        # Preprocess the content
        processed_content = self.preprocess_mermaid(markdown_content, mermaid_diagrams)
        processed_content = self.preprocess_math(processed_content)
        processed_content = self.preprocess_image_paths(processed_content, asset_paths)

        # Add TOC marker if requested
        if toc:
            processed_content = "[TOC]\n\n" + processed_content

        # Configure extensions based on parameters
        extensions = self.markdown_extensions.copy()

        # Add TOC extension if requested
        if toc:
            extensions.append('markdown.extensions.toc')

        # Convert Markdown to HTML
        html_content = markdown.markdown(processed_content, extensions=extensions)

        # Add math rendering support
        if self.math_engine == "mathjax":
            math_script = """
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>
<script>
  window.MathJax = {
    tex: {
      inlineMath: [['\\\\(', '\\\\)']],
      displayMath: [['\\\\[', '\\\\]']],
      processEscapes: true
    }
  };
</script>
"""
        else:  # KaTeX
            math_script = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '\\\\(', right: '\\\\)', display: false},
        {left: '\\\\[', right: '\\\\]', display: true}
      ]
    });
  });
</script>
"""

        # Add Mermaid support if needed
        if mermaid_diagrams:
            mermaid_script = """
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
"""
        else:
            mermaid_script = ""

        # Create a complete HTML document
        title = front_matter.get("title", "Markdown Document") if front_matter else "Markdown Document"

        # Define theme-specific CSS
        if theme == "dark":
            theme_css = """
        body {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        pre {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        code {
            background-color: rgba(255, 255, 255, 0.1);
            color: #e0e0e0;
        }
        blockquote {
            border-left: 4px solid #444;
            color: #aaa;
        }
        table, th, td {
            border: 1px solid #444;
        }
        th {
            background-color: #2d2d2d;
        }
        a {
            color: #58a6ff;
        }
        """
        elif theme == "light":
            theme_css = """
        body {
            background-color: #ffffff;
            color: #333333;
        }
        pre {
            background-color: #f8f8f8;
            color: #333333;
        }
        code {
            background-color: rgba(0, 0, 0, 0.05);
            color: #333333;
        }
        blockquote {
            border-left: 4px solid #eee;
            color: #777;
        }
        table, th, td {
            border: 1px solid #eee;
        }
        th {
            background-color: #f8f8f8;
        }
        a {
            color: #0366d6;
        }
        """
        else:  # default theme
            theme_css = ""

        # Add numbering CSS if requested
        if numbering:
            numbering_css = """
        body {
            counter-reset: h1;
        }
        h1 {
            counter-reset: h2;
        }
        h2 {
            counter-reset: h3;
        }
        h3 {
            counter-reset: h4;
        }
        h4 {
            counter-reset: h5;
        }
        h5 {
            counter-reset: h6;
        }
        h1:before {
            counter-increment: h1;
            content: counter(h1) ". ";
        }
        h2:before {
            counter-increment: h2;
            content: counter(h1) "." counter(h2) " ";
        }
        h3:before {
            counter-increment: h3;
            content: counter(h1) "." counter(h2) "." counter(h3) " ";
        }
        h4:before {
            counter-increment: h4;
            content: counter(h1) "." counter(h2) "." counter(h3) "." counter(h4) " ";
        }
        h5:before {
            counter-increment: h5;
            content: counter(h1) "." counter(h2) "." counter(h3) "." counter(h4) "." counter(h5) " ";
        }
        h6:before {
            counter-increment: h6;
            content: counter(h1) "." counter(h2) "." counter(h3) "." counter(h4) "." counter(h5) "." counter(h6) " ";
        }
        """
        else:
            numbering_css = ""

        # Add TOC CSS if requested
        if toc:
            toc_css = """
        .toc {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 1em;
            margin-bottom: 1em;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 1em;
        }
        .toc li {
            margin: 0.5em 0;
        }
        .toc a {
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        """
        else:
            toc_css = ""

        html_document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        code {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            padding: 0.2em 0.4em;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 16px;
            color: #666;
            margin-left: 0;
        }}
        img {{
            max-width: 100%;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
        }}
        .task-list-item {{
            list-style-type: none;
        }}
        .task-list-item input {{
            margin-right: 0.5em;
        }}
        .mermaid-diagram {{
            text-align: center;
            margin: 20px 0;
        }}
        {theme_css}
        {numbering_css}
        {toc_css}
    </style>
    {math_script}
    {mermaid_script}
</head>
<body>
    {html_content}
</body>
</html>
"""

        return html_document

    def render_mermaid_to_svg(self, mermaid_code: str) -> Optional[str]:
        """
        Render a Mermaid diagram to SVG

        Args:
            mermaid_code: Mermaid diagram code

        Returns:
            SVG content or None if rendering failed
        """
        try:
            # Try to use the MermaidProcessor from the main application if available
            from mermaid_processor import MermaidProcessor
            return MermaidProcessor.render_mermaid_to_svg(mermaid_code)
        except ImportError:
            logger.warning("MermaidProcessor not found, using fallback method")

            # Fallback method using Node.js and mermaid-cli if available
            try:
                # Create a temporary file for the Mermaid code
                with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.mmd', delete=False) as mmd_file:
                    mmd_file.write(mermaid_code)
                    mmd_path = mmd_file.name

                # Output SVG path
                svg_path = mmd_path + '.svg'

                # Try to find mmdc (mermaid-cli)
                import shutil
                mmdc_path = shutil.which('mmdc')

                if not mmdc_path:
                    logger.warning("mermaid-cli not found, cannot render Mermaid diagram")
                    return None

                # Run mmdc to generate SVG
                import subprocess
                subprocess.run([
                    mmdc_path,
                    '-i', mmd_path,
                    '-o', svg_path,
                    '-b', 'transparent'
                ], check=True)

                # Read the SVG file
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()

                # Clean up temporary files
                os.unlink(mmd_path)
                os.unlink(svg_path)

                return svg_content

            except Exception as e:
                logger.error(f"Error rendering Mermaid diagram: {str(e)}")
                return None

    def extract_and_render_mermaid(self, markdown_content: str) -> Dict[str, str]:
        """
        Extract and render all Mermaid diagrams in the Markdown content

        Args:
            markdown_content: Markdown content

        Returns:
            Dictionary mapping Mermaid code to SVG content
        """
        # Find all Mermaid code blocks
        mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
        mermaid_blocks = re.findall(mermaid_pattern, markdown_content, re.DOTALL)

        # Render each Mermaid diagram
        mermaid_diagrams = {}
        for mermaid_code in mermaid_blocks:
            mermaid_code = mermaid_code.strip()
            svg_content = self.render_mermaid_to_svg(mermaid_code)
            if svg_content:
                mermaid_diagrams[mermaid_code] = svg_content

        return mermaid_diagrams


if __name__ == "__main__":
    # Example usage
    import argparse

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MDZ Renderer')
    parser.add_argument('markdown_file', help='Path to the markdown file')
    parser.add_argument('--output', '-o', help='Path to save the HTML output')
    parser.add_argument('--format', '-f', choices=['html', 'pdf', 'epub', 'docx'], default='html',
                       help='Output format (default: html)')
    parser.add_argument('--math', choices=['mathjax', 'katex'], default='mathjax',
                       help='Math rendering engine (default: mathjax)')
    parser.add_argument('--toc', action='store_true', help='Include table of contents')
    parser.add_argument('--numbering', action='store_true', help='Enable section numbering')
    parser.add_argument('--theme', choices=['default', 'light', 'dark'], default='default',
                       help='Theme for the output (default: default)')

    # Parse arguments
    args = parser.parse_args()

    # Read the markdown file
    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Create a renderer
    renderer = MDZRenderer(math_engine=args.math)

    # Extract front matter
    markdown_without_front_matter, front_matter = renderer.extract_front_matter(markdown_content)

    # Extract and render Mermaid diagrams
    mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)

    # Check if we should use front matter settings
    toc = args.toc or front_matter.get("toc", False)
    numbering = args.numbering or front_matter.get("numbering", False)
    theme = args.theme or front_matter.get("theme", "default")

    # Render to HTML
    html_content = renderer.render_to_html(
        markdown_without_front_matter,
        front_matter=front_matter,
        mermaid_diagrams=mermaid_diagrams,
        toc=toc,
        numbering=numbering,
        theme=theme
    )

    # Save or print the HTML
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved HTML output to {args.output}")
    else:
        print(html_content)
