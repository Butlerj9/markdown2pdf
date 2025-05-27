#!/usr/bin/env python3
"""
Markdown Export Fix
------------------
This module provides functions to fix issues with exporting markdown to various formats.
"""

import os
import sys
import logging

# Get the logger
logger = logging.getLogger(__name__)

def arrange_engines_for_export(found_engines, preferred_engine):
    """
    Arrange engines based on preference and reliability
    
    Args:
        found_engines: Dictionary of found engines
        preferred_engine: Preferred engine name
        
    Returns:
        List of engines to try in order
    """
    # Start with the preferred engine if available
    try_engines = []
    
    # Add the preferred engine first if it exists
    if preferred_engine in found_engines:
        try_engines.append(preferred_engine)
    
    # Add other engines in order of reliability
    for engine in ['xelatex', 'pdflatex', 'lualatex', 'wkhtmltopdf', 'weasyprint']:
        if engine in found_engines and engine != preferred_engine:
            try_engines.append(engine)
    
    # If no engines were found, add a placeholder
    if not try_engines:
        try_engines.append('auto')
    
    logger.info(f"Arranged engines for export: {try_engines}")
    return try_engines

def preprocess_markdown_for_engine(markdown_text, engine_type):
    """
    Preprocess markdown based on export engine
    
    Args:
        markdown_text: Markdown text to preprocess
        engine_type: Engine type (xelatex, pdflatex, etc.)
        
    Returns:
        Preprocessed markdown text
    """
    # Make a copy of the markdown text
    processed_text = markdown_text
    
    # Process based on engine type
    if engine_type in ['xelatex', 'pdflatex', 'lualatex']:
        # LaTeX-specific preprocessing
        processed_text = preprocess_for_latex(processed_text)
    elif engine_type == 'wkhtmltopdf':
        # wkhtmltopdf-specific preprocessing
        processed_text = preprocess_for_wkhtmltopdf(processed_text)
    elif engine_type == 'weasyprint':
        # WeasyPrint-specific preprocessing
        processed_text = preprocess_for_weasyprint(processed_text)
    elif engine_type == 'docx':
        # DOCX-specific preprocessing
        processed_text = preprocess_for_docx(processed_text)
    elif engine_type == 'epub':
        # EPUB-specific preprocessing
        processed_text = preprocess_for_epub(processed_text)
    elif engine_type == 'html':
        # HTML-specific preprocessing
        processed_text = preprocess_for_html(processed_text)
    
    logger.info(f"Preprocessed markdown for {engine_type}")
    return processed_text

def preprocess_for_latex(markdown_text):
    """Preprocess markdown for LaTeX engines"""
    # No special preprocessing needed for now
    return markdown_text

def preprocess_for_wkhtmltopdf(markdown_text):
    """Preprocess markdown for wkhtmltopdf"""
    # No special preprocessing needed for now
    return markdown_text

def preprocess_for_weasyprint(markdown_text):
    """Preprocess markdown for WeasyPrint"""
    # No special preprocessing needed for now
    return markdown_text

def preprocess_for_docx(markdown_text):
    """Preprocess markdown for DOCX export"""
    # No special preprocessing needed for now
    return markdown_text

def preprocess_for_epub(markdown_text):
    """Preprocess markdown for EPUB export"""
    # No special preprocessing needed for now
    return markdown_text

def preprocess_for_html(markdown_text):
    """Preprocess markdown for HTML export"""
    # No special preprocessing needed for now
    return markdown_text

def update_pandoc_command_for_engine(engine, cmd):
    """
    Update pandoc command based on engine
    
    Args:
        engine: Engine name
        cmd: Current pandoc command
        
    Returns:
        Updated pandoc command
    """
    # Add engine-specific options
    if engine == 'xelatex':
        if '--pdf-engine=xelatex' not in cmd:
            cmd.append('--pdf-engine=xelatex')
    elif engine == 'pdflatex':
        if '--pdf-engine=pdflatex' not in cmd:
            cmd.append('--pdf-engine=pdflatex')
    elif engine == 'lualatex':
        if '--pdf-engine=lualatex' not in cmd:
            cmd.append('--pdf-engine=lualatex')
    elif engine == 'wkhtmltopdf':
        if '--pdf-engine=wkhtmltopdf' not in cmd:
            cmd.append('--pdf-engine=wkhtmltopdf')
    elif engine == 'weasyprint':
        if '--pdf-engine=weasyprint' not in cmd:
            cmd.append('--pdf-engine=weasyprint')
    
    logger.info(f"Updated pandoc command for {engine}: {cmd}")
    return cmd
