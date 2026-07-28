<!-- @chapter: Templates and Themes -->

<!-- @index-term: templates -->
<!-- @index-term: themes -->

# Templates and Themes

BookBinder separates visual presentation into two layers: **templates** control layout and structure, while **themes** control colors and typography. This separation lets you mix and match — use the `technical` template with the `warm` theme, or the `modern` template with the `dark` theme.

## Built-in Templates

<!-- @index-term: default template -->
<!-- @index-term: modern template -->
<!-- @index-term: technical template -->

BookBinder ships with three templates:

| Template | Description | Best For |
|----------|-------------|----------|
| `default` | Classic book layout with serif typography | General-purpose books, manuals |
| `modern` | Clean sans-serif design with generous whitespace | User guides, marketing docs |
| `technical` | Compact layout with monospace accents, alternating table rows | API docs, developer guides |

List available templates:

```bash
python make_a_book.py --list-templates
```

### Selecting a Template

Three ways to select a template (in priority order):

```bash
# 1. CLI flag (highest priority)
python make_a_book.py BOOK.md --template modern

# 2. Inline directive in Markdown
<!-- @template: modern -->

# 3. In @book-meta YAML
<!-- @book-meta
template: modern
-->
```

## Built-in Themes

<!-- @index-term: default theme -->
<!-- @index-term: warm theme -->
<!-- @index-term: cool theme -->
<!-- @index-term: dark theme -->
<!-- @index-term: minimal theme -->
<!-- @index-term: academic theme -->

BookBinder ships with six color themes:

| Theme | Accent Color | Description |
|-------|-------------|-------------|
| `default` | Blue (#2c5a8a) | Professional blue on white |
| `warm` | Golden (#b78a51) | Warm amber tones, inviting feel |
| `cool` | Teal (#2a7a8a) | Cool blue-green, modern |
| `dark` | Light blue (#4a9eff) | Dark background, light text |
| `minimal` | Gray (#555555) | Monochrome, distraction-free |
| `academic` | Deep red (#8b2252) | Traditional academic styling |

List available themes:

```bash
python make_a_book.py --list-themes
```

### Selecting a Theme

```bash
# CLI flag
python make_a_book.py BOOK.md --theme warm

# In @book-meta YAML
<!-- @book-meta
theme: warm
-->
```

### Accent Color Override

Override just the accent color without creating a full custom theme:

```markdown
<!-- @book-meta
theme: warm
accent_color: "#e67e22"
-->
```

This uses the `warm` theme's fonts and background but replaces the accent color.

## Theme Anatomy

<!-- @index-term: CSS custom properties -->
<!-- @index-term: YAML theme -->

A theme is a YAML file defining CSS custom properties. Here's the complete structure:

```yaml
# themes/my_theme.yaml
name: my_theme
description: A custom theme for my project

colors:
  accent: "#2c5a8a"        # Primary accent (headings, links, borders)
  accent-light: "#f0f4f8"  # Light accent (backgrounds, callout fills)
  accent-dark: "#1a3a5c"   # Dark accent (hover states, emphasis)
  text: "#1a1a1a"          # Body text color
  bg: "#ffffff"            # Page background
  code-bg: "#f7f8fa"       # Code block background

fonts:
  heading: "'Georgia', serif"
  body: "'Charter', 'Georgia', serif"
  mono: "'JetBrains Mono', monospace"
```

These values become CSS custom properties:

```css
:root {
    --accent: #2c5a8a;
    --accent-light: #f0f4f8;
    --accent-dark: #1a3a5c;
    --text: #1a1a1a;
    --bg: #ffffff;
    --code-bg: #f7f8fa;
    --font-heading: 'Georgia', serif;
    --font-body: 'Charter', 'Georgia', serif;
    --font-mono: 'JetBrains Mono', monospace;
}
```

## Template Anatomy

<!-- @index-term: template structure -->
<!-- @index-term: style.css -->
<!-- @index-term: cover.html -->

A template is a directory containing three files:

```
templates/my_template/
├── style.css           ← Main stylesheet
├── cover.html          ← Front cover (Jinja2 template)
└── back_cover.html     ← Back cover (Jinja2 template)
```

### style.css

The stylesheet uses CSS custom properties from the active theme. This means a single template works with any theme:

```css
/* Use theme variables */
h1, h2, h3 {
    color: var(--accent);
    font-family: var(--font-heading);
}

body {
    color: var(--text);
    background: var(--bg);
    font-family: var(--font-body);
}

code, pre {
    font-family: var(--font-mono);
    background: var(--code-bg);
}

.callout {
    border-left: 4px solid var(--accent);
    background: var(--accent-light);
}
```

### cover.html

A Jinja2 template for the front cover. Available variables:

| Variable | Source |
|----------|--------|
| `{{ title }}` | `@book-meta` title |
| `{{ subtitle }}` | `@book-meta` subtitle |
| `{{ author }}` | `@book-meta` author |
| `{{ version }}` | `@book-meta` version |
| `{{ date }}` | `@book-meta` date |
| `{{ cover_image }}` | `@book-meta` cover_image |
| `{{ publisher }}` | `@book-meta` publisher |
| `{{ isbn }}` | `@book-meta` isbn |

Example cover template:

```html
<div class="cover-page">
    <div class="cover-content">
        {% if cover_image %}
        <img src="{{ cover_image }}" class="cover-image" alt="Cover">
        {% endif %}
        <h1 class="cover-title">{{ title }}</h1>
        {% if subtitle %}
        <h2 class="cover-subtitle">{{ subtitle }}</h2>
        {% endif %}
        {% if author %}
        <p class="cover-author">{{ author }}</p>
        {% endif %}
        {% if version %}
        <p class="cover-version">Version {{ version }}</p>
        {% endif %}
    </div>
</div>
```

### back_cover.html

Same Jinja2 variables as the front cover. Typically shows publisher info, ISBN, and a brief description.

## Creating a Custom Theme

<!-- @index-term: custom theme -->

1. Create a YAML file in `book_binder/templates/themes/`:

```bash
cp book_binder/templates/themes/default.yaml book_binder/templates/themes/my_project.yaml
```

2. Edit the colors and fonts:

```yaml
name: my_project
description: Custom theme for My Project documentation

colors:
  accent: "#e74c3c"
  accent-light: "#fdf2f2"
  accent-dark: "#922b21"
  text: "#2c3e50"
  bg: "#ffffff"
  code-bg: "#f8f9fa"

fonts:
  heading: "'Inter', 'Helvetica Neue', sans-serif"
  body: "'Source Sans Pro', 'Helvetica', sans-serif"
  mono: "'Fira Code', 'Consolas', monospace"
```

3. Use it:

```bash
python make_a_book.py BOOK.md --theme my_project
```

<!-- @tip: Start by copying an existing theme that's close to what you want, then adjust colors. The `warm` theme is a good starting point for most custom themes. -->

## Creating a Custom Template

<!-- @index-term: custom template -->

1. Create a directory in `book_binder/templates/`:

```bash
mkdir book_binder/templates/my_layout
```

2. Create the three required files:

```bash
# Start from an existing template
cp book_binder/templates/modern/style.css book_binder/templates/my_layout/
cp book_binder/templates/modern/cover.html book_binder/templates/my_layout/
cp book_binder/templates/modern/back_cover.html book_binder/templates/my_layout/
```

3. Customize `style.css` for your layout needs. Key CSS classes to style:

| CSS Class | Element |
|-----------|---------|
| `.cover-page` | Front cover container |
| `.back-cover` | Back cover container |
| `.chapter-break` | Chapter title page |
| `.chapter-header` | Chapter heading |
| `.figure` | Figure container |
| `.figure-caption` | Figure caption text |
| `.callout` | Callout box |
| `.callout-tip` | Tip-specific styling |
| `.callout-note` | Note-specific styling |
| `.callout-warning` | Warning-specific styling |
| `.callout-important` | Important-specific styling |
| `.toc` | Table of contents |
| `.index-section` | Back-of-book index |
| `.two-column` | Two-column layout region |
| `.dedication-page` | Dedication page |
| `.foreword` | Foreword section |
| `.highlight` | Syntax-highlighted code |
| `.page-break` | Page break element |
| `.no-break` | Prevent page break inside |

4. Use your template:

```bash
python make_a_book.py BOOK.md --template my_layout
```

## Page Size and Orientation

<!-- @index-term: paper size -->
<!-- @index-term: page orientation -->

Templates automatically adapt to the paper size and orientation specified via CLI:

```bash
python make_a_book.py BOOK.md --paper A4 --orientation portrait
python make_a_book.py BOOK.md --paper Letter --orientation landscape
```

Supported paper sizes:

| Size | Dimensions |
|------|-----------|
| `A4` | 210 × 297 mm |
| `Letter` | 8.5 × 11 in |
| `A3` | 297 × 420 mm |
| `Legal` | 8.5 × 14 in |

The paper size and orientation are available as CSS custom properties (`--paper-size` and `--orientation`) for templates that need to adjust layout based on page dimensions.

## Design Guidelines

When creating custom templates and themes, keep these principles in mind:

### For Themes

- **Contrast**: Ensure sufficient contrast between text and background (WCAG AA minimum)
- **Accent usage**: The accent color should be used sparingly — headings, links, borders, callout accents
- **Code readability**: `code-bg` should provide enough contrast for syntax-highlighted code
- **Print-friendliness**: If the book will be printed, avoid very dark backgrounds

### For Templates

- **Use CSS custom properties**: Always reference `var(--accent)`, `var(--font-body)`, etc. instead of hardcoding colors. This ensures your template works with any theme.
- **Page breaks**: Use `page-break-before: always` on `.chapter-break` and `.page-break` elements
- **Avoid orphans/widows**: Use `orphans: 3; widows: 3;` on body text
- **Figure handling**: Figures should have `page-break-inside: avoid` to prevent splitting across pages
- **Responsive to paper size**: Test your template with both A4 and Letter sizes

<!-- @note: BookBinder's PDF engine (Playwright/Chromium) supports CSS Paged Media properties like `@page`, `page-break-before`, `page-break-after`, and `page-break-inside`. Use these for precise print layout control. -->

## Example: Complete Custom Setup

Here's a complete example of a book using a custom theme with accent override:

```markdown
<!-- @book-meta
title: "Project Phoenix Documentation"
subtitle: "Internal Developer Reference"
author: "Phoenix Team"
version: "3.1"
date: "2026"
template: technical
theme: cool
accent_color: "#e67e22"
file_name: "PhoenixDocs"
-->

<!-- @cover -->
# Project Phoenix
## Internal Developer Reference
*Version 3.1 — 2026*
<!-- @end-cover -->

<!-- @toc -->

<!-- @include: chapters/01_overview.md -->
<!-- @include: chapters/02_api.md -->
<!-- @include: chapters/03_deployment.md -->

<!-- @back-cover -->
## Project Phoenix
Internal documentation. Not for external distribution.
<!-- @end-back-cover -->

<!-- @index -->
```

Build with:

```bash
python make_a_book.py BOOK.md
# Output: PhoenixDocs.pdf (technical template, cool theme, orange accent)