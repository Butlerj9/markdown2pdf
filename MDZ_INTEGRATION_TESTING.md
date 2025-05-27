# MDZ Format Integration and Testing

This document provides comprehensive instructions for integrating and testing the MDZ format in the Markdown rendering application.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Testing](#testing)
  - [Basic Tests](#basic-tests)
  - [Compression Tests](#compression-tests)
  - [Export Tests](#export-tests)
  - [Editor Integration Tests](#editor-integration-tests)
- [Integration with External Editors](#integration-with-external-editors)
  - [Visual Studio Code](#visual-studio-code)
  - [Obsidian](#obsidian)
  - [Typora](#typora)
- [Troubleshooting](#troubleshooting)

## Overview

The MDZ format (`.mdz`) is a compressed Markdown document bundle that includes the main document, metadata, and associated assets (images, diagrams, etc.) in a single file. This document provides instructions for integrating and testing the MDZ format in the Markdown rendering application.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.6 or higher
- Zstandard library (`zstandard`)
- Markdown parsing library (one of: `markdown-it-py`, `markdown`, `mistune`)
- YAML parsing library (`pyyaml`)
- Image processing library (`Pillow`)
- Pandoc (for export functionality)

You can check and install the required dependencies using the provided script:

```bash
python check_mdz_dependencies.py
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/markdown-renderer.git
   cd markdown-renderer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r mdz_requirements.txt
   ```

3. Run the dependency checker:
   ```bash
   python check_mdz_dependencies.py
   ```

4. Run the main application with MDZ support:
   ```bash
   python main_with_mdz.py
   ```

## Testing

The MDZ format comes with a comprehensive test suite that covers various aspects of the implementation. You can run all tests using the provided script:

```bash
python run_mdz_tests.py --all
```

Or you can run specific tests:

```bash
python run_mdz_tests.py --basic
python run_mdz_tests.py --compression
python run_mdz_tests.py --export
python run_mdz_tests.py --editor
```

### Basic Tests

The basic tests cover the core functionality of the MDZ format:

- MDZ bundle creation and extraction
- Markdown parsing and rendering
- Front matter extraction
- Mermaid diagram rendering
- LaTeX math rendering

To run the basic tests:

```bash
python test_mdz_basic.py --all
```

### Compression Tests

The compression tests focus on the Zstandard compression functionality:

- Different compression levels
- Compression and decompression speed
- Repeated compression and decompression
- Handling of corrupted files

To run the compression tests:

```bash
python test_mdz_compression.py --all
```

You can also test specific aspects:

```bash
python test_mdz_compression.py --levels
python test_mdz_compression.py --speed
python test_mdz_compression.py --repeated
python test_mdz_compression.py --corrupted
```

### Export Tests

The export tests verify the ability to export MDZ files to various formats:

- HTML
- PDF (via XeLaTeX)
- EPUB
- DOCX

To run the export tests:

```bash
python test_mdz_export.py --all
```

Or test specific export formats:

```bash
python test_mdz_export.py --html
python test_mdz_export.py --pdf
python test_mdz_export.py --epub
python test_mdz_export.py --docx
```

### Editor Integration Tests

The editor integration tests check the integration with external editors:

- Visual Studio Code
- Obsidian
- Typora

These tests require manual verification:

```bash
python test_mdz_editor_integration.py --all
```

Or test specific editors:

```bash
python test_mdz_editor_integration.py --vscode
python test_mdz_editor_integration.py --obsidian
python test_mdz_editor_integration.py --typora
```

## Integration with External Editors

The MDZ format can be integrated with various external editors. The following sections provide instructions for each editor.

### Visual Studio Code

1. Create a VS Code extension for MDZ support:
   ```bash
   mkdir vscode-mdz-extension
   cd vscode-mdz-extension
   ```

2. Create the following files:

   **package.json**:
   ```json
   {
     "name": "mdz-support",
     "displayName": "MDZ Support",
     "description": "Support for MDZ Markdown bundle format",
     "version": "0.1.0",
     "engines": {
       "vscode": "^1.60.0"
     },
     "categories": [
       "Other"
     ],
     "activationEvents": [
       "onLanguage:markdown",
       "onFileSystem:mdz"
     ],
     "main": "./extension.js",
     "contributes": {
       "commands": [
         {
           "command": "mdz.extract",
           "title": "Extract MDZ Bundle"
         },
         {
           "command": "mdz.create",
           "title": "Create MDZ Bundle"
         }
       ],
       "menus": {
         "explorer/context": [
           {
             "when": "resourceExtname == .mdz",
             "command": "mdz.extract",
             "group": "mdz"
           },
           {
             "when": "resourceExtname == .md",
             "command": "mdz.create",
             "group": "mdz"
           }
         ]
       }
     }
   }
   ```

   **extension.js**:
   ```javascript
   const vscode = require('vscode');
   const { spawn } = require('child_process');
   const path = require('path');
   const fs = require('fs');

   function activate(context) {
       console.log('MDZ Support extension is now active');

       // Register the extract command
       let extractCommand = vscode.commands.registerCommand('mdz.extract', function (uri) {
           if (!uri) {
               vscode.window.showErrorMessage('No file selected');
               return;
           }

           const mdzPath = uri.fsPath;
           const outputDir = path.dirname(mdzPath);
           const outputFile = path.join(outputDir, path.basename(mdzPath, '.mdz') + '.md');

           // Run the Python script to extract the MDZ bundle
           const pythonProcess = spawn('python', [
               '-c',
               `
               import sys
               sys.path.append('${path.dirname(context.extensionPath)}')
               from mdz_bundle import extract_mdz_to_markdown
               extract_mdz_to_markdown('${mdzPath}', '${outputFile}', extract_assets=True)
               `
           ]);

           pythonProcess.stdout.on('data', (data) => {
               console.log(`stdout: ${data}`);
           });

           pythonProcess.stderr.on('data', (data) => {
               console.error(`stderr: ${data}`);
               vscode.window.showErrorMessage(`Error extracting MDZ bundle: ${data}`);
           });

           pythonProcess.on('close', (code) => {
               if (code === 0) {
                   vscode.window.showInformationMessage(`MDZ bundle extracted to ${outputFile}`);
                   vscode.workspace.openTextDocument(outputFile).then(doc => {
                       vscode.window.showTextDocument(doc);
                   });
               } else {
                   vscode.window.showErrorMessage(`Error extracting MDZ bundle (exit code: ${code})`);
               }
           });
       });

       // Register the create command
       let createCommand = vscode.commands.registerCommand('mdz.create', function (uri) {
           if (!uri) {
               vscode.window.showErrorMessage('No file selected');
               return;
           }

           const mdPath = uri.fsPath;
           const outputDir = path.dirname(mdPath);
           const outputFile = path.join(outputDir, path.basename(mdPath, '.md') + '.mdz');

           // Run the Python script to create the MDZ bundle
           const pythonProcess = spawn('python', [
               '-c',
               `
               import sys
               sys.path.append('${path.dirname(context.extensionPath)}')
               from mdz_bundle import create_mdz_from_markdown_file
               create_mdz_from_markdown_file('${mdPath}', '${outputFile}', include_images=True)
               `
           ]);

           pythonProcess.stdout.on('data', (data) => {
               console.log(`stdout: ${data}`);
           });

           pythonProcess.stderr.on('data', (data) => {
               console.error(`stderr: ${data}`);
               vscode.window.showErrorMessage(`Error creating MDZ bundle: ${data}`);
           });

           pythonProcess.on('close', (code) => {
               if (code === 0) {
                   vscode.window.showInformationMessage(`MDZ bundle created at ${outputFile}`);
               } else {
                   vscode.window.showErrorMessage(`Error creating MDZ bundle (exit code: ${code})`);
               }
           });
       });

       context.subscriptions.push(extractCommand);
       context.subscriptions.push(createCommand);
   }

   function deactivate() {}

   module.exports = {
       activate,
       deactivate
   };
   ```

3. Install the extension:
   ```bash
   code --install-extension /path/to/vscode-mdz-extension
   ```

4. Usage:
   - Right-click on a `.mdz` file and select "Extract MDZ Bundle"
   - Right-click on a `.md` file and select "Create MDZ Bundle"

### Obsidian

1. Create an Obsidian plugin for MDZ support:
   ```bash
   mkdir obsidian-mdz-plugin
   cd obsidian-mdz-plugin
   ```

2. Create the following files:

   **manifest.json**:
   ```json
   {
     "id": "mdz-support",
     "name": "MDZ Support",
     "version": "0.1.0",
     "minAppVersion": "0.12.0",
     "description": "Support for MDZ Markdown bundle format",
     "author": "Your Name",
     "isDesktopOnly": true
   }
   ```

   **main.js**:
   ```javascript
   'use strict';

   const { Plugin, Notice } = require('obsidian');
   const { exec } = require('child_process');
   const path = require('path');
   const fs = require('fs');

   class MDZPlugin extends Plugin {
       async onload() {
           console.log('Loading MDZ Support plugin');

           // Register a file menu hook for .mdz files
           this.registerEvent(
               this.app.workspace.on('file-menu', (menu, file) => {
                   if (file && file.extension === 'mdz') {
                       menu.addItem((item) => {
                           item
                               .setTitle('Extract MDZ Bundle')
                               .setIcon('extract')
                               .onClick(async () => {
                                   const mdzPath = this.app.vault.adapter.getFullPath(file.path);
                                   const outputDir = path.dirname(mdzPath);
                                   const outputFile = path.join(outputDir, path.basename(mdzPath, '.mdz') + '.md');

                                   // Run the Python script to extract the MDZ bundle
                                   exec(
                                       `python -c "
                                       import sys
                                       sys.path.append('${this.app.vault.adapter.basePath}')
                                       from mdz_bundle import extract_mdz_to_markdown
                                       extract_mdz_to_markdown('${mdzPath}', '${outputFile}', extract_assets=True)
                                       "`,
                                       (error, stdout, stderr) => {
                                           if (error) {
                                               console.error(`Error: ${error.message}`);
                                               new Notice(`Error extracting MDZ bundle: ${error.message}`);
                                               return;
                                           }
                                           if (stderr) {
                                               console.error(`stderr: ${stderr}`);
                                               new Notice(`Error extracting MDZ bundle: ${stderr}`);
                                               return;
                                           }
                                           console.log(`stdout: ${stdout}`);
                                           new Notice(`MDZ bundle extracted to ${outputFile}`);
                                           this.app.workspace.openLinkText(outputFile, '', true);
                                       }
                                   );
                               });
                       });
                   }

                   if (file && file.extension === 'md') {
                       menu.addItem((item) => {
                           item
                               .setTitle('Create MDZ Bundle')
                               .setIcon('package')
                               .onClick(async () => {
                                   const mdPath = this.app.vault.adapter.getFullPath(file.path);
                                   const outputDir = path.dirname(mdPath);
                                   const outputFile = path.join(outputDir, path.basename(mdPath, '.md') + '.mdz');

                                   // Run the Python script to create the MDZ bundle
                                   exec(
                                       `python -c "
                                       import sys
                                       sys.path.append('${this.app.vault.adapter.basePath}')
                                       from mdz_bundle import create_mdz_from_markdown_file
                                       create_mdz_from_markdown_file('${mdPath}', '${outputFile}', include_images=True)
                                       "`,
                                       (error, stdout, stderr) => {
                                           if (error) {
                                               console.error(`Error: ${error.message}`);
                                               new Notice(`Error creating MDZ bundle: ${error.message}`);
                                               return;
                                           }
                                           if (stderr) {
                                               console.error(`stderr: ${stderr}`);
                                               new Notice(`Error creating MDZ bundle: ${stderr}`);
                                               return;
                                           }
                                           console.log(`stdout: ${stdout}`);
                                           new Notice(`MDZ bundle created at ${outputFile}`);
                                       }
                                   );
                               });
                       });
                   }
               })
           );
       }

       onunload() {
           console.log('Unloading MDZ Support plugin');
       }
   }

   module.exports = MDZPlugin;
   ```

3. Install the plugin:
   - Copy the plugin directory to your Obsidian vault's plugins directory:
     ```bash
     cp -r obsidian-mdz-plugin /path/to/your/vault/.obsidian/plugins/
     ```
   - Enable the plugin in Obsidian settings

4. Usage:
   - Right-click on a `.mdz` file and select "Extract MDZ Bundle"
   - Right-click on a `.md` file and select "Create MDZ Bundle"

### Typora

Typora doesn't support custom plugins, but you can create external scripts to work with MDZ files:

1. Create a script for Typora integration:
   ```bash
   mkdir typora-mdz-integration
   cd typora-mdz-integration
   ```

2. Create the following file:

   **typora_mdz_integration.py**:
   ```python
   #!/usr/bin/env python3
   """
   Typora MDZ Integration Script
   ----------------------------
   This script provides integration between Typora and MDZ files.
   """

   import os
   import sys
   import argparse
   import subprocess
   from pathlib import Path

   def open_in_typora(file_path):
       """Open a file in Typora"""
       # Adjust the path to Typora executable based on your system
       typora_path = "C:\\Program Files\\Typora\\Typora.exe"  # Windows
       # typora_path = "/Applications/Typora.app/Contents/MacOS/Typora"  # macOS
       # typora_path = "typora"  # Linux

       subprocess.run([typora_path, file_path])

   def extract_mdz(mdz_path):
       """Extract an MDZ file and open it in Typora"""
       # Import the MDZ bundle module
       sys.path.append(os.path.dirname(os.path.abspath(__file__)))
       from mdz_bundle import extract_mdz_to_markdown

       # Create a temporary directory for extraction
       temp_dir = os.path.join(os.path.dirname(mdz_path), ".mdz_temp")
       os.makedirs(temp_dir, exist_ok=True)

       # Extract the MDZ file
       output_file = os.path.join(temp_dir, os.path.basename(mdz_path).replace(".mdz", ".md"))
       extract_mdz_to_markdown(mdz_path, output_file, extract_assets=True)

       # Open the extracted file in Typora
       open_in_typora(output_file)

   def create_mdz(md_path):
       """Create an MDZ file from a Markdown file"""
       # Import the MDZ bundle module
       sys.path.append(os.path.dirname(os.path.abspath(__file__)))
       from mdz_bundle import create_mdz_from_markdown_file

       # Create the MDZ file
       output_file = md_path.replace(".md", ".mdz")
       create_mdz_from_markdown_file(md_path, output_file, include_images=True)

       print(f"Created MDZ file: {output_file}")

   def main():
       """Main function"""
       parser = argparse.ArgumentParser(description="Typora MDZ Integration")
       subparsers = parser.add_subparsers(dest="command", help="Command to run")

       # Extract command
       extract_parser = subparsers.add_parser("extract", help="Extract an MDZ file and open it in Typora")
       extract_parser.add_argument("mdz_file", help="Path to the MDZ file")

       # Create command
       create_parser = subparsers.add_parser("create", help="Create an MDZ file from a Markdown file")
       create_parser.add_argument("md_file", help="Path to the Markdown file")

       args = parser.parse_args()

       if args.command == "extract":
           extract_mdz(args.mdz_file)
       elif args.command == "create":
           create_mdz(args.md_file)
       else:
           parser.print_help()

   if __name__ == "__main__":
       main()
   ```

3. Create a batch file for Windows:
   ```batch
   @echo off
   python "C:\path\to\typora_mdz_integration.py" extract %1
   ```

4. Associate `.mdz` files with the batch file:
   - Right-click on a `.mdz` file
   - Select "Open with" > "Choose another app"
   - Browse to the batch file and select it
   - Check "Always use this app to open .mdz files"

5. Usage:
   - Double-click on a `.mdz` file to extract it and open it in Typora
   - Run the script to create an MDZ file:
     ```bash
     python typora_mdz_integration.py create path/to/document.md
     ```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing dependencies, run the dependency checker:

```bash
python check_mdz_dependencies.py
```

### Compression Issues

If you encounter issues with compression or decompression:

1. Make sure the Zstandard library is installed:
   ```bash
   pip install zstandard
   ```

2. Check if the file is a valid MDZ bundle:
   ```bash
   python test_mdz_basic.py --bundle
   ```

### Rendering Issues

If you encounter issues with rendering:

1. Make sure the required Markdown parser is installed:
   ```bash
   pip install markdown-it-py mdit-py-plugins
   ```

2. Check if the renderer is working correctly:
   ```bash
   python test_mdz_basic.py --renderer
   ```

### Export Issues

If you encounter issues with export:

1. Make sure Pandoc is installed:
   ```bash
   pandoc --version
   ```

2. Check if the export functionality is working correctly:
   ```bash
   python test_mdz_export.py --html
   ```

### Editor Integration Issues

If you encounter issues with editor integration:

1. Make sure the editor is installed and accessible from the command line
2. Check if the integration scripts are in the correct location
3. Run the editor integration tests:
   ```bash
   python test_mdz_editor_integration.py --all
   ```
