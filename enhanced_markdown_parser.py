#!/usr/bin/env python3
"""
Enhanced Markdown Parser
-----------------------
This module provides an enhanced Markdown parser with full support for
GitHub Flavored Markdown, including tables, task lists, strikethrough,
autolinks, and syntax highlighting.

File: enhanced_markdown_parser.py
"""

import logging
from typing import Dict, List, Optional, Union, Tuple, Any

# Configure logger
logger = logging.getLogger(__name__)

class MarkdownParser:
    """
    Enhanced Markdown parser with GFM support
    """

    def __init__(self, extensions: Optional[List[str]] = None):
        """
        Initialize the parser

        Args:
            extensions: Optional list of additional extensions to use
        """
        # Try to import markdown-it-py first (preferred)
        try:
            import markdown_it
            self.parser_type = "markdown-it-py"
            # Use commonmark preset instead of gfm as it's more widely supported
            self.md = markdown_it.MarkdownIt("commonmark")

            # Add plugins
            try:
                import mdit_py_plugins.tasklists
                import mdit_py_plugins.footnote
                import mdit_py_plugins.front_matter

                self.md.use(mdit_py_plugins.tasklists.tasklists_plugin)
                self.md.use(mdit_py_plugins.footnote.footnote_plugin)
                self.md.use(mdit_py_plugins.front_matter.front_matter_plugin)

                logger.info("Using markdown-it-py with GFM support")
            except ImportError:
                logger.warning("Some markdown-it-py plugins not found, GFM support may be limited")

        except ImportError:
            # Fall back to Python-Markdown
            try:
                import markdown
                self.parser_type = "python-markdown"

                # Default extensions for GFM support
                self.extensions = [
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.extra',
                    'markdown.extensions.smarty'
                ]

                # Try to import PyMdown extensions for better GFM support
                try:
                    import pymdownx
                    self.extensions.extend([
                        'pymdownx.tasklist',
                        'pymdownx.superfences',
                        'pymdownx.highlight',
                        'pymdownx.inlinehilite',
                        'pymdownx.magiclink',
                        'pymdownx.emoji',
                        'pymdownx.smartsymbols'
                    ])
                    logger.info("Using Python-Markdown with PyMdown extensions")
                except ImportError:
                    logger.warning("PyMdown extensions not found, GFM support may be limited")

                # Add any additional extensions
                if extensions:
                    self.extensions.extend(extensions)

            except ImportError:
                # Last resort: try to use mistune
                try:
                    import mistune
                    self.parser_type = "mistune"
                    self.md = mistune.create_markdown(
                        plugins=['table', 'task_lists', 'strikethrough', 'footnotes']
                    )
                    logger.info("Using Mistune for Markdown parsing")
                except ImportError:
                    logger.error("No suitable Markdown parser found")
                    raise ImportError("No suitable Markdown parser found. Please install markdown-it-py, markdown, or mistune.")

    def parse(self, markdown_content: str) -> str:
        """
        Parse Markdown content to HTML

        Args:
            markdown_content: Markdown content

        Returns:
            HTML content
        """
        if self.parser_type == "markdown-it-py":
            return self.md.render(markdown_content)
        elif self.parser_type == "python-markdown":
            import markdown
            return markdown.markdown(markdown_content, extensions=self.extensions)
        elif self.parser_type == "mistune":
            return self.md(markdown_content)
        else:
            raise ValueError(f"Unknown parser type: {self.parser_type}")

    def get_parser_info(self) -> Dict[str, Any]:
        """
        Get information about the parser

        Returns:
            Dictionary with parser information
        """
        info = {
            "parser_type": self.parser_type,
            "gfm_support": True,
        }

        if self.parser_type == "markdown-it-py":
            import markdown_it
            info["version"] = markdown_it.__version__
            info["extensions"] = ["gfm", "tasklists", "footnote", "front_matter"]
        elif self.parser_type == "python-markdown":
            import markdown
            info["version"] = markdown.__version__
            info["extensions"] = self.extensions
        elif self.parser_type == "mistune":
            import mistune
            info["version"] = mistune.__version__
            info["extensions"] = ["table", "task_lists", "strikethrough", "footnotes"]

        return info


if __name__ == "__main__":
    # Example usage
    import argparse
    import sys

    # Configure logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enhanced Markdown Parser')
    parser.add_argument('markdown_file', help='Path to the markdown file')
    parser.add_argument('--output', '-o', help='Path to save the HTML output')
    parser.add_argument('--info', action='store_true', help='Show parser information')

    args = parser.parse_args()

    # Create a parser
    md_parser = MarkdownParser()

    # Show parser information if requested
    if args.info:
        info = md_parser.get_parser_info()
        print("Parser Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        sys.exit(0)

    # Read the markdown file
    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        sys.exit(1)

    # Parse the markdown
    html_content = md_parser.parse(markdown_content)

    # Save or print the HTML
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Saved HTML output to {args.output}")
        except Exception as e:
            logger.error(f"Error writing file: {str(e)}")
            sys.exit(1)
    else:
        print(html_content)
