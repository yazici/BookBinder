"""Markdown processor — resolves includes, extracts metadata, processes semantic markers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from book_binder.diagrams import render_puml_to_svg
from book_binder.figures import FigureRegistry
from book_binder.index import IndexGenerator
from book_binder.metadata import BookMetadata
from book_binder.toc import TocGenerator

# =============================================================================
# MARKER PATTERNS
# =============================================================================

RE_BOOK_META = re.compile(r"<!--\s*@book-meta\s*\n(.*?)\n\s*-->", re.DOTALL)
RE_INCLUDE = re.compile(r"<!--\s*@include:\s*(.+?)\s*-->")
RE_CHAPTER = re.compile(r"<!--\s*@chapter:\s*(.+?)\s*-->")
RE_PAGE_BREAK = re.compile(r"<!--\s*@page-break\s*-->")
RE_COVER_START = re.compile(r"<!--\s*@cover\s*-->")
RE_COVER_END = re.compile(r"<!--\s*@end-cover\s*-->")
RE_BACK_COVER_START = re.compile(r"<!--\s*@back-cover\s*-->")
RE_BACK_COVER_END = re.compile(r"<!--\s*@end-back-cover\s*-->")
RE_FOREWORD_START = re.compile(r"<!--\s*@foreword\s*-->")
RE_FOREWORD_END = re.compile(r"<!--\s*@end-foreword\s*-->")
RE_TOC = re.compile(r"<!--\s*@toc\s*-->")
RE_INDEX = re.compile(r"<!--\s*@index\s*-->")
RE_FIGURE = re.compile(r"<!--\s*@figure:\s*(.+?)\s*-->")
RE_FIG_REF = re.compile(r"<!--\s*@fig-ref:\s*(.+?)\s*-->")
RE_TIP = re.compile(r"<!--\s*@tip:\s*(.+?)\s*-->")
RE_NOTE = re.compile(r"<!--\s*@note:\s*(.+?)\s*-->")
RE_WARNING = re.compile(r"<!--\s*@warning:\s*(.+?)\s*-->")
RE_IMPORTANT = re.compile(r"<!--\s*@important:\s*(.+?)\s*-->")
RE_SIDEBAR = re.compile(r"<!--\s*@sidebar:\s*(.+?)\s*-->")
RE_INDEX_TERM = re.compile(r"<!--\s*@index-term:\s*(.+?)\s*-->")
RE_LAYOUT_TWO_COL = re.compile(r"<!--\s*@layout:\s*two-column\s*-->")
RE_LAYOUT_SINGLE = re.compile(r"<!--\s*@layout:\s*single\s*-->")
RE_COLOR_PALETTE = re.compile(r"<!--\s*@color-palette:\s*(.+?)\s*-->")
RE_DEDICATION = re.compile(r"<!--\s*@dedication:\s*(.+?)\s*-->")
RE_TEMPLATE = re.compile(r"<!--\s*@template:\s*(.+?)\s*-->")
RE_SOURCE_DIR = re.compile(r"<!--\s*@_source_dir:\s*(.+?)\s*-->")


class MarkdownProcessor:
    """Processes markdown source: resolves includes, extracts metadata, transforms markers.

    This is the first stage of the pipeline. It takes raw markdown text and produces
    processed text with HTML markers ready for the markdown-to-HTML converter.
    """

    def __init__(self) -> None:
        self.figures = FigureRegistry()
        self.index = IndexGenerator()
        self.toc = TocGenerator()
        self.metadata = BookMetadata()
        self._current_chapter: str = ""
        self._current_source_dir: Path | None = None

    def process(self, source_path: Path) -> str:
        """Full processing pipeline: read → includes → metadata → markers."""
        text = source_path.read_text(encoding="utf-8")
        base_dir = source_path.parent

        # 1. Resolve @include directives recursively
        text = self._resolve_includes(text, base_dir)

        # 2. Extract @book-meta
        text = self._extract_metadata(text)

        # 3. Extract @template directive (if present outside meta)
        text = self._extract_template(text)

        # 4. Process all semantic markers
        text = self._process_markers(text, base_dir)

        return text

    def _resolve_includes(self, text: str, base_dir: Path, depth: int = 0) -> str:
        """Recursively resolve @include directives."""
        if depth > 10:
            raise RecursionError("Include depth exceeded 10 levels — possible circular include.")

        def replace_include(match: re.Match) -> str:
            include_path = base_dir / match.group(1).strip()
            if not include_path.exists():
                return f"<!-- MISSING INCLUDE: {match.group(1)} -->"
            included_text = include_path.read_text(encoding="utf-8")
            included_dir = include_path.parent.resolve()
            # Inject source-dir marker so figures resolve relative to the included file
            marker = f"<!-- @_source_dir: {included_dir} -->\n"
            resolved = self._resolve_includes(included_text, include_path.parent, depth + 1)
            return marker + resolved

        return RE_INCLUDE.sub(replace_include, text)

    def _extract_metadata(self, text: str) -> str:
        """Extract @book-meta YAML block and populate self.metadata."""
        match = RE_BOOK_META.search(text)
        if match:
            data = yaml.safe_load(match.group(1)) or {}
            self.metadata = BookMetadata.from_dict(data)
            text = text[: match.start()] + text[match.end() :]
        return text

    def _extract_template(self, text: str) -> str:
        """Extract standalone @template directive."""
        match = RE_TEMPLATE.search(text)
        if match:
            self.metadata.template = match.group(1).strip()
            text = text[: match.start()] + text[match.end() :]
        return text

    def _resolve_figure(self, img_path: Path) -> Path | None:
        """Resolve a figure path, handling diagram rendering for .puml files.

        Resolution order:
        1. If the file exists directly (png, svg, jpg, etc.), return it.
        2. If it's a .puml file, try to find/render an SVG:
           a. Check for a pre-rendered .svg sibling
           b. Attempt PlantUML rendering to SVG
        3. Return None if nothing resolves.
        """
        # Direct file exists
        if img_path.exists():
            suffix = img_path.suffix.lower()
            # If it's a .puml file, we need to render it to SVG
            if suffix == ".puml":
                svg_path = render_puml_to_svg(img_path)
                return svg_path  # May be None if rendering fails
            return img_path

        # File doesn't exist — check if it's a .puml reference with a .svg sibling
        if img_path.suffix.lower() == ".puml":
            svg_sibling = img_path.with_suffix(".svg")
            if svg_sibling.exists():
                return svg_sibling

        # Check for common image format alternatives
        if img_path.suffix.lower() in (".png", ".jpg", ".jpeg"):
            svg_alt = img_path.with_suffix(".svg")
            if svg_alt.exists():
                return svg_alt

        return None

    def _make_figure_html(self, figure_spec: str, base_dir: Path) -> str:
        """Generate HTML for a single figure marker.

        Args:
            figure_spec: The content after @figure: (path | caption | id)
            base_dir: The book root directory (fallback for resolution)

        Resolution order for figure paths:
            1. Absolute path (starts with /) → used directly
            2. Relative to the chapter file's directory
            3. Inside the chapter's figures/ subfolder (bare filename shorthand)
            4. Fallback: relative to the book root (BOOK.md directory)
        """
        parts = [p.strip() for p in figure_spec.split("|")]
        path = parts[0] if len(parts) >= 1 else ""
        caption = parts[1] if len(parts) >= 2 else ""
        fig_id = parts[2] if len(parts) >= 3 else ""

        fig = self.figures.register(path, caption, fig_id, self._current_chapter)

        # Resolve path: absolute if starts with /, else relative to source dir
        if path.startswith("/"):
            img_path = Path(path)
        else:
            img_path = (self._current_source_dir or base_dir) / path
        resolved_path = self._resolve_figure(img_path)
        # Fallback: check figures/ subfolder of the chapter directory
        if not resolved_path and self._current_source_dir:
            resolved_path = self._resolve_figure(self._current_source_dir / "figures" / path)
        # Fallback: try book root if not found relative to chapter
        if not resolved_path and self._current_source_dir and self._current_source_dir != base_dir:
            resolved_path = self._resolve_figure(base_dir / path)

        if resolved_path and resolved_path.exists():
            uri = resolved_path.resolve().as_uri()
            img_tag = f'<img src="{uri}" alt="{caption}">'
        else:
            # Show descriptive placeholder with caption and path
            placeholder_caption = caption if caption else path
            img_tag = (
                f'<div class="figure-placeholder">'
                f'<span class="figure-placeholder-caption">{placeholder_caption}</span>'
                f'<span class="figure-placeholder-path">{path}</span>'
                f'</div>'
            )

        return (
            f'\n\n<div class="figure no-break" id="{fig.fig_id}">'
            f"{img_tag}"
            f'<div class="figure-caption">'
            f'<span class="figure-number">Figure {fig.number}.</span> {caption}'
            f"</div></div>\n\n"
        )

    def _process_markers(self, text: str, base_dir: Path) -> str:
        """Process all semantic markers and convert to HTML-ready markers."""
        self._current_source_dir = base_dir

        # --- Source directory tracking + Figures (processed together to maintain
        #     positional context — source_dir markers update the active directory
        #     before subsequent figures are resolved) ---
        RE_SOURCE_OR_FIGURE = re.compile(
            r"(?:<!--\s*@_source_dir:\s*(.+?)\s*-->)|(?:<!--\s*@figure:\s*(.+?)\s*-->)"
        )

        def source_or_figure_replace(m: re.Match) -> str:
            if m.group(1) is not None:
                # Source directory marker
                self._current_source_dir = Path(m.group(1).strip())
                return ""
            else:
                # Figure marker
                return self._make_figure_html(m.group(2), base_dir)

        text = RE_SOURCE_OR_FIGURE.sub(source_or_figure_replace, text)

        # --- Cover sections ---
        text = RE_COVER_START.sub('<div class="cover-page"><div class="cover-content">', text)
        text = RE_COVER_END.sub("</div></div>", text)
        text = RE_BACK_COVER_START.sub('<div class="back-cover page-break"><div class="back-cover-content">', text)
        text = RE_BACK_COVER_END.sub("</div></div>", text)

        # --- Foreword ---
        text = RE_FOREWORD_START.sub('<div class="foreword">', text)
        text = RE_FOREWORD_END.sub("</div>", text)

        # --- Dedication ---
        def dedication_replace(m: re.Match) -> str:
            content = m.group(1).strip()
            return (
                f'\n\n<div class="dedication-page">'
                f'<p class="dedication-text">{content}</p>'
                f"</div>\n\n"
            )
        text = RE_DEDICATION.sub(dedication_replace, text)

        # --- Chapter breaks ---
        def chapter_replace(m: re.Match) -> str:
            title = m.group(1).strip()
            self._current_chapter = title
            anchor = self.toc.add_chapter(title)
            return (
                f'\n\n<div class="chapter-break chapter-header" id="{anchor}">'
                f"<h1>{title}</h1></div>\n\n"
            )
        text = RE_CHAPTER.sub(chapter_replace, text)

        # --- Page breaks ---
        text = RE_PAGE_BREAK.sub('\n\n<div class="page-break"></div>\n\n', text)

        # --- Figures already processed above with source_dir tracking ---

        # --- Figure references ---
        def fig_ref_replace(m: re.Match) -> str:
            ref_id = m.group(1).strip()
            fig = self.figures.get(ref_id)
            if fig:
                return f'<a href="#{fig.fig_id}" class="fig-ref">Figure {fig.number}</a>'
            return f'<span class="fig-ref">[Figure ??:{ref_id}]</span>'
        text = RE_FIG_REF.sub(fig_ref_replace, text)

        # --- Callouts ---
        def callout_replace(kind: str):
            def replacer(m: re.Match) -> str:
                content = m.group(1).strip()
                return (
                    f'\n\n<div class="callout callout-{kind}">'
                    f'<div class="callout-header"></div>'
                    f'<div class="callout-body">{content}</div>'
                    f"</div>\n\n"
                )
            return replacer

        text = RE_TIP.sub(callout_replace("tip"), text)
        text = RE_NOTE.sub(callout_replace("note"), text)
        text = RE_WARNING.sub(callout_replace("warning"), text)
        text = RE_IMPORTANT.sub(callout_replace("important"), text)
        text = RE_SIDEBAR.sub(callout_replace("sidebar"), text)

        # --- Index terms ---
        def index_term_replace(m: re.Match) -> str:
            term = m.group(1).strip()
            anchor = self.index.add_term(term, self._current_chapter)
            return f'<span id="{anchor}" class="index-anchor"></span>'
        text = RE_INDEX_TERM.sub(index_term_replace, text)

        # --- Layout ---
        text = RE_LAYOUT_TWO_COL.sub('\n\n<div class="two-column">\n\n', text)
        text = RE_LAYOUT_SINGLE.sub("\n\n</div>\n\n", text)

        # --- Color palette ---
        def palette_replace(m: re.Match) -> str:
            colors = [c.strip() for c in m.group(1).split(",")]
            swatches = "".join(
                f'<div class="color-swatch" style="background:{c}" data-color="{c}"></div>'
                for c in colors
            )
            return f'\n\n<div class="color-palette">{swatches}</div>\n\n'
        text = RE_COLOR_PALETTE.sub(palette_replace, text)

        # --- TOC placeholder ---
        text = RE_TOC.sub('\n\n<div id="toc-placeholder"></div>\n\n', text)


        # --- Index placeholder ---
        text = RE_INDEX.sub('\n\n<div id="index-placeholder"></div>\n\n', text)

        return text