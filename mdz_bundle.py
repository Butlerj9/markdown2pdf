#!/usr/bin/env python3
"""
MDZ Bundle Format Handler
------------------------
This module provides functionality to read and write .mdz files,
which are Markdown documents bundled with assets using Zstandard compression.

File: mdz_bundle.py
"""

import os
import io
import json
import tarfile
import tempfile
import shutil
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO, Tuple, Any

# Import Zstandard library
try:
    import zstandard as zstd
except ImportError:
    raise ImportError("Zstandard library not found. Please install it with 'pip install zstandard'")

# Configure logger
logger = logging.getLogger(__name__)

class MDZBundle:
    """
    Class for handling .mdz bundle files (Markdown + assets with Zstandard compression)
    """
    
    # Default bundle structure
    DEFAULT_STRUCTURE = {
        "index.md": "",  # Main Markdown document
        "metadata.yaml": "",  # Optional YAML metadata
        "mermaid/": {},  # Directory for Mermaid diagram files
        "images/": {},  # Directory for image files
        "additional_assets/": {}  # Directory for any additional files
    }
    
    def __init__(self, compression_level: int = 3):
        """
        Initialize a new MDZ bundle
        
        Args:
            compression_level: Zstandard compression level (1-22, default: 3)
        """
        self.compression_level = min(max(1, compression_level), 22)  # Ensure valid compression level
        self.content = {}
        self.temp_dir = None
        self.main_content = ""
        self.metadata = {}
        self.extracted_paths = {}
        
        # Initialize with default structure
        for path in self.DEFAULT_STRUCTURE:
            if path.endswith('/'):
                self.content[path] = {}
            else:
                self.content[path] = self.DEFAULT_STRUCTURE[path]
    
    def create_from_markdown(self, markdown_content: str, metadata: Optional[Dict] = None) -> None:
        """
        Create a new MDZ bundle from markdown content and optional metadata
        
        Args:
            markdown_content: The main markdown content
            metadata: Optional metadata dictionary
        """
        self.main_content = markdown_content
        self.content["index.md"] = markdown_content
        
        if metadata:
            self.metadata = metadata
            self.content["metadata.yaml"] = yaml.dump(metadata, default_flow_style=False)
    
    def add_file(self, file_path: str, content: Union[str, bytes], internal_path: Optional[str] = None) -> str:
        """
        Add a file to the bundle
        
        Args:
            file_path: Original file path
            content: File content (string or bytes)
            internal_path: Path within the bundle (if None, will be determined automatically)
            
        Returns:
            The internal path where the file was stored
        """
        # Determine the internal path if not provided
        if internal_path is None:
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.mmd', '.mermaid']:
                internal_path = f"mermaid/{filename}"
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                internal_path = f"images/{filename}"
            else:
                internal_path = f"additional_assets/{filename}"
        
        # Ensure the directory exists in the bundle
        dir_path = os.path.dirname(internal_path)
        if dir_path:
            self._ensure_directory(dir_path)
        
        # Add the file to the bundle
        self.content[internal_path] = content
        logger.debug(f"Added file to bundle: {internal_path}")
        
        return internal_path
    
    def _ensure_directory(self, dir_path: str) -> None:
        """
        Ensure a directory exists in the bundle
        
        Args:
            dir_path: Directory path within the bundle
        """
        # Normalize path to use forward slashes and end with a slash
        dir_path = dir_path.replace('\\', '/')
        if not dir_path.endswith('/'):
            dir_path += '/'
        
        # Create the directory if it doesn't exist
        if dir_path not in self.content:
            self.content[dir_path] = {}
            logger.debug(f"Created directory in bundle: {dir_path}")
    
    def extract_front_matter(self, markdown_content: str) -> Tuple[str, Dict]:
        """
        Extract YAML front matter from markdown content
        
        Args:
            markdown_content: Markdown content with potential front matter
            
        Returns:
            Tuple of (markdown_without_front_matter, front_matter_dict)
        """
        import re
        
        # Regular expression to match YAML front matter
        front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(front_matter_pattern, markdown_content, re.DOTALL)
        
        if match:
            front_matter_text = match.group(1)
            try:
                front_matter = yaml.safe_load(front_matter_text)
                if not isinstance(front_matter, dict):
                    front_matter = {}
            except Exception as e:
                logger.warning(f"Error parsing front matter: {str(e)}")
                front_matter = {}
            
            # Remove front matter from markdown
            markdown_without_front_matter = markdown_content[match.end():]
            return markdown_without_front_matter, front_matter
        
        # No front matter found
        return markdown_content, {}
    
    def save(self, output_path: str) -> None:
        """
        Save the bundle to a .mdz file
        
        Args:
            output_path: Path to save the .mdz file
        """
        # Create a temporary directory for building the tar file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the bundle structure in the temporary directory
            for path, content in self.content.items():
                full_path = os.path.join(temp_dir, path)
                
                if isinstance(content, dict):  # Directory
                    os.makedirs(full_path, exist_ok=True)
                else:  # File
                    # Create parent directories if they don't exist
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Write the file content
                    mode = 'wb' if isinstance(content, bytes) else 'w'
                    with open(full_path, mode) as f:
                        f.write(content)
            
            # Create a tar file in memory
            tar_data = io.BytesIO()
            with tarfile.open(fileobj=tar_data, mode='w') as tar:
                # Add all files from the temporary directory
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        tar.add(file_path, arcname=arcname)
            
            # Compress the tar data with Zstandard
            tar_data.seek(0)
            compressor = zstd.ZstdCompressor(level=self.compression_level)
            compressed_data = compressor.compress(tar_data.getvalue())
            
            # Write the compressed data to the output file
            with open(output_path, 'wb') as f:
                f.write(compressed_data)
            
            logger.info(f"Saved MDZ bundle to {output_path} (compression level: {self.compression_level})")
    
    def load(self, input_path: str) -> None:
        """
        Load a .mdz file
        
        Args:
            input_path: Path to the .mdz file
        """
        # Read the compressed data
        with open(input_path, 'rb') as f:
            compressed_data = f.read()
        
        # Decompress the data
        decompressor = zstd.ZstdDecompressor()
        tar_data = io.BytesIO(decompressor.decompress(compressed_data))
        
        # Clear existing content
        self.content = {}
        
        # Extract the tar file
        with tarfile.open(fileobj=tar_data, mode='r') as tar:
            for member in tar.getmembers():
                if member.isdir():
                    # Add directory to content
                    dir_path = member.name
                    if not dir_path.endswith('/'):
                        dir_path += '/'
                    self.content[dir_path] = {}
                else:
                    # Extract file content
                    f = tar.extractfile(member)
                    if f is not None:
                        content = f.read()
                        
                        # Try to decode as text if it's a text file
                        if member.name.endswith(('.md', '.txt', '.yaml', '.yml', '.json', '.mmd', '.mermaid')):
                            try:
                                content = content.decode('utf-8')
                            except UnicodeDecodeError:
                                # Keep as binary if decoding fails
                                pass
                        
                        self.content[member.name] = content
        
        # Extract main content and metadata
        if "index.md" in self.content:
            self.main_content = self.content["index.md"]
            
            # Check for front matter in the main content
            if isinstance(self.main_content, str):
                markdown_content, front_matter = self.extract_front_matter(self.main_content)
                if front_matter:
                    self.metadata.update(front_matter)
                    self.main_content = markdown_content
        
        # Load metadata from metadata.yaml if it exists
        if "metadata.yaml" in self.content and isinstance(self.content["metadata.yaml"], str):
            try:
                yaml_metadata = yaml.safe_load(self.content["metadata.yaml"])
                if isinstance(yaml_metadata, dict):
                    self.metadata.update(yaml_metadata)
            except Exception as e:
                logger.warning(f"Error parsing metadata.yaml: {str(e)}")
        
        logger.info(f"Loaded MDZ bundle from {input_path}")
    
    def extract_to_directory(self, output_dir: str) -> Dict[str, str]:
        """
        Extract the bundle to a directory
        
        Args:
            output_dir: Directory to extract to
            
        Returns:
            Dictionary mapping internal paths to extracted file paths
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear the extracted paths dictionary
        self.extracted_paths = {}
        
        # Extract all files
        for path, content in self.content.items():
            if isinstance(content, dict):  # Directory
                # Create the directory
                dir_path = os.path.join(output_dir, path)
                os.makedirs(dir_path, exist_ok=True)
            else:  # File
                # Create parent directories if they don't exist
                file_path = os.path.join(output_dir, path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write the file content
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(file_path, mode) as f:
                    f.write(content)
                
                # Add to extracted paths
                self.extracted_paths[path] = file_path
        
        logger.info(f"Extracted MDZ bundle to {output_dir}")
        return self.extracted_paths
    
    def extract_to_temp(self) -> Dict[str, str]:
        """
        Extract the bundle to a temporary directory
        
        Returns:
            Dictionary mapping internal paths to extracted file paths
        """
        # Create a new temporary directory
        if self.temp_dir:
            # Clean up previous temporary directory
            self.cleanup_temp()
        
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_bundle_")
        
        # Extract to the temporary directory
        return self.extract_to_directory(self.temp_dir)
    
    def cleanup_temp(self) -> None:
        """
        Clean up the temporary directory
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.extracted_paths = {}
            logger.debug("Cleaned up temporary directory")
    
    def get_main_content(self) -> str:
        """
        Get the main markdown content
        
        Returns:
            The main markdown content
        """
        return self.main_content
    
    def get_metadata(self) -> Dict:
        """
        Get the metadata
        
        Returns:
            The metadata dictionary
        """
        return self.metadata
    
    def get_asset_path(self, internal_path: str) -> Optional[str]:
        """
        Get the path to an extracted asset
        
        Args:
            internal_path: Internal path within the bundle
            
        Returns:
            The path to the extracted asset, or None if not found
        """
        return self.extracted_paths.get(internal_path)
    
    def __enter__(self):
        """
        Context manager entry
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - clean up temporary directory
        """
        self.cleanup_temp()


def create_mdz_from_markdown_file(markdown_file: str, output_file: str, 
                                 compression_level: int = 3,
                                 include_images: bool = True,
                                 base_dir: Optional[str] = None) -> None:
    """
    Create an MDZ bundle from a markdown file
    
    Args:
        markdown_file: Path to the markdown file
        output_file: Path to save the MDZ bundle
        compression_level: Zstandard compression level (1-22, default: 3)
        include_images: Whether to include referenced images
        base_dir: Base directory for resolving relative paths (defaults to markdown file's directory)
    """
    # Determine base directory
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(markdown_file))
    
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Create a new MDZ bundle
    bundle = MDZBundle(compression_level=compression_level)
    
    # Extract front matter
    markdown_without_front_matter, front_matter = bundle.extract_front_matter(markdown_content)
    
    # Create the bundle from the markdown content
    bundle.create_from_markdown(markdown_content, front_matter)
    
    # Include referenced images if requested
    if include_images:
        import re
        
        # Find all image references in the markdown
        image_pattern = r'!\[.*?\]\((.*?)\)'
        image_references = re.findall(image_pattern, markdown_content)
        
        for image_ref in image_references:
            # Skip URLs
            if image_ref.startswith(('http://', 'https://')):
                continue
            
            # Resolve the image path
            image_path = os.path.join(base_dir, image_ref)
            
            if os.path.exists(image_path):
                try:
                    # Read the image file
                    with open(image_path, 'rb') as f:
                        image_content = f.read()
                    
                    # Add the image to the bundle
                    bundle.add_file(image_path, image_content)
                except Exception as e:
                    logger.warning(f"Error adding image {image_path}: {str(e)}")
    
    # Save the bundle
    bundle.save(output_file)
    logger.info(f"Created MDZ bundle {output_file} from {markdown_file}")


def extract_mdz_to_markdown(mdz_file: str, output_file: str, extract_assets: bool = True) -> Dict:
    """
    Extract an MDZ bundle to a markdown file
    
    Args:
        mdz_file: Path to the MDZ bundle
        output_file: Path to save the markdown file
        extract_assets: Whether to extract assets
        
    Returns:
        Metadata dictionary
    """
    # Create a new MDZ bundle
    bundle = MDZBundle()
    
    # Load the MDZ bundle
    bundle.load(mdz_file)
    
    # Get the main content
    main_content = bundle.get_main_content()
    
    # Write the markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    # Extract assets if requested
    if extract_assets:
        # Extract to the same directory as the output file
        output_dir = os.path.dirname(os.path.abspath(output_file))
        bundle.extract_to_directory(output_dir)
    
    logger.info(f"Extracted MDZ bundle {mdz_file} to {output_file}")
    return bundle.get_metadata()


if __name__ == "__main__":
    # Example usage
    import argparse
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MDZ Bundle Format Handler')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create an MDZ bundle from a markdown file')
    create_parser.add_argument('markdown_file', help='Path to the markdown file')
    create_parser.add_argument('output_file', help='Path to save the MDZ bundle')
    create_parser.add_argument('--compression', type=int, default=3, 
                              help='Zstandard compression level (1-22, default: 3)')
    create_parser.add_argument('--no-images', action='store_true', 
                              help='Do not include referenced images')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract an MDZ bundle to a markdown file')
    extract_parser.add_argument('mdz_file', help='Path to the MDZ bundle')
    extract_parser.add_argument('output_file', help='Path to save the markdown file')
    extract_parser.add_argument('--no-assets', action='store_true', 
                               help='Do not extract assets')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'create':
        create_mdz_from_markdown_file(
            args.markdown_file, 
            args.output_file, 
            compression_level=args.compression,
            include_images=not args.no_images
        )
    elif args.command == 'extract':
        extract_mdz_to_markdown(
            args.mdz_file, 
            args.output_file, 
            extract_assets=not args.no_assets
        )
    else:
        parser.print_help()
