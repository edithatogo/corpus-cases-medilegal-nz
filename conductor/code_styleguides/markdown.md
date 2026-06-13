# Markdown Style Guide

## 1. General Principles
*   Use standard GitHub Flavored Markdown (GFM).
*   Maintain a single, blank line between paragraphs and sections.
*   Enforce a maximum line length of 100 characters for prose, where possible, to ensure readable diffs.

## 2. Headings
*   Use ATX headings (`# Heading`). Do not use Setext headings (underlined with `=` or `-`).
*   Always include a space after the heading marker: `# Title`, not `#Title`.
*   Maintain a hierarchical structure: do not skip heading levels (e.g., `#` followed directly by `###`).

## 3. Lists
*   Use asterisks `*` for unordered lists.
*   Indent nested lists with 4 spaces.
*   Maintain a space after list markers.

## 4. Metadata (YAML Frontmatter)
For processed corpus Markdown files (Format A), the YAML frontmatter block must:
*   Begin and end with exactly three hyphens (`---`).
*   Include standard fields in camel_case or snake_case, strictly defined.
*   Use double quotes for string values containing special characters or colons.
