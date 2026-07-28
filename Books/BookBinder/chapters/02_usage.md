<!-- @chapter: Usage -->

<!-- @index-term: usage -->
<!-- @index-term: CLI -->
<!-- @index-term: command line -->

# Usage

This chapter covers how to use BookBinder from the command line — from the simplest one-liner to advanced multi-file book projects.

## Basic Usage

The simplest invocation converts a single Markdown file to PDF:

```bash
python make_a_book.py BOOK.md
```

This reads `BOOK.md`, processes all semantic markers, applies the default template and theme, and writes a PDF to the same directory. The output filename is derived from the book's title metadata.

## Command-Line Options

```
python make_a_book.py [OPTIONS] SOURCE.md
```

| Option | Description |
|--------|-------------|
| `SOURCE.md` | The Markdown file to convert (required) |
| `-o, --output PATH` | Explicit output path (overrides auto-naming) |
| `--template NAME` | Layout template: `default`, `modern`, `technical` |
| `--theme NAME` | Color theme: `default`, `warm`, `cool`, `dark`, `minimal`, `academic` |
| `--paper SIZE` | Paper size: `A4`, `Letter`, `A3`, `Legal` |
| `--orientation DIR` | `portrait` or `landscape` |
| `--no-cover` | Skip the cover page |
| `--html-only` | Output HTML instead of PDF |
| `--self-bootstrap` | Install missing dependencies |
| `--force-dependencies` | Upgrade all dependencies |
| `--list-templates` | List available templates and exit |
| `--list-themes` | List available themes and exit |
| `--verbose` | Enable verbose error output |

## Examples

### Generate a PDF with defaults

```bash
python make_a_book.py my_book/BOOK.md
```

Output: `my_book/MyBookTitle.pdf` (filename derived from `@book-meta` title)

### Specify output path

```bash
python make_a_book.py BOOK.md -o /tmp/handbook.pdf
```

### Choose a template and theme

```bash
python make_a_book.py BOOK.md --template modern --theme cool
```

### Generate HTML for debugging

```bash
python make_a_book.py BOOK.md --html-only
```

This produces an HTML file you can open in any browser to inspect layout, styling, and content before committing to PDF.

<!-- @tip: Use `--html-only` during development to iterate quickly. HTML renders instantly while PDF generation takes a few seconds. -->

### US Letter paper, landscape

```bash
python make_a_book.py BOOK.md --paper Letter --orientation landscape
```

### Skip the cover page

```bash
python make_a_book.py BOOK.md --no-cover
```

## Project Structure

A BookBinder project is simply a directory containing a `BOOK.md` file and optional chapter files:

```
MyBook/
├── BOOK.md              ← Main entry point
├── chapters/
│   ├── 01_intro.md
│   ├── 02_getting_started.md
│   ├── 03_advanced.md
│   └── ...
└── figures/             ← Optional images/diagrams
    ├── architecture.png
    └── workflow.puml
```

<!-- @note: The directory structure is a convention, not a requirement. BookBinder resolves `@include` paths relative to the file containing the directive. You can organize files however you prefer. -->

### The BOOK.md File

`BOOK.md` is the entry point. It typically contains:

1. **Metadata block** — title, author, theme selection
2. **Cover section** — front cover content
3. **Table of contents** — auto-generated
4. **Include directives** — pulling in chapter files
5. **Index** — auto-generated from index terms

Here's a minimal example:

```markdown
<!-- @​book-meta
title: "My Project Handbook"
subtitle: "A Complete Reference"
author: "Your Name"
version: "1.0"
date: "2026"
-->

<!-- @​cover -->
# My Project Handbook
## A Complete Reference
<!-- @​end-cover -->

<!-- @​toc -->

<!-- @​include: chapters/01_intro.md -->
<!-- @​include: chapters/02_details.md -->

<!-- @​index -->
```

### Chapter Files

Each chapter file is a standalone Markdown file. It typically starts with a chapter marker:

```markdown
<!-- @​chapter: Introduction -->

# Introduction

Your chapter content here...
```

The `@chapter` marker creates a page break, registers the chapter in the table of contents, and sets the current chapter context for figure numbering and index terms.

## The Build Pipeline

When you run `make_a_book.py`, the following pipeline executes:

<!-- @index-term: pipeline -->

1. **Markdown Processing** — Resolves `@include` directives recursively, extracts `@book-meta` YAML, processes all semantic markers into HTML-ready markup
2. **Template & Theme Loading** — Loads the CSS stylesheet and cover HTML templates based on metadata or CLI flags
3. **HTML Rendering** — Converts processed Markdown to HTML using Python-Markdown with extensions (tables, fenced code, syntax highlighting), injects TOC and index, wraps in a complete HTML document
4. **PDF Generation** — Launches headless Chromium via Playwright, loads the HTML, and prints to PDF with proper page sizing

## Output Filename Logic

If you don't specify `-o`, BookBinder derives the output filename:

1. If `file_name` is set in `@book-meta`, that name is used
2. Otherwise, the `title` is converted to PascalCase with punctuation removed

Examples:

| Title | Output Filename |
|-------|----------------|
| "GDL User's Guide" | `GDLUsersGuide.pdf` |
| "My Project Handbook" | `MyProjectHandbook.pdf` |
| "BookBinder User Guide" | `BookBinderUserGuide.pdf` |

The output file is always placed in the same directory as the source `BOOK.md`.

## Working with Multiple Books

You can have multiple books in a single repository:

```
Books/
├── UserGuide/
│   ├── BOOK.md
│   └── chapters/
├── DevGuide/
│   ├── BOOK.md
│   └── chapters/
└── APIReference/
    ├── BOOK.md
    └── chapters/
```

Build each independently:

```bash
python make_a_book.py Books/UserGuide/BOOK.md
python make_a_book.py Books/DevGuide/BOOK.md
python make_a_book.py Books/APIReference/BOOK.md
```

<!-- @tip: Create a simple shell script or Makefile to build all books at once if your project has many. -->

## Error Handling

If something goes wrong, BookBinder prints a concise error message. For full stack traces, add `--verbose`:

```bash
python make_a_book.py BOOK.md --verbose
```

Common errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing dependency: ...` | Python package not installed | Run `--self-bootstrap` |
| `Source file not found` | Wrong path to BOOK.md | Check the file path |
| `Expected a Markdown file (.md)` | Non-.md file passed | Rename or use correct file |
| `Include depth exceeded 10 levels` | Circular `@include` | Check for include loops |
| `MISSING INCLUDE: path` | Referenced file doesn't exist | Create the file or fix the path |