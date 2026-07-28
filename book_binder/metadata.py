"""Book metadata dataclass — parsed from @book-meta YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BookMetadata:
    """Parsed book metadata from @book-meta YAML block."""

    title: str = "Untitled"
    subtitle: str = ""
    author: str = ""
    version: str = ""
    date: str = ""
    theme: str = "default"
    template: str = "default"
    accent_color: str = ""
    cover_image: str = ""
    dedication: str = ""
    foreword_author: str = ""
    publisher: str = ""
    isbn: str = ""
    language: str = "en"
    file_name: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BookMetadata:
        """Create metadata from a dictionary, ignoring unknown keys."""
        known_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def derive_filename(self, extension: str = ".pdf") -> str:
        """Derive output filename from file_name field or sanitized title.

        Priority:
            1. file_name field (if set in @book-meta)
            2. Sanitized title in PascalCase (spaces/punctuation removed)

        Examples:
            "GDL User's Guide" → "GDLUsersGuide.pdf"
            "GDL Developer's Guide" → "GDLDevelopersGuide.pdf"
        """
        if self.file_name:
            name = self.file_name
            # Ensure it has the right extension
            if not name.endswith(extension):
                name = name.rsplit(".", 1)[0] if "." in name else name
                name += extension
            return name

        # Sanitize title to PascalCase filename
        import re
        # Remove possessives and common punctuation
        sanitized = self.title.replace("'s", "s").replace("'s", "s")
        # Split on non-alphanumeric, capitalize each word, join
        words = re.split(r"[^a-zA-Z0-9]+", sanitized)
        pascal = "".join(w.capitalize() if not w.isupper() else w for w in words if w)
        if not pascal:
            pascal = "Book"
        return pascal + extension
