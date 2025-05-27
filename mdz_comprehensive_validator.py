#!/usr/bin/env python3
"""
MDZ Comprehensive Validator
-------------------------
This script provides comprehensive validation of the MDZ format stack.

File: mdz_comprehensive_validator.py
"""

import os
import sys
import logging
import argparse
import tempfile
import shutil
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDZValidator:
    """
    MDZ Validator class for comprehensive testing of the MDZ format stack
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the MDZ validator

        Args:
            output_dir: Optional directory to store test files and results
        """
        # Create a temporary directory if no output directory is provided
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        else:
            self.output_dir = tempfile.mkdtemp(prefix="mdz_validator_")

        # Create subdirectories for test files and results
        self.test_files_dir = os.path.join(self.output_dir, "test_files")
        self.results_dir = os.path.join(self.output_dir, "results")
        self.reference_dir = os.path.join(self.output_dir, "reference")

        os.makedirs(self.test_files_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.reference_dir, exist_ok=True)

        # Initialize test results
        self.test_results = {}

    def generate_test_files(self):
        """
        Generate test files with various combinations of Markdown features
        """
        logger.info("Generating test files...")

        # Generate test files
        self._generate_basic_markdown_test()
        self._generate_gfm_test()
        self._generate_yaml_frontmatter_test()
        self._generate_mermaid_test()
        self._generate_latex_math_test()
        self._generate_image_test()
        self._generate_comprehensive_test()

        logger.info(f"Generated test files in {self.test_files_dir}")

    def _generate_basic_markdown_test(self):
        """Generate a basic Markdown test file"""
        content = """# Basic Markdown Test

This is a basic Markdown test file.

## Headings

### Level 3 Heading

#### Level 4 Heading

##### Level 5 Heading

###### Level 6 Heading

## Text Formatting

*Italic text*

**Bold text**

***Bold and italic text***

~~Strikethrough text~~

## Lists

### Unordered List

- Item 1
- Item 2
  - Nested item 1
  - Nested item 2
- Item 3

### Ordered List

1. First item
2. Second item
   1. Nested item 1
   2. Nested item 2
3. Third item

## Links

[Link to Google](https://www.google.com)

[Link to heading](#headings)

## Blockquotes

> This is a blockquote.
>
> > This is a nested blockquote.

## Code

Inline code: `print("Hello, world!")`

```python
def hello_world():
    print("Hello, world!")
```

## Horizontal Rule

---

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "basic_markdown_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_gfm_test(self):
        """Generate a GitHub Flavored Markdown test file"""
        content = """# GitHub Flavored Markdown Test

This file tests GitHub Flavored Markdown features.

## Tables

| Name  | Age | Occupation |
|-------|-----|------------|
| Alice | 28  | Engineer   |
| Bob   | 35  | Designer   |
| Carol | 42  | Manager    |

## Task Lists

- [x] Task 1 (completed)
- [ ] Task 2 (not completed)
- [ ] Task 3 (not completed)

## Autolinks

Visit https://github.com for more information.

## Strikethrough

This is ~~strikethrough~~ text.

## Emoji

:smile: :heart: :thumbsup:

## Syntax Highlighting

```javascript
function hello() {
    console.log("Hello, world!");
}
```

```css
body {
    font-family: Arial, sans-serif;
    color: #333;
}
```

## Footnotes

Here is a footnote reference[^1].

[^1]: This is the footnote content.

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "gfm_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_yaml_frontmatter_test(self):
        """Generate a test file with YAML front matter"""
        content = """---
title: "YAML Front Matter Test"
author: "MDZ Validator"
date: "2025-05-01"
tags: ["markdown", "yaml", "front-matter", "test"]
toc: true
numbering: true
theme: "default"
highlight_style: "github"
---

# YAML Front Matter Test

This file tests YAML front matter processing.

## Metadata

The front matter of this document contains the following metadata:

- Title: YAML Front Matter Test
- Author: MDZ Validator
- Date: 2025-05-01
- Tags: markdown, yaml, front-matter, test
- TOC: true
- Numbering: true
- Theme: default
- Highlight Style: github

## Content

The content of this document should be processed according to the settings in the front matter.

### Code Block

```python
def process_front_matter(markdown_content):
    # Process YAML front matter in Markdown content
    if markdown_content.startswith('---'):
        end_index = markdown_content.find('---', 3)
        if end_index != -1:
            front_matter = markdown_content[3:end_index].strip()
            content = markdown_content[end_index+3:].strip()
            return front_matter, content
    return None, markdown_content
```

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "yaml_frontmatter_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_mermaid_test(self):
        """Generate a test file with Mermaid diagrams"""
        content = """# Mermaid Diagrams Test

This file tests Mermaid diagram rendering.

## Flowchart

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    C --> E[End]
    D --> B
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

## Class Diagram

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

## Entity Relationship Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

## Gantt Chart

```mermaid
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2025-05-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2025-05-12, 12d
    another task     :24d
```

## Pie Chart

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "mermaid_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_latex_math_test(self):
        """Generate a test file with LaTeX math"""
        content = """# LaTeX Math Test

This file tests LaTeX math rendering.

## Inline Math

Einstein's famous equation: $E = mc^2$

The Pythagorean theorem: $a^2 + b^2 = c^2$

The quadratic formula: $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$

## Display Math

The Cauchy-Schwarz inequality:

$$\\left( \\sum_{k=1}^n a_k b_k \\right)^2 \\leq \\left( \\sum_{k=1}^n a_k^2 \\right) \\left( \\sum_{k=1}^n b_k^2 \\right)$$

Maxwell's equations:

$$\\begin{aligned}
\\nabla \\times \\vec{\\mathbf{B}} -\\, \\frac1c\\, \\frac{\\partial\\vec{\\mathbf{E}}}{\\partial t} & = \\frac{4\\pi}{c}\\vec{\\mathbf{j}} \\\\
\\nabla \\cdot \\vec{\\mathbf{E}} & = 4 \\pi \\rho \\\\
\\nabla \\times \\vec{\\mathbf{E}}\\, +\\, \\frac1c\\, \\frac{\\partial\\vec{\\mathbf{B}}}{\\partial t} & = \\vec{\\mathbf{0}} \\\\
\\nabla \\cdot \\vec{\\mathbf{B}} & = 0
\\end{aligned}$$

The probability density function for a normal distribution:

$$f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{1}{2}\\left(\\frac{x-\\mu}{\\sigma}\\right)^2}$$

## Mixed Math and Text

The area of a circle is $A = \\pi r^2$, where $r$ is the radius.

The volume of a sphere is $V = \\frac{4}{3} \\pi r^3$.

## Math in Lists

1. The first derivative of $f(x) = x^2$ is $f'(x) = 2x$.
2. The second derivative is $f''(x) = 2$.
3. The integral of $f(x) = x^2$ is $\\int x^2 dx = \\frac{x^3}{3} + C$.

## Math in Tables

| Function | Derivative | Integral |
|----------|------------|----------|
| $x^n$ | $nx^{n-1}$ | $\\frac{x^{n+1}}{n+1} + C$ |
| $e^x$ | $e^x$ | $e^x + C$ |
| $\\ln(x)$ | $\\frac{1}{x}$ | $x\\ln(x) - x + C$ |
| $\\sin(x)$ | $\\cos(x)$ | $-\\cos(x) + C$ |
| $\\cos(x)$ | $-\\sin(x)$ | $\\sin(x) + C$ |

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "latex_math_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _generate_image_test(self):
        """Generate a test file with images"""
        # Create test images
        self._create_test_images()

        content = """# Image Test

This file tests image rendering.

## PNG Image

![PNG Test Image](test_image.png)

## JPG Image

![JPG Test Image](test_image.jpg)

## SVG Image

![SVG Test Image](test_image.svg)

## Image with Size Attributes

![PNG Test Image with Size](test_image.png){width=50%}

## Image with Caption

![This is a caption for the image](test_image.png)

## Image in a Table

| Image | Description |
|-------|-------------|
| ![Small Image](test_image_small.png) | A small test image |
| ![Another Small Image](test_image_small.jpg) | Another small test image |

## Image with Link

[![Linked Image](test_image_small.png)](https://example.com)

## Multiple Images

![Image 1](test_image.png) ![Image 2](test_image.jpg)

## Image in a List

- Item with image: ![Small Image](test_image_small.png)
- Another item with image: ![Small Image](test_image_small.jpg)

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "image_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_test_images(self):
        """Create test images for the image test"""
        try:
            from PIL import Image, ImageDraw

            # Create a PNG image
            img = Image.new("RGB", (300, 200), color="white")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(20, 20), (280, 180)], outline="blue", width=2)
            draw.text((150, 100), "Test PNG Image", fill="black")
            img.save(os.path.join(self.test_files_dir, "test_image.png"))

            # Create a small PNG image
            img_small = img.resize((150, 100))
            img_small.save(os.path.join(self.test_files_dir, "test_image_small.png"))

            # Create a JPG image
            img = Image.new("RGB", (300, 200), color="white")
            draw = ImageDraw.Draw(img)
            draw.rectangle([(20, 20), (280, 180)], outline="red", width=2)
            draw.text((150, 100), "Test JPG Image", fill="black")
            img.save(os.path.join(self.test_files_dir, "test_image.jpg"))

            # Create a small JPG image
            img_small = img.resize((150, 100))
            img_small.save(os.path.join(self.test_files_dir, "test_image_small.jpg"))

            logger.info("Created test images using PIL")
        except ImportError:
            # If PIL is not available, create simple files
            logger.warning("PIL not available, creating simple test image files")

            # Create a PNG image
            with open(os.path.join(self.test_files_dir, "test_image.png"), "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

            # Create a small PNG image
            with open(os.path.join(self.test_files_dir, "test_image_small.png"), "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 50)

            # Create a JPG image
            with open(os.path.join(self.test_files_dir, "test_image.jpg"), "wb") as f:
                f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

            # Create a small JPG image
            with open(os.path.join(self.test_files_dir, "test_image_small.jpg"), "wb") as f:
                f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 50)

        # Create an SVG image
        svg_content = """<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="white"/>
  <rect x="20" y="20" width="260" height="160" stroke="green" stroke-width="2" fill="none"/>
  <text x="150" y="100" font-family="Arial" font-size="16" text-anchor="middle">Test SVG Image</text>
</svg>"""

        with open(os.path.join(self.test_files_dir, "test_image.svg"), "w", encoding="utf-8") as f:
            f.write(svg_content)

    def _generate_comprehensive_test(self):
        """Generate a comprehensive test file with all features"""
        content = """---
title: "Comprehensive MDZ Test"
author: "MDZ Validator"
date: "2025-05-01"
tags: ["markdown", "mdz", "test", "comprehensive"]
toc: true
numbering: true
theme: "default"
highlight_style: "github"
---

# Comprehensive MDZ Test

This file tests all features of the MDZ format.

## Basic Markdown

### Text Formatting

*Italic text*

**Bold text**

***Bold and italic text***

~~Strikethrough text~~

### Lists

#### Unordered List

- Item 1
- Item 2
  - Nested item 1
  - Nested item 2
- Item 3

#### Ordered List

1. First item
2. Second item
   1. Nested item 1
   2. Nested item 2
3. Third item

### Links

[Link to Google](https://www.google.com)

[Link to heading](#basic-markdown)

### Blockquotes

> This is a blockquote.
>
> > This is a nested blockquote.

### Code

Inline code: `print("Hello, world!")`

```python
def hello_world():
    print("Hello, world!")
```

### Horizontal Rule

---

## GitHub Flavored Markdown

### Tables

| Name  | Age | Occupation |
|-------|-----|------------|
| Alice | 28  | Engineer   |
| Bob   | 35  | Designer   |
| Carol | 42  | Manager    |

### Task Lists

- [x] Task 1 (completed)
- [ ] Task 2 (not completed)
- [ ] Task 3 (not completed)

### Autolinks

Visit https://github.com for more information.

### Strikethrough

This is ~~strikethrough~~ text.

### Emoji

:smile: :heart: :thumbsup:

### Syntax Highlighting

```javascript
function hello() {
    console.log("Hello, world!");
}
```

```css
body {
    font-family: Arial, sans-serif;
    color: #333;
}
```

### Footnotes

Here is a footnote reference[^1].

[^1]: This is the footnote content.

## Mermaid Diagrams

### Flowchart

```mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    C --> E[End]
    D --> B
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

## LaTeX Math

### Inline Math

Einstein's famous equation: $E = mc^2$

The Pythagorean theorem: $a^2 + b^2 = c^2$

### Display Math

The Cauchy-Schwarz inequality:

$$\\left( \\sum_{k=1}^n a_k b_k \\right)^2 \\leq \\left( \\sum_{k=1}^n a_k^2 \\right) \\left( \\sum_{k=1}^n b_k^2 \\right)$$

## Images

### PNG Image

![PNG Test Image](test_image.png)

### JPG Image

![JPG Test Image](test_image.jpg)

### SVG Image

![SVG Test Image](test_image.svg)

## Combined Features

### Table with Math and Code

| Feature | Example | Description |
|---------|---------|-------------|
| Math | $E = mc^2$ | Einstein's equation |
| Code | `print("Hello")` | Python code |
| Mermaid | ```mermaid graph TD; A-->B;``` | Mermaid diagram |

### List with Images and Math

1. Item with image: ![Small Image](test_image_small.png)
2. Item with math: $a^2 + b^2 = c^2$
3. Item with code: `console.log("Hello")`

### Blockquote with Math and Code

> This blockquote contains math: $E = mc^2$
>
> And code: `print("Hello")`
>
> And an image: ![Small Image](test_image_small.jpg)

## Conclusion

This document tests all the features of the MDZ format.

"""

        # Save the test file
        file_path = os.path.join(self.test_files_dir, "comprehensive_test.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def create_mdz_bundles(self):
        """Create MDZ bundles from the test files"""
        logger.info("Creating MDZ bundles...")

        try:
            from mdz_bundle import create_mdz_from_markdown_file
        except ImportError:
            logger.error("MDZ bundle module not found")
            return False

        # Create MDZ bundles for each test file
        for file_name in os.listdir(self.test_files_dir):
            if file_name.endswith(".md"):
                md_path = os.path.join(self.test_files_dir, file_name)
                mdz_path = os.path.join(self.test_files_dir, file_name.replace(".md", ".mdz"))

                try:
                    create_mdz_from_markdown_file(md_path, mdz_path, include_images=True)
                    logger.info(f"Created MDZ bundle: {mdz_path}")
                except Exception as e:
                    logger.error(f"Error creating MDZ bundle for {file_name}: {str(e)}")
                    return False

        return True

    def test_mdz_extraction(self):
        """Test MDZ bundle extraction"""
        logger.info("Testing MDZ bundle extraction...")

        try:
            from mdz_bundle import extract_mdz_to_markdown
        except ImportError:
            logger.error("MDZ bundle module not found")
            return False

        # Create a directory for extracted files
        extracted_dir = os.path.join(self.results_dir, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)

        # Extract each MDZ bundle
        for file_name in os.listdir(self.test_files_dir):
            if file_name.endswith(".mdz"):
                mdz_path = os.path.join(self.test_files_dir, file_name)
                extracted_md_path = os.path.join(extracted_dir, file_name.replace(".mdz", ".md"))

                try:
                    metadata = extract_mdz_to_markdown(mdz_path, extracted_md_path, extract_assets=True)
                    logger.info(f"Extracted MDZ bundle: {mdz_path} -> {extracted_md_path}")

                    # Save metadata for reference
                    metadata_path = os.path.join(extracted_dir, file_name.replace(".mdz", "_metadata.json"))
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)
                except Exception as e:
                    logger.error(f"Error extracting MDZ bundle {file_name}: {str(e)}")
                    return False

        return True

    def test_html_export(self):
        """Test HTML export"""
        logger.info("Testing HTML export...")

        try:
            from mdz_renderer import MDZRenderer
            from mdz_bundle import MDZBundle
        except ImportError:
            logger.error("MDZ modules not found")
            return False

        # Create a directory for HTML exports
        html_dir = os.path.join(self.results_dir, "html")
        os.makedirs(html_dir, exist_ok=True)

        # Export each MDZ bundle to HTML
        for file_name in os.listdir(self.test_files_dir):
            if file_name.endswith(".mdz"):
                mdz_path = os.path.join(self.test_files_dir, file_name)
                html_path = os.path.join(html_dir, file_name.replace(".mdz", ".html"))

                try:
                    # Load the MDZ bundle
                    bundle = MDZBundle()
                    bundle.load(mdz_path)

                    # Extract to a temporary directory
                    extracted_assets = bundle.extract_to_temp()

                    # Create a renderer
                    renderer = MDZRenderer()

                    # Extract front matter
                    markdown_without_front_matter, front_matter = renderer.extract_front_matter(bundle.get_main_content())

                    # Extract and render Mermaid diagrams
                    mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)

                    # Render to HTML
                    html_content = renderer.render_to_html(
                        markdown_without_front_matter,
                        front_matter=front_matter,
                        mermaid_diagrams=mermaid_diagrams,
                        asset_paths=extracted_assets
                    )

                    # Save the HTML content
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    logger.info(f"Exported HTML: {html_path}")
                except Exception as e:
                    logger.error(f"Error exporting HTML for {file_name}: {str(e)}")
                    return False

        return True

    def test_pdf_export(self):
        """Test PDF export"""
        logger.info("Testing PDF export...")

        try:
            from mdz_renderer import MDZRenderer
            from mdz_bundle import MDZBundle
        except ImportError:
            logger.error("MDZ modules not found")
            return False

        # Check if pandoc is available
        try:
            import subprocess
            result = subprocess.run(["pandoc", "--version"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
            if result.returncode != 0:
                logger.error("Pandoc is not installed")
                return False
        except FileNotFoundError:
            logger.error("Pandoc is not installed")
            return False

        # Create a directory for PDF exports
        pdf_dir = os.path.join(self.results_dir, "pdf")
        os.makedirs(pdf_dir, exist_ok=True)

        # Export each MDZ bundle to PDF
        for file_name in os.listdir(self.test_files_dir):
            if file_name.endswith(".mdz"):
                mdz_path = os.path.join(self.test_files_dir, file_name)
                pdf_path = os.path.join(pdf_dir, file_name.replace(".mdz", ".pdf"))

                try:
                    # Load the MDZ bundle
                    bundle = MDZBundle()
                    bundle.load(mdz_path)

                    # Extract to a temporary directory
                    extracted_assets = bundle.extract_to_temp()

                    # Create a renderer
                    renderer = MDZRenderer()

                    # Extract front matter
                    markdown_without_front_matter, front_matter = renderer.extract_front_matter(bundle.get_main_content())

                    # Extract and render Mermaid diagrams
                    mermaid_diagrams = renderer.extract_and_render_mermaid(markdown_without_front_matter)

                    # Render to PDF
                    pdf_content = renderer.render_to_pdf(
                        markdown_without_front_matter,
                        front_matter=front_matter,
                        mermaid_diagrams=mermaid_diagrams,
                        asset_paths=extracted_assets
                    )

                    if pdf_content:
                        # Save the PDF content
                        with open(pdf_path, "wb") as f:
                            f.write(pdf_content)

                        logger.info(f"Exported PDF: {pdf_path}")
                    else:
                        logger.error(f"Failed to render PDF for {file_name}")
                        return False
                except Exception as e:
                    logger.error(f"Error exporting PDF for {file_name}: {str(e)}")
                    return False

        return True

    def validate_outputs(self):
        """Validate the outputs"""
        logger.info("Validating outputs...")

        # Validate HTML outputs
        html_dir = os.path.join(self.results_dir, "html")
        if os.path.exists(html_dir):
            for file_name in os.listdir(html_dir):
                if file_name.endswith(".html"):
                    html_path = os.path.join(html_dir, file_name)

                    # Read the HTML content
                    with open(html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()

                    # Check for basic HTML structure
                    if not html_content.startswith("<!DOCTYPE html>"):
                        logger.warning(f"Invalid HTML structure in {file_name}")

                    # Check for title
                    if "<title>" not in html_content:
                        logger.warning(f"Missing title in {file_name}")

                    # Check for content
                    if "<body>" not in html_content:
                        logger.warning(f"Missing body in {file_name}")

                    # Check for specific features based on the file name
                    if "basic_markdown" in file_name:
                        if "<h1" not in html_content and "<H1" not in html_content:
                            logger.warning(f"Missing heading in {file_name}")
                        if "<ul" not in html_content and "<UL" not in html_content:
                            logger.warning(f"Missing unordered list in {file_name}")
                        if "<ol" not in html_content and "<OL" not in html_content:
                            logger.warning(f"Missing ordered list in {file_name}")
                        if "<blockquote" not in html_content and "<BLOCKQUOTE" not in html_content:
                            logger.warning(f"Missing blockquote in {file_name}")
                        if "<code" not in html_content and "<CODE" not in html_content:
                            logger.warning(f"Missing code in {file_name}")
                        # Don't return False for warnings

                    elif "gfm" in file_name:
                        if "<table" not in html_content and "<TABLE" not in html_content:
                            logger.warning(f"Missing table in {file_name}")
                        if "task-list-item" not in html_content and "checkbox" not in html_content:
                            logger.warning(f"Missing task list in {file_name}")

                    elif "mermaid" in file_name:
                        if "<svg" not in html_content:
                            logger.warning(f"Missing SVG in {file_name} - Mermaid diagrams may not be rendered")

                    elif "latex_math" in file_name:
                        if "MathJax" not in html_content:
                            logger.warning(f"Missing MathJax in {file_name} - LaTeX math may not be rendered")

                    elif "image" in file_name:
                        if "<img" not in html_content and "<IMG" not in html_content:
                            logger.warning(f"Missing images in {file_name}")

                    elif "comprehensive" in file_name:
                        # Check for all features
                        if "<h1" not in html_content and "<H1" not in html_content:
                            logger.warning(f"Missing heading in {file_name}")
                        if "<table" not in html_content and "<TABLE" not in html_content:
                            logger.warning(f"Missing table in {file_name}")
                        if "task-list-item" not in html_content and "checkbox" not in html_content:
                            logger.warning(f"Missing task list in {file_name}")
                        if "<img" not in html_content and "<IMG" not in html_content:
                            logger.warning(f"Missing images in {file_name}")

                    logger.info(f"Validated HTML: {file_name}")

        # Validate PDF outputs
        pdf_dir = os.path.join(self.results_dir, "pdf")
        if os.path.exists(pdf_dir):
            for file_name in os.listdir(pdf_dir):
                if file_name.endswith(".pdf"):
                    pdf_path = os.path.join(pdf_dir, file_name)

                    # Check if the PDF file exists and has content
                    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                        logger.error(f"Invalid PDF file: {file_name}")
                        return False

                    logger.info(f"Validated PDF: {file_name}")

        return True

    def run_validation(self):
        """Run the validation process"""
        logger.info("Running MDZ validation...")

        # Generate test files
        self.generate_test_files()

        # Create MDZ bundles
        if not self.create_mdz_bundles():
            logger.error("Failed to create MDZ bundles")
            return False

        # Test MDZ extraction
        if not self.test_mdz_extraction():
            logger.error("Failed to extract MDZ bundles")
            return False

        # Test HTML export
        if not self.test_html_export():
            logger.error("Failed to export HTML")
            return False

        # Test PDF export
        if not self.test_pdf_export():
            logger.error("Failed to export PDF")
            return False

        # Validate outputs
        if not self.validate_outputs():
            logger.error("Failed to validate outputs")
            return False

        logger.info("MDZ validation completed successfully")
        return True


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MDZ Comprehensive Validator")
    parser.add_argument("--output-dir", "-o", help="Directory to store test files and results")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip PDF export tests")
    parser.add_argument("--skip-html", action="store_true", help="Skip HTML export tests")
    parser.add_argument("--generate-only", action="store_true", help="Only generate test files, don't run validation")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing outputs, don't generate or export")

    args = parser.parse_args()

    # Create a validator
    validator = MDZValidator(output_dir=args.output_dir)

    if args.validate_only:
        # Only validate existing outputs
        if not validator.validate_outputs():
            logger.error("Validation failed")
            return 1
    elif args.generate_only:
        # Only generate test files
        validator.generate_test_files()
    else:
        # Run the full validation process
        success = True

        # Generate test files
        validator.generate_test_files()

        # Create MDZ bundles
        if not validator.create_mdz_bundles():
            logger.error("Failed to create MDZ bundles")
            success = False

        # Test MDZ extraction
        if success and not validator.test_mdz_extraction():
            logger.error("Failed to extract MDZ bundles")
            success = False

        # Test HTML export
        if success and not args.skip_html and not validator.test_html_export():
            logger.error("Failed to export HTML")
            success = False

        # Test PDF export
        if success and not args.skip_pdf and not validator.test_pdf_export():
            logger.error("Failed to export PDF")
            success = False

        # Validate outputs
        if success and not validator.validate_outputs():
            logger.error("Failed to validate outputs")
            success = False

        if success:
            logger.info("MDZ validation completed successfully")
            print("\nResults are available in the following directories:")
            print(f"  Test files: {validator.test_files_dir}")
            print(f"  Results: {validator.results_dir}")
            return 0
        else:
            logger.error("MDZ validation failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
