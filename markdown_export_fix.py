#!/usr/bin/env python3
"""
Fixed Export Functions
---------------------
Streamlined export functions to handle PDF, HTML, and DOCX exports
with support for wkhtmltopdf, WeasyPrint, and LaTeX engines.
File: src--markdown_export_fix.py
"""

from logging_config import get_logger

logger = get_logger()

def arrange_engines_for_export(found_engines, preferred_engine):
    """Arrange engines in order of preference for export attempts"""
    logger.debug(f"Arranging engines for export, preferred: {preferred_engine}")
    try_engines = []

    # SIMPLIFIED FIX: If a specific engine is selected, ONLY use that engine
    if preferred_engine != "Auto-select" and preferred_engine in found_engines:
        try_engines = [preferred_engine]
        logger.debug(f"Using ONLY the preferred engine: {preferred_engine}")
        return try_engines

    # Auto-select mode - only reached if no specific engine was chosen
    logger.debug("Auto-select mode: arranging engines by priority")

    # Try LaTeX engines first
    for engine in ["xelatex", "pdflatex", "lualatex"]:
        if engine in found_engines and engine not in try_engines:
            try_engines.append(engine)
            logger.debug(f"Adding LaTeX engine: {engine}")

    # Then HTML-based engines
    for engine in ["weasyprint", "wkhtmltopdf"]:
        if engine in found_engines and engine not in try_engines:
            try_engines.append(engine)
            logger.debug(f"Adding HTML engine: {engine}")

    # Then any remaining engines (except prince which is no longer supported)
    for engine in found_engines:
        if engine not in try_engines and engine != 'prince':
            try_engines.append(engine)
            logger.debug(f"Adding remaining engine: {engine}")

    if not try_engines and found_engines:
        # Use the first available engine as a last resort
        first_engine = next(iter(found_engines))
        try_engines.append(first_engine)
        logger.debug(f"No engines in preferred order found, using: {first_engine}")

    logger.debug(f"Final engine order: {', '.join(try_engines)}")
    return try_engines


def preprocess_markdown_for_engine(markdown_text, engine_type):
    """
    Preprocess markdown content based on the export engine being used
    """
    logger.debug(f"Preprocessing markdown for engine: {engine_type}")

    import re

    # Replace mermaid code blocks with a simple code block
    mermaid_pattern = r'```mermaid\s+(.*?)\s+```'
    replacement = r'```\n[Diagram code removed - mermaid diagrams not supported]\n```'
    markdown_text = re.sub(mermaid_pattern, replacement, markdown_text, flags=re.DOTALL)

    # Handle page breaks based on engine type
    if engine_type in ["xelatex", "pdflatex", "lualatex"]:
        # Process page breaks for LaTeX
        markdown_text = markdown_text.replace("<!-- PAGE_BREAK -->", "\\pagebreak")
    elif engine_type == "epub":
        # Process page breaks for EPUB
        markdown_text = markdown_text.replace("<!-- PAGE_BREAK -->",
                                           '<div style="page-break-before: always;" class="epub-page-break"></div>')
    else:
        # Process page breaks for HTML-based engines
        markdown_text = markdown_text.replace("<!-- PAGE_BREAK -->",
                                            '<div style="page-break-before: always;"></div>')

    # Process restart numbering markers
    markdown_text = process_restart_numbering(markdown_text)

    # Process custom bullet styles based on engine type
    markdown_text = process_custom_bullets(markdown_text, engine_type)

    return markdown_text


def process_restart_numbering(markdown_text):
    """
    Process restart numbering markers in markdown

    Args:
        markdown_text: The markdown text to process

    Returns:
        Processed markdown text
    """
    import re

    # Find all headings with restart numbering markers
    pattern = r'(#+)\s+<!-- RESTART_NUMBERING -->\s+(.*)'

    # Replace with a special attribute for pandoc
    processed_text = re.sub(pattern, r'\1 \2 {.reset-counter}', markdown_text)

    return processed_text


def process_custom_bullets(markdown_text, engine_type="html"):
    """
    Process custom bullet styles in markdown

    Args:
        markdown_text: The markdown text to process
        engine_type: The export engine type (default: html)

    Returns:
        Processed markdown text with appropriate bullet styling
    """
    logger.debug(f"Processing custom bullets for engine: {engine_type}")

    if engine_type in ["xelatex", "pdflatex", "lualatex"]:
        # For LaTeX engines, convert custom bullet markers to standard ones
        # This avoids Unicode issues in LaTeX
        import re

        # Replace any custom bullet markers with standard ones
        # This is a simplified approach that works with our LaTeX template
        markdown_text = re.sub(r'^(\s*)[-*+]\s+', r'\1* ', markdown_text, flags=re.MULTILINE)

        logger.debug("Standardized bullet markers for LaTeX export")
        return markdown_text
    elif engine_type == "epub":
        # For EPUB, add a wrapper div with EPUB-specific class
        markdown_text = "<div class='epub-content custom-bullets-enabled'>\n" + markdown_text + "\n</div>"
        logger.debug("Added EPUB-specific custom bullets wrapper to markdown")
        return markdown_text
    else:
        # For HTML-based engines, add a wrapper div for CSS styling
        markdown_text = "<div class='custom-bullets-enabled'>\n" + markdown_text + "\n</div>"
        logger.debug("Added custom bullets wrapper to markdown")
        return markdown_text

def update_pandoc_command_for_engine(engine, cmd):
    """Add engine-specific options to pandoc command with proper formatting"""
    logger.debug(f"Updating pandoc command for engine: {engine}")

    if engine == "weasyprint":
        # No special options needed for weasyprint
        logger.debug("No special options needed for WeasyPrint")
        return cmd
    elif engine == "wkhtmltopdf":
        # Fix for wkhtmltopdf parameters - must use separate arguments
        logger.debug("Adding wkhtmltopdf-specific options")

        # Remove any problematic options first
        cmd_filtered = [arg for arg in cmd if '--pdf-engine-opt=--javascript-delay' not in arg]

        # Add critical options to prevent freezing
        cmd_filtered.append('--pdf-engine-opt=--enable-local-file-access')
        cmd_filtered.append('--pdf-engine-opt=--enable-javascript')

        # Use a shorter JavaScript delay (5 seconds) to avoid hanging
        cmd_filtered.append('--pdf-engine-opt=--javascript-delay')
        cmd_filtered.append('--pdf-engine-opt=5000')

        # Set a page load timeout
        cmd_filtered.append('--pdf-engine-opt=--page-load-timeout')
        cmd_filtered.append('--pdf-engine-opt=10000')  # 10 seconds

        # Set a strict timeout for the entire process
        cmd_filtered.append('--pdf-engine-opt=--timeout')
        cmd_filtered.append('--pdf-engine-opt=30000')  # 30 seconds

        # Critical options to prevent freezing
        cmd_filtered.append('--pdf-engine-opt=--no-stop-slow-scripts')

        # Add options to help prevent hanging
        cmd_filtered.append('--pdf-engine-opt=--load-error-handling')
        cmd_filtered.append('--pdf-engine-opt=ignore')

        # Add options to limit resource usage
        cmd_filtered.append('--pdf-engine-opt=--load-media-error-handling')
        cmd_filtered.append('--pdf-engine-opt=ignore')

        # Disable network access to prevent hanging on external resources
        cmd_filtered.append('--pdf-engine-opt=--disable-external-links')

        # Disable plugins which can cause hanging
        cmd_filtered.append('--pdf-engine-opt=--disable-plugins')

        # Disable Java which can cause hanging
        cmd_filtered.append('--pdf-engine-opt=--disable-java')

        # Disable smart shrinking which can cause issues
        cmd_filtered.append('--pdf-engine-opt=--disable-smart-shrinking')

        # Use low quality to speed up rendering
        cmd_filtered.append('--pdf-engine-opt=--image-quality')
        cmd_filtered.append('--pdf-engine-opt=50')  # 50% quality

        return cmd_filtered
    elif engine in ["xelatex", "pdflatex", "lualatex"]:
        # Add LaTeX-specific options
        logger.debug(f"Adding {engine}-specific options")

        # Ensure we have options for proper unicode handling in LaTeX
        if engine == "xelatex":
            # Add specific options for XeLaTeX if needed
            # For example, to handle unicode better
            cmd.append('--variable=mainfont:DejaVu Serif')
            cmd.append('--variable=sansfont:DejaVu Sans')
            cmd.append('--variable=monofont:DejaVu Sans Mono')
            # Add an extra option to help with diagrams
            cmd.append('--variable=graphics:true')
        elif engine == "pdflatex":
            # Add specific options for pdflatex if needed
            cmd.append('--variable=fontenc:T1')
            cmd.append('--variable=inputenc:utf8')
            # Add package for image handling
            cmd.append('--variable=graphicx:true')
        elif engine == "lualatex":
            # Add specific options for LuaLaTeX
            cmd.append('--variable=mainfont:DejaVu Serif')
            cmd.append('--variable=sansfont:DejaVu Sans')
            cmd.append('--variable=monofont:DejaVu Sans Mono')
            cmd.append('--variable=graphics:true')

        return cmd

    return cmd