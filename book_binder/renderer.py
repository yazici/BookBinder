"""HTML renderer — assembles the final HTML document from processed markdown."""

from __future__ import annotations

import markdown

from book_binder.metadata import BookMetadata
from book_binder.processor import MarkdownProcessor
from book_binder.templates import LoadedTemplate, Theme


class HtmlRenderer:
    """Assembles the final HTML document from processed content.

    Combines:
    - Theme CSS variables (:root block)
    - Template stylesheet (style.css)
    - Front cover (from template or inline)
    - Dedication page
    - TOC (clickable)
    - Body content (markdown → HTML)
    - Index (auto-generated)
    - Back cover (from template or inline)
    """

    def __init__(
        self,
        template: LoadedTemplate,
        theme: Theme,
        paper_size: str = "A4",
        orientation: str = "portrait",
    ) -> None:
        self.template = template
        self.theme = theme
        self.paper_size = paper_size
        self.orientation = orientation

    def render(self, processor: MarkdownProcessor, processed_text: str, skip_cover: bool = False) -> str:
        """Render the complete HTML document."""
        meta = processor.metadata

        # Convert markdown to HTML
        content_html = self._markdown_to_html(processed_text)

        # Generate TOC and inject
        toc_html = processor.toc.generate_html()
        content_html = content_html.replace(
            '<div id="toc-placeholder"></div>', toc_html
        )

        # Generate index and inject
        index_html = processor.index.generate_html()
        content_html = content_html.replace(
            '<div id="index-placeholder"></div>', index_html
        )

        # Build the full document
        parts: list[str] = []

        # Front cover
        if not skip_cover:
            # Check if there's an inline cover in the content (from @cover markers)
            if '<div class="cover-page">' in content_html:
                # Inline cover is already in the content, don't add template cover
                pass
            else:
                # Use template cover
                cover_html = self.template.render_cover(meta)
                if cover_html:
                    parts.append(cover_html)

        parts.append(content_html)

        # Back cover (if not already inline)
        if '<div class="back-cover' not in content_html:
            back_cover_html = self.template.render_back_cover(meta)
            if back_cover_html:
                parts.append(back_cover_html)

        body_content = "\n".join(parts)

        # Assemble full HTML
        css_vars = self.theme.to_css_variables(self.paper_size, self.orientation)
        template_css = self.template.css

        return self._wrap_html(meta.title, css_vars, template_css, body_content, meta.language)

    def _markdown_to_html(self, text: str) -> str:
        """Convert processed markdown text to HTML."""
        return markdown.markdown(
            text,
            extensions=[
                "extra",
                "tables",
                "fenced_code",
                "sane_lists",
                "toc",
                "codehilite",
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "guess_lang": False,
                }
            },
        )

    def _wrap_html(
        self,
        title: str,
        css_vars: str,
        template_css: str,
        body: str,
        language: str,
    ) -> str:
        """Wrap content in a complete HTML document."""
        return (
            f'<!doctype html>\n'
            f'<html lang="{language}">\n'
            f'<head>\n'
            f'<meta charset="utf-8">\n'
            f'<title>{title}</title>\n'
            f'<style>\n{css_vars}\n{template_css}\n</style>\n'
            f'</head>\n'
            f'<body>\n'
            f'{body}\n'
            f'</body>\n'
            f'</html>'
        )