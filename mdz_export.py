#!/usr/bin/env python3
"""
MDZ Export Module - Handles exporting to the MDZ format
"""

import os
import json
import tempfile
import hashlib
import shutil
import logging
import zstandard as zstd
import yaml
from typing import Dict, Any, List, Optional, Tuple
from PyQt6.QtWidgets import QMessageBox, QApplication

# Get the logger
logger = logging.getLogger(__name__)

class MDZExporter:
    """Class for handling MDZ export operations"""

    def __init__(self):
        """Initialize the MDZ exporter"""
        self.temp_dir = None
        self.files = []
        self.metadata = {}

    def export_to_mdz(self, markdown_text: str, output_file: str,
                      document_settings: Dict[str, Any],
                      assets: List[Dict[str, Any]] = None) -> bool:
        """
        Export markdown content to an MDZ file

        Args:
            markdown_text: The markdown content to export
            output_file: Path to save the MDZ file
            document_settings: Document settings to include in the metadata
            assets: List of assets to include in the bundle

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Create a temporary directory for the bundle contents
            self.temp_dir = tempfile.mkdtemp(prefix="mdz_export_")
            logger.debug(f"Created temporary directory: {self.temp_dir}")

            # Reset the file list
            self.files = []

            # Create the main markdown file
            main_file_path = os.path.join(self.temp_dir, "main.md")
            with open(main_file_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            self.files.append({"path": "main.md", "type": "markdown"})

            # Create the metadata file
            self.metadata = {
                "version": "1.0",
                "format": "mdz",
                "settings": document_settings
            }

            # Add timestamp
            import datetime
            self.metadata["created"] = datetime.datetime.now().isoformat()

            # Write metadata to YAML file
            metadata_path = os.path.join(self.temp_dir, "metadata.yaml")
            with open(metadata_path, "w", encoding="utf-8") as f:
                yaml.dump(self.metadata, f, default_flow_style=False)
            self.files.append({"path": "metadata.yaml", "type": "metadata"})

            # Process and include assets if provided
            if assets:
                for asset in assets:
                    self._add_asset(asset)

            # Create the manifest file
            manifest = {
                "files": self.files,
                "main": "main.md"
            }
            manifest_path = os.path.join(self.temp_dir, "manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            # Create the MDZ bundle
            self._create_mdz_bundle(output_file)

            # Clean up
            self._cleanup()

            return True

        except Exception as e:
            logger.error(f"Error exporting to MDZ: {str(e)}")
            self._cleanup()
            return False

    def _add_asset(self, asset: Dict[str, Any]) -> None:
        """
        Add an asset to the bundle

        Args:
            asset: Asset information dictionary with 'path', 'data', and 'type'
        """
        try:
            # Get asset information
            asset_path = asset.get("path", "")
            asset_data = asset.get("data", b"")
            asset_type = asset.get("type", "binary")

            if not asset_path:
                logger.warning("Asset path is empty, skipping")
                return

            # Create the assets directory if it doesn't exist
            assets_dir = os.path.join(self.temp_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)

            # Determine the target path
            target_path = os.path.join(assets_dir, os.path.basename(asset_path))

            # Write the asset
            if asset_type == "text":
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(asset_data)
            else:
                with open(target_path, "wb") as f:
                    f.write(asset_data)

            # Add to the file list
            self.files.append({
                "path": f"assets/{os.path.basename(asset_path)}",
                "type": asset_type
            })

        except Exception as e:
            logger.error(f"Error adding asset {asset.get('path', 'unknown')}: {str(e)}")

    def _create_mdz_bundle(self, output_file: str) -> None:
        """
        Create the MDZ bundle file using Zstandard compression

        Args:
            output_file: Path to save the MDZ file
        """
        try:
            # Create a temporary file for the bundle
            temp_bundle = tempfile.NamedTemporaryFile(delete=False, suffix=".mdz.tmp")
            temp_bundle.close()

            # Create a zip archive of the temp directory
            import zipfile
            with zipfile.ZipFile(temp_bundle.name, "w") as zipf:
                for root, _, files in os.walk(self.temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.temp_dir)
                        zipf.write(file_path, arcname)

            # Calculate the checksum of the zip file to use as the password
            with open(temp_bundle.name, "rb") as f:
                file_data = f.read()
                checksum = hashlib.sha256(file_data).hexdigest()

            # Compress the zip file with Zstandard using the checksum as the password
            compressor = zstd.ZstdCompressor(level=3, dict_data=zstd.ZstdCompressionDict(checksum.encode()))
            compressed_data = compressor.compress(file_data)

            # Write the compressed data to the output file
            with open(output_file, "wb") as f:
                f.write(compressed_data)

            # Clean up the temporary bundle file
            os.unlink(temp_bundle.name)

            logger.info(f"Created MDZ bundle: {output_file}")

        except Exception as e:
            logger.error(f"Error creating MDZ bundle: {str(e)}")
            raise

    def _cleanup(self) -> None:
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {str(e)}")
            finally:
                self.temp_dir = None


def create_mdz_file(markdown_path: str, output_file: str, assets: List[str] = None) -> bool:
    """
    Create an MDZ file from a markdown file

    Args:
        markdown_path: Path to the markdown file
        output_file: Path to save the MDZ file
        assets: List of asset file paths to include

    Returns:
        bool: True if creation was successful, False otherwise
    """
    try:
        # Read the markdown file
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        # Extract YAML front matter if present
        metadata = {}
        if markdown_text.startswith("---"):
            end_index = markdown_text.find("---", 3)
            if end_index != -1:
                yaml_content = markdown_text[3:end_index].strip()
                try:
                    metadata = yaml.safe_load(yaml_content)
                    # Remove the front matter from the markdown text
                    markdown_text = markdown_text[end_index+3:].strip()
                except Exception as e:
                    logger.warning(f"Error parsing YAML front matter: {str(e)}")

        # Create document settings from metadata
        document_settings = {
            "title": metadata.get("title", os.path.basename(markdown_path)),
            "author": metadata.get("author", ""),
            "date": metadata.get("date", ""),
            "tags": metadata.get("tags", []),
            "page": {
                "size": metadata.get("page_size", "A4"),
                "orientation": metadata.get("orientation", "portrait"),
                "margins": {
                    "top": metadata.get("margin_top", 25),
                    "right": metadata.get("margin_right", 25),
                    "bottom": metadata.get("margin_bottom", 25),
                    "left": metadata.get("margin_left", 25)
                }
            }
        }

        # Process assets
        asset_list = []
        if assets:
            for asset_path in assets:
                if os.path.exists(asset_path):
                    # Determine asset type
                    asset_type = "binary"
                    if asset_path.lower().endswith((".txt", ".md", ".json", ".yaml", ".yml", ".css", ".js", ".html", ".xml", ".svg")):
                        asset_type = "text"
                        with open(asset_path, "r", encoding="utf-8") as f:
                            asset_data = f.read()
                    else:
                        with open(asset_path, "rb") as f:
                            asset_data = f.read()

                    # Add to asset list
                    asset_list.append({
                        "path": asset_path,
                        "data": asset_data,
                        "type": asset_type
                    })

        # Create the MDZ exporter
        exporter = MDZExporter()

        # Export to MDZ
        return exporter.export_to_mdz(markdown_text, output_file, document_settings, asset_list)

    except Exception as e:
        logger.error(f"Error creating MDZ file: {str(e)}")
        return False

def extract_mdz_file(mdz_file: str, output_dir: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Extract an MDZ file

    Args:
        mdz_file: Path to the MDZ file
        output_dir: Directory to extract to (if None, a temporary directory is created)

    Returns:
        Tuple of (markdown_content, metadata)
    """
    try:
        # Create a temporary directory if output_dir is not provided
        temp_dir = output_dir or tempfile.mkdtemp(prefix="mdz_extract_")

        # Read the MDZ file
        with open(mdz_file, "rb") as f:
            compressed_data = f.read()

        # Calculate the checksum to use as the password
        checksum = hashlib.sha256(compressed_data).hexdigest()

        # Decompress the data using Zstandard with the checksum as the password
        decompressor = zstd.ZstdDecompressor(dict_data=zstd.ZstdCompressionDict(checksum.encode()))
        decompressed_data = decompressor.decompress(compressed_data)

        # Create a temporary file for the decompressed data
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.write(decompressed_data)
        temp_zip.close()

        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(temp_zip.name, "r") as zipf:
            zipf.extractall(temp_dir)

        # Clean up the temporary zip file
        os.unlink(temp_zip.name)

        # Read the manifest file
        manifest_path = os.path.join(temp_dir, "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Get the main markdown file
        main_file = manifest.get("main", "main.md")
        main_file_path = os.path.join(temp_dir, main_file)

        # Read the markdown content
        with open(main_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Read the metadata file
        metadata_path = os.path.join(temp_dir, "metadata.yaml")
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        # Clean up if output_dir was not provided
        if not output_dir:
            shutil.rmtree(temp_dir)

        return markdown_content, metadata

    except Exception as e:
        logger.error(f"Error extracting MDZ file: {str(e)}")
        return "", {}
