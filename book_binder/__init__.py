"""
BookBinder — Modular OOP Markdown-to-PDF book generator.

Converts Markdown with semantic markers into professionally formatted PDFs.
Features: clickable TOC, auto-index, front/back covers, foreword, tip sections,
referenceable figures, selectable templates (CSS/HTML files), justified text.

Architecture:
    bookbinder/
    ├── metadata.py      — BookMetadata dataclass
    ├── figures.py       — FigureRegistry (numbered, linkable figures)
    ├── index.py         — IndexGenerator (auto back-of-book index)
    ├── toc.py           — TocGenerator (clickable table of contents)
    ├── processor.py     — MarkdownProcessor (includes, markers)
    ├── renderer.py      — HtmlRenderer (assembles final HTML)
    ├── pdf.py           — PdfRenderer (HTML → PDF via Playwright)
    ├── maker.py         — BookMaker (orchestrator)
    ├── bootstrap.py     — Dependency management
    └── templates/
        ├── __init__.py  — Template/theme loader
        ├── themes/      — YAML theme definitions
        ├── default/     — Default template (style.css, cover.html, back_cover.html)
        ├── modern/      — Modern template
        └── technical/   — Technical template
"""

__version__ = "2.0.0"

# Lazy imports to avoid import errors when dependencies aren't installed yet
__all__ = [
    "BookMaker",
    "BookMetadata",
    "FigureRegistry",
    "Figure",
    "IndexGenerator",
    "IndexEntry",
    "TocGenerator",
    "Chapter",
    "MarkdownProcessor",
    "HtmlRenderer",
    "PdfRenderer",
]


def __getattr__(name: str):
    """Lazy import to allow bootstrap to run before deps are available."""
    if name == "BookMaker":
        from book_binder.maker import BookMaker
        return BookMaker
    if name == "BookMetadata":
        from book_binder.metadata import BookMetadata
        return BookMetadata
    if name in ("FigureRegistry", "Figure"):
        from book_binder import figures
        return getattr(figures, name)
    if name in ("IndexGenerator", "IndexEntry"):
        from book_binder import index
        return getattr(index, name)
    if name in ("TocGenerator", "Chapter"):
        from book_binder import toc
        return getattr(toc, name)
    if name == "MarkdownProcessor":
        from book_binder.processor import MarkdownProcessor
        return MarkdownProcessor
    if name == "HtmlRenderer":
        from book_binder.renderer import HtmlRenderer
        return HtmlRenderer
    if name == "PdfRenderer":
        from book_binder.pdf import PdfRenderer
        return PdfRenderer
    raise AttributeError(f"module 'book_binder' has no attribute {name!r}")
