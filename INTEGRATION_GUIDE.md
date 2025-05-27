# Content Processing System Integration Guide

This guide explains how to integrate the modular content processing system with the existing Markdown to PDF converter application.

## Overview

The content processing system provides a modular way to handle different content types in Markdown documents, including:

- GitHub Flavored Markdown
- Mermaid diagrams
- LaTeX/Math notation
- SVG and images
- Code blocks with syntax highlighting
- HTML5 media (video/audio)
- Interactive visualizations (Plotly, Chart.js)
- External content via iframes
- Custom content types via plugins

## Integration Steps

### 1. Import the Content Processing Integration

In your main application file (e.g., `markdown_to_pdf_converter.py`), import the content processing integration:

```python
from content_processing_integration import get_integration
```

### 2. Initialize the Integration

Initialize the content processing integration in your application's initialization code:

```python
def __init__(self):
    # Existing initialization code...
    
    # Initialize content processing integration
    self.content_processor = get_integration()
```

### 3. Use the Integration for Preview

Replace the existing preview rendering code with the content processing integration:

```python
def render_preview(self, markdown_content):
    # Process content for preview
    processed_content = self.content_processor.process_content_for_preview(markdown_content)
    
    # Get required scripts and styles
    scripts = self.content_processor.get_required_scripts()
    styles = self.content_processor.get_required_styles()
    
    # Create HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
        /* Your existing styles... */
    </style>
    {styles}
    {scripts}
</head>
<body>
    {processed_content}
</body>
</html>"""
    
    return html
```

### 4. Use the Integration for Export

Replace the existing export preprocessing code with the content processing integration:

```python
def _export_to_pdf(self, output_file):
    # Get the markdown content
    markdown_content = self.editor.toPlainText()
    
    # Process content for PDF export
    processed_content = self.content_processor.process_content_for_export(markdown_content, 'pdf')
    
    # Continue with the existing PDF export code...
```

Similarly, update the other export methods (`_export_to_html`, `_export_to_docx`, etc.) to use the content processing integration.

### 5. Check Dependencies

Add dependency checking to your application:

```python
def check_dependencies(self):
    # Check content processor dependencies
    dependency_status = self.content_processor.check_dependencies()
    
    # Log dependency status
    for processor, status in dependency_status.items():
        if status:
            logger.info(f"Dependency check passed for {processor}")
        else:
            logger.warning(f"Dependency check failed for {processor}")
    
    # Continue with existing dependency checks...
```

## Adding New Content Types

### Creating a Custom Processor

To add support for a new content type, create a new processor class that inherits from `ContentProcessor`:

```python
from content_processors.base_processor import ContentProcessor

class MyCustomProcessor(ContentProcessor):
    def __init__(self, config=None):
        super().__init__(config)
        # Initialize your processor...
    
    def detect(self, content):
        # Detect your content type...
        return []
    
    def process_for_preview(self, content, metadata):
        # Process for preview...
        return content
    
    def process_for_export(self, content, metadata, format_type):
        # Process for export...
        return content
    
    def get_required_scripts(self):
        # Return required scripts...
        return []
    
    def get_required_styles(self):
        # Return required styles...
        return []
    
    def get_dependencies(self):
        # Return required dependencies...
        return []
    
    def check_dependencies(self):
        # Check if dependencies are available...
        return True
```

### Creating a Plugin

To create a plugin, create a new Python file in the `plugins` directory:

```python
# my_plugin.py

from content_processors.base_processor import ContentProcessor

class MyCustomProcessor(ContentProcessor):
    # Implementation...
    pass

def register_plugin(plugin_system):
    plugin_system.register_processor(MyCustomProcessor, priority=100)
```

## Testing

You can test the content processing system using the provided test script:

```bash
python test_content_processing.py sample_content.md --format preview --output preview.html
```

This will process the sample content and output the result to `preview.html`.

## Troubleshooting

If you encounter issues with the content processing system:

1. Check the logs for error messages
2. Verify that all dependencies are installed
3. Check that the content processors are registered correctly
4. Try processing a simple document to isolate the issue

## Conclusion

By following this guide, you should be able to integrate the modular content processing system with your existing Markdown to PDF converter application. This will provide a more robust and extensible way to handle different content types in Markdown documents.
