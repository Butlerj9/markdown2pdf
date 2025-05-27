# MDZ Format Integration with External Editors

This document provides instructions for integrating the `.mdz` format with popular external editors such as Visual Studio Code, Obsidian, and Typora.

## What is the MDZ Format?

The MDZ format (`.mdz`) is a compressed Markdown document bundle that includes:

- The main Markdown document (`index.md`)
- YAML metadata (`metadata.yaml`)
- Embedded assets (images, SVGs, etc.)
- Mermaid diagrams
- Additional resources

The bundle is compressed using Zstandard (zstd) compression, providing excellent compression ratios while maintaining fast decompression speeds.

## Bundle Structure

```
document.mdz
├── index.md (Main Markdown document)
├── metadata.yaml (Optional YAML metadata)
├── mermaid/
│   └── *.mmd, *.svg (Mermaid diagram files)
├── images/
│   └── *.svg, *.png, *.jpg (Image files)
└── additional_assets/
    └── (any additional files)
```

## Visual Studio Code Integration

### Prerequisites

1. Install the following VS Code extensions:
   - Markdown All in One
   - Markdown Preview Enhanced
   - YAML

2. Install the required Python packages:
   ```bash
   pip install zstandard markdown pyyaml pymdown-extensions
   ```

### Setup

1. **Create a VS Code Extension for MDZ Support**

   Create a new directory for the extension:
   ```bash
   mkdir vscode-mdz-extension
   cd vscode-mdz-extension
   ```

2. **Initialize the Extension**

   ```bash
   npm init -y
   npm install --save-dev @types/vscode
   ```

3. **Create the Extension Files**

   Create a `package.json` file:
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

   Create an `extension.js` file:
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

4. **Install the Extension**

   - Press `F5` to run the extension in a new VS Code window
   - Or package the extension:
     ```bash
     vsce package
     ```
   - Install the packaged extension:
     ```bash
     code --install-extension mdz-support-0.1.0.vsix
     ```

5. **Usage**

   - Right-click on a `.md` file and select "Create MDZ Bundle" to create an MDZ bundle
   - Right-click on a `.mdz` file and select "Extract MDZ Bundle" to extract the bundle

## Obsidian Integration

### Prerequisites

1. Install the required Python packages:
   ```bash
   pip install zstandard markdown pyyaml pymdown-extensions
   ```

2. Install the Obsidian Custom Plugin API (if you want to create a plugin)

### Setup

1. **Create an Obsidian Plugin for MDZ Support**

   Create a new directory for the plugin:
   ```bash
   mkdir obsidian-mdz-plugin
   cd obsidian-mdz-plugin
   ```

2. **Initialize the Plugin**

   ```bash
   npm init -y
   npm install --save-dev obsidian
   ```

3. **Create the Plugin Files**

   Create a `manifest.json` file:
   ```json
   {
     "id": "mdz-support",
     "name": "MDZ Support",
     "version": "0.1.0",
     "minAppVersion": "0.12.0",
     "description": "Support for MDZ Markdown bundle format",
     "author": "Your Name",
     "authorUrl": "https://github.com/yourusername",
     "isDesktopOnly": true
   }
   ```

   Create a `main.js` file:
   ```javascript
   const { Plugin, Notice, Menu } = require('obsidian');
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

4. **Install the Plugin**

   - Copy the plugin directory to your Obsidian plugins directory:
     ```bash
     cp -r obsidian-mdz-plugin /path/to/your/obsidian/vault/.obsidian/plugins/
     ```
   - Enable the plugin in Obsidian settings

5. **Usage**

   - Right-click on a `.md` file and select "Create MDZ Bundle" to create an MDZ bundle
   - Right-click on a `.mdz` file and select "Extract MDZ Bundle" to extract the bundle

## Typora Integration

Typora doesn't support custom plugins, but you can create external scripts to work with MDZ files.

### Setup

1. **Create a Script for MDZ Integration**

   Create a file named `typora_mdz_integration.py`:
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

2. **Create File Associations**

   - **Windows**:
     1. Create a batch file `open_mdz.bat`:
        ```batch
        @echo off
        python path\to\typora_mdz_integration.py extract %1
        ```
     2. Associate `.mdz` files with this batch file:
        - Right-click on a `.mdz` file
        - Select "Open with" > "Choose another app"
        - Browse to the batch file and select it
        - Check "Always use this app to open .mdz files"

   - **macOS**:
     1. Create an AppleScript:
        ```applescript
        on open theFiles
            repeat with theFile in theFiles
                do shell script "python /path/to/typora_mdz_integration.py extract " & quoted form of POSIX path of theFile
            end repeat
        end open
        ```
     2. Save as an application using Script Editor
     3. Associate `.mdz` files with this application

   - **Linux**:
     1. Create a desktop entry file:
        ```
        [Desktop Entry]
        Type=Application
        Name=MDZ Opener
        Exec=python /path/to/typora_mdz_integration.py extract %f
        MimeType=application/mdz;
        ```
     2. Register the MIME type and associate it with the desktop entry

3. **Usage**

   - Double-click on a `.mdz` file to extract it and open it in Typora
   - Run the script to create an MDZ file:
     ```bash
     python typora_mdz_integration.py create path/to/document.md
     ```

## General Integration Tips

1. **File Association**

   Associate `.mdz` files with a custom handler script that:
   - Extracts the MDZ bundle to a temporary directory
   - Opens the extracted Markdown file in your preferred editor
   - Monitors for changes and updates the MDZ bundle when the file is saved

2. **Command-Line Tools**

   Use the provided command-line tools for working with MDZ files:
   ```bash
   # Extract an MDZ file
   python mdz_bundle.py extract document.mdz document.md

   # Create an MDZ file
   python mdz_bundle.py create document.md document.mdz
   ```

3. **Editor Extensions**

   For editors that support extensions (like VS Code), create extensions that:
   - Add syntax highlighting for MDZ files
   - Provide commands for creating and extracting MDZ bundles
   - Support live preview of MDZ content

4. **Continuous Integration**

   For collaborative workflows, set up CI/CD pipelines that:
   - Extract MDZ files for editing
   - Validate the content
   - Rebuild the MDZ bundles
   - Commit the changes

## Troubleshooting

1. **Missing Dependencies**

   If you encounter errors about missing dependencies, install them:
   ```bash
   pip install zstandard markdown pyyaml pymdown-extensions
   ```

2. **Path Issues**

   Ensure that the `mdz_bundle.py` file is in your Python path or specify the full path to it in your scripts.

3. **Permission Issues**

   Make sure your scripts have execute permissions:
   ```bash
   chmod +x typora_mdz_integration.py
   ```

4. **Editor Integration Issues**

   If your editor doesn't recognize the MDZ format:
   - Extract the MDZ file manually
   - Edit the extracted Markdown file
   - Create a new MDZ file from the edited Markdown file
