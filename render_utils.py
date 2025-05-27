#!/usr/bin/env python3
"""
Render Utilities for Markdown to PDF Converter
----------------------------------------------
Contains utilities for rendering Markdown to HTML and PDF.
File: src--render_utils.py
"""

import os
import tempfile
import subprocess
import time
import traceback
from logging_config import get_logger, EnhancedLogger

logger = get_logger()

class RenderUtils:
    """Utilities for rendering Markdown to HTML and PDF output"""

    @staticmethod
    def generate_css_from_settings(settings):
        """Generate enhanced CSS from current settings"""
        logger.debug("Generating CSS from settings")

        # Base CSS with better support for Mermaid and fixed heading styles
        css = f"""
        /* Body styles */
        body {{
            font-family: "{settings["fonts"]["body"].get("family", settings["fonts"]["body"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["body"].get("size", settings["fonts"]["body"].get("font_size", 11))}pt;
            line-height: {settings["fonts"]["body"].get("line_height", 1.5)};
            color: {settings["colors"]["text"]};
            background-color: {settings["colors"]["background"]};
            max-width: 100%;
            box-sizing: border-box;
            padding: 20px;
            margin: 0;
        }}

        /* Hide the document title */
        body > h1:first-of-type, body > header > h1:first-of-type {{
            display: none !important;
        }}

        header {{
            display: none !important;
        }}

        /* Common heading properties */
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
            page-break-inside: avoid;
        }}

        /* Individual heading styles */
        h1 {{
            font-family: "{settings["fonts"]["headings"]["h1"].get("family", settings["fonts"]["headings"]["h1"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h1"].get("size", settings["fonts"]["headings"]["h1"].get("font_size", 18))}pt;
            color: {settings["fonts"]["headings"]["h1"]["color"]};
            line-height: {settings["fonts"]["headings"]["h1"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h1"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h1"]["margin_bottom"]}pt;
        }}

        h2 {{
            font-family: "{settings["fonts"]["headings"]["h2"].get("family", settings["fonts"]["headings"]["h2"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h2"].get("size", settings["fonts"]["headings"]["h2"].get("font_size", 16))}pt;
            color: {settings["fonts"]["headings"]["h2"]["color"]};
            line-height: {settings["fonts"]["headings"]["h2"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h2"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h2"]["margin_bottom"]}pt;
        }}

        h3 {{
            font-family: "{settings["fonts"]["headings"]["h3"].get("family", settings["fonts"]["headings"]["h3"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h3"].get("size", settings["fonts"]["headings"]["h3"].get("font_size", 14))}pt;
            color: {settings["fonts"]["headings"]["h3"]["color"]};
            line-height: {settings["fonts"]["headings"]["h3"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h3"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h3"]["margin_bottom"]}pt;
        }}

        h4 {{
            font-family: "{settings["fonts"]["headings"]["h4"].get("family", settings["fonts"]["headings"]["h4"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h4"].get("size", settings["fonts"]["headings"]["h4"].get("font_size", 13))}pt;
            color: {settings["fonts"]["headings"]["h4"]["color"]};
            line-height: {settings["fonts"]["headings"]["h4"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h4"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h4"]["margin_bottom"]}pt;
        }}

        h5 {{
            font-family: "{settings["fonts"]["headings"]["h5"].get("family", settings["fonts"]["headings"]["h5"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h5"].get("size", settings["fonts"]["headings"]["h5"].get("font_size", 12))}pt;
            color: {settings["fonts"]["headings"]["h5"]["color"]};
            line-height: {settings["fonts"]["headings"]["h5"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h5"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h5"]["margin_bottom"]}pt;
        }}

        h6 {{
            font-family: "{settings["fonts"]["headings"]["h6"].get("family", settings["fonts"]["headings"]["h6"].get("font_family", "Arial"))}", Arial, sans-serif;
            font-size: {settings["fonts"]["headings"]["h6"].get("size", settings["fonts"]["headings"]["h6"].get("font_size", 11))}pt;
            color: {settings["fonts"]["headings"]["h6"]["color"]};
            line-height: {settings["fonts"]["headings"]["h6"]["spacing"]};
            margin-top: {settings["fonts"]["headings"]["h6"]["margin_top"]}pt;
            margin-bottom: {settings["fonts"]["headings"]["h6"]["margin_bottom"]}pt;
        }}

        /* Paragraph styles */
        p {{
            margin-top: {settings.get("paragraphs", settings.get("paragraph", {})).get("margin_top", 0)}pt;
            margin-bottom: {settings.get("paragraphs", settings.get("paragraph", {})).get("margin_bottom", 10)}pt;
            line-height: {settings.get("paragraphs", settings.get("paragraph", {})).get("spacing", 1.5)};
            text-indent: {settings.get("paragraphs", settings.get("paragraph", {})).get("first_line_indent", 0)}pt;
            text-align: {settings.get("paragraphs", settings.get("paragraph", {})).get("alignment", "left")};
        }}

        /* Links */
        a {{
            color: {settings["colors"]["links"]};
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* Code blocks */
        pre, code {{
            font-family: "{settings["code"].get("font_family", "Consolas")}", "Courier New", monospace;
            font-size: {settings["code"].get("font_size", 10)}pt;
        }}

        pre {{
            background-color: {settings["code"].get("background", "#F5F5F5")};
            border: 1px solid {settings["code"].get("border_color", "#CCCCCC")};
            padding: 10px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15pt 0;
            page-break-inside: avoid;
        }}

        th {{
            background-color: {settings["table"].get("header_bg", "#EEEEEE")};
            color: {settings["colors"]["text"]};
            border: 1px solid {settings["table"].get("border_color", "#CCCCCC")};
            padding: {settings["table"].get("cell_padding", 5)}pt;
        }}

        td {{
            border: 1px solid {settings["table"].get("border_color", "#CCCCCC")};
            padding: {settings["table"].get("cell_padding", 5)}pt;
        }}

        /* Lists */
        ul {{
            padding-left: {settings["lists"].get("bullet_indent", 30)}pt;
            margin-top: 0;
            margin-bottom: {settings["lists"].get("item_spacing", 5)}pt;
        }}

        /* Custom bullet styles */
        ul.dash-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.dash-bullets > li:before {{
            content: '\2013';
            position: absolute;
            left: -1.5em;
        }}

        ul.triangle-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.triangle-bullets > li:before {{
            content: '\25B6';
            position: absolute;
            left: -1.5em;
        }}

        ul.arrow-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.arrow-bullets > li:before {{
            content: '\27A1';
            position: absolute;
            left: -1.5em;
        }}

        ul.checkmark-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.checkmark-bullets > li:before {{
            content: '\2713';
            position: absolute;
            left: -1.5em;
        }}

        ul.star-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.star-bullets > li:before {{
            content: '\2605';
            position: absolute;
            left: -1.5em;
        }}

        ul.diamond-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.diamond-bullets > li:before {{
            content: '\25C6';
            position: absolute;
            left: -1.5em;
        }}

        ul.heart-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.heart-bullets > li:before {{
            content: '\2665';
            position: absolute;
            left: -1.5em;
        }}

        ul.pointer-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.pointer-bullets > li:before {{
            content: '\261E';
            position: absolute;
            left: -1.5em;
        }}

        ul.greater-bullets > li {{
            list-style-type: none;
            position: relative;
        }}
        ul.greater-bullets > li:before {{
            content: '\00BB';
            position: absolute;
            left: -1.5em;
        }}

        ol {{
            padding-left: {settings["lists"].get("number_indent", 30)}pt;
            margin-top: 0;
            margin-bottom: {settings["lists"].get("item_spacing", 5)}pt;
        }}

        li {{
            margin-bottom: {settings["lists"].get("item_spacing", 5)}pt;
        }}

        /* Mermaid diagram support */
        .mermaid {{
            display: block;
            margin: 1em auto;
            max-width: 100%;
            text-align: center;
            overflow: visible;
        }}

        /* Fix to ensure Mermaid diagrams render correctly */
        .mermaid svg {{
            max-width: 100%;
            height: auto !important;
        }}

        /* Page break styling */
        .page-break {{
            page-break-before: always;
            height: 0;
            display: block;
        }}
        """

        # Add technical numbering styles if enabled - FIXED to avoid double numbering
        if settings["format"]["technical_numbering"]:
            # Get the heading level at which numbering starts (default to 1 if not specified)
            numbering_start = settings["format"].get("numbering_start", 1)

            # Base CSS for technical numbering
            css += """
            /* Technical numbering styles - FIXED for proper HTML display */
            body {
                /* Using custom counter mechanism */
                counter-reset: h1counter h2counter h3counter h4counter h5counter h6counter;
            }

            /* Hide standard pandoc numbering if CSS numbering is active */
            body:not(.pandoc-numbering) .header-section-number {
                display: none;
            }

            /* Reset counter styles for headings with reset-counter class */
            body:not(.pandoc-numbering) h1.reset-counter {
                counter-reset: h1counter h2counter h3counter h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h2.reset-counter {
                counter-reset: h2counter h3counter h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h3.reset-counter {
                counter-reset: h3counter h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h4.reset-counter {
                counter-reset: h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h5.reset-counter {
                counter-reset: h5counter h6counter;
            }

            body:not(.pandoc-numbering) h6.reset-counter {
                counter-reset: h6counter;
            }
            """

            # Add CSS for each heading level based on the numbering start level
            # We need to completely disable the :before content for levels below numbering_start

            # Set up counter-reset for all heading levels
            css += """
            /* Counter setup for all heading levels */
            body:not(.pandoc-numbering) h1 {
                counter-increment: h1counter;
                counter-reset: h2counter h3counter h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h2 {
                counter-increment: h2counter;
                counter-reset: h3counter h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h3 {
                counter-increment: h3counter;
                counter-reset: h4counter h5counter h6counter;
            }

            body:not(.pandoc-numbering) h4 {
                counter-increment: h4counter;
                counter-reset: h5counter h6counter;
            }

            body:not(.pandoc-numbering) h5 {
                counter-increment: h5counter;
                counter-reset: h6counter;
            }

            body:not(.pandoc-numbering) h6 {
                counter-increment: h6counter;
            }
            """

            # Now add the :before content only for levels at or above numbering_start
            if numbering_start <= 1:
                css += """
                /* H1 numbering */
                body:not(.pandoc-numbering) h1:before {
                    content: counter(h1counter) ". ";
                }
                """

            if numbering_start <= 2:
                css += """
                /* H2 numbering */
                body:not(.pandoc-numbering) h2:before {
                    content: """ + (f"counter(h1counter) \".\" " if numbering_start <= 1 else "") + """counter(h2counter) " ";
                }
                """

            if numbering_start <= 3:
                css += """
                /* H3 numbering */
                body:not(.pandoc-numbering) h3:before {
                    content: """ + (f"counter(h1counter) \".\" counter(h2counter) \".\" " if numbering_start <= 1 else (f"counter(h2counter) \".\" " if numbering_start <= 2 else "")) + """counter(h3counter) " ";
                }
                """

            if numbering_start <= 4:
                css += """
                /* H4 numbering */
                body:not(.pandoc-numbering) h4:before {
                    content: """ + (f"counter(h1counter) \".\" counter(h2counter) \".\" counter(h3counter) \".\" " if numbering_start <= 1 else (f"counter(h2counter) \".\" counter(h3counter) \".\" " if numbering_start <= 2 else (f"counter(h3counter) \".\" " if numbering_start <= 3 else ""))) + """counter(h4counter) " ";
                }
                """

            if numbering_start <= 5:
                css += """
                /* H5 numbering */
                body:not(.pandoc-numbering) h5:before {
                    content: """ + (f"counter(h1counter) \".\" counter(h2counter) \".\" counter(h3counter) \".\" counter(h4counter) \".\" " if numbering_start <= 1 else (f"counter(h2counter) \".\" counter(h3counter) \".\" counter(h4counter) \".\" " if numbering_start <= 2 else (f"counter(h3counter) \".\" counter(h4counter) \".\" " if numbering_start <= 3 else (f"counter(h4counter) \".\" " if numbering_start <= 4 else "")))) + """counter(h5counter) " ";
                }
                """

            if numbering_start <= 6:
                css += """
                /* H6 numbering */
                body:not(.pandoc-numbering) h6:before {
                    content: """ + (f"counter(h1counter) \".\" counter(h2counter) \".\" counter(h3counter) \".\" counter(h4counter) \".\" counter(h5counter) \".\" " if numbering_start <= 1 else (f"counter(h2counter) \".\" counter(h3counter) \".\" counter(h4counter) \".\" counter(h5counter) \".\" " if numbering_start <= 2 else (f"counter(h3counter) \".\" counter(h4counter) \".\" counter(h5counter) \".\" " if numbering_start <= 3 else (f"counter(h4counter) \".\" counter(h5counter) \".\" " if numbering_start <= 4 else (f"counter(h5counter) \".\" " if numbering_start <= 5 else ""))))) + """counter(h6counter) " ";
                }
                """

        logger.debug("CSS generation completed")
        return css

    @staticmethod
    def generate_latex_template():
        """Generate a simplified LaTeX template with basic styling"""
        logger.debug("Generating simplified LaTeX template")
        template = r"""
\documentclass[
$if(fontsize)$
$fontsize$,
$endif$
$if(papersize)$
$papersize$,
$endif$
$for(classoption)$
$classoption$$sep$,
$endfor$
]{article}

\usepackage{geometry}
\geometry{
$if(geometry)$
$for(geometry)$
$geometry$$sep$,
$endfor$
$endif$
$if(margin-top)$
top=$margin-top$mm,
$endif$
$if(margin-right)$
right=$margin-right$mm,
$endif$
$if(margin-bottom)$
bottom=$margin-bottom$mm,
$endif$
$if(margin-left)$
left=$margin-left$mm,
$endif$
}

\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{multicol}
\usepackage{array}
\usepackage{enumitem}

% Configure bullet list styles
\setlist[itemize,1]{label=\textbullet}
\setlist[itemize,2]{label=\textopenbullet}
\setlist[itemize,3]{label=\textdiamondsuit}

% Set main font
$if(mainfont)$
\setmainfont{$mainfont$}
$endif$

% Set sans font for headings
$if(sansfont)$
\setsansfont{$sansfont$}
$endif$

% Set monospace font for code
$if(monofont)$
\setmonofont{$monofont$}
$endif$

% Setup colors
$if(text-color)$
\definecolor{textcolor}{HTML}{$text-color$}
\color{textcolor}
$endif$

$if(heading-color)$
\definecolor{headingcolor}{HTML}{$heading-color$}
$endif$

$if(link-color)$
\definecolor{linkcolor}{HTML}{$link-color$}
\hypersetup{
    colorlinks=true,
    linkcolor=linkcolor,
    urlcolor=linkcolor
}
$endif$

% Fix for handling technical numbering correctly
\setcounter{secnumdepth}{$if(secnumdepth)$$secnumdepth$$else$-2$endif$}

% Style headings
$if(heading-color)$
\titleformat{\section}{\Large\bfseries\sffamily\color{headingcolor}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\sffamily\color{headingcolor}}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\sffamily\color{headingcolor}}{\thesubsubsection}{1em}{}
$endif$

% Setup page numbering if enabled
$if(page-numbering)$
\pagestyle{fancy}
\fancyhf{}
$if(page-number-format)$
\fancyfoot[C]{$page-number-format$}
$else$
\fancyfoot[C]{\thepage}
$endif$
\renewcommand{\headrulewidth}{0pt}
$else$
\pagestyle{empty}
$endif$

% Code block styling
\definecolor{codebg}{HTML}{F8F8F8}
\definecolor{codeborder}{HTML}{E0E0E0}
\lstset{
    backgroundcolor=\color{codebg},
    frame=single,
    rulecolor=\color{codeborder},
    basicstyle=\ttfamily\small,
    breaklines=true,
    postbreak=\mbox{\textcolor{gray}{-->}\space},
}

% Define a command for horizontal lines
\newcommand{\horizontalline}{
  \noindent\rule{\textwidth}{0.5pt}
}

\begin{document}

$if(title)$
\title{$title$}
$if(author)$
\author{$author$}
$endif$
$if(date)$
\date{$date$}
$endif$
\maketitle
$endif$

$if(toc)$
\tableofcontents
\newpage
$endif$

$body$

\end{document}
"""

        return template

    @staticmethod
    def update_preview(md_editor, page_preview, document_settings):
        """Update the HTML preview with page layout and styling"""
        # Add a counter to track how many times this method is called
        if not hasattr(RenderUtils, '_update_preview_count'):
            RenderUtils._update_preview_count = 0
        RenderUtils._update_preview_count += 1

        logger.debug(f"RenderUtils.update_preview call #{RenderUtils._update_preview_count}")

        # Add a debounce mechanism to prevent multiple rapid calls
        current_time = time.time()
        if hasattr(RenderUtils, '_last_preview_update_time'):
            # If less than 100ms has passed since the last update, skip this update
            if current_time - RenderUtils._last_preview_update_time < 0.1:
                logger.debug("Skipping duplicate RenderUtils.update_preview call (debounce)")
                return

        # Update the timestamp
        RenderUtils._last_preview_update_time = current_time

        try:
            # Check if page_preview is valid
            if not page_preview:
                logger.error("Page preview is None or invalid")
                return

            # Get markdown text safely
            try:
                markdown_text = md_editor.toPlainText()
                logger.debug(f"Got markdown text, length: {len(markdown_text)}")
            except Exception as e:
                logger.error(f"Error getting markdown text: {str(e)}")
                markdown_text = ""

            # Update page preview settings safely
            try:
                logger.debug("Updating document settings in page_preview")
                page_preview.update_document_settings(document_settings)
            except Exception as e:
                logger.error(f"Error updating document settings: {str(e)}")

            # Using built-in zoom functionality
            logger.debug("Using built-in zoom functionality in page_preview.py")

            if not markdown_text:
                # Set a default message in the preview with proper page layout
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {
                            background-color: #e0e0e0;
                            margin: 0;
                            padding: 20px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                        }
                        .page {
                            position: relative;
                            width: 210mm;
                            min-height: 297mm;
                            box-sizing: border-box;
                            margin: 0 auto;
                            background-color: white;
                            border: 1px solid #ccc;
                            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                        }
                        .page-content {
                            position: absolute;
                            top: 25mm;
                            right: 25mm;
                            bottom: 25mm;
                            left: 25mm;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            overflow: hidden;
                        }
                        .margin-box {
                            position: absolute;
                            top: 25mm;
                            right: 25mm;
                            bottom: 25mm;
                            left: 25mm;
                            border: 1px dotted rgba(200, 200, 200, 0.5);
                            pointer-events: none;
                            z-index: 10;
                        }
                        .empty-preview-message {
                            text-align: center;
                            font-family: sans-serif;
                            color: #555;
                        }
                    </style>
                </head>
                <body>
                <div class="page current-page">
                    <div class="margin-box"></div>
                    <div class="page-content">
                        <div class="empty-preview-message">
                            <h2>Markdown to PDF Preview</h2>
                            <p>Your document preview will appear here as you type.</p>
                        </div>
                    </div>
                </div>
                </body>
                </html>
                """
                try:
                    page_preview.update_preview(html)
                    logger.debug("Set empty preview message with proper page layout")
                except Exception as e:
                    logger.error(f"Error setting empty preview: {str(e)}")
                return

            # Use try-finally to ensure cleanup even if errors occur
            md_path = None
            css_file_name = None
            html_file_name = None

            try:
                # Create temporary markdown file
                with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.md', delete=False) as md_file:
                    # Process any page break markers for HTML preview
                    # We'll handle page breaks in the HTML output instead of here
                    processed_text = markdown_text

                    # Import the page break handler
                    from page_break_handler import find_page_breaks_in_markdown

                    # Log page break information
                    page_breaks = find_page_breaks_in_markdown(processed_text)
                    logger.debug(f"Found {len(page_breaks)} page breaks at lines: {page_breaks}")

                    logger.debug(f"Writing processed Markdown to temporary file (length: {len(processed_text)})")
                    md_file.write(processed_text)
                    md_path = md_file.name

                # Create temporary HTML file for preview
                html_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
                html_file.close()
                html_file_name = html_file.name
                logger.debug(f"Created temporary HTML file: {html_file_name}")

                # Generate CSS from current settings
                css_content = RenderUtils.generate_css_from_settings(document_settings)

                # Add page break styles to CSS
                from page_break_handler import inject_page_break_styles
                css_content = inject_page_break_styles(css_content)

                with tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.css', delete=False) as css_file:
                    css_file.write(css_content)
                    css_file_name = css_file.name
                logger.debug(f"Created temporary CSS file: {css_file_name}")

                # Run pandoc to convert markdown to HTML
                try:
                    pandoc_cmd = [
                        r'C:\Users\joshd\AppData\Local\Pandoc\pandoc.exe',
                        md_path,
                        '-o', html_file_name,
                        '--standalone',
                        '--css=' + css_file_name,
                        '--mathjax',
                        '-f', 'markdown+fenced_divs+pipe_tables+backtick_code_blocks',
                        '-t', 'html5'
                    ]

                    # Add title metadata to prevent warnings
                    pandoc_cmd.extend(['--metadata', 'title=Preview'])

                    # Add TOC if needed
                    if document_settings.get("toc", {}).get("include", False):
                        pandoc_cmd.extend([
                            '--toc',
                            f'--toc-depth={document_settings.get("toc", {}).get("depth", 3)}'
                        ])

                    # Add technical numbering if enabled
                    if document_settings.get("format", {}).get("technical_numbering", False):
                        pandoc_cmd.extend(['--number-sections'])
                        # Set the heading level at which numbering starts
                        numbering_start = document_settings.get("format", {}).get("numbering_start", 1)
                        pandoc_cmd.extend(['--variable', f'secnumdepth={7-numbering_start}'])
                    else:
                        pandoc_cmd.extend(['--variable', 'secnumdepth=-2'])
                        pandoc_cmd.extend(['--variable', 'disable-numbering=true'])

                    # Log the command
                    EnhancedLogger.log_command(logger, pandoc_cmd)

                    # Run pandoc with improved error handling
                    result = subprocess.run(
                        pandoc_cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    # Log any output from pandoc
                    if result.stdout:
                        logger.debug(f"Pandoc stdout: {result.stdout}")
                    if result.stderr:
                        logger.warning(f"Pandoc stderr: {result.stderr}")

                    # Read the generated HTML
                    with open(html_file_name, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    # Process page breaks in the HTML content
                    from page_break_handler import process_page_breaks_for_preview
                    modified_html = process_page_breaks_for_preview(html_content)

                    # Ensure the body has the right styling
                    modified_html = modified_html.replace(
                        '<body>',
                        f'<body style="background-color: {document_settings.get("colors", {}).get("background", "#FFFFFF")};">'
                    )

                    logger.debug(f"HTML content generated (length: {len(modified_html)})")

                    # Update the preview with a try-except block to prevent blank previews
                    try:
                        # Make sure document settings are applied before updating preview
                        page_preview.update_document_settings(document_settings)

                        # Store the HTML content for later use
                        page_preview._last_html_content = modified_html

                        # Update the preview
                        page_preview.update_preview(modified_html)
                        logger.debug("Preview updated successfully")
                    except Exception as preview_error:
                        logger.error(f"Error updating preview: {str(preview_error)}")
                        EnhancedLogger.log_exception(logger, preview_error)
                        # Try to show an error message in the preview
                        try:
                            error_html = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; padding: 20px;">
                                <h2 style="color: #d9534f;">Preview Update Error</h2>
                                <p>Error updating preview: {str(preview_error)}</p>
                                <pre>{traceback.format_exc()}</pre>
                            </body>
                            </html>
                            """
                            page_preview.update_preview(error_html)
                        except Exception as e2:
                            logger.critical(f"Failed to show error in preview: {str(e2)}")

                except Exception as e:
                    logger.error(f"Preview error with Pandoc: {str(e)}")
                    EnhancedLogger.log_exception(logger, e)

                    # Try to show an error message in the preview
                    try:
                        error_msg = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px;">
                            <h2 style="color: #d9534f;">Preview Error</h2>
                            <p>Error running Pandoc: {str(e)}</p>
                            <pre>{traceback.format_exc()}</pre>
                        </body>
                        </html>
                        """
                        page_preview.update_preview(error_msg)
                    except Exception as e2:
                        logger.critical(f"Failed to show error in preview: {str(e2)}")

            except Exception as e:
                logger.error(f"Error preparing preview: {str(e)}")
                EnhancedLogger.log_exception(logger, e)

                # Try to show an error message in the preview
                try:
                    error_msg = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #d9534f;">Preview Error</h2>
                        <p>Error preparing preview: {str(e)}</p>
                        <pre>{traceback.format_exc()}</pre>
                    </body>
                    </html>
                    """
                    page_preview.update_preview(error_msg)
                except Exception as e2:
                    logger.critical(f"Failed to show error in preview: {str(e2)}")

            finally:
                logger.debug("Cleaning up temporary files")
                # Clean up temp files
                for temp_file in [md_path, css_file_name, html_file_name]:
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.unlink(temp_file)
                            logger.debug(f"Deleted temporary file: {temp_file}")
                        except Exception as cleanup_error:
                            logger.warning(f"Error cleaning up temp file {temp_file}: {str(cleanup_error)}")
        except KeyboardInterrupt:
            logger.warning("Preview update interrupted by user")
            # Try to show a message in the preview
            try:
                error_msg = """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #d9534f;">Preview Interrupted</h2>
                    <p>The preview update was interrupted. Please try again.</p>
                </body>
                </html>
                """
                if page_preview:
                    page_preview.update_preview(error_msg)
            except Exception:
                pass
        except Exception as e:
            logger.critical(f"Critical error in update_preview: {str(e)}")
            EnhancedLogger.log_exception(logger, e)
            # Try to show a critical error message in the preview
            try:
                if page_preview:
                    error_msg = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #d9534f;">Critical Error</h2>
                        <p>A critical error occurred while updating the preview: {str(e)}</p>
                        <pre>{traceback.format_exc()}</pre>
                    </body>
                    </html>
                    """
                    page_preview.update_preview(error_msg)
            except Exception:
                pass

        EnhancedLogger.log_function_exit(logger, "update_preview")

    @staticmethod
    def run_process_with_timeout(command, progress_dialog=None, timeout=120):
        """Run a command with timeout and progress dialog updates"""
        logger.debug("Running process with timeout")
        EnhancedLogger.log_function_entry(logger, "run_process_with_timeout", command, timeout=timeout)
        EnhancedLogger.log_command(logger, command)

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Track the start time
            start_time = time.time()
            logger.debug(f"Process started at {start_time}")

            # Poll the process with timeout
            while process.poll() is None:
                # Check if we've exceeded the timeout
                if time.time() - start_time > timeout:
                    # Process is taking too long, terminate it
                    logger.warning(f"Process timed out after {timeout} seconds")
                    process.terminate()
                    time.sleep(0.5)
                    if process.poll() is None:
                        logger.warning("Process did not terminate, killing it")
                        process.kill()
                    return None, None, f"Process timed out after {timeout} seconds", -1

                # Check if user canceled
                if progress_dialog:
                    from PyQt6.QtWidgets import QApplication, QMessageBox
                    QApplication.processEvents()
                    if progress_dialog.standardButton(progress_dialog.clickedButton()) == QMessageBox.StandardButton.Cancel:
                        logger.info("Process canceled by user")
                        process.terminate()
                        time.sleep(0.5)
                        if process.poll() is None:
                            logger.warning("Process did not terminate after cancel, killing it")
                            process.kill()
                        return None, None, "Process canceled by user", -2

                # Wait a bit before polling again
                time.sleep(0.1)

            # Get the output
            stdout, stderr = process.communicate()
            logger.debug(f"Process completed with return code {process.returncode}")
            if stdout:
                logger.debug(f"Process stdout: {stdout[:1000]}...")
            if stderr:
                logger.warning(f"Process stderr: {stderr}")

            EnhancedLogger.log_function_exit(logger, "run_process_with_timeout",
                                            f"Return code: {process.returncode}")
            return stdout, stderr, None, process.returncode

        except Exception as e:
            logger.error(f"Error running process: {str(e)}")
            EnhancedLogger.log_exception(logger, e)
            EnhancedLogger.log_function_exit(logger, "run_process_with_timeout",
                                           f"Error: {str(e)}")
            return None, None, str(e), -3