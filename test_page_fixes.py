#!/usr/bin/env python3
"""
Test script to verify the page preview fixes:
1. No blank line at the top (title removal)
2. Better page height utilization
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from page_preview import PagePreview
from render_utils import RenderUtils

def test_page_fixes():
    """Test the page preview fixes"""
    print("Testing page preview fixes...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create page preview instance
    preview = PagePreview()
    
    # Test markdown content
    test_content = """# JOSHUA DAVID BUTLER

Oakland, CA 94612 | (510) 692-1491 | josh.d.butler@gmail.com

## SUMMARY

Highly experienced technology leader with 20+ years in software development, hardware-software integration, and startup leadership. Expert in cross-functional agile, DevOps methodologies, and IoT ecosystem development.

## PROFESSIONAL EXPERIENCE

### CATALYST, Oakland, CA

**Founder & CEO | 10/2022 - Present**

- Founded 3rd-tier technology consultancy focused on helping businesses implement transformative AI solutions
- Developed proprietary frameworks for AI integration that consistently deliver 5-10x productivity improvements

### PREVIOUS ROLES

**Senior Software Engineer** - Various companies (2010-2022)
- Led development teams of 5-15 engineers
- Implemented CI/CD pipelines reducing deployment time by 80%
- Architected scalable microservices handling millions of requests daily

## TECHNICAL SKILLS

- **Languages**: Python, JavaScript, TypeScript, Go, Rust, C++
- **Frameworks**: React, Node.js, Django, FastAPI, Express
- **Cloud**: AWS, Azure, GCP, Docker, Kubernetes
- **Databases**: PostgreSQL, MongoDB, Redis, Elasticsearch

## EDUCATION

**Bachelor of Science in Computer Science**
University of California, Berkeley | 2008

This is additional content to test page height utilization and ensure we're using the full page space effectively.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
"""
    
    print("1. Testing HTML content cleaning...")
    
    # Test the clean_html_content method
    test_html_with_title = """<h1 class="title">Document</h1>
<p class="title">Some title</p>
<div class="title">Another title</div>
<p></p>
<br>
<br>
Document
<h1>JOSHUA DAVID BUTLER</h1>
<p>Oakland, CA 94612 | (510) 692-1491 | josh.d.butler@gmail.com</p>"""
    
    cleaned = preview.clean_html_content(test_html_with_title)
    print(f"Original HTML (first 200 chars): {test_html_with_title[:200]}")
    print(f"Cleaned HTML (first 200 chars): {cleaned[:200]}")
    
    # Check if title elements were removed
    has_title_elements = any([
        'class="title"' in cleaned,
        'Document\n' in cleaned,
        cleaned.startswith('<p></p>'),
        cleaned.startswith('<br>')
    ])
    
    if not has_title_elements:
        print("✓ Title elements and blank lines successfully removed")
    else:
        print("✗ Title elements or blank lines still present")
    
    print("\n2. Testing page height calculation...")
    
    # Test document settings
    test_settings = {
        "fonts": {
            "body": {
                "size": 12,
                "line_height": 1.5
            }
        }
    }
    
    preview.set_document_settings(test_settings)
    
    # Test automatic page break calculation
    pages = preview.calculate_automatic_page_breaks(test_content)
    print(f"Content split into {len(pages)} pages")
    
    # Check if we're using reasonable page capacity
    if len(pages) <= 2:  # Should fit in 1-2 pages with better height utilization
        print("✓ Page height utilization improved - content fits in fewer pages")
    else:
        print(f"✗ Page height utilization may need improvement - {len(pages)} pages generated")
    
    print("\n3. Testing complete preview rendering...")
    
    # Test the complete preview update process
    try:
        # Simulate the render process
        RenderUtils.render_markdown_to_preview(test_content, preview, test_settings)
        print("✓ Preview rendering completed successfully")
    except Exception as e:
        print(f"✗ Preview rendering failed: {e}")
    
    print("\nTest completed!")
    
    # Clean up
    app.quit()

if __name__ == "__main__":
    test_page_fixes()
