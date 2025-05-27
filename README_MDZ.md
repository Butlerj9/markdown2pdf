# Markdown to PDF Converter with MDZ Support

This project extends the existing Markdown to PDF Converter application to support the new `.mdz` format, which is a compressed Markdown document bundle that includes the main document, metadata, and associated assets.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [MDZ Format](#mdz-format)
- [Integration with External Editors](#integration-with-external-editors)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Markdown to PDF Converter application has been extended to support the `.mdz` format, which allows bundling Markdown documents with their associated assets (images, diagrams, etc.) in a single compressed file. This makes it easier to share and distribute Markdown documents with all their dependencies.

## Features

- **MDZ Format Support**: Open, save, and export `.mdz` files directly from the application.
- **GitHub Flavored Markdown**: Full support for GFM syntax including tables, task lists, and fenced code blocks.
- **YAML Front Matter**: Metadata can be included in YAML format at the beginning of the document.
- **Mermaid Diagrams**: Embedded Mermaid diagrams are supported and can be pre-rendered to SVG.
- **SVG Embedding**: SVG images can be embedded directly in the document.
- **LaTeX Math**: Mathematical expressions using LaTeX syntax are supported via MathJax or KaTeX.
- **Asset Bundling**: All referenced assets (images, diagrams, etc.) are bundled with the document.
- **Export Support**: Export to PDF, HTML, EPUB, and DOCX formats.
- **External Editor Integration**: Integration with VS Code, Obsidian, and Typora.

## Installation

### Prerequisites

- Python 3.6+
- PyQt6
- Pandoc
- Zstandard

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/markdown-to-pdf-converter.git
   cd markdown-to-pdf-converter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install additional dependencies for MDZ support:
   ```bash
   pip install zstandard markdown pyyaml pymdown-extensions
   ```

4. Run the application with MDZ support:
   ```bash
   python main_with_mdz.py
   ```

## Usage

### Opening an MDZ File

1. Launch the application
2. Click on "File" > "Open"
3. Select a `.mdz` file
4. The file will be extracted and opened in the editor

### Saving as MDZ

1. Edit your Markdown document
2. Click on "File" > "Save As"
3. Select "MDZ Bundles (*.mdz)" from the file type dropdown
4. Enter a file name and click "Save"

### Exporting to MDZ

1. Open a Markdown document
2. Click on "File" > "Export to MDZ"
3. Select a location to save the MDZ file
4. Click "Save"

### Importing from MDZ

1. Click on "File" > "Import from MDZ"
2. Select a `.mdz` file
3. The file will be extracted and opened in the editor

### Exporting to Other Formats

1. Open a Markdown or MDZ document
2. Click on "File" > "Export to PDF/HTML/EPUB/DOCX"
3. Select a location to save the exported file
4. Click "Save"

## MDZ Format

The MDZ format is a compressed Markdown document bundle that includes:

- The main Markdown document (`index.md`)
- YAML metadata (`metadata.yaml`)
- Embedded assets (images, SVGs, etc.)
- Mermaid diagrams
- Additional resources

The bundle is compressed using Zstandard (zstd) compression, providing excellent compression ratios while maintaining fast decompression speeds.

For more details, see the [MDZ Format Specification](MDZ_FORMAT.md).

## Integration with External Editors

The MDZ format can be integrated with various external editors:

- **Visual Studio Code**: Using a custom extension for MDZ support.
- **Obsidian**: Using a plugin for MDZ support.
- **Typora**: Using external scripts for MDZ integration.

For detailed integration instructions, see the [MDZ Editor Integration Guide](MDZ_EDITOR_INTEGRATION.md).

## API Reference

### Python API

```python
from mdz_bundle import MDZBundle, create_mdz_from_markdown_file, extract_mdz_to_markdown

# Create an MDZ bundle
bundle = MDZBundle()
bundle.create_from_markdown("# Hello World", {"title": "Example"})
bundle.add_file("image.png", image_data)
bundle.save("document.mdz")

# Load an MDZ bundle
bundle = MDZBundle()
bundle.load("document.mdz")
content = bundle.get_main_content()
metadata = bundle.get_metadata()

# Extract an MDZ bundle
extract_mdz_to_markdown("document.mdz", "document.md")

# Create an MDZ bundle from a file
create_mdz_from_markdown_file("document.md", "document.mdz")
```

### Command-Line Tools

```bash
# Create an MDZ bundle from a Markdown file
python mdz_bundle.py create document.md document.mdz

# Extract an MDZ bundle to a Markdown file
python mdz_bundle.py extract document.mdz document.md
```

## Testing

To test the MDZ format implementation:

```bash
# Test all components
python test_mdz_format.py --all

# Test only the MDZ bundle implementation
python test_mdz_format.py --bundle

# Test only the MDZ renderer implementation
python test_mdz_format.py --renderer
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing dependencies, install them:
```bash
pip install zstandard markdown pyyaml pymdown-extensions
```

### Path Issues

Ensure that the `mdz_bundle.py` and `mdz_renderer.py` files are in your Python path or specify the full path to them in your scripts.

### Permission Issues

Make sure your scripts have execute permissions:
```bash
chmod +x test_mdz_format.py
```

### Rendering Issues

If you encounter issues with rendering Mermaid diagrams or LaTeX math:
- Make sure you have the required dependencies installed
- Check the console for error messages
- Try using a different rendering engine

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
