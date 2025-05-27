#!/usr/bin/env python3
"""
Test script for MDZ export integration with the main application
"""

import os
import sys
import logging
import tempfile
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mdz_export_integration():
    """Test MDZ export integration with the main application"""

    # Create a test markdown file
    temp_dir = tempfile.mkdtemp(prefix="mdz_export_test_")
    test_md_path = os.path.join(temp_dir, "test.md")

    # Create test markdown content
    markdown_content = """# Test MDZ Export

This is a test of the MDZ export functionality.

## Features

- Zstandard compression
- File checksum as password
- Bundled assets

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

## Math Example

$E = mc^2$

"""

    # Write the test markdown file
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Initialize the application
    app = QApplication(sys.argv)

    # Create the converter
    converter = AdvancedMarkdownToPDF()

    # Load the test file directly
    with open(test_md_path, 'r', encoding='utf-8') as file:
        converter.markdown_editor.setPlainText(file.read())

    converter.current_file = test_md_path
    converter.update_preview()

    # Test MDZ export
    logger.info("Testing MDZ export...")

    # Create the output file path
    output_file = os.path.join(temp_dir, "test_output.mdz")

    # Export to MDZ
    result = converter._export_to_mdz(output_file)

    # Check if the export was successful
    if result:
        logger.info(f"MDZ export successful: {output_file}")

        # Check if the file exists
        if os.path.exists(output_file):
            logger.info(f"MDZ file exists: {output_file}")
            logger.info(f"MDZ file size: {os.path.getsize(output_file)} bytes")

            # Try to extract the MDZ file
            from mdz_export import extract_mdz_file

            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            logger.info(f"Extracting MDZ file to: {extract_dir}")
            markdown_content, metadata = extract_mdz_file(output_file, extract_dir)

            # Check if the extraction was successful
            if markdown_content:
                logger.info("MDZ extraction successful")
                logger.info(f"Extracted markdown content length: {len(markdown_content)}")
                logger.info(f"Extracted metadata: {metadata}")

                # Check if the extracted files exist
                manifest_path = os.path.join(extract_dir, "manifest.json")
                metadata_path = os.path.join(extract_dir, "metadata.yaml")
                main_md_path = os.path.join(extract_dir, "main.md")

                if os.path.exists(manifest_path):
                    logger.info(f"Manifest file exists: {manifest_path}")
                if os.path.exists(metadata_path):
                    logger.info(f"Metadata file exists: {metadata_path}")
                if os.path.exists(main_md_path):
                    logger.info(f"Main markdown file exists: {main_md_path}")

                # Check if the assets directory exists
                assets_dir = os.path.join(extract_dir, "assets")
                if os.path.exists(assets_dir):
                    logger.info(f"Assets directory exists: {assets_dir}")

                    # List all files in the assets directory
                    assets = os.listdir(assets_dir)
                    logger.info(f"Assets: {assets}")
            else:
                logger.error("MDZ extraction failed")
        else:
            logger.error(f"MDZ file does not exist: {output_file}")
    else:
        logger.error("MDZ export failed")

    # Clean up
    converter.close()

    # Remove the test files
    try:
        os.remove(test_md_path)
        if os.path.exists(output_file):
            os.remove(output_file)
        os.rmdir(temp_dir)
    except Exception as e:
        logger.warning(f"Error cleaning up test files: {e}")

    logger.info("MDZ export integration test completed")
    return result

if __name__ == "__main__":
    result = test_mdz_export_integration()
    sys.exit(0 if result else 1)
