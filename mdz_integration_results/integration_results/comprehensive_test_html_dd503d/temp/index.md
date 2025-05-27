---
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

$$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$

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

