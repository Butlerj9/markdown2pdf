# Page Break Test Document

This document tests the page break functionality in the Markdown to PDF converter.

## Page 1 Content

This is the first page of the document. It contains some regular content that should appear on page 1.

### Regular Headings Don't Break Pages

This is an H3 heading. It should NOT create a page break because only explicit page break markers (---, ***, ___) should create page breaks.

#### Another Heading

This is an H4 heading. Again, this should NOT create a page break.

Here's some more content to fill up the first page. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

---

## Page 2 Content

This content should appear on page 2 because the three dashes (---) above create an explicit page break.

### More Content on Page 2

Here's some content for page 2. The page break was created by the horizontal rule (---) above, not by the heading.

This page should have different content from page 1, and you should be able to navigate between them using the page navigation controls.

***

## Page 3 Content

This content should appear on page 3 because the three asterisks (***) above create another explicit page break.

### Testing Different Page Break Markers

The previous page break was created using *** (three asterisks). This is another valid page break marker.

Let's add some more content to make this page substantial. Here are some bullet points:

- First bullet point
- Second bullet point
- Third bullet point
- Fourth bullet point

And some numbered items:

1. First numbered item
2. Second numbered item
3. Third numbered item
4. Fourth numbered item

___

## Page 4 Content

This content should appear on page 4 because the three underscores (___) above create yet another explicit page break.

### Final Page

This is the final page of our test document. The page break was created using ___ (three underscores), which is the third type of valid page break marker.

## Summary

This document demonstrates:

1. **Regular headings (H1, H2, H3, H4, etc.) do NOT create page breaks**
2. **Only explicit page break markers create page breaks:**
   - `---` (three dashes)
   - `***` (three asterisks) 
   - `___` (three underscores)
3. **Automatic page breaks are calculated based on content length and font settings**

The page preview should show 4 pages total, and you should be able to navigate between them using the page navigation controls.
