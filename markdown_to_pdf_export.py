#!/usr/bin/env python3
"""
Markdown to PDF Export Functionality
----------------------------------
Contains the PDF export functionality for the Markdown to PDF Converter.
File: src--markdown_to_pdf_export.py
"""

import os
import tempfile
import subprocess
import traceback
import re
import time
from PyQt6.QtWidgets import QMessageBox, QApplication, QFileDialog
from logging_config import get_logger, EnhancedLogger
from render_utils import RenderUtils

logger = get_logger()

class MarkdownToPDFExport:
    """PDF export functionality for the Markdown to PDF Converter"""

    @staticmethod
    def export_to_pdf(self):
        """Export the current document to PDF using pandoc and the selected PDF engine with improved mermaid support"""
        logger.info("Starting PDF export process with enhanced mermaid support")

        if not self.markdown_editor.toPlainText():
            logger.warning("No content to export")
            QMessageBox.warning(self, 'Warning', 'No content to export.')
            return

        # Ask for the output file location
        default_filename = "document.pdf"
        if self.current_file:
            default_filename = os.path.splitext(os.path.basename(self.current_file))[0] + ".pdf"

        # Get start directory from saved paths
        start_dir = self.dialog_paths.get("export", "")
        logger.debug(f"Export directory path: {start_dir}")
        if not start_dir or not os.path.exists(start_dir):
            start_dir = default_filename
        else:
            start_dir = os.path.join(start_dir, default_filename)

        output_file, _ = QFileDialog.getSaveFileName(
            self, 'Export to PDF', start_dir, 'PDF Files (*.pdf);;All Files (*)'
        )
        logger.info(f"Selected output file: {output_file}")

        if not output_file:
            return

        # Add .pdf extension if not present
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'

        # Save the directory for next time
        self.dialog_paths["export"] = os.path.dirname(output_file)
        self.save_settings()

        # Show a progress dialog with cancel button
        progress = QMessageBox(QMessageBox.Icon.Information, 'Exporting', 'Exporting to PDF...')
        progress.setStandardButtons(QMessageBox.StandardButton.Cancel)
        progress.show()
        QApplication.processEvents()

        # Determine which engine(s) to use based on user's preference
        from markdown_export_fix import arrange_engines_for_export
        preferred_engine = self.document_settings.get("format", {}).get("preferred_engine", "xelatex")
        try_engines = arrange_engines_for_export(self.found_engines, preferred_engine)

        logger.debug(f"Will try these engines in order: {try_engines}")

        # Try each engine in order until one succeeds or all fail
        for engine in try_engines:
            try:
                # Update progress message
                progress.setText(f'Trying PDF engine: {engine}...')
                QApplication.processEvents()

                logger.info(f"Attempting export with engine: {engine}")

                # Use try-finally to ensure cleanup even if errors occur
                md_file = None
                css_file = None
                template_file = None
                no_numbers_file = None
                header_file = None

                try:
                    # Create temporary markdown file
                    markdown_text = self.markdown_editor.toPlainText()

                    # Pre-process the markdown based on engine with enhanced mermaid support
                    from markdown_export_fix import preprocess_markdown_for_engine
                    markdown_text = preprocess_markdown_for_engine(markdown_text, engine)

                    # Create temporary markdown file
                    with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                        md_file.write(markdown_text)
                        md_path = md_file.name

                    logger.debug(f"Created temporary markdown file: {md_path}")

                    # Create CSS file from settings
                    css_content = RenderUtils.generate_css_from_settings(self.document_settings)
                    css_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False)
                    css_file.write(css_content)
                    css_file.close()

                    logger.debug(f"Created temporary CSS file: {css_file.name}")

                    # Prepare pandoc command
                    cmd = ['pandoc', md_path, '-o', output_file, '--standalone']

                    # Add PDF engine
                    engine_path = self.found_engines.get(engine, engine)
                    cmd.append(f'--pdf-engine={engine_path}')

                    # Add engine-specific options with improved mermaid support
                    from markdown_export_fix import update_pandoc_command_for_engine
                    cmd = update_pandoc_command_for_engine(engine, cmd)

                    # Add CSS and other common options
                    cmd.append(f'--css={css_file.name}')

                    # Add template for LaTeX engines
                    use_latex = engine in ["xelatex", "pdflatex", "lualatex"]
                    if use_latex:
                        # Use the custom template from the templates directory
                        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "custom.latex")
                        logger.info(f"Using custom LaTeX template: {template_path}")

                        if os.path.exists(template_path):
                            cmd.append(f'--template={template_path}')
                        else:
                            # Fallback to generating a template if the file doesn't exist
                            logger.info("Using default pandoc template")
                            template_content = RenderUtils.generate_latex_template()
                            template_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.latex', delete=False)
                            template_file.write(template_content)
                            template_file.close()
                            cmd.append(f'--template={template_file.name}')

                    # Add enhanced header file for Mermaid support
                    if engine not in ["xelatex", "pdflatex", "lualatex"]:
                        # Only include Mermaid script for non-LaTeX engines with improved initialization
                        header_content = """
                        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                        <script>
                        (function() {
                            var attempts = 0;
                            var maxAttempts = 20;

                            function initMermaid() {
                                attempts++;
                                try {
                                    if (typeof mermaid !== 'undefined') {
                                        console.log("Mermaid found, initializing...");

                                        mermaid.initialize({
                                            startOnLoad: true,
                                            theme: 'default',
                                            securityLevel: 'loose',
                                            flowchart: {
                                                useMaxWidth: false,
                                                htmlLabels: true,
                                                curve: 'basis',
                                                padding: 15
                                            },
                                            fontFamily: 'Arial, sans-serif',
                                            fontSize: 14
                                        });

                                        var diagrams = document.querySelectorAll('.mermaid');
                                        console.log("Found " + diagrams.length + " Mermaid diagrams");

                                        if (diagrams.length > 0) {
                                            console.log("Initializing Mermaid diagrams");
                                            mermaid.init(undefined, diagrams);
                                            console.log("Mermaid initialization complete");
                                        }
                                    } else if (attempts < maxAttempts) {
                                        console.log("Mermaid not found yet, retrying in 1 second (attempt " + attempts + " of " + maxAttempts + ")");
                                        setTimeout(initMermaid, 1000);
                                    } else {
                                        console.error("Failed to initialize Mermaid after " + maxAttempts + " attempts");
                                    }
                                } catch(e) {
                                    console.error("Error initializing Mermaid:", e);
                                    if (attempts < maxAttempts) {
                                        console.log("Error occurred, retrying in 1 second (attempt " + attempts + " of " + maxAttempts + ")");
                                        setTimeout(initMermaid, 1000);
                                    }
                                }
                            }

                            // Wait for document to fully load
                            window.addEventListener('load', function() {
                                // Give a bit more time for everything to settle
                                setTimeout(initMermaid, 2000);
                            });

                            // Also try immediate initialization
                            setTimeout(initMermaid, 500);
                        })();
                        </script>
                        <style>
                        /* Enhanced styling for edge labels in mermaid diagrams */
                        .edgeLabel {
                            background-color: #E8E8E8 !important;
                            color: #333333 !important;
                            padding: 2px !important;
                            border-radius: 4px !important;
                            font-family: Arial, sans-serif !important;
                        }
                        .edgeLabel rect {
                            fill: #E8E8E8 !important;
                            rx: 4px !important;
                            ry: 4px !important;
                        }
                        .mermaid-fallback {
                            border: 1px solid #ddd;
                            padding: 15px;
                            margin: 20px 0;
                            border-radius: 5px;
                            background-color: #f8f9fa;
                        }
                        </style>
                        """
                        header_file = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.html', delete=False)
                        header_file.write(header_content)
                        header_file.close()
                        cmd.extend(['--include-in-header', header_file.name])

                    # Add TOC if needed
                    if self.document_settings.get("toc", {}).get("include", False):
                        cmd.append('--toc')
                        cmd.append(f'--toc-depth={self.document_settings.get("toc", {}).get("depth", 3)}')
                        cmd.append('-V')
                        cmd.append(f'toc-title={self.document_settings.get("toc", {}).get("title", "Table of Contents")}')

                    # Add technical numbering options
                    if not self.document_settings.get("format", {}).get("technical_numbering", False):
                        cmd.extend(['--variable', 'secnumdepth=-2'])
                        cmd.extend(['--variable', 'disable-numbering=true'])
                    else:
                        cmd.append('--number-sections')

                    # Add common variables
                    page_settings = self.document_settings.get("page", {})
                    page_size = page_settings.get("size", "A4").lower()
                    margins = page_settings.get("margins", {"top": 25.4, "right": 25.4, "bottom": 25.4, "left": 25.4})

                    cmd.extend([
                        '-V', f'papersize={page_size}',
                        '-V', f'margin-top={margins.get("top", 25.4)}mm',
                        '-V', f'margin-right={margins.get("right", 25.4)}mm',
                        '-V', f'margin-bottom={margins.get("bottom", 25.4)}mm',
                        '-V', f'margin-left={margins.get("left", 25.4)}mm'
                    ])

                    # Add mathjax for math support
                    cmd.append('--mathjax')

                    # Log the command
                    logger.info(f"Running pandoc command: {' '.join(cmd)}")

                    # Run the command with increased timeout for complex mermaid diagrams
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=300  # 5 minute timeout (increased)
                    )

                    # Check if export was successful
                    if result.returncode == 0:
                        # Success!
                        logger.info(f"PDF export successful with engine: {engine}")
                        progress.close()
                        QMessageBox.information(
                            self, 'Export Successful',
                            f'Document exported successfully to:\n{output_file}'
                        )
                        return True
                    else:
                        # This engine failed, log error and exit if it's the only engine we're trying
                        logger.warning(f"Engine {engine} failed: {result.stderr}")

                        # If only trying one engine or this was the last one, show error to user
                        if len(try_engines) == 1 or engine == try_engines[-1]:
                            progress.close()
                            QMessageBox.critical(
                                self, 'Export Error',
                                f'Error exporting to PDF with {engine}:\n{result.stderr}'
                            )
                            return False

                        # Otherwise, continue to the next engine

                except Exception as e:
                    # Error with this engine, log and exit if it's the only one we're trying
                    logger.error(f"Exception with engine {engine}: {str(e)}")

                    # If only trying one engine or this was the last one, show error to user
                    if len(try_engines) == 1 or engine == try_engines[-1]:
                        progress.close()
                        QMessageBox.critical(
                            self, 'Export Error',
                            f'Error exporting to PDF with {engine}:\n{str(e)}'
                        )
                        return False

                    # Otherwise, continue to the next engine

                finally:
                    # Clean up temporary files
                    for file_path in [
                        getattr(md_file, 'name', None),
                        getattr(css_file, 'name', None),
                        getattr(template_file, 'name', None),
                        getattr(no_numbers_file, 'name', None),
                        getattr(header_file, 'name', None)
                    ]:
                        if file_path and os.path.exists(file_path):
                            try:
                                os.unlink(file_path)
                                logger.debug(f"Deleted temporary file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Error cleaning up temp file {file_path}: {e}")

            except Exception as e:
                logger.error(f"Serious error with engine {engine}: {str(e)}")

                # If only trying one engine or this was the last one, show error to user
                if len(try_engines) == 1 or engine == try_engines[-1]:
                    progress.close()
                    QMessageBox.critical(
                        self, 'Export Error',
                        f'Error exporting to PDF with {engine}:\n{str(e)}'
                    )
                    return False

        # If we've tried all engines and none worked (shouldn't normally reach here)
        progress.close()
        QMessageBox.critical(
            self, 'Export Error',
            'Failed to export PDF with any available engine.'
        )
        return False



