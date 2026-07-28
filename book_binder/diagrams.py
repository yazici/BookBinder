"""Diagram renderer — converts PlantUML (.puml) files to SVG for embedding.

PlantUML jar is auto-downloaded on first use if Java is available but no
plantuml installation is found. The jar is cached locally at:
    Scripts/BookBinder/.cache/plantuml.jar
"""

from __future__ import annotations

import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

# PlantUML jar download URL (MIT-licensed, stable release)
PLANTUML_JAR_URL = "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
PLANTUML_JAR_VERSION = "1.2024.8"

# Local cache directory (relative to this file)
_CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
_LOCAL_JAR = _CACHE_DIR / "plantuml.jar"


def _ensure_plantuml_jar() -> Path | None:
    """Download the PlantUML jar if not already cached. Returns jar path or None."""
    if _LOCAL_JAR.exists():
        return _LOCAL_JAR

    # Need Java to use the jar
    java = shutil.which("java")
    if not java:
        return None

    # Download
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        print(f"[BookBinder] Downloading PlantUML {PLANTUML_JAR_VERSION}...")
        urllib.request.urlretrieve(PLANTUML_JAR_URL, str(_LOCAL_JAR))
        print(f"[BookBinder] PlantUML jar cached at: {_LOCAL_JAR}")
        return _LOCAL_JAR
    except (OSError, urllib.error.URLError) as exc:
        print(f"[BookBinder] Failed to download PlantUML: {exc}")
        # Clean up partial download
        _LOCAL_JAR.unlink(missing_ok=True)
        return None


def find_plantuml() -> list[str] | None:
    """Find a working PlantUML invocation command.

    Checks in order:
    1. PLANTUML_JAR environment variable → java -jar $PLANTUML_JAR
    2. `plantuml` on PATH (e.g. from apt install plantuml)
    3. Common jar locations (system-wide)
    4. Local cached jar (auto-downloaded)

    Returns the command list (e.g. ["java", "-jar", "/path/to/plantuml.jar"])
    or None if not found.
    """
    java = shutil.which("java")

    # 1. Environment variable
    jar_env = os.environ.get("PLANTUML_JAR")
    if jar_env and Path(jar_env).exists() and java:
        return [java, "-jar", jar_env]

    # 2. plantuml CLI on PATH
    plantuml_cli = shutil.which("plantuml")
    if plantuml_cli:
        return [plantuml_cli]

    # 3. Common jar locations
    if java:
        common_jars = [
            Path.home() / ".local" / "share" / "plantuml" / "plantuml.jar",
            Path.home() / "plantuml.jar",
            Path("/usr/share/plantuml/plantuml.jar"),
            Path("/usr/local/share/plantuml/plantuml.jar"),
            Path("/opt/plantuml/plantuml.jar"),
        ]
        for jar_path in common_jars:
            if jar_path.exists():
                return [java, "-jar", str(jar_path)]

    # 4. Local cached jar (download if needed)
    if java:
        jar = _ensure_plantuml_jar()
        if jar:
            return [java, "-jar", str(jar)]

    return None


def render_puml_to_svg(puml_path: Path, output_dir: Path | None = None) -> Path | None:
    """Render a .puml file to .svg.

    If a .svg with the same stem already exists next to the .puml, returns
    that path without re-rendering (pre-rendered diagrams take priority).

    Args:
        puml_path: Path to the .puml source file.
        output_dir: Directory for the output SVG. Defaults to same dir as puml.

    Returns:
        Path to the rendered .svg file, or None if rendering failed.
    """
    if not puml_path.exists():
        return None

    # Check for pre-rendered SVG (same name, .svg extension)
    svg_sibling = puml_path.with_suffix(".svg")
    if svg_sibling.exists():
        return svg_sibling

    # Also check in output_dir if specified
    if output_dir:
        svg_in_output = output_dir / (puml_path.stem + ".svg")
        if svg_in_output.exists():
            return svg_in_output

    # Try to render
    cmd = find_plantuml()
    if cmd is None:
        return None

    target_dir = output_dir or puml_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        render_cmd = cmd + [
            "-tsvg",
            "-o", str(target_dir),
            str(puml_path),
        ]
        result = subprocess.run(
            render_cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            expected_svg = target_dir / (puml_path.stem + ".svg")
            if expected_svg.exists():
                return expected_svg
    except (subprocess.TimeoutExpired, OSError):
        pass

    return None


def can_render_diagrams() -> bool:
    """Check if PlantUML rendering is available."""
    return find_plantuml() is not None