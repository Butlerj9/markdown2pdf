#!/usr/bin/env python3
"""
Unified MDZ Format Handler
------------------------
This module provides a unified interface for reading and writing .mdz files,
supporting both tar-based and checksum dictionary compression methods.

File: unified_mdz.py
"""

import os
import io
import json
import tarfile
import tempfile
import shutil
import logging
import yaml
import hashlib
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO, Tuple, Any

# Import Zstandard library
try:
    import zstandard as zstd
except ImportError:
    raise ImportError("Zstandard library not found. Please install it with 'pip install zstandard'")

# Configure logger
logger = logging.getLogger(__name__)

class CompressionMethod:
    """Enum for compression methods"""
    STANDARD = "standard"  # Tar-based approach
    SECURE = "secure"      # Checksum dictionary approach

class UnifiedMDZ:
    """
    Unified class for handling .mdz bundle files with multiple compression methods
    """

    # Default bundle structure
    DEFAULT_STRUCTURE = {
        "index.md": "",  # Main Markdown document
        "metadata.yaml": "",  # Optional YAML metadata
        "mermaid/": {},  # Directory for Mermaid diagram files
        "images/": {},  # Directory for image files
        "additional_assets/": {}  # Directory for any additional files
    }

    def __init__(self, compression_level: int = 3, compression_method: str = CompressionMethod.STANDARD):
        """
        Initialize a new MDZ bundle

        Args:
            compression_level: Zstandard compression level (1-22, default: 3)
            compression_method: Compression method to use (standard or secure)
        """
        self.compression_level = min(max(1, compression_level), 22)  # Ensure valid compression level
        self.compression_method = compression_method
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

    def add_file(self, path: str, content: Union[str, bytes]) -> None:
        """
        Add a file to the MDZ bundle

        Args:
            path: Path within the bundle
            content: File content (string or bytes)
        """
        self.content[path] = content

    def add_directory(self, path: str) -> None:
        """
        Add a directory to the MDZ bundle

        Args:
            path: Directory path within the bundle
        """
        if not path.endswith('/'):
            path += '/'
        self.content[path] = {}

    def get_main_content(self) -> str:
        """
        Get the main markdown content

        Returns:
            Main markdown content
        """
        return self.main_content

    def get_metadata(self) -> Dict:
        """
        Get the metadata

        Returns:
            Metadata dictionary
        """
        return self.metadata

    def extract_front_matter(self, content: str) -> Tuple[str, Dict]:
        """
        Extract YAML front matter from markdown content

        Args:
            content: Markdown content

        Returns:
            Tuple of (content_without_front_matter, front_matter_dict)
        """
        front_matter = {}
        content_without_front_matter = content

        # Check for YAML front matter
        if content.startswith('---'):
            try:
                # Find the end of the front matter
                end_index = content.find('---', 3)
                if end_index != -1:
                    # Extract the front matter
                    front_matter_text = content[3:end_index].strip()
                    front_matter = yaml.safe_load(front_matter_text) or {}

                    # Remove the front matter from the content
                    content_without_front_matter = content[end_index + 3:].strip()
            except Exception as e:
                logger.warning(f"Error parsing front matter: {str(e)}")

        return content_without_front_matter, front_matter

    def save(self, output_path: str) -> None:
        """
        Save the MDZ bundle to a file

        Args:
            output_path: Path to save the MDZ bundle
        """
        if self.compression_method == CompressionMethod.STANDARD:
            self._save_standard(output_path)
        else:
            self._save_secure(output_path)

    def _save_standard(self, output_path: str) -> None:
        """
        Save using the standard (tar-based) method

        Args:
            output_path: Path to save the MDZ bundle
        """
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="mdz_save_")

            # Write all files to the temporary directory
            for path, content in self.content.items():
                if isinstance(content, dict):  # Directory
                    # Create the directory
                    dir_path = os.path.join(temp_dir, path)
                    os.makedirs(dir_path, exist_ok=True)
                else:  # File
                    # Create parent directories if they don't exist
                    file_path = os.path.join(temp_dir, path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Write the file content
                    mode = 'wb' if isinstance(content, bytes) else 'w'
                    with open(file_path, mode) as f:
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

            # Clean up the temporary directory
            shutil.rmtree(temp_dir)

            logger.info(f"Saved MDZ bundle to {output_path} (compression level: {self.compression_level}, method: standard)")
        except Exception as e:
            logger.error(f"Error saving MDZ bundle: {str(e)}")
            raise

    def _save_secure(self, output_path: str) -> None:
        """
        Save using the secure (checksum dictionary) method

        Args:
            output_path: Path to save the MDZ bundle
        """
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp(prefix="mdz_save_")

            # Write all files to the temporary directory
            for path, content in self.content.items():
                if isinstance(content, dict):  # Directory
                    # Create the directory
                    dir_path = os.path.join(temp_dir, path)
                    os.makedirs(dir_path, exist_ok=True)
                else:  # File
                    # Create parent directories if they don't exist
                    file_path = os.path.join(temp_dir, path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Write the file content
                    mode = 'wb' if isinstance(content, bytes) else 'w'
                    with open(file_path, mode) as f:
                        f.write(content)

            # Create a temporary zip file
            temp_bundle = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")

            # Create a zip file with all the content
            with zipfile.ZipFile(temp_bundle.name, "w") as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname=arcname)

            # Read the zip file
            with open(temp_bundle.name, "rb") as f:
                file_data = f.read()

            # Calculate the checksum to use as the password
            checksum = hashlib.sha256(file_data).hexdigest()

            # Compress the zip file with Zstandard using the checksum as the password
            compressor = zstd.ZstdCompressor(level=self.compression_level, dict_data=zstd.ZstdCompressionDict(checksum.encode()))
            compressed_data = compressor.compress(file_data)

            # Write the compressed data to the output file
            with open(output_path, "wb") as f:
                f.write(compressed_data)

            # Clean up temporary files
            os.unlink(temp_bundle.name)
            shutil.rmtree(temp_dir)

            logger.info(f"Saved MDZ bundle to {output_path} (compression level: {self.compression_level}, method: secure)")
        except Exception as e:
            logger.error(f"Error saving MDZ bundle: {str(e)}")
            raise

    def load(self, input_path: str) -> None:
        """
        Load a .mdz file

        Args:
            input_path: Path to the .mdz file
        """
        # Read the compressed data
        with open(input_path, 'rb') as f:
            compressed_data = f.read()

        # Try both methods to load the file
        try:
            # First try the standard method
            self._load_standard(compressed_data)
            self.compression_method = CompressionMethod.STANDARD
        except Exception as e:
            logger.debug(f"Standard loading failed, trying secure method: {str(e)}")
            try:
                # If that fails, try the secure method
                self._load_secure(compressed_data)
                self.compression_method = CompressionMethod.SECURE
            except Exception as e2:
                # If both fail, raise an error
                logger.error(f"Error loading MDZ bundle: {str(e2)}")
                raise ValueError(f"Could not load MDZ file with either method. Standard error: {str(e)}, Secure error: {str(e2)}")

    def _load_standard(self, compressed_data: bytes) -> None:
        """
        Load using the standard (tar-based) method

        Args:
            compressed_data: Compressed data
        """
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
        self._process_content()

    def _load_secure(self, compressed_data: bytes) -> None:
        """
        Load using the secure (checksum dictionary) method

        Args:
            compressed_data: Compressed data
        """
        # Calculate the checksum to use as the password
        checksum = hashlib.sha256(compressed_data).hexdigest()

        # Decompress the data using Zstandard with the checksum as the password
        decompressor = zstd.ZstdDecompressor(dict_data=zstd.ZstdCompressionDict(checksum.encode()))
        decompressed_data = decompressor.decompress(compressed_data)

        # Create a temporary file for the decompressed data
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.write(decompressed_data)
        temp_zip.close()

        # Clear existing content
        self.content = {}

        # Extract the zip file
        with zipfile.ZipFile(temp_zip.name, "r") as zipf:
            for info in zipf.infolist():
                if info.filename.endswith('/'):
                    # Add directory to content
                    self.content[info.filename] = {}
                else:
                    # Extract file content
                    content = zipf.read(info.filename)

                    # Try to decode as text if it's a text file
                    if info.filename.endswith(('.md', '.txt', '.yaml', '.yml', '.json', '.mmd', '.mermaid')):
                        try:
                            content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            # Keep as binary if decoding fails
                            pass

                    self.content[info.filename] = content

        # Clean up the temporary file
        os.unlink(temp_zip.name)

        # Extract main content and metadata
        self._process_content()

    def _process_content(self) -> None:
        """Process the loaded content to extract main content and metadata"""
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

    def extract_to_directory(self, output_dir: str) -> Dict[str, str]:
        """
        Extract all files to a directory

        Args:
            output_dir: Directory to extract to

        Returns:
            Dictionary mapping bundle paths to extracted file paths
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Clear extracted paths
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
        Extract all files to a temporary directory

        Returns:
            Dictionary mapping bundle paths to extracted file paths
        """
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="mdz_extract_")

        # Extract to the temporary directory
        return self.extract_to_directory(self.temp_dir)

    def cleanup(self) -> None:
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def get_file_types(self) -> Dict[str, int]:
        """
        Get a dictionary of file types and their counts in the bundle

        Returns:
            Dictionary mapping file extensions to counts
        """
        file_types = {}
        for path in self.content:
            if isinstance(self.content[path], dict):
                continue  # Skip directories

            # Get the file extension
            ext = os.path.splitext(path)[1].lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                file_types['(no extension)'] = file_types.get('(no extension)', 0) + 1

        return file_types

    def get_file_sizes(self) -> Dict[str, int]:
        """
        Get a dictionary of file sizes in the bundle

        Returns:
            Dictionary mapping file paths to sizes in bytes
        """
        file_sizes = {}
        for path in self.content:
            if isinstance(self.content[path], dict):
                continue  # Skip directories

            # Get the file size
            content = self.content[path]
            if isinstance(content, str):
                file_sizes[path] = len(content.encode('utf-8'))
            else:
                file_sizes[path] = len(content)

        return file_sizes

    def get_total_size(self) -> int:
        """
        Get the total size of all files in the bundle

        Returns:
            Total size in bytes
        """
        return sum(self.get_file_sizes().values())

    def get_file_list(self, file_type: str = None) -> List[str]:
        """
        Get a list of files in the bundle, optionally filtered by file type

        Args:
            file_type: File extension to filter by (e.g., '.md', '.png')

        Returns:
            List of file paths
        """
        if file_type:
            return [path for path in self.content if not isinstance(self.content[path], dict) and path.lower().endswith(file_type.lower())]
        else:
            return [path for path in self.content if not isinstance(self.content[path], dict)]

    def get_directory_list(self) -> List[str]:
        """
        Get a list of directories in the bundle

        Returns:
            List of directory paths
        """
        return [path for path in self.content if isinstance(self.content[path], dict)]


# Utility functions

def create_mdz_from_markdown_file(markdown_file: str, output_file: str,
                                 compression_level: int = 3,
                                 compression_method: str = CompressionMethod.STANDARD,
                                 include_images: bool = True,
                                 base_dir: Optional[str] = None) -> None:
    """
    Create an MDZ bundle from a markdown file

    Args:
        markdown_file: Path to the markdown file
        output_file: Path to save the MDZ bundle
        compression_level: Zstandard compression level (1-22, default: 3)
        compression_method: Compression method to use (standard or secure)
        include_images: Whether to include referenced images
        base_dir: Base directory for resolving relative paths (defaults to markdown file's directory)
    """
    # Determine base directory
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(markdown_file))

    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Extract front matter
    markdown_without_front_matter, front_matter = UnifiedMDZ().extract_front_matter(markdown_content)

    # Create a new MDZ bundle
    bundle = UnifiedMDZ(compression_level=compression_level, compression_method=compression_method)
    bundle.create_from_markdown(markdown_content, front_matter)

    # Include images if requested
    if include_images:
        # Find all image references in the markdown
        import re
        image_pattern = r'!\[.*?\]\((.*?)\)'
        image_refs = re.findall(image_pattern, markdown_without_front_matter)

        for image_ref in image_refs:
            # Skip external URLs
            if image_ref.startswith(('http://', 'https://')):
                continue

            # Resolve the image path
            image_path = os.path.join(base_dir, image_ref)
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()

                    # Add the image to the bundle
                    bundle.add_file(image_ref, image_data)

                    # Create parent directories if needed
                    dir_path = os.path.dirname(image_ref)
                    if dir_path and dir_path + '/' not in bundle.content:
                        bundle.add_directory(dir_path)
                except Exception as e:
                    logger.warning(f"Error adding image {image_ref}: {str(e)}")

    # Save the bundle
    bundle.save(output_file)

    logger.info(f"Created MDZ bundle from {markdown_file} at {output_file}")


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
    bundle = UnifiedMDZ()

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

    # Return the metadata
    return bundle.get_metadata()


def get_mdz_info(mdz_file: str) -> Dict:
    """
    Get information about an MDZ file

    Args:
        mdz_file: Path to the MDZ file

    Returns:
        Dictionary with MDZ file information
    """
    # Get the file size
    file_size = os.path.getsize(mdz_file)

    # Create a new MDZ bundle
    bundle = UnifiedMDZ()

    # Load the MDZ bundle
    bundle.load(mdz_file)

    # Get file information
    file_types = bundle.get_file_types()
    file_sizes = bundle.get_file_sizes()
    total_uncompressed_size = bundle.get_total_size()

    # Calculate compression ratio
    compression_ratio = total_uncompressed_size / file_size if file_size > 0 else 0

    # Get metadata
    metadata = bundle.get_metadata()

    # Return the information
    return {
        'file_size': file_size,
        'compression_method': bundle.compression_method,
        'file_types': file_types,
        'file_count': len(bundle.get_file_list()),
        'directory_count': len(bundle.get_directory_list()),
        'total_uncompressed_size': total_uncompressed_size,
        'compression_ratio': compression_ratio,
        'metadata': metadata
    }


if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Unified MDZ Format Handler')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create an MDZ bundle from a markdown file')
    create_parser.add_argument('markdown_file', help='Path to the markdown file')
    create_parser.add_argument('output_file', help='Path to save the MDZ bundle')
    create_parser.add_argument('--compression', type=int, default=3,
                              help='Zstandard compression level (1-22, default: 3)')
    create_parser.add_argument('--method', choices=['standard', 'secure'], default='standard',
                              help='Compression method to use (standard or secure, default: standard)')
    create_parser.add_argument('--no-images', action='store_true',
                              help='Do not include referenced images')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract an MDZ bundle to a markdown file')
    extract_parser.add_argument('mdz_file', help='Path to the MDZ bundle')
    extract_parser.add_argument('output_file', help='Path to save the markdown file')
    extract_parser.add_argument('--no-assets', action='store_true',
                               help='Do not extract assets')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get information about an MDZ file')
    info_parser.add_argument('mdz_file', help='Path to the MDZ file')

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Run the command
    if args.command == 'create':
        create_mdz_from_markdown_file(
            args.markdown_file,
            args.output_file,
            compression_level=args.compression,
            compression_method=args.method,
            include_images=not args.no_images
        )
    elif args.command == 'extract':
        extract_mdz_to_markdown(
            args.mdz_file,
            args.output_file,
            extract_assets=not args.no_assets
        )
    elif args.command == 'info':
        info = get_mdz_info(args.mdz_file)

        # Print the information
        print(f"MDZ File: {args.mdz_file}")
        print(f"File Size: {info['file_size']} bytes")
        print(f"Compression Method: {info['compression_method']}")
        print(f"Compression Ratio: {info['compression_ratio']:.2f}x")
        print(f"Total Uncompressed Size: {info['total_uncompressed_size']} bytes")
        print(f"File Count: {info['file_count']}")
        print(f"Directory Count: {info['directory_count']}")
        print("File Types:")
        for ext, count in info['file_types'].items():
            print(f"  {ext}: {count}")
        print("Metadata:")
        for key, value in info['metadata'].items():
            print(f"  {key}: {value}")
    else:
        parser.print_help()
