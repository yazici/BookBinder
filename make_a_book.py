#!/usr/bin/env python3
"""
book_maker.py — CLI entry point for BookBinder.

Converts Markdown books with semantic markers into professionally formatted PDFs.
This is the main script users invoke directly.

Usage:
    python book_maker.py BOOK.md
    python book_maker.py BOOK.md -o output.pdf --template modern --theme warm
    python book_maker.py BOOK.md --html-only
    python book_maker.py --self-bootstrap
    python book_maker.py --list-templates
    python book_maker.py --list-themes

Dependencies:
    pip install markdown jinja2 playwright pyyaml pygments
    playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Handle bootstrap before importing the package (which needs the deps)
if "--self-bootstrap" in sys.argv or "--force-dependencies" in sys.argv:
    # Add package to path
    sys.path.insert(0, str(Path(__file__).parent))
    from book_binder.bootstrap import bootstrap
    bootstrap(force="--force-dependencies" in sys.argv)
    if "--self-bootstrap" in sys.argv and len(sys.argv) <= 2:
        print("[BookBinder] Bootstrap complete.")
        raise SystemExit(0)

# Add package to path for normal operation
sys.path.insert(0, str(Path(__file__).parent))

try:
    from book_binder.maker import BookMaker
    from book_binder.templates import available_templates, available_themes
except ImportError as exc:
    print(
        f"Missing dependency: {exc}\n"
        "Run: python make_a_book.py --self-bootstrap",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BookBinder — Convert Markdown books to beautifully formatted PDFs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Semantic Markers (HTML comments — invisible in normal MD rendering):
  <!-- @book-meta ... -->              Book metadata (YAML block)
  <!-- @template: name -->             Select layout template
  <!-- @cover --> ... <!-- @end-cover -->  Front cover section
  <!-- @back-cover --> ... <!-- @end-back-cover -->  Back cover
  <!-- @foreword --> ... <!-- @end-foreword -->  Foreword section
  <!-- @toc -->                        Table of contents
  <!-- @index -->                      Back-of-book index
  <!-- @include: path.md -->           Include another file
  <!-- @chapter: Name -->              Chapter break
  <!-- @page-break -->                 Page break
  <!-- @figure: path | caption -->     Figure (auto-numbered)
  <!-- @figure: path | caption | id --> Figure with explicit ID
  <!-- @fig-ref: id -->                Reference a figure
  <!-- @tip: text -->                  Tip callout
  <!-- @note: text -->                 Note callout
  <!-- @warning: text -->              Warning callout
  <!-- @important: text -->            Important callout
  <!-- @index-term: term -->           Mark term for index
  <!-- @dedication: text -->           Dedication page
  <!-- @layout: two-column -->         Two-column layout
  <!-- @layout: single -->             Single-column layout

Examples:
  python book_maker.py BOOK.md
  python book_maker.py BOOK.md -o handbook.pdf --template modern --theme cool
  python book_maker.py BOOK.md --paper Letter --orientation landscape
  python book_maker.py BOOK.md --html-only
""",
    )

    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Markdown file to convert.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path. Defaults to source with .pdf/.html extension.",
    )
    parser.add_argument(
        "--template",
        default="",
        help="Layout template name (default, modern, technical).",
    )
    parser.add_argument(
        "--theme",
        default="",
        help="Color theme name (default, warm, cool, dark, minimal, academic).",
    )
    parser.add_argument(
        "--paper",
        default="A4",
        help="Paper size: A4, Letter, A3, Legal (default: A4).",
    )
    parser.add_argument(
        "--orientation",
        choices=["portrait", "landscape"],
        default="portrait",
        help="Page orientation (default: portrait).",
    )
    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Skip the cover page.",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Output HTML instead of PDF.",
    )
    parser.add_argument(
        "--self-bootstrap",
        action="store_true",
        help="Install missing dependencies before building.",
    )
    parser.add_argument(
        "--force-dependencies",
        action="store_true",
        help="Upgrade all dependencies.",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit.",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )

    args = parser.parse_args()

    # Info commands
    if args.list_templates:
        print("Available templates:")
        for t in available_templates():
            print(f"  • {t}")
        return

    if args.list_themes:
        print("Available themes:")
        for t in available_themes():
            print(f"  • {t}")
        return

    # Validate source
    if not args.source:
        parser.error("Source markdown file is required.")

    source = args.source.resolve()
    if not source.exists():
        print(f"Error: Source file not found: {source}", file=sys.stderr)
        raise SystemExit(1)
    if source.suffix.lower() != ".md":
        print(f"Error: Expected a Markdown file (.md): {source}", file=sys.stderr)
        raise SystemExit(1)

    # Build
    maker = BookMaker(
        source_path=source,
        template_name=args.template,
        theme_name=args.theme,
        paper_size=args.paper,
        orientation=args.orientation,
        skip_cover=args.no_cover,
    )

    if args.html_only:
        output = args.output.resolve() if args.output else None
        actual = maker.save_html(output)
        print(f"HTML generated: {actual}")
    else:
        output = args.output.resolve() if args.output else None
        actual = maker.build_pdf(output)
        print(f"PDF generated: {actual}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if "--verbose" in sys.argv:
            import traceback
            traceback.print_exc()
        raise SystemExit(1)