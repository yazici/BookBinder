<!-- @chapter: Extended Markdown Syntax -->

<!-- @index-term: extended syntax -->
<!-- @index-term: semantic markers -->

# Extended Markdown Syntax

BookBinder extends standard Markdown with **semantic markers** — special HTML comments that are invisible in normal Markdown renderers but control book structure, layout, and formatting when processed by BookBinder.

All markers use the format:

```markdown
<!-- @marker-name: value -->
```

or for block markers:

```markdown
<!-- @marker-start -->
content
<!-- @end-marker-start -->
```

Because they are HTML comments, your Markdown files remain valid and render normally in GitHub, VS Code preview, or any other Markdown viewer.

## Book Metadata

<!-- @index-term: metadata -->
<!-- @index-term: book-meta -->

The `@book-meta` block defines your book's metadata as YAML inside an HTML comment:

```markdown
<!-- @book-meta
title: "My Book Title"
subtitle: "An Informative Subtitle"
author: "Author Name"
version: "2.0"
date: "2026"
theme: warm
template: modern
accent_color: "#b78a51"
cover_image: "covers/front.png"
publisher: "Publisher Name"
isbn: "978-0-000000-00-0"
language: "en"
file_name: "MyBookTitle"
-->
```

### Available Metadata Fields

| Field | Purpose | Default |
|-------|---------|---------|
| `title` | Book title (used in cover, headers, filename) | "Untitled" |
| `subtitle` | Subtitle (cover and title page) | — |
| `author` | Author name(s) | — |
| `version` | Version string | — |
| `date` | Publication date | — |
| `theme` | Color theme name | "default" |
| `template` | Layout template name | "default" |
| `accent_color` | Override theme accent color (hex) | — |
| `cover_image` | Path to cover image | — |
| `publisher` | Publisher name (back cover) | — |
| `isbn` | ISBN (back cover) | — |
| `language` | HTML lang attribute | "en" |
| `file_name` | Explicit output filename (without extension) | — |

<!-- @tip: You can also set the template outside the metadata block with a standalone `<!-- @template: name -->` directive anywhere in the file. -->

## File Includes

<!-- @index-term: includes -->
<!-- @index-term: @include -->

The `@include` directive inserts the contents of another Markdown file:

```markdown
<!-- @include: chapters/01_introduction.md -->
<!-- @include: chapters/02_getting_started.md -->
<!-- @include: appendix/glossary.md -->
```

### Path Resolution

Paths are resolved **relative to the file containing the directive**. This means included files can themselves include other files with paths relative to their own location.

### Recursive Includes

Includes are resolved recursively up to 10 levels deep:

```markdown
<!-- In BOOK.md -->
<!-- @include: parts/part1.md -->

<!-- In parts/part1.md -->
<!-- @include: chapters/ch1.md -->
<!-- @include: chapters/ch2.md -->

<!-- In parts/chapters/ch1.md -->
<!-- @include: sections/intro.md -->
```

<!-- @warning: Circular includes (A includes B which includes A) will trigger an error after 10 levels of recursion. -->

### Missing Includes

If an included file doesn't exist, BookBinder inserts a visible placeholder:

```html
<!-- MISSING INCLUDE: path/to/file.md -->
```

This renders in the output so you can spot missing files during development.

## Cover Pages

<!-- @index-term: cover -->

### Front Cover

```markdown
<!-- @cover -->

# Book Title

## Subtitle

*Description or tagline*

<!-- @figure: covers/hero.png | Cover illustration -->

<!-- @end-cover -->
```

The content between `@cover` and `@end-cover` is wrapped in a full-page cover layout. If no inline cover is provided, BookBinder uses the template's `cover.html` Jinja2 template with metadata variables.

### Back Cover

```markdown
<!-- @back-cover -->

## About This Book

Brief description for the back cover.

<!-- @end-back-cover -->
```

## Chapters and Structure

<!-- @index-term: chapters -->
<!-- @index-term: @chapter -->

### Chapter Breaks

```markdown
<!-- @chapter: Getting Started -->
```

This creates:
- A page break before the chapter
- A chapter header with the title
- A TOC entry
- Sets the current chapter context (for figure numbering and index terms)

### Page Breaks

```markdown
<!-- @page-break -->
```

Forces a page break at that point in the output. Useful between major sections that don't warrant a full chapter marker.

### Dedication Page

```markdown
<!-- @dedication: To my family, who tolerated the sound of a mechanical keyboard at 2 AM. -->
```

Renders a centered dedication page with elegant typography.

## Table of Contents

<!-- @index-term: table of contents -->
<!-- @index-term: TOC -->

```markdown
<!-- @toc -->
```

Generates a clickable table of contents from all `@chapter` markers. Place it after the cover and before the first chapter include.

The TOC is automatically populated — you don't need to maintain it manually.

## Figures and Cross-References

<!-- @index-term: figures -->
<!-- @index-term: @figure -->

### Basic Figure

```markdown
<!-- @figure: diagrams/architecture.png | System architecture overview -->
```

This renders a numbered figure with caption: "Figure 1. System architecture overview"

### Figure with Explicit ID

```markdown
<!-- @figure: diagrams/flow.png | Data flow diagram | data-flow -->
```

The third parameter sets an explicit ID for cross-referencing.

### Figure Path Resolution

Figures are resolved in this order:

1. Absolute path (starts with `/`)
2. Relative to the chapter file's directory
3. Inside the chapter's `figures/` subfolder (bare filename shorthand)
4. Relative to the book root (`BOOK.md` directory)

### Cross-Referencing Figures

```markdown
As shown in <!-- @fig-ref: data-flow -->, the data flows through three stages.
```

Renders as: "As shown in Figure 2, the data flows through three stages." — with a clickable link to the figure.

### PlantUML Diagrams

<!-- @index-term: PlantUML -->
<!-- @index-term: diagrams -->

BookBinder can render `.puml` files directly:

```markdown
<!-- @figure: diagrams/sequence.puml | Authentication sequence -->
```

If Java and PlantUML are available, the `.puml` file is rendered to SVG automatically. If a pre-rendered `.svg` file exists alongside the `.puml`, it's used without re-rendering.

<!-- @note: PlantUML rendering requires Java. If Java is not installed, BookBinder looks for a pre-rendered `.svg` with the same name. Include pre-rendered SVGs in version control for environments without Java. -->

## Callouts

<!-- @index-term: callouts -->
<!-- @index-term: admonitions -->

BookBinder provides four callout types for highlighting important information:

### Tip

```markdown
<!-- @tip: Use `--html-only` during development for faster iteration. -->
```

<!-- @tip: This is how a tip callout looks in the rendered output. -->

### Note

```markdown
<!-- @note: This feature requires BookBinder 1.0 or later. -->
```

<!-- @note: This is how a note callout looks in the rendered output. -->

### Warning

```markdown
<!-- @warning: This operation cannot be undone. Back up your data first. -->
```

<!-- @warning: This is how a warning callout looks in the rendered output. -->

### Important

```markdown
<!-- @important: You must run bootstrap before first use. -->
```

<!-- @important: This is how an important callout looks in the rendered output. -->

### Sidebar

```markdown
<!-- @sidebar: Historical context — BookBinder was originally designed for game documentation. -->
```

Sidebars are styled as supplementary information panels, visually distinct from the main text flow.

## Index

<!-- @index-term: index -->
<!-- @index-term: back-of-book index -->

### Marking Index Terms

Sprinkle index term markers throughout your text:

```markdown
<!-- @index-term: authentication -->
<!-- @index-term: OAuth 2.0 -->
```

These are invisible in the output but register the term at that location.

### Generating the Index

```markdown
<!-- @index -->
```

Place this at the end of your book. It generates an alphabetical back-of-book index with page/section references for every marked term.

## Layout Control

<!-- @index-term: layout -->
<!-- @index-term: two-column -->

### Two-Column Layout

```markdown
<!-- @layout: two-column -->

Content here flows in two columns. Useful for reference tables,
glossaries, or dense information.

<!-- @layout: single -->
```

Switch back to single-column with `<!-- @layout: single -->`.

## Foreword

<!-- @index-term: foreword -->

```markdown
<!-- @foreword -->

This book represents three years of development experience...

*— Foreword Author*

<!-- @end-foreword -->
```

The foreword section receives special styling (typically italic, indented) appropriate for introductory material written by someone other than the main author.

## Color Palette

<!-- @index-term: color palette -->

Display a visual color palette (useful for design documentation):

```markdown
<!-- @color-palette: #2c5a8a, #4a9eff, #f0f4f8, #1a3a5c, #ffffff -->
```

Renders as a row of color swatches with hex values.

## Template Selection (Inline)

You can select a template outside the metadata block:

```markdown
<!-- @template: technical -->
```

This overrides the template specified in `@book-meta` (but CLI `--template` takes highest priority).

## Marker Reference

Complete list of all semantic markers:

| Marker | Purpose |
|--------|---------|
| `<!-- @book-meta ... -->` | Book metadata (YAML) |
| `<!-- @template: name -->` | Select template |
| `<!-- @cover -->` | Start front cover |
| `<!-- @end-cover -->` | End front cover |
| `<!-- @back-cover -->` | Start back cover |
| `<!-- @end-back-cover -->` | End back cover |
| `<!-- @foreword -->` | Start foreword |
| `<!-- @end-foreword -->` | End foreword |
| `<!-- @toc -->` | Table of contents |
| `<!-- @index -->` | Back-of-book index |
| `<!-- @include: path -->` | Include file |
| `<!-- @chapter: Name -->` | Chapter break |
| `<!-- @page-break -->` | Page break |
| `<!-- @figure: path \| caption -->` | Figure |
| `<!-- @figure: path \| caption \| id -->` | Figure with ID |
| `<!-- @fig-ref: id -->` | Figure reference |
| `<!-- @tip: text -->` | Tip callout |
| `<!-- @note: text -->` | Note callout |
| `<!-- @warning: text -->` | Warning callout |
| `<!-- @important: text -->` | Important callout |
| `<!-- @sidebar: text -->` | Sidebar callout |
| `<!-- @index-term: term -->` | Index term |
| `<!-- @dedication: text -->` | Dedication page |
| `<!-- @layout: two-column -->` | Two-column layout |
| `<!-- @layout: single -->` | Single-column layout |
| `<!-- @color-palette: colors -->` | Color swatches |

## Priority and Override Order

When the same setting is specified in multiple places, this priority applies (highest first):

1. **CLI flags** (`--template`, `--theme`)
2. **Inline directives** (`<!-- @template: ... -->`)
3. **Metadata block** (`@book-meta` YAML)
4. **Defaults** (template: "default", theme: "default")