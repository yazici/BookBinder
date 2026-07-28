"""TOC generator — produces a clickable table of contents."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chapter:
    """A chapter entry with title and anchor for TOC linking."""

    number: int
    title: str
    anchor: str


class TocGenerator:
    """Generates a clickable table of contents with internal page anchors.

    Each chapter registered here gets a unique anchor ID. The TOC entries
    are rendered as clickable links that jump to the chapter heading.
    """

    def __init__(self) -> None:
        self._chapters: list[Chapter] = []

    def add_chapter(self, title: str) -> str:
        """Add a chapter and return its anchor ID."""
        num = len(self._chapters) + 1
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30].strip("-")
        anchor = f"chapter-{num}-{slug}" if slug else f"chapter-{num}"
        self._chapters.append(Chapter(number=num, title=title, anchor=anchor))
        return anchor

    @property
    def chapters(self) -> list[Chapter]:
        return list(self._chapters)

    @property
    def has_chapters(self) -> bool:
        return len(self._chapters) > 0

    def generate_html(self) -> str:
        """Generate clickable TOC HTML."""
        if not self._chapters:
            return ""

        entries = []
        for ch in self._chapters:
            entries.append(
                f'<div class="toc-entry">'
                f'<a href="#{ch.anchor}" class="toc-link">'
                f'<span class="toc-number">{ch.number:02d}</span>'
                f'<span class="toc-title">{ch.title}</span>'
                f'<span class="toc-dots"></span>'
                f"</a>"
                f"</div>"
            )

        return (
            '<div class="toc page-break">\n'
            '<h1 class="toc-heading">Contents</h1>\n'
            '<div class="toc-list">\n'
            + "\n".join(entries)
            + "\n</div>\n</div>"
        )