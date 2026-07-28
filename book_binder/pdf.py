"""PDF renderer — converts HTML to PDF using Playwright/Chromium."""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


class PdfRenderer:
    """Renders HTML to PDF using a headless Chromium browser via Playwright.

    The HTML is written to a temporary file, loaded in Chromium, and printed
    to PDF with full CSS @page support, backgrounds, and custom margins.
    """

    def __init__(self, paper: str = "A4", orientation: str = "portrait") -> None:
        self.paper = paper
        self.orientation = orientation

    async def render_async(self, html: str, output_path: Path) -> None:
        """Render HTML string to PDF file (async)."""
        temp_html = output_path.with_suffix(".bookbinder.tmp.html")
        temp_html.write_text(html, encoding="utf-8")

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                page = await browser.new_page()

                await page.goto(
                    temp_html.resolve().as_uri(),
                    wait_until="networkidle",
                )

                await page.pdf(
                    path=str(output_path),
                    format=self.paper,
                    landscape=(self.orientation == "landscape"),
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={
                        "top": "0",
                        "right": "0",
                        "bottom": "0",
                        "left": "0",
                    },
                )

                await browser.close()
        finally:
            temp_html.unlink(missing_ok=True)

    def render(self, html: str, output_path: Path) -> None:
        """Render HTML string to PDF file (sync wrapper)."""
        asyncio.run(self.render_async(html, output_path))