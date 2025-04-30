#!/usr/bin/env python3
"""
Advanced Markdown to PDF Converter - Main Entry Point
----------------------------------------------------
This script launches the Markdown to PDF converter application.
File: src--main.py
"""

import sys
import os
import logging
import argparse
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from logging_config import initialize_logger, get_logger

os.environ["PATH"] += os.pathsep + r"C:\Users\joshd\AppData\Roaming\npm"

# Configure logger
logger = initialize_logger()

def check_dependencies():
    """Check for critical dependencies like Pandoc"""
    logger.info("Checking application dependencies...")

    # Check for Pandoc
    from shutil import which
    import subprocess

    pandoc_path = which('pandoc')
    if pandoc_path:
        try:
            result = subprocess.run(['pandoc', '--version'], shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            pandoc_version = result.stdout.splitlines()[0] if result.stdout else "Unknown version"
            logger.info(f"Pandoc found: {pandoc_version}")
        except Exception as e:
            logger.warning(f"Pandoc found at {pandoc_path} but version check failed: {str(e)}")
    else:
        logger.warning("Pandoc not found. PDF export functionality may be limited.")
        return False, "Pandoc not found. PDF export functionality may be limited."

    # No additional dependency checks needed

    return True, None

# Mermaid-related functions removed

def main():
    """Main entry point for the application"""
    logger.info("Starting Advanced Markdown to PDF Converter")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Advanced Markdown to PDF Converter")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no GUI)")
    parser.add_argument("--input", type=str, help="Input markdown file")
    parser.add_argument("--output", type=str, help="Output file (PDF, DOCX, HTML, etc.)")
    parser.add_argument("--document-style", type=str, help="Document style preset to use")
    parser.add_argument("--engine", type=str, help="PDF engine to use (xelatex, weasyprint, wkhtmltopdf)")
    parser.add_argument("--format", type=str, help="Output format (pdf, docx, html, epub)")
    args = parser.parse_args()

    # Check dependencies
    deps_ok, error_msg = check_dependencies()
    if not deps_ok and not args.headless:
        # Show a warning but continue anyway
        QMessageBox.warning(None, "Missing Dependencies",
                          error_msg or "Some required dependencies are missing.")

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced Markdown to PDF Converter")
    app.setOrganizationName("MarkdownToPDF")

    # Create the main window
    window = AdvancedMarkdownToPDF()

    # Handle headless mode with input/output files
    if args.headless and args.input and args.output:
        logger.info(f"Running in headless mode: {args.input} -> {args.output}")

        # Load the input file
        with open(args.input, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        # Apply document style if specified
        if args.document_style:
            window.preset_combo.setCurrentText(args.document_style)
            window.apply_style_preset(args.document_style)

        # Set engine if specified
        if args.engine and args.engine in window.found_engines:
            window.document_settings["format"]["preferred_engine"] = args.engine

        # Set the markdown text
        window.markdown_editor.setPlainText(markdown_text)

        # Determine output format
        output_format = args.format
        if not output_format and args.output:
            # Try to determine format from output file extension
            ext = os.path.splitext(args.output)[1].lower()
            if ext in ['.pdf', '.docx', '.html', '.epub']:
                output_format = ext[1:]  # Remove the dot

        # Default to PDF if no format specified
        if not output_format:
            output_format = 'pdf'

        logger.info(f"Exporting to {output_format.upper()} format")

        # Export to the specified format
        result = False
        if output_format.lower() == 'docx':
            # For DOCX, use the export_to_docx method
            result = window.export_to_docx(args.output)
        elif output_format.lower() == 'html':
            # For HTML, use the export_to_html method
            result = window.export_to_html(args.output)
        elif output_format.lower() == 'epub':
            # For EPUB, use the export_to_epub method
            result = window.export_to_epub(args.output)
        else:
            # Default to PDF for all other formats
            result = window.export_to_pdf(args.output)

        # Return appropriate exit code
        if not result:
            return 1

        # Exit the application
        return 0

    # Normal GUI mode
    if not args.headless:
        # Restore window geometry if available
        settings = QSettings("MarkdownToPDF", "AdvancedConverter")
        if settings.contains("window_geometry"):
            window.restoreGeometry(settings.value("window_geometry"))

        # Save settings before exit
        app.aboutToQuit.connect(window.save_settings)

        # Show the window
        window.show()

        # Enter the application event loop
        result = app.exec()

        # Log application exit
        logger.info(f"Application exited with code: {result}")
        return result

    return 0

if __name__ == "__main__":
    sys.exit(main())