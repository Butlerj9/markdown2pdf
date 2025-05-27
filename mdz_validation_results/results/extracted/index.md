---
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

