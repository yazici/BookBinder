"""Figure registry — tracks numbered, referenceable figures."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Figure:
    """A registered figure with number and optional ID for cross-referencing."""

    number: int
    path: str
    caption: str
    fig_id: str
    chapter: str = ""


class FigureRegistry:
    """Tracks all figures for numbering and cross-referencing.

    Figures are auto-numbered sequentially. Each figure gets a unique ID
    (either explicit from the markdown or auto-generated) that can be
    referenced elsewhere in the document with @fig-ref markers.
    """

    def __init__(self) -> None:
        self._figures: list[Figure] = []
        self._by_id: dict[str, Figure] = {}
        self._counter: int = 0

    def register(self, path: str, caption: str, fig_id: str = "", chapter: str = "") -> Figure:
        """Register a new figure and return its Figure object."""
        self._counter += 1
        if not fig_id:
            # Auto-generate ID from caption
            slug = re.sub(r"[^a-z0-9]+", "-", caption.lower())[:40].strip("-")
            fig_id = f"fig-{self._counter}-{slug}" if slug else f"fig-{self._counter}"
        fig = Figure(
            number=self._counter,
            path=path,
            caption=caption,
            fig_id=fig_id,
            chapter=chapter,
        )
        self._figures.append(fig)
        self._by_id[fig_id] = fig
        return fig

    def get(self, fig_id: str) -> Figure | None:
        """Look up a figure by its ID."""
        return self._by_id.get(fig_id)

    @property
    def all_figures(self) -> list[Figure]:
        """All registered figures in order."""
        return list(self._figures)

    @property
    def count(self) -> int:
        return self._counter