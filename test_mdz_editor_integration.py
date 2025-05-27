#!/usr/bin/env python3
"""
MDZ Editor Integration Test Script
--------------------------------
This script tests the integration of the MDZ format with external editors.

File: test_mdz_editor_integration.py
"""

import os
import sys
import tempfile
import shutil
import logging
import argparse
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_mdz_file():
    """
    Create a test MDZ file
    
    Returns:
        Tuple of (temp_dir, mdz_path)
    """
    try:
        from mdz_bundle import MDZBundle
    except ImportError:
        logger.error("MDZ bundle module not found")
        return None, None
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="mdz_editor_test_")
    
    # Create a test Markdown file
    md_content = """---
title: "MDZ Editor Integration Test"
author: "Test Script"
---

# MDZ Editor Integration Test

This is a test document for MDZ editor integration.

## Features

- GitHub Flavored Markdown
- YAML front matter
- Mermaid diagrams
- LaTeX math

```mermaid
graph TD
    A[Start] --> B[End]
```

Inline math: $E = mc^2$

![Test Image](test_image.png)
"""
    
    md_path = os.path.join(temp_dir, "test.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Create a test image
    img_path = os.path.join(temp_dir, "test_image.png")
    create_test_image(img_path)
    
    # Create an MDZ bundle
    bundle = MDZBundle()
    
    # Add content
    bundle.create_from_markdown(md_content, {"title": "MDZ Editor Integration Test"})
    
    # Add the image
    with open(img_path, "rb") as f:
        image_content = f.read()
    bundle.add_file(img_path, image_content)
    
    # Save the bundle
    mdz_path = os.path.join(temp_dir, "test.mdz")
    bundle.save(mdz_path)
    
    logger.info(f"Created test MDZ file: {mdz_path}")
    return temp_dir, mdz_path

def create_test_image(path):
    """Create a simple test image"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a 100x100 white image
        img = Image.new("RGB", (100, 100), color="white")
        
        # Draw a red rectangle
        draw = ImageDraw.Draw(img)
        draw.rectangle([(10, 10), (90, 90)], outline="red", width=2)
        
        # Save the image
        img.save(path)
    except ImportError:
        # If PIL is not available, create a simple binary file
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

def test_vscode_integration(mdz_path):
    """
    Test integration with Visual Studio Code
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        True if successful, False otherwise
    """
    # Check if VS Code is installed
    vscode_path = None
    if sys.platform == "win32":
        vscode_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft VS Code", "Code.exe")
        ]
        for path in vscode_paths:
            if os.path.exists(path):
                vscode_path = path
                break
    elif sys.platform == "darwin":
        vscode_path = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    else:
        # Try to find code in PATH
        try:
            vscode_path = subprocess.check_output(["which", "code"], text=True).strip()
        except:
            pass
    
    if not vscode_path:
        logger.warning("Visual Studio Code not found")
        return False
    
    logger.info(f"Found Visual Studio Code at: {vscode_path}")
    
    # Create a simple VS Code extension for MDZ support
    extension_dir = os.path.join(os.path.dirname(mdz_path), "vscode-mdz-extension")
    os.makedirs(extension_dir, exist_ok=True)
    
    # Create package.json
    package_json = """{
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
}"""
    
    with open(os.path.join(extension_dir, "package.json"), "w", encoding="utf-8") as f:
        f.write(package_json)
    
    # Create extension.js
    extension_js = """const vscode = require('vscode');
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
};"""
    
    with open(os.path.join(extension_dir, "extension.js"), "w", encoding="utf-8") as f:
        f.write(extension_js)
    
    logger.info(f"Created VS Code extension in: {extension_dir}")
    
    # Print instructions
    print("\nVS Code Integration Test:")
    print("------------------------")
    print(f"1. Install the extension: code --install-extension {extension_dir}")
    print(f"2. Open the MDZ file: code {mdz_path}")
    print("3. Right-click on the file and select 'Extract MDZ Bundle'")
    print("4. Edit the extracted Markdown file")
    print("5. Right-click on the Markdown file and select 'Create MDZ Bundle'")
    
    return True

def test_obsidian_integration(mdz_path):
    """
    Test integration with Obsidian
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        True if successful, False otherwise
    """
    # Check if Obsidian is installed
    obsidian_path = None
    if sys.platform == "win32":
        obsidian_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Obsidian", "Obsidian.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Obsidian", "Obsidian.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Obsidian", "Obsidian.exe")
        ]
        for path in obsidian_paths:
            if os.path.exists(path):
                obsidian_path = path
                break
    elif sys.platform == "darwin":
        obsidian_path = "/Applications/Obsidian.app/Contents/MacOS/Obsidian"
    
    if not obsidian_path:
        logger.warning("Obsidian not found")
        return False
    
    logger.info(f"Found Obsidian at: {obsidian_path}")
    
    # Create a simple Obsidian plugin for MDZ support
    plugin_dir = os.path.join(os.path.dirname(mdz_path), "obsidian-mdz-plugin")
    os.makedirs(plugin_dir, exist_ok=True)
    
    # Create manifest.json
    manifest_json = """{
  "id": "mdz-support",
  "name": "MDZ Support",
  "version": "0.1.0",
  "minAppVersion": "0.12.0",
  "description": "Support for MDZ Markdown bundle format",
  "author": "Test Script",
  "isDesktopOnly": true
}"""
    
    with open(os.path.join(plugin_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(manifest_json)
    
    # Create main.js
    main_js = """'use strict';

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

module.exports = MDZPlugin;"""
    
    with open(os.path.join(plugin_dir, "main.js"), "w", encoding="utf-8") as f:
        f.write(main_js)
    
    logger.info(f"Created Obsidian plugin in: {plugin_dir}")
    
    # Print instructions
    print("\nObsidian Integration Test:")
    print("-------------------------")
    print(f"1. Copy the plugin to your Obsidian vault: {plugin_dir} -> <vault>/.obsidian/plugins/mdz-support/")
    print("2. Enable the plugin in Obsidian settings")
    print(f"3. Copy the MDZ file to your vault: {mdz_path} -> <vault>/")
    print("4. Right-click on the file and select 'Extract MDZ Bundle'")
    print("5. Edit the extracted Markdown file")
    print("6. Right-click on the Markdown file and select 'Create MDZ Bundle'")
    
    return True

def test_typora_integration(mdz_path):
    """
    Test integration with Typora
    
    Args:
        mdz_path: Path to the test MDZ file
        
    Returns:
        True if successful, False otherwise
    """
    # Check if Typora is installed
    typora_path = None
    if sys.platform == "win32":
        typora_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Typora", "Typora.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Typora", "Typora.exe")
        ]
        for path in typora_paths:
            if os.path.exists(path):
                typora_path = path
                break
    elif sys.platform == "darwin":
        typora_path = "/Applications/Typora.app/Contents/MacOS/Typora"
    
    if not typora_path:
        logger.warning("Typora not found")
        return False
    
    logger.info(f"Found Typora at: {typora_path}")
    
    # Create a script for Typora integration
    script_dir = os.path.join(os.path.dirname(mdz_path), "typora-mdz-integration")
    os.makedirs(script_dir, exist_ok=True)
    
    # Create the integration script
    script_content = """#!/usr/bin/env python3
\"\"\"
Typora MDZ Integration Script
----------------------------
This script provides integration between Typora and MDZ files.
\"\"\"

import os
import sys
import argparse
import subprocess
from pathlib import Path

def open_in_typora(file_path):
    \"\"\"Open a file in Typora\"\"\"
    # Adjust the path to Typora executable based on your system
    typora_path = "C:\\\\Program Files\\\\Typora\\\\Typora.exe"  # Windows
    # typora_path = "/Applications/Typora.app/Contents/MacOS/Typora"  # macOS
    # typora_path = "typora"  # Linux

    subprocess.run([typora_path, file_path])

def extract_mdz(mdz_path):
    \"\"\"Extract an MDZ file and open it in Typora\"\"\"
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
    \"\"\"Create an MDZ file from a Markdown file\"\"\"
    # Import the MDZ bundle module
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from mdz_bundle import create_mdz_from_markdown_file

    # Create the MDZ file
    output_file = md_path.replace(".md", ".mdz")
    create_mdz_from_markdown_file(md_path, output_file, include_images=True)

    print(f"Created MDZ file: {output_file}")

def main():
    \"\"\"Main function\"\"\"
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
"""
    
    script_path = os.path.join(script_dir, "typora_mdz_integration.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Create a batch file for Windows
    if sys.platform == "win32":
        batch_content = f"""@echo off
python "{script_path}" extract %1
"""
        
        batch_path = os.path.join(script_dir, "open_mdz.bat")
        with open(batch_path, "w", encoding="utf-8") as f:
            f.write(batch_content)
    
    logger.info(f"Created Typora integration script in: {script_dir}")
    
    # Print instructions
    print("\nTypora Integration Test:")
    print("----------------------")
    print(f"1. Extract the MDZ file: python {script_path} extract {mdz_path}")
    print("2. Edit the extracted Markdown file in Typora")
    print(f"3. Create an MDZ file: python {script_path} create <path_to_md_file>")
    print("\nFor Windows users:")
    print(f"1. Associate .mdz files with {os.path.join(script_dir, 'open_mdz.bat')}")
    print("2. Double-click on an MDZ file to open it in Typora")
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MDZ Editor Integration Test Script")
    parser.add_argument("--vscode", action="store_true", help="Test integration with Visual Studio Code")
    parser.add_argument("--obsidian", action="store_true", help="Test integration with Obsidian")
    parser.add_argument("--typora", action="store_true", help="Test integration with Typora")
    parser.add_argument("--all", action="store_true", help="Test integration with all editors")
    
    args = parser.parse_args()
    
    # If no arguments are provided, show help
    if not (args.vscode or args.obsidian or args.typora or args.all):
        parser.print_help()
        return
    
    # Create a test MDZ file
    temp_dir, mdz_path = create_test_mdz_file()
    if not mdz_path:
        logger.error("Failed to create test MDZ file")
        return
    
    try:
        # Test integration with Visual Studio Code
        if args.vscode or args.all:
            logger.info("Testing integration with Visual Studio Code...")
            test_vscode_integration(mdz_path)
        
        # Test integration with Obsidian
        if args.obsidian or args.all:
            logger.info("Testing integration with Obsidian...")
            test_obsidian_integration(mdz_path)
        
        # Test integration with Typora
        if args.typora or args.all:
            logger.info("Testing integration with Typora...")
            test_typora_integration(mdz_path)
        
        logger.info("MDZ editor integration tests completed")
        
        # Keep the temporary directory for testing
        print(f"\nTest files are located in: {temp_dir}")
        print("Please delete this directory when you're done testing.")
    
    except Exception as e:
        logger.error(f"Error testing MDZ editor integration: {str(e)}")
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary directory: {str(e)}")

if __name__ == "__main__":
    main()
