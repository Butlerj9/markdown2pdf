#!/usr/bin/env python3
"""
Comprehensive test for MDZ format support
"""

import os
import sys
import json
import logging
import tempfile
import hashlib
import shutil
import yaml
from PyQt6.QtWidgets import QApplication
from markdown_to_pdf_converter import AdvancedMarkdownToPDF
from mdz_export import create_mdz_file, extract_mdz_file

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDZTester:
    """Test MDZ format support"""

    def __init__(self):
        """Initialize the tester"""
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_test_")
        self.test_files = []
        self.results = {
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }

    def cleanup(self):
        """Clean up temporary files"""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Error removing file {file_path}: {e}")

        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Error removing directory {self.temp_dir}: {e}")

    def create_test_markdown(self, name, content, metadata=None):
        """Create a test markdown file"""
        file_path = os.path.join(self.temp_dir, f"{name}.md")

        # Add YAML front matter if metadata is provided
        if metadata:
            yaml_content = yaml.dump(metadata)
            content = f"---\n{yaml_content}---\n\n{content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def create_test_asset(self, name, content):
        """Create a test asset file"""
        file_path = os.path.join(self.temp_dir, name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def calculate_file_checksum(self, file_path):
        """Calculate the SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def test_mdz_creation(self, markdown_path, output_path, assets=None):
        """Test MDZ file creation"""
        logger.info(f"Testing MDZ creation: {output_path}")

        # Create the MDZ file
        result = create_mdz_file(markdown_path, output_path, assets)

        # Check if the file was created
        if result and os.path.exists(output_path):
            logger.info(f"MDZ file created: {output_path}")
            logger.info(f"MDZ file size: {os.path.getsize(output_path)} bytes")

            # Read the content of the markdown file
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Calculate the checksum of the content
            checksum = hashlib.sha256(markdown_content.encode('utf-8')).hexdigest()
            logger.info(f"Original content checksum: {checksum}")

            return True, checksum
        else:
            logger.error(f"MDZ file creation failed: {output_path}")
            return False, None

    def test_mdz_extraction(self, mdz_path, extract_dir, expected_checksum):
        """Test MDZ file extraction"""
        logger.info(f"Testing MDZ extraction: {mdz_path}")

        # Create the extraction directory
        os.makedirs(extract_dir, exist_ok=True)

        # Extract the MDZ file
        markdown_content, metadata = extract_mdz_file(mdz_path, extract_dir)

        # Check if the extraction was successful
        if markdown_content:
            logger.info("MDZ extraction successful")
            logger.info(f"Extracted markdown content length: {len(markdown_content)}")
            logger.info(f"Extracted metadata: {metadata}")

            # Check if the extracted files exist
            manifest_path = os.path.join(extract_dir, "manifest.json")
            metadata_path = os.path.join(extract_dir, "metadata.yaml")
            main_md_path = os.path.join(extract_dir, "main.md")

            files_exist = True
            if os.path.exists(manifest_path):
                logger.info(f"Manifest file exists: {manifest_path}")
            else:
                logger.error(f"Manifest file does not exist: {manifest_path}")
                files_exist = False

            if os.path.exists(metadata_path):
                logger.info(f"Metadata file exists: {metadata_path}")
            else:
                logger.error(f"Metadata file does not exist: {metadata_path}")
                files_exist = False

            if os.path.exists(main_md_path):
                logger.info(f"Main markdown file exists: {main_md_path}")
            else:
                logger.error(f"Main markdown file does not exist: {main_md_path}")
                files_exist = False

            # Check if the assets directory exists
            assets_dir = os.path.join(extract_dir, "assets")
            if os.path.exists(assets_dir):
                logger.info(f"Assets directory exists: {assets_dir}")

                # List all files in the assets directory
                assets = os.listdir(assets_dir)
                logger.info(f"Assets: {assets}")

            # Verify the checksum
            if expected_checksum:
                # Calculate the checksum of the extracted content
                extracted_checksum = hashlib.sha256(markdown_content.encode('utf-8')).hexdigest()
                logger.info(f"Extracted content checksum: {extracted_checksum}")

                if extracted_checksum == expected_checksum:
                    logger.info("Checksum verification successful")
                    return True, files_exist
                else:
                    logger.error("Checksum verification failed")
                    return False, files_exist

            return True, files_exist
        else:
            logger.error("MDZ extraction failed")
            return False, False

    def test_mdz_integration(self, name, markdown_content, metadata=None, assets=None):
        """Test MDZ integration (creation and extraction)"""
        logger.info(f"Running MDZ integration test: {name}")

        # Create a test markdown file
        markdown_path = self.create_test_markdown(name, markdown_content, metadata)

        # Create asset files if provided
        asset_paths = []
        if assets:
            for asset_name, asset_content in assets.items():
                asset_path = self.create_test_asset(asset_name, asset_content)
                asset_paths.append(asset_path)

        # Create the output path
        output_path = os.path.join(self.temp_dir, f"{name}.mdz")

        # Test MDZ creation
        creation_success, _ = self.test_mdz_creation(markdown_path, output_path, asset_paths)

        # Test MDZ extraction
        extract_dir = os.path.join(self.temp_dir, f"{name}_extracted")
        extraction_success, files_exist = self.test_mdz_extraction(output_path, extract_dir, None)

        # Record the test results
        test_result = {
            "name": name,
            "creation_success": creation_success,
            "extraction_success": extraction_success,
            "files_exist": files_exist
        }

        self.results["tests"].append(test_result)
        self.results["summary"]["total"] += 1

        if creation_success and extraction_success and files_exist:
            self.results["summary"]["passed"] += 1
            logger.info(f"MDZ integration test passed: {name}")
            return True
        else:
            self.results["summary"]["failed"] += 1
            logger.error(f"MDZ integration test failed: {name}")
            return False

    def test_mdz_app_integration(self, name, markdown_content, metadata=None):
        """Test MDZ integration with the main application"""
        logger.info(f"Running MDZ app integration test: {name}")

        # Create a test markdown file
        markdown_path = self.create_test_markdown(name, markdown_content, metadata)

        # Create the output path
        output_path = os.path.join(self.temp_dir, f"{name}.mdz")

        # Initialize the application
        app = QApplication(sys.argv)

        # Create the converter
        converter = AdvancedMarkdownToPDF()

        # Load the test file
        with open(markdown_path, 'r', encoding='utf-8') as file:
            converter.markdown_editor.setPlainText(file.read())

        converter.current_file = markdown_path
        converter.update_preview()

        # Export to MDZ
        result = converter._export_to_mdz(output_path)

        # Check if the export was successful
        if result and os.path.exists(output_path):
            logger.info(f"MDZ export successful: {output_path}")
            logger.info(f"MDZ file size: {os.path.getsize(output_path)} bytes")

            # Test extraction
            extract_dir = os.path.join(self.temp_dir, f"{name}_app_extracted")
            markdown_content, metadata = extract_mdz_file(output_path, extract_dir)

            # Check if the extraction was successful
            if markdown_content:
                logger.info("MDZ extraction successful")

                # Record the test results
                test_result = {
                    "name": f"{name}_app",
                    "export_success": True,
                    "extraction_success": True
                }

                self.results["tests"].append(test_result)
                self.results["summary"]["total"] += 1
                self.results["summary"]["passed"] += 1

                logger.info(f"MDZ app integration test passed: {name}")
                return True
            else:
                logger.error("MDZ extraction failed")

                # Record the test results
                test_result = {
                    "name": f"{name}_app",
                    "export_success": True,
                    "extraction_success": False
                }

                self.results["tests"].append(test_result)
                self.results["summary"]["total"] += 1
                self.results["summary"]["failed"] += 1

                logger.error(f"MDZ app integration test failed: {name}")
                return False
        else:
            logger.error(f"MDZ export failed: {output_path}")

            # Record the test results
            test_result = {
                "name": f"{name}_app",
                "export_success": False,
                "extraction_success": False
            }

            self.results["tests"].append(test_result)
            self.results["summary"]["total"] += 1
            self.results["summary"]["failed"] += 1

            logger.error(f"MDZ app integration test failed: {name}")
            return False

    def run_all_tests(self):
        """Run all MDZ tests"""
        logger.info("Running all MDZ tests")

        # Test 1: Basic MDZ file
        self.test_mdz_integration(
            "basic",
            "# Basic MDZ Test\n\nThis is a basic test of the MDZ format.",
            {"title": "Basic MDZ Test", "author": "Test Author"}
        )

        # Test 2: MDZ file with assets
        self.test_mdz_integration(
            "with_assets",
            "# MDZ Test with Assets\n\nThis test includes assets.\n\n![Image](test_image.png)\n\n```mermaid\ngraph TD;\n    A-->B;\n    A-->C;\n    B-->D;\n    C-->D;\n```",
            {"title": "MDZ Test with Assets", "author": "Test Author"},
            {
                "test_image.png": "This is a test image content",
                "test_data.json": '{"name": "Test Data", "value": 42}'
            }
        )

        # Test 3: MDZ file with complex content
        self.test_mdz_integration(
            "complex",
            "# Complex MDZ Test\n\n## Math Formulas\n\n$E = mc^2$\n\n## Code Blocks\n\n```python\ndef hello_world():\n    print('Hello, world!')\n```\n\n## Tables\n\n| Name | Age | Occupation |\n|------|-----|------------|\n| John | 30  | Developer  |\n| Jane | 25  | Designer   |\n| Bob  | 40  | Manager    |",
            {"title": "Complex MDZ Test", "author": "Test Author", "tags": ["math", "code", "tables"]}
        )

        # Test 4: MDZ app integration
        self.test_mdz_app_integration(
            "app_integration",
            "# MDZ App Integration Test\n\nThis tests the integration with the main application.",
            {"title": "MDZ App Integration Test", "author": "Test Author"}
        )

        # Write results to file
        results_path = os.path.join(self.temp_dir, "mdz_test_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"Test results written to: {results_path}")
        logger.info(f"Summary: Passed {self.results['summary']['passed']}/{self.results['summary']['total']} tests ({self.results['summary']['passed']/self.results['summary']['total']*100:.2f}%)")

        return self.results["summary"]["passed"] == self.results["summary"]["total"]

def main():
    """Main function"""
    tester = MDZTester()

    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
