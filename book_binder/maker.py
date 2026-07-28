"""BookMaker — main orchestrator that ties all components together."""

from __future__ import annotations

from pathlib import Path

from book_binder.processor import MarkdownProcessor
from book_binder.renderer import HtmlRenderer
from book_binder.pdf import PdfRenderer
from book_binder.templates import load_template, load_theme


class BookMaker:
    """Main orchestrator for the book generation pipeline.

    Pipeline:
        1. MarkdownProcessor: resolve includes, extract metadata, process markers
        2. Template + Theme loading based on metadata/CLI options
        3. HtmlRenderer: assemble final HTML with CSS, covers, TOC, index
        4. PdfRenderer: convert HTML to PDF via Playwright/Chromium

    Usage:
        maker = BookMaker(source_path)
        maker.build_pdf(output_path)
        # or
        html = maker.build_html()
    """

    def __init__(
        self,
        source_path: Path,
        *,
        template_name: str = "",
        theme_name: str = "",
        paper_size: str = "A4",
        orientation: str = "portrait",
        skip_cover: bool = False,
    ) -> None:
        self.source_path = source_path.resolve()
        self._template_override = template_name
        self._theme_override = theme_name
        self.paper_size = paper_size
        self.orientation = orientation
        self.skip_cover = skip_cover

        # These are populated during build
        self._processor: MarkdownProcessor | None = None
        self._html: str | None = None

    @property
    def processor(self) -> MarkdownProcessor:
        """Access the processor (available after build)."""
        if self._processor is None:
            raise RuntimeError("Call build_html() or build_pdf() first.")
        return self._processor

    def build_html(self) -> str:
        """Run the full pipeline and return the HTML string."""
        # 1. Process markdown
        self._processor = MarkdownProcessor()
        processed_text = self._processor.process(self.source_path)

        # 2. Determine template and theme
        meta = self._processor.metadata
        template_name = self._template_override or meta.template or "default"
        theme_name = self._theme_override or meta.theme or "default"
        accent_override = meta.accent_color

        template = load_template(template_name)
        theme = load_theme(theme_name, accent_override)

        # 3. Render HTML
        renderer = HtmlRenderer(
            template=template,
            theme=theme,
            paper_size=self.paper_size,
            orientation=self.orientation,
        )
        self._html = renderer.render(
            self._processor,
            processed_text,
            skip_cover=self.skip_cover,
        )
        return self._html

    def derive_output_path(self, extension: str = ".pdf") -> Path:
        """Derive the output path from metadata (file_name or sanitized title).

        The output file is placed in the same directory as the source file.
        Examples:
            "GDL User's Guide" → <source_dir>/GDLUsersGuide.pdf
            "GDL Developer's Guide" → <source_dir>/GDLDevelopersGuide.pdf
        """
        # We need metadata, so do a quick parse if not already done
        if self._processor is None:
            import yaml
            import re
            from book_binder.metadata import BookMetadata
            text = self.source_path.read_text(encoding="utf-8")
            match = re.search(r"<!--\s*@book-meta\s*\n(.*?)\n\s*-->", text, re.DOTALL)
            if match:
                data = yaml.safe_load(match.group(1)) or {}
                meta = BookMetadata.from_dict(data)
            else:
                meta = BookMetadata()
        else:
            meta = self._processor.metadata

        filename = meta.derive_filename(extension)
        return self.source_path.parent / filename

    def build_pdf(self, output_path: Path | None = None) -> Path:
        """Run the full pipeline and write a PDF file.

        If output_path is None, derives filename from metadata.
        Returns the actual output path used.
        """
        if output_path is None:
            output_path = self.derive_output_path(".pdf")
        html = self.build_html()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_renderer = PdfRenderer(paper=self.paper_size, orientation=self.orientation)
        pdf_renderer.render(html, output_path)
        return output_path

    def save_html(self, output_path: Path | None = None) -> Path:
        """Run the full pipeline and write the HTML file.

        If output_path is None, derives filename from metadata.
        Returns the actual output path used.
        """
        if output_path is None:
            output_path = self.derive_output_path(".html")
        html = self.build_html()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        return output_path
