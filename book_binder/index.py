"""Index generator — auto-generates a clickable back-of-book index."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class IndexEntry:
    """An entry in the back-of-book index."""

    term: str
    chapter: str = ""
    anchor: str = ""


class IndexGenerator:
    """Collects index terms and generates a clickable alphabetical index.

    Terms are marked in the source with <!-- @index-term: term --> markers.
    The generator collects all terms, deduplicates them, groups by letter,
    and produces a clickable HTML index for the back of the book.
    """

    def __init__(self) -> None:
        self._entries: list[IndexEntry] = []

    def add_term(self, term: str, chapter: str = "") -> str:
        """Add a term and return an anchor ID to place in the document."""
        anchor = f"idx-{len(self._entries)}-{re.sub(r'[^a-z0-9]', '', term.lower())}"
        self._entries.append(IndexEntry(term=term, chapter=chapter, anchor=anchor))
        return anchor

    @property
    def entries(self) -> list[IndexEntry]:
        return list(self._entries)

    @property
    def has_entries(self) -> bool:
        return len(self._entries) > 0

    def generate_html(self) -> str:
        """Generate the index HTML grouped alphabetically with links."""
        if not self._entries:
            return ""

        # Group by first letter
        grouped: dict[str, list[IndexEntry]] = {}
        for entry in sorted(self._entries, key=lambda e: e.term.lower()):
            letter = entry.term[0].upper() if entry.term else "#"
            grouped.setdefault(letter, []).append(entry)

        html_parts = [
            '<div class="book-index page-break">',
            '<h1 class="index-title">Index</h1>',
            '<div class="index-columns">',
        ]

        for letter, entries in sorted(grouped.items()):
            html_parts.append('<div class="index-letter-group">')
            html_parts.append(f'<h2 class="index-letter">{letter}</h2>')
            # Deduplicate terms
            seen: set[str] = set()
            for entry in entries:
                key = entry.term.lower()
                if key in seen:
                    continue
                seen.add(key)
                html_parts.append(
                    f'<div class="index-entry">'
                    f'<a href="#{entry.anchor}" class="index-link">{entry.term}</a>'
                    f"</div>"
                )
            html_parts.append("</div>")

        html_parts.append("</div>")  # index-columns
        html_parts.append("</div>")  # book-index
        return "\n".join(html_parts)