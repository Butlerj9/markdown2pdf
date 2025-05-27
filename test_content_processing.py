#!/usr/bin/env python3
"""
Test Content Processing
--------------------
Test script for the content processing system.
"""

import os
import sys
import argparse
from logging_config import get_logger
from content_processing_integration import get_integration

logger = get_logger()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test content processing')
    parser.add_argument('input_file', help='Input Markdown file')
    parser.add_argument('--format', choices=['preview', 'pdf', 'html', 'docx', 'epub'], default='preview',
                        help='Output format (default: preview)')
    parser.add_argument('--output', help='Output file (default: stdout)')
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Read input file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get content processing integration
    integration = get_integration()
    
    # Check dependencies
    dependency_status = integration.check_dependencies()
    logger.info(f"Dependency status: {dependency_status}")
    
    # Process content
    if args.format == 'preview':
        processed_content = integration.process_content_for_preview(content)
        
        # Add required scripts and styles for preview
        scripts = integration.get_required_scripts()
        styles = integration.get_required_styles()
        
        # Create HTML document
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
    {styles}
    {scripts}
</head>
<body>
    {processed_content}
</body>
</html>"""
        
        processed_content = html
    else:
        processed_content = integration.process_content_for_export(content, args.format)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        logger.info(f"Output written to {args.output}")
    else:
        print(processed_content)

if __name__ == '__main__':
    main()
