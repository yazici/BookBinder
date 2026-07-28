"""Template system — loads CSS/HTML template files and YAML theme definitions from disk.

Templates are directories containing:
    style.css       — Main stylesheet (uses CSS custom properties)
    cover.html      — Front cover Jinja2 template
    back_cover.html — Back cover Jinja2 template

Themes are YAML files in the themes/ subdirectory defining CSS custom properties.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template as JinjaTemplate

from book_binder.metadata import BookMetadata

# Root directory for all templates
_TEMPLATES_DIR = Path(__file__).parent


def available_templates() -> list[str]:
    """List all available template names (directories with style.css)."""
    return sorted(
        d.name
        for d in _TEMPLATES_DIR.iterdir()
        if d.is_dir() and (d / "style.css").exists()
    )


def available_themes() -> list[str]:
    """List all available theme names (YAML files in themes/)."""
    themes_dir = _TEMPLATES_DIR / "themes"
    if not themes_dir.exists():
        return []
    return sorted(p.stem for p in themes_dir.glob("*.yaml"))


class Theme:
    """A loaded theme with color and font definitions."""

    def __init__(self, name: str, data: dict[str, Any]) -> None:
        self.name = name
        self.description: str = data.get("description", "")
        colors = data.get("colors", {})
        fonts = data.get("fonts", {})

        # Color properties
        self.accent: str = colors.get("accent", "#2c5a8a")
        self.accent_light: str = colors.get("accent-light", "#f0f4f8")
        self.accent_dark: str = colors.get("accent-dark", "#1a3a5c")
        self.text: str = colors.get("text", "#1a1a1a")
        self.bg: str = colors.get("bg", "#ffffff")
        self.code_bg: str = colors.get("code-bg", "#f7f8fa")

        # Font properties
        self.font_heading: str = fonts.get("heading", "'Georgia', serif")
        self.font_body: str = fonts.get("body", "'Charter', 'Georgia', serif")
        self.font_mono: str = fonts.get("mono", "'JetBrains Mono', monospace")

    def to_css_variables(self, paper_size: str = "A4", orientation: str = "portrait") -> str:
        """Generate a :root block with all CSS custom properties."""
        return (
            ":root {\n"
            f"    --accent: {self.accent};\n"
            f"    --accent-light: {self.accent_light};\n"
            f"    --accent-dark: {self.accent_dark};\n"
            f"    --text: {self.text};\n"
            f"    --bg: {self.bg};\n"
            f"    --code-bg: {self.code_bg};\n"
            f"    --font-heading: {self.font_heading};\n"
            f"    --font-body: {self.font_body};\n"
            f"    --font-mono: {self.font_mono};\n"
            f"    --paper-size: {paper_size};\n"
            f"    --orientation: {orientation};\n"
            "}\n"
        )

    def with_accent_override(self, accent: str) -> "Theme":
        """Return a copy with a custom accent color."""
        import copy
        t = copy.copy(self)
        t.accent = accent
        return t


def load_theme(name: str, accent_override: str = "") -> Theme:
    """Load a theme by name from the themes/ directory."""
    theme_file = _TEMPLATES_DIR / "themes" / f"{name}.yaml"
    if not theme_file.exists():
        # Fall back to default
        theme_file = _TEMPLATES_DIR / "themes" / "default.yaml"
    data = yaml.safe_load(theme_file.read_text(encoding="utf-8")) or {}
    theme = Theme(name=name, data=data)
    if accent_override:
        theme = theme.with_accent_override(accent_override)
    return theme


class LoadedTemplate:
    """A fully loaded template with CSS and HTML cover templates ready to render."""

    def __init__(self, name: str, template_dir: Path) -> None:
        self.name = name
        self._dir = template_dir

        # Load CSS
        css_path = template_dir / "style.css"
        self.css: str = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

        # Load cover templates (Jinja2)
        cover_path = template_dir / "cover.html"
        self._cover_template: str = cover_path.read_text(encoding="utf-8") if cover_path.exists() else ""

        back_cover_path = template_dir / "back_cover.html"
        self._back_cover_template: str = back_cover_path.read_text(encoding="utf-8") if back_cover_path.exists() else ""

    def render_cover(self, meta: BookMetadata, cover_image: str = "") -> str:
        """Render the front cover HTML with metadata variables."""
        if not self._cover_template:
            return ""
        tpl = JinjaTemplate(self._cover_template)
        return tpl.render(
            title=meta.title,
            subtitle=meta.subtitle,
            author=meta.author,
            version=meta.version,
            date=meta.date,
            cover_image=cover_image,
            publisher=meta.publisher,
            isbn=meta.isbn,
        )

    def render_back_cover(self, meta: BookMetadata) -> str:
        """Render the back cover HTML with metadata variables."""
        if not self._back_cover_template:
            return ""
        tpl = JinjaTemplate(self._back_cover_template)
        return tpl.render(
            title=meta.title,
            subtitle=meta.subtitle,
            author=meta.author,
            version=meta.version,
            date=meta.date,
            publisher=meta.publisher,
            isbn=meta.isbn,
        )


def load_template(name: str) -> LoadedTemplate:
    """Load a template by name. Falls back to 'default' if not found."""
    template_dir = _TEMPLATES_DIR / name
    if not template_dir.exists() or not (template_dir / "style.css").exists():
        template_dir = _TEMPLATES_DIR / "default"
    return LoadedTemplate(name=name, template_dir=template_dir)


__all__ = [
    "Theme",
    "LoadedTemplate",
    "load_theme",
    "load_template",
    "available_templates",
    "available_themes",
]